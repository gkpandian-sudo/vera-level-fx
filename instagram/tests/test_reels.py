import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_reels_package_imports():
    from reels import animator, audio, render, scenes  # noqa: F401


# ── animator.py tests ─────────────────────────────────────────────────────────
import numpy as np


def test_radial_bg_shape():
    from reels.animator import radial_bg
    bg = radial_bg()
    assert bg.shape == (1920, 1080, 3)
    assert bg.dtype == np.uint8


def test_countup_frame_shape():
    from reels.animator import countup_frame
    frame = countup_frame(t=0.5, start=0, end=1000, dur=2.0,
                          fmt='${:.0f}', color=(255, 255, 255),
                          fontsize=80, center=(540, 960))
    assert frame.shape == (1920, 1080, 3)


def test_cascade_text_frame_shape():
    from reels.animator import cascade_text_frame
    frame = cascade_text_frame(t=0.5, lines=['Line 1', 'Line 2'], dur=2.0,
                               stagger=0.2, color=(255, 255, 255),
                               fontsize=40, top_y=800)
    assert frame.shape == (1920, 1080, 3)


def test_fade_in_frame_alpha():
    from reels.animator import fade_in_frame
    frame_start = fade_in_frame(t=0.01, text='Hello', dur=1.0,
                                color=(240, 192, 64), fontsize=60,
                                center=(540, 960))
    frame_end   = fade_in_frame(t=1.0,  text='Hello', dur=1.0,
                                color=(240, 192, 64), fontsize=60,
                                center=(540, 960))
    assert frame_start.shape == (1920, 1080, 3)
    assert frame_end.mean() > frame_start.mean()


def test_typewriter_frame_grows():
    from reels.animator import typewriter_frame
    f0 = typewriter_frame(t=0.0, text='HELLO', dur=2.0,
                          color=(255, 255, 255), fontsize=60, center=(540, 960))
    f1 = typewriter_frame(t=2.0, text='HELLO', dur=2.0,
                          color=(255, 255, 255), fontsize=60, center=(540, 960))
    assert f0.shape == (1920, 1080, 3)
    assert f1.sum() >= f0.sum()


# ── audio.py tests ────────────────────────────────────────────────────────────

def test_audio_get_track_returns_path_or_none():
    from reels.audio import get_track
    path = get_track('daily')
    # Returns None when file doesn't exist — graceful fallback
    assert path is None or str(path).endswith('.mp3')


def test_audio_unknown_type_returns_none():
    from reels.audio import get_track
    assert get_track('unknown_type') is None


def test_audio_build_clip_none_when_no_file():
    from reels.audio import build_audio_clip
    result = build_audio_clip(None, 10.0)
    assert result is None


# ── render.py tests ───────────────────────────────────────────────────────────

def test_render_creates_mp4(tmp_path):
    import numpy as np
    from moviepy.editor import VideoClip
    from reels.render import render

    def make_frame(t):
        return np.full((1920, 1080, 3), int(t * 50) % 256, dtype=np.uint8)

    clips = [VideoClip(make_frame, duration=1.0).set_fps(30)]
    out   = tmp_path / 'test.mp4'
    render(clips, audio_path=None, out_path=str(out), fps=30)
    assert out.exists()
    assert out.stat().st_size > 1000
