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


def test_make_daily_reel_returns_clips():
    from reels.scenes import make_daily_reel
    clips = make_daily_reel({'account': SAMPLE_ACCOUNT, 'openTrades': SAMPLE_OPEN,
                             'dailyGain': SAMPLE_DAILY_GAIN})
    assert len(clips) == 5
    total_dur = sum(c.duration for c in clips)
    assert 11.0 < total_dur < 22.0


def test_make_weekly_reel_returns_clips():
    from reels.scenes import make_weekly_reel
    clips = make_weekly_reel({'account': SAMPLE_ACCOUNT,
                              'dailyGain': SAMPLE_DAILY_GAIN}, recovery_day=5)
    assert len(clips) >= 4
    total_dur = sum(c.duration for c in clips)
    assert 11.0 < total_dur < 22.0


def test_make_trust_reel_returns_clips():
    from reels.scenes import make_trust_reel
    clips = make_trust_reel({'account': SAMPLE_ACCOUNT})
    assert len(clips) >= 4
    total_dur = sum(c.duration for c in clips)
    assert 11.0 < total_dur < 22.0


SAMPLE_DAILY_GAIN = [
    ['2026-01-31', 2.1, 210], ['2026-02-28', -1.5, -150],
    ['2026-03-31', 3.2, 320], ['2026-04-30', -0.8, -80],
    ['2026-05-31', 1.9, 190], ['2026-06-30', -96.8, -9680],
]


def test_make_monthly_reel_returns_clips():
    from reels.scenes import make_monthly_reel
    clips = make_monthly_reel({'account': SAMPLE_ACCOUNT,
                               'dailyGain': SAMPLE_DAILY_GAIN})
    assert len(clips) >= 4
    total_dur = sum(c.duration for c in clips)
    assert 11.0 < total_dur < 22.0


def test_make_transparency_reel_returns_clips():
    from reels.scenes import make_transparency_reel
    clips = make_transparency_reel({'account': SAMPLE_ACCOUNT,
                                    'dailyGain': SAMPLE_DAILY_GAIN})
    assert len(clips) >= 3
    total_dur = sum(c.duration for c in clips)
    assert 8.0 < total_dur < 22.0


def test_make_recovery_plan_reel_returns_clips():
    from reels.scenes import make_recovery_plan_reel
    clips = make_recovery_plan_reel(recovery_day=3)
    assert len(clips) >= 4
    total_dur = sum(c.duration for c in clips)
    assert 11.0 < total_dur < 22.0


def test_make_edu_reel_returns_clips():
    from reels.scenes import make_edu_reel
    clips = make_edu_reel('risk', {'title': 'Risk', 'body': 'content'})
    assert len(clips) >= 4
    total_dur = sum(c.duration for c in clips)
    assert 11.0 < total_dur < 22.0


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
    # At t=dur, spring should be fully settled (within 1%)
    assert abs(ease_spring(1.0, 1.0) - 1.0) < 0.01


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


# ── Task 2: Animated background + scanlines ───────────────────────────────────

def test_scanline_overlay_shape():
    from reels.animator import scanline_overlay
    ov = scanline_overlay()
    assert ov.size == (1080, 1920)
    assert ov.mode == 'RGBA'

def test_animated_bg_frame_differs_over_time():
    from reels.animator import animated_bg_frame
    import numpy as np
    f0 = np.array(animated_bg_frame(t=0.0))
    f2 = np.array(animated_bg_frame(t=2.0))
    assert not np.array_equal(f0, f2)

def test_animated_bg_frame_shape():
    from reels.animator import animated_bg_frame
    import numpy as np
    frame = np.array(animated_bg_frame(t=0.5))
    assert frame.shape == (1920, 1080, 3)


# ── Task 3: Pulsing live dot + odometer ──────────────────────────────────────

def test_draw_pulsing_dot_returns_image():
    from PIL import Image
    from reels.animator import draw_pulsing_dot
    img = Image.new('RGB', (1080, 1920), (0, 24, 53))
    result = draw_pulsing_dot(img, pos=(540, 200), t=0.5, positive=True)
    assert result.size == (1080, 1920)

