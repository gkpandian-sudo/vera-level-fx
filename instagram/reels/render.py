from __future__ import annotations


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


def render(clips: list, audio_path: 'Path | None', out_path: str,
           fps: int = 30, flash: bool = True) -> None:
    """Concatenate VideoClips, optionally insert flash cuts, add audio, write MP4.

    clips      — list of MoviePy VideoClip
    audio_path — Path to MP3/WAV, or None for silent
    out_path   — output file path (string)
    flash      — if True, insert a 2-frame emerald flash between each clip
    """
    from moviepy.editor import concatenate_videoclips

    if flash and len(clips) > 1:
        interleaved: list = [clips[0]]
        for clip in clips[1:]:
            interleaved.append(_flash_clip(fps))
            interleaved.append(clip)
        clips = interleaved

    final = concatenate_videoclips(clips, method='compose')

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
