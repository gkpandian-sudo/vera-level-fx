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


# ── scenes.py tests ───────────────────────────────────────────────────────────

SAMPLE_ACCOUNT = {
    'balance': 973, 'equity': 971, 'gain': -96.8,
    'daily': 0.43, 'winRate': 71.0, 'profitFactor': 1.42,
    'pips': 3812, 'trades': 287, 'drawdown': 96.8,
}
SAMPLE_OPEN = [
    {'symbol': 'XAUUSD', 'action': 'buy',  'profit': 12.50},
    {'symbol': 'EURUSD', 'action': 'sell', 'profit': -4.20},
]


def test_make_daily_reel_returns_four_clips():
    from reels.scenes import make_daily_reel
    clips = make_daily_reel({'account': SAMPLE_ACCOUNT, 'openTrades': SAMPLE_OPEN})
    assert len(clips) == 4
    total_dur = sum(c.duration for c in clips)
    assert 9.0 < total_dur < 11.0


def test_make_weekly_reel_returns_four_clips():
    from reels.scenes import make_weekly_reel
    clips = make_weekly_reel({'account': SAMPLE_ACCOUNT}, recovery_day=5)
    assert len(clips) == 4
    total_dur = sum(c.duration for c in clips)
    assert 11.0 < total_dur < 13.0


def test_make_trust_reel_returns_four_clips():
    from reels.scenes import make_trust_reel
    clips = make_trust_reel({'account': SAMPLE_ACCOUNT})
    assert len(clips) == 4
    total_dur = sum(c.duration for c in clips)
    assert 11.0 < total_dur < 13.0


SAMPLE_DAILY_GAIN = [
    ['2026-01-31', 2.1, 210], ['2026-02-28', -1.5, -150],
    ['2026-03-31', 3.2, 320], ['2026-04-30', -0.8, -80],
    ['2026-05-31', 1.9, 190], ['2026-06-30', -96.8, -9680],
]


def test_make_monthly_reel_returns_four_clips():
    from reels.scenes import make_monthly_reel
    data = {'account': SAMPLE_ACCOUNT, 'dailyGain': SAMPLE_DAILY_GAIN}
    clips = make_monthly_reel(data)
    assert len(clips) == 4
    total_dur = sum(c.duration for c in clips)
    assert 26.0 < total_dur < 30.0


def test_make_transparency_reel_returns_four_clips():
    from reels.scenes import make_transparency_reel
    clips = make_transparency_reel({'account': SAMPLE_ACCOUNT})
    assert len(clips) == 4
    total_dur = sum(c.duration for c in clips)
    assert 23.0 < total_dur < 27.0


def test_make_recovery_plan_reel_returns_four_clips():
    from reels.scenes import make_recovery_plan_reel
    clips = make_recovery_plan_reel()
    assert len(clips) == 4
    total_dur = sum(c.duration for c in clips)
    assert 26.0 < total_dur < 30.0


def test_make_edu_reel_returns_four_clips():
    from reels.scenes import make_edu_reel
    content = {
        'rule_num': 1,
        'title': '1% Risk Rule',
        'body': 'Never risk more than 1% of your account per trade.',
        'example_account': 10000,
        'example_risk': 100,
        'example_rr': '1:3',
    }
    clips = make_edu_reel('risk', content)
    assert len(clips) == 4
    total_dur = sum(c.duration for c in clips)
    assert 20.0 < total_dur < 24.0


def test_publish_reel_function_exists():
    import os, sys, inspect
    os.environ.setdefault('IG_USER_ID', 'dummy')
    os.environ.setdefault('META_ACCESS_TOKEN', 'dummy')
    sys.modules.pop('post', None)
    from post import publish_reel
    sig = inspect.signature(publish_reel)
    assert 'video_url' in sig.parameters
    assert 'caption' in sig.parameters


# ── Task 1: Spring easing + glow text ────────────────────────────────────────

def test_ease_spring_reaches_one():
    from reels.animator import ease_spring
    assert abs(ease_spring(10.0, 1.0) - 1.0) < 0.01   # fully settled


def test_ease_spring_overshoots():
    from reels.animator import ease_spring
    peak = max(ease_spring(t * 0.1, 1.0) for t in range(1, 30))
    assert peak > 1.0   # must overshoot


def test_draw_glow_text_shape():
    from PIL import Image
    from reels.animator import draw_glow_text
    img = Image.new('RGB', (1080, 1920), (0, 24, 53))
    result = draw_glow_text(img, (540, 960), '+12.4%', 120, (5, 150, 105))
    assert result.size == (1080, 1920)
    assert result.mode == 'RGB'