def test_odometer_frame_shape():
    from reels.animator import odometer_frame
    import numpy as np
    frame = odometer_frame(t=1.0, value=1234.5, dur=2.0,
                           fmt='{:.1f}', color=(255, 255, 255),
                           fontsize=100, center=(540, 960))
    assert frame.shape == (1920, 1080, 3)


# ── Task 6: Flash-cut transitions ────────────────────────────────────────────

def test_render_with_flash_creates_mp4(tmp_path):
    """Flash=True adds flash frames between clips."""
    import numpy as np
    from moviepy.editor import VideoClip
    from reels.render import render

    def make_frame(t):
        return np.full((1920, 1080, 3), 40, dtype=np.uint8)

    clips     = [VideoClip(make_frame, duration=1.0).set_fps(30),
                 VideoClip(make_frame, duration=1.0).set_fps(30)]
    out_plain = tmp_path / 'plain.mp4'
    out_flash = tmp_path / 'flash.mp4'

    render(clips, audio_path=None, out_path=str(out_plain), fps=30, flash=False)
    render(clips, audio_path=None, out_path=str(out_flash), fps=30, flash=True)

    assert out_plain.exists() and out_flash.exists()
    assert out_flash.stat().st_size > 0


# ── Task 4: Equity curve + win-rate ring ─────────────────────────────────────

def test_equity_curve_clip_shape():
    from reels.effects import equity_curve_clip
    daily_gain = [
        ['02/20/2026', 0.0, 0], ['03/01/2026', 2.1, 210],
        ['04/01/2026', -1.5, -150], ['05/01/2026', 3.2, 320],
        ['06/01/2026', -0.8, -80], ['07/01/2026', 1.9, 190],
    ]
    clip = equity_curve_clip(daily_gain, duration=4.0)
    import numpy as np
    frame = clip.get_frame(2.0)
    assert frame.shape == (1920, 1080, 3)
    assert clip.duration == 4.0

def test_progress_ring_clip_shape():
    from reels.effects import progress_ring_clip
    clip = progress_ring_clip(win_rate=71.0, duration=4.0)
    import numpy as np
    frame = clip.get_frame(2.0)
    assert frame.shape == (1920, 1080, 3)

def test_progress_ring_clip_zero():
    from reels.effects import progress_ring_clip
    clip = progress_ring_clip(win_rate=0.0, duration=2.0)
    assert clip.duration == 2.0


def test_ticker_tape_overlay_shape():
    from reels.effects import ticker_tape_overlay
    from PIL import Image
    img = Image.new('RGB', (1080, 1920), (0, 24, 53))
    result = ticker_tape_overlay(img, t=1.0)
    assert result.size == (1080, 1920)
    assert result.mode == 'RGB'

def test_candlestick_bg_overlay_shape():
    from reels.effects import candlestick_bg_overlay
    from PIL import Image
    img = Image.new('RGB', (1080, 1920), (0, 24, 53))
    result = candlestick_bg_overlay(img)
    assert result.size == (1080, 1920)

def test_glow_border_overlay_shape():
    from reels.effects import glow_border_overlay
    from PIL import Image
    img = Image.new('RGB', (1080, 1920), (0, 24, 53))
    result = glow_border_overlay(img, t=0.5)
    assert result.size == (1080, 1920)


def test_daily_reel_no_intro_clip():
    from reels.scenes import make_daily_reel
    clips = make_daily_reel({'account': SAMPLE_ACCOUNT, 'openTrades': SAMPLE_OPEN,
                             'dailyGain': SAMPLE_DAILY_GAIN})
    assert len(clips) == 5
    # Hero (odometer, 4s) must be first — intro would have bumped it to index 1
    assert clips[0].duration == 4.0, f"Expected hero at index 0 (4s), got: {[c.duration for c in clips]}"


def test_weekly_reel_no_intro_clip():
    from reels.scenes import make_weekly_reel
    clips = make_weekly_reel({'account': SAMPLE_ACCOUNT, 'dailyGain': SAMPLE_DAILY_GAIN})
    assert len(clips) == 5
    # Hero (spring gain, 4s) must be first
    assert clips[0].duration == 4.0, f"Expected hero at index 0 (4s), got: {[c.duration for c in clips]}"


