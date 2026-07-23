from __future__ import annotations

W, H = 1080, 1920


def _flash_clip(fps: int = 30) -> 'VideoClip':
    """2-frame (~66ms) emerald flash VideoClip inserted between scenes."""
    import numpy as np
    from moviepy.editor import VideoClip
    from reels.animator import EMERALD

    color = np.array([[EMERALD]], dtype=np.uint8)
    tile  = np.tile(color, (1920, 1080, 1))

    def make_frame(t):
        factor = max(0.0, 1.0 - t / (2 / fps))
        return (tile * factor).astype(np.uint8)

    return VideoClip(make_frame, duration=2 / fps).set_fps(fps)


def _zoom_punch_bridge(clip_a, clip_b, dur: float = 0.20, fps: int = 30) -> 'VideoClip':
    """Zoom-punch: A scales out while darkening, B scales in from slightly large."""
    import numpy as np
    from PIL import Image
    from moviepy.editor import VideoClip

    n = max(1, int(dur * fps))
    frames_a = [clip_a.get_frame(clip_a.duration - (n - i) / fps) for i in range(n)]
    frames_b = [clip_b.get_frame(i / fps) for i in range(n)]

    def make_frame(t):
        idx = min(int(t * fps), n - 1)
        p = idx / max(n - 1, 1)
        # A: scale 1.0 → 1.08, darken
        fa = frames_a[idx].astype(np.float32) * (1.0 - 0.3 * p)
        fa_img = Image.fromarray(fa.clip(0, 255).astype(np.uint8))
        s = 1.0 + 0.08 * p
        new_w, new_h = int(W * s), int(H * s)
        fa_img = fa_img.resize((new_w, new_h), Image.BILINEAR)
        ox, oy = (new_w - W) // 2, (new_h - H) // 2
        fa_crop = np.array(fa_img.crop((ox, oy, ox + W, oy + H))).astype(np.float32)
        # B: scale 1.06 → 1.0
        fb = frames_b[idx].astype(np.float32)
        sb = 1.06 - 0.06 * p
        fb_img = Image.fromarray(fb.clip(0, 255).astype(np.uint8))
        nw, nh = int(W * sb), int(H * sb)
        fb_img = fb_img.resize((nw, nh), Image.BILINEAR)
        ox2, oy2 = (nw - W) // 2, (nh - H) // 2
        fb_crop = np.array(fb_img.crop((ox2, oy2, ox2 + W, oy2 + H))).astype(np.float32)
        # Blend: first half = A zooming out, second half = B zooming in
        blend = p
        out = (fa_crop * (1 - blend) + fb_crop * blend).clip(0, 255).astype(np.uint8)
        return out

    return VideoClip(make_frame, duration=dur).set_fps(fps)


def _dissolve_bridge(clip_a, clip_b, dur: float = 0.25, fps: int = 30) -> 'VideoClip':
    """Simple cross-dissolve — use before broker card only."""
    import numpy as np
    from moviepy.editor import VideoClip

    n = max(1, int(dur * fps))
    frames_a = [clip_a.get_frame(clip_a.duration - (n - i) / fps) for i in range(n)]
    frames_b = [clip_b.get_frame(i / fps) for i in range(n)]

    def make_frame(t):
        idx = min(int(t * fps), n - 1)
        p = idx / max(n - 1, 1)
        fa = frames_a[idx].astype(np.float32)
        fb = frames_b[idx].astype(np.float32)
        return (fa * (1 - p) + fb * p).clip(0, 255).astype(np.uint8)

    return VideoClip(make_frame, duration=dur).set_fps(fps)


def _glitch_bridge(clip_a, clip_b, dur: float = 0.18, fps: int = 30) -> 'VideoClip':
    """RGB channel split + row displacement glitch — use on trust reel cuts only."""
    import numpy as np
    from moviepy.editor import VideoClip

    n = max(1, int(dur * fps))
    frames = [clip_a.get_frame(clip_a.duration - (n - i) / fps) for i in range(n // 2)] + \
             [clip_b.get_frame(i / fps) for i in range(n - n // 2)]
    rng = np.random.default_rng(42)

    def make_frame(t):
        idx = min(int(t * fps), n - 1)
        f = frames[idx].copy()
        strength = int(8 * (1 - abs(idx / n - 0.5) * 2))
        f[:, :, 0] = np.roll(f[:, :, 0], strength, axis=1)
        f[:, :, 2] = np.roll(f[:, :, 2], -strength, axis=1)
        bands = rng.integers(0, H - 40, 6)
        for row in bands:
            height = rng.integers(4, 20)
            shift = rng.integers(-20, 20)
            f[row:row+height] = np.roll(f[row:row+height], shift, axis=1)
        return f

    return VideoClip(make_frame, duration=dur).set_fps(fps)


_BRIDGES = {
    'zoom_punch': _zoom_punch_bridge,
    'dissolve':   _dissolve_bridge,
    'glitch':     _glitch_bridge,
}


def render(clips: list, audio_path: 'Path | None', out_path: str,
           fps: int = 30, flash: bool = True, transitions: 'list | None' = None) -> None:
    """Concatenate VideoClips, insert transitions, add audio, write MP4.

    clips       — list of MoviePy VideoClip
    audio_path  — Path to MP3/WAV, or None for silent
    out_path    — output file path (string)
    flash       — if True (and transitions is None), insert a 2-frame emerald
                  flash between each clip (original behavior)
    transitions — optional list of per-gap transition types; transitions[i] sits
                  between clips[i] and clips[i+1]. Values: 'flash',
                  'zoom_punch', 'dissolve', 'glitch', or None (hard cut).
                  Shorter lists than gaps leave remaining gaps as hard cuts.
    """
    from moviepy.editor import concatenate_videoclips

    if transitions is not None and len(clips) > 1:
        interleaved: list = [clips[0]]
        for i, clip in enumerate(clips[1:]):
            kind = transitions[i] if i < len(transitions) else None
            if kind == 'flash':
                interleaved.append(_flash_clip(fps))
            elif kind in _BRIDGES:
                interleaved.append(_BRIDGES[kind](clips[i], clip, fps=fps))
            interleaved.append(clip)
        clips = interleaved
    elif flash and len(clips) > 1:
        interleaved = [clips[0]]
        for clip in clips[1:]:
            interleaved.append(_flash_clip(fps))
            interleaved.append(clip)
        clips = interleaved

    final = concatenate_videoclips(clips, method='chain')

    if audio_path is not None:
        from reels.audio import build_audio_clip
        audio = build_audio_clip(audio_path, final.duration)
        if audio is not None:
            final = final.set_audio(audio)

    final.write_videofile(
        out_path,
        fps=fps,
        codec='libx264',
        audio_codec='aac',
        preset='fast',
        threads=4,
        logger=None,
    )