def test_trust_reel_no_fake_ring_when_wr_zero():
    from reels.scenes import make_trust_reel
    clips = make_trust_reel({'account': {'winRate': 0, 'profitFactor': 1.0,
                                          'gain': 5.0, 'trades': 100, 'pips': 500}})
    assert len(clips) >= 4
    # Hero clip (index 0) should be 5s duration whether ring or verify card
    assert clips[0].duration == 5.0


def test_monthly_reel_total_duration_under_14s():
    from reels.scenes import make_monthly_reel
    clips = make_monthly_reel({'account': SAMPLE_ACCOUNT,
                               'dailyGain': SAMPLE_DAILY_GAIN})
    total = sum(c.duration for c in clips)
    assert total < 14.0, f"Monthly reel too long: {total}s (should be <14s)"


def test_transparency_reel_ends_without_broker_card():
    from reels.scenes import make_transparency_reel
    clips = make_transparency_reel({'account': SAMPLE_ACCOUNT, 'dailyGain': SAMPLE_DAILY_GAIN})
    # Broker card is 3.0s — last clip must NOT be 3.0s
    assert clips[-1].duration != 3.0, "Broker card still in transparency reel"
    assert len(clips) == 3


def test_recovery_plan_reel_accepts_balance_pf():
    from reels.scenes import make_recovery_plan_reel
    clips = make_recovery_plan_reel(recovery_day=5, balance=1500.0, pf=0.9)
    assert len(clips) >= 3
    total = sum(c.duration for c in clips)
    assert 8.0 < total < 18.0

def test_make_signup_reel_returns_clips():
    from reels.scenes import make_signup_reel
    clips = make_signup_reel()
    assert len(clips) >= 3
    total = sum(c.duration for c in clips)
    assert 10.0 < total < 20.0

def test_make_milestone_reel_returns_clips():
    from reels.scenes import make_milestone_reel
    clips = make_milestone_reel({'account': SAMPLE_ACCOUNT}, 'PF crossed 1.0')
    assert len(clips) >= 3
    total = sum(c.duration for c in clips)
    assert 9.0 < total < 18.0


# ── make_trades_reel ──────────────────────────────────────────────────────────

SAMPLE_HISTORY = [
    {
        'symbol': 'XAUUSD', 'action': 'Buy',
        'openTime':  '07/20/2026 02:00', 'closeTime':  '07/20/2026 04:00',
        'openPrice': 2300.50, 'closePrice': 2315.00,
        'profit': 14.50, 'commission': -0.80, 'pips': 15,
    },
    {
        'symbol': 'XAUUSD', 'action': 'Buy',
        'openTime':  '07/20/2026 06:00', 'closeTime':  '07/20/2026 07:30',
        'openPrice': 2310.00, 'closePrice': 2312.00,
        'profit': 2.00, 'commission': -0.76, 'pips': 2,
    },
]

SAMPLE_DATA = {
    'account': {
        'balance': 1500.0, 'gain': 2.5, 'winRate': 60.0,
        'trades': 12, 'pips': 500, 'profitFactor': 1.3,
    },
    'history': SAMPLE_HISTORY,
}


def test_make_trades_reel_returns_list_of_clips():
    from reels.scenes import make_trades_reel
    from moviepy.editor import VideoClip
    clips = make_trades_reel(SAMPLE_DATA)
    assert isinstance(clips, list)
    assert len(clips) >= 1
    assert all(isinstance(c, VideoClip) for c in clips)


def test_make_trades_reel_empty_history_returns_clips():
    from reels.scenes import make_trades_reel
    data = dict(SAMPLE_DATA, history=[])
    clips = make_trades_reel(data)
    assert isinstance(clips, list)
    assert len(clips) >= 1


def test_make_thumbnail_trades_returns_pil_image():
    from reels.scenes import make_thumbnail
    from PIL import Image
    img = make_thumbnail('trades', SAMPLE_DATA)
    assert isinstance(img, Image.Image)
    assert img.size == (1080, 1920)
