# Instagram Reels Automation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fully automated Instagram Reels pipeline (MP4, 1080×1920, 30fps, baked-in audio) to the existing Vera Level FX automation — covering all 7 post types, published via Meta Graph API on Mon/Wed/Fri.

**Architecture:** A new `instagram/reels/` module sits alongside the static image pipeline (`run.py`/`generate.py`) and does not touch it. PIL generates every frame lazily inside MoviePy `VideoClip(make_frame, duration)` closures; no ImageMagick required. A new `run_reel.py` entry point mirrors `run.py`, and a new `insta-reel.yml` workflow drives it.

**Tech Stack:** Python 3.11 · moviepy==1.0.3 · Pillow · numpy · ffmpeg (pre-installed on ubuntu-latest)

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `instagram/requirements.txt` | MODIFY | Add `moviepy==1.0.3` |
| `instagram/reels/__init__.py` | CREATE | Module init (empty) |
| `instagram/reels/animator.py` | CREATE | PIL frame-generation primitives: radial_bg, particles, countup, cascade_text, fade_in, typewriter |
| `instagram/reels/audio.py` | CREATE | Track selection by post type; builds trimmed AudioFileClip with volume + fade |
| `instagram/reels/render.py` | CREATE | Concatenates VideoClip list, adds audio, writes MP4 via MoviePy/ffmpeg |
| `instagram/reels/scenes.py` | CREATE | 7 post-type scene composers — each returns a list of 4 VideoClips (intro/hero/data/cta) |
| `instagram/post.py` | MODIFY | Add `publish_reel(video_url, caption)` — REELS container + 5-min poll + publish |
| `instagram/run_reel.py` | CREATE | Entry point: reads env vars, calls scenes → render → commit → publish_reel |
| `.github/workflows/insta-reel.yml` | CREATE | Scheduled (Mon/Wed/Fri) + manual trigger workflow |
| `instagram/assets/audio/README.md` | CREATE | Sourcing guide for 6 CC0 audio tracks |
| `instagram/reels/.gitkeep` | CREATE | Ensures output directory is tracked |
| `instagram/tests/test_reels.py` | CREATE | Unit tests for animator primitives + scenes + audio |

---

## Task 1: Scaffold — Dependencies + Directory Structure

**Files:**
- Modify: `instagram/requirements.txt`
- Create: `instagram/reels/__init__.py`
- Create: `instagram/reels/.gitkeep`
- Create: `instagram/assets/audio/README.md`

- [ ] **Step 1: Add moviepy to requirements**

Edit `instagram/requirements.txt` to:

```
matplotlib==3.8.4
numpy==1.26.4
requests==2.31.0
Pillow==10.3.0
moviepy==1.0.3
```

- [ ] **Step 2: Create reels module**

Create `instagram/reels/__init__.py`:

```python
```

(empty file — just marks the package)

- [ ] **Step 3: Create output directory placeholder**

Create `instagram/reels/.gitkeep` (empty file).

- [ ] **Step 4: Create audio sourcing README**

Create `instagram/assets/audio/README.md`:

```markdown
# Audio Tracks

Six CC0/royalty-free audio tracks are required. Source from:
- pixabay.com/music (free for commercial use, no attribution needed)
- freemusicarchive.org (filter CC0)

Requirements per track:
- Duration: ≥ 35 seconds
- Format: MP3
- Normalised to -14 LUFS (optional but preferred)

| Filename | Post Type | Feel |
|----------|-----------|------|
| pulse.mp3 | daily | Upbeat, energetic |
| momentum.mp3 | weekly, trust | Driving, confident |
| reflect.mp3 | monthly | Measured, thoughtful |
| tension.mp3 | transparency | Dark, atmospheric |
| rise.mp3 | recovery-plan | Hopeful, building |
| calm.mp3 | edu | Clean, focused |

Place each file in this directory: `instagram/assets/audio/<filename>.mp3`

If a track is missing, audio.py returns None and the Reel renders without music.
```

- [ ] **Step 5: Write the import smoke-test**

Create `instagram/tests/test_reels.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_reels_package_imports():
    from reels import animator, audio, render, scenes  # noqa: F401
```

- [ ] **Step 6: Run test — expect FAIL (module doesn't exist yet)**

```
cd vera-level-fx
python -m pytest instagram/tests/test_reels.py::test_reels_package_imports -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 7: Commit scaffold**

```bash
git add instagram/requirements.txt instagram/reels/__init__.py instagram/reels/.gitkeep instagram/assets/audio/README.md instagram/tests/test_reels.py
git commit -m "scaffold: add reels module structure + moviepy dependency"
```

---

## Task 2: `animator.py` — PIL Frame-Generation Primitives

**Files:**
- Create: `instagram/reels/animator.py`
- Test: `instagram/tests/test_reels.py`

All functions return `np.ndarray` of shape `(1920, 1080, 3)` uint8 for a single frame at time `t`. MoviePy calls these lazily inside `VideoClip(make_frame, duration=dur)`.

- [ ] **Step 1: Write failing tests for animator**

Append to `instagram/tests/test_reels.py`:

```python
import numpy as np


def test_radial_bg_shape():
    from reels.animator import radial_bg
    bg = radial_bg()
    assert bg.shape == (1920, 1080, 3)
    assert bg.dtype == np.uint8


def test_countup_frame_shape():
    from reels.animator import countup_frame
    frame = countup_frame(t=0.5, start=0, end=1000, dur=2.0,
                          fmt='${:.0f}', color=(255,255,255),
                          fontsize=80, center=(540, 960))
    assert frame.shape == (1920, 1080, 3)


def test_cascade_text_frame_shape():
    from reels.animator import cascade_text_frame
    frame = cascade_text_frame(t=0.5, lines=['Line 1', 'Line 2'], dur=2.0,
                               stagger=0.2, color=(255,255,255),
                               fontsize=40, top_y=800)
    assert frame.shape == (1920, 1080, 3)


def test_fade_in_frame_alpha():
    from reels.animator import fade_in_frame
    frame_start = fade_in_frame(t=0.01, text='Hello', dur=1.0,
                                color=(240,192,64), fontsize=60, center=(540,960))
    frame_end = fade_in_frame(t=1.0, text='Hello', dur=1.0,
                              color=(240,192,64), fontsize=60, center=(540,960))
    assert frame_start.shape == (1920, 1080, 3)
    # At t=1.0 the text is fully visible — gold channel should be brighter
    assert frame_end.mean() > frame_start.mean()


def test_typewriter_frame_grows():
    from reels.animator import typewriter_frame
    f0 = typewriter_frame(t=0.0, text='HELLO', dur=2.0,
                          color=(255,255,255), fontsize=60, center=(540,960))
    f1 = typewriter_frame(t=2.0, text='HELLO', dur=2.0,
                          color=(255,255,255), fontsize=60, center=(540,960))
    assert f0.shape == (1920, 1080, 3)
    # More pixels lit at end than start
    assert f1.sum() >= f0.sum()
```

- [ ] **Step 2: Run — expect FAIL**

```
python -m pytest instagram/tests/test_reels.py -k "animator or radial or countup or cascade or fade or typewriter" -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement `animator.py`**

Create `instagram/reels/animator.py`:

```python
from __future__ import annotations
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1080, 1920

NAVY  = (1,  14,  31)
GOLD  = (240, 192, 64)
WHITE = (255, 255, 255)
CREAM = (240, 238, 232)
MUTED = (184, 207, 234)
GREEN = (0,  224, 150)
RED   = (255, 107, 107)
AMBER = (255, 160, 64)

_FONT_DIR  = Path(__file__).parent.parent / 'assets' / 'fonts'
_BG_CACHE: np.ndarray | None = None


def _ease_out(t: float, dur: float) -> float:
    x = min(t / max(dur, 1e-6), 1.0)
    return 1 - (1 - x) ** 3


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates: list[str] = []
    if bold:
        candidates += [
            str(_FONT_DIR / 'Roboto-Bold.ttf'),
            '/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        ]
    candidates += [
        str(_FONT_DIR / 'Roboto-Regular.ttf'),
        '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            pass
    return ImageFont.load_default()


def radial_bg() -> np.ndarray:
    """Static navy radial gradient, cached. Returns (H, W, 3) uint8."""
    global _BG_CACHE
    if _BG_CACHE is not None:
        return _BG_CACHE
    cx, cy = W // 2, H // 2
    Y, X   = np.mgrid[0:H, 0:W]
    dist   = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2).astype(float)
    max_d  = np.sqrt(cx ** 2 + cy ** 2)
    t_arr  = np.clip(dist / max_d, 0, 1)
    r = np.clip(1  * (1 - t_arr) + 0  * t_arr, 0, 255).astype(np.uint8)
    g = np.clip(14 * (1 - t_arr) + 4  * t_arr, 0, 255).astype(np.uint8)
    b = np.clip(31 * (1 - t_arr) + 12 * t_arr, 0, 255).astype(np.uint8)
    _BG_CACHE = np.stack([r, g, b], axis=-1)
    return _BG_CACHE


def _particle_overlay(t: float, n: int = 8, opacity: float = 0.08,
                      seed: int = 42) -> Image.Image:
    """RGBA PIL image with n slow-drifting gold particles."""
    rng    = np.random.default_rng(seed)
    xs     = rng.integers(80, W - 80, n)
    ys0    = rng.integers(H // 2, H - 50, n)
    speeds = rng.uniform(30, 80, n)
    sizes  = rng.integers(4, 11, n)

    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    for i in range(n):
        y   = int((ys0[i] - speeds[i] * t) % H)
        alp = int(opacity * 255)
        r   = int(sizes[i])
        draw.ellipse([xs[i] - r, y - r, xs[i] + r, y + r],
                     fill=(*GOLD, alp))
    return overlay


def _bg_frame(t: float) -> Image.Image:
    """Full background PIL image (radial gradient + particles) at time t."""
    bg   = Image.fromarray(radial_bg())
    part = _particle_overlay(t)
    bg   = bg.convert('RGBA')
    bg.alpha_composite(part)
    return bg.convert('RGB')


def _draw_alpha_text(img: Image.Image, pos: tuple, text: str,
                     font: ImageFont.FreeTypeFont,
                     color: tuple, alpha: int) -> Image.Image:
    """Draw text with alpha onto an RGB PIL Image. Returns new RGB Image."""
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    draw.text(pos, text, fill=(*color, alpha), font=font, anchor='mm')
    base = img.convert('RGBA')
    base.alpha_composite(overlay)
    return base.convert('RGB')


def countup_frame(t: float, start: float, end: float, dur: float,
                  fmt: str, color: tuple, fontsize: int,
                  center: tuple) -> np.ndarray:
    """Single frame: large number counting from start→end with ease-out."""
    value = start + (end - start) * _ease_out(t, dur)
    text  = fmt.format(value)
    img   = _bg_frame(t)
    img   = _draw_alpha_text(img, center, text,
                             _load_font(fontsize, bold=True), color, 255)
    return np.array(img)


def cascade_text_frame(t: float, lines: list, dur: float, stagger: float,
                       color: tuple, fontsize: int, top_y: int) -> np.ndarray:
    """Single frame: lines slide up + fade in sequentially."""
    img    = _bg_frame(t)
    font   = _load_font(fontsize)
    line_h = fontsize + 20
    cx     = W // 2
    for i, line in enumerate(lines):
        start_t  = i * stagger
        elapsed  = max(t - start_t, 0)
        progress = _ease_out(elapsed, 0.4)
        alpha    = int(255 * min(progress, 1.0))
        offset_y = int(20 * (1 - progress))
        y        = top_y + i * line_h + offset_y
        img      = _draw_alpha_text(img, (cx, y), line, font, color, alpha)
    return np.array(img)


def fade_in_frame(t: float, text: str, dur: float, color: tuple,
                  fontsize: int, center: tuple) -> np.ndarray:
    """Single frame: text fades in (opacity 0→1)."""
    alpha = int(255 * _ease_out(t, dur))
    img   = _bg_frame(t)
    img   = _draw_alpha_text(img, center, text,
                             _load_font(fontsize, bold=True), color, alpha)
    return np.array(img)


def typewriter_frame(t: float, text: str, dur: float, color: tuple,
                     fontsize: int, center: tuple) -> np.ndarray:
    """Single frame: characters appear one by one."""
    n_chars = int(len(text) * _ease_out(t, dur))
    visible = text[:n_chars]
    img     = _bg_frame(t)
    if visible:
        img = _draw_alpha_text(img, center, visible,
                               _load_font(fontsize, bold=True), color, 255)
    return np.array(img)


def slide_bar_frame(t: float, dur: float, y: int,
                    thickness: int = 8) -> np.ndarray:
    """Single frame: gold horizontal bar sweeping L→R."""
    img  = _bg_frame(t)
    w    = int(W * _ease_out(t, dur))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, y, w, y + thickness], fill=GOLD)
    return np.array(img)


def logo_fade_frame(t: float, brand: str = 'VERA LEVEL FX') -> np.ndarray:
    """Single frame: brand name + gold bar intro at time t (1.5s clip)."""
    cy      = H // 2
    progress = _ease_out(t, 0.5)

    img = _bg_frame(t)

    # Gold sweep bar
    bar_w = int(W * _ease_out(t, 0.8))
    draw  = ImageDraw.Draw(img)
    draw.rectangle([0, cy - 4, bar_w, cy + 4], fill=GOLD)

    # Brand name fades in after 0.4s
    alpha   = int(255 * _ease_out(max(t - 0.4, 0), 0.7))
    img     = _draw_alpha_text(img, (W // 2, cy - 80), brand,
                               _load_font(56, bold=True), GOLD, alpha)
    tag_a   = int(255 * _ease_out(max(t - 0.7, 0), 0.5))
    img     = _draw_alpha_text(img, (W // 2, cy + 50), 'Live IC Markets Account',
                               _load_font(30), MUTED, tag_a)
    return np.array(img)


def cta_fade_frame(t: float, line1: str, line2: str = '') -> np.ndarray:
    """Single frame: CTA text fades in (2s clip)."""
    alpha1 = int(255 * _ease_out(t, 1.0))
    alpha2 = int(255 * _ease_out(max(t - 0.4, 0), 1.0))
    img    = _bg_frame(t)
    img    = _draw_alpha_text(img, (W // 2, H // 2 - 40), line1,
                              _load_font(36, bold=True), GOLD, alpha1)
    if line2:
        img = _draw_alpha_text(img, (W // 2, H // 2 + 40), line2,
                               _load_font(30), MUTED, alpha2)
    return np.array(img)
```

- [ ] **Step 4: Run tests — expect PASS**

```
python -m pytest instagram/tests/test_reels.py -k "animator or radial or countup or cascade or fade or typewriter" -v
```

Expected: all 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add instagram/reels/animator.py instagram/tests/test_reels.py
git commit -m "feat: add reels/animator.py - PIL frame-generation primitives"
```

---

## Task 3: `audio.py` — Track Selection + AudioFileClip

**Files:**
- Create: `instagram/reels/audio.py`
- Test: `instagram/tests/test_reels.py`

- [ ] **Step 1: Write failing test**

Append to `instagram/tests/test_reels.py`:

```python
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
```

- [ ] **Step 2: Run — expect FAIL**

```
python -m pytest instagram/tests/test_reels.py -k "audio" -v
```

- [ ] **Step 3: Implement `audio.py`**

Create `instagram/reels/audio.py`:

```python
from __future__ import annotations
from pathlib import Path

AUDIO_DIR = Path(__file__).parent.parent / 'assets' / 'audio'

TRACK_MAP: dict[str, str] = {
    'daily':         'pulse.mp3',
    'weekly':        'momentum.mp3',
    'trust':         'momentum.mp3',
    'monthly':       'reflect.mp3',
    'transparency':  'tension.mp3',
    'recovery-plan': 'rise.mp3',
    'edu':           'calm.mp3',
}


def get_track(post_type: str) -> Path | None:
    """Return Path to the audio file for this post type, or None if missing."""
    filename = TRACK_MAP.get(post_type)
    if not filename:
        return None
    path = AUDIO_DIR / filename
    return path if path.exists() else None


def build_audio_clip(track_path: 'Path | None', duration: float):
    """Return a MoviePy AudioFileClip trimmed to duration, or None."""
    if track_path is None:
        return None
    try:
        from moviepy.editor import AudioFileClip
        clip = (AudioFileClip(str(track_path))
                .subclip(0, min(duration, AudioFileClip(str(track_path)).duration))
                .volumex(0.15)
                .audio_fadein(0.5)
                .audio_fadeout(1.0)
                .set_duration(duration))
        return clip
    except Exception:
        return None
```

- [ ] **Step 4: Run — expect PASS**

```
python -m pytest instagram/tests/test_reels.py -k "audio" -v
```

- [ ] **Step 5: Commit**

```bash
git add instagram/reels/audio.py
git commit -m "feat: add reels/audio.py - CC0 track selection with graceful fallback"
```

---

## Task 4: `render.py` — MoviePy Composition + MP4 Export

**Files:**
- Create: `instagram/reels/render.py`
- Test: `instagram/tests/test_reels.py`

- [ ] **Step 1: Write failing test**

Append to `instagram/tests/test_reels.py`:

```python
def test_render_creates_mp4(tmp_path):
    import numpy as np
    from moviepy.editor import VideoClip
    from reels.render import render

    def make_frame(t):
        return np.full((1920, 1080, 3), int(t * 50), dtype=np.uint8)

    clips = [VideoClip(make_frame, duration=1.0).set_fps(30)]
    out   = tmp_path / 'test.mp4'
    render(clips, audio_path=None, out_path=str(out), fps=30)
    assert out.exists()
    assert out.stat().st_size > 1000
```

- [ ] **Step 2: Run — expect FAIL**

```
python -m pytest instagram/tests/test_reels.py::test_render_creates_mp4 -v
```

Note: this test requires ffmpeg installed locally. Skip with `-k "not render"` if not available.

- [ ] **Step 3: Implement `render.py`**

Create `instagram/reels/render.py`:

```python
from __future__ import annotations
from pathlib import Path


def render(clips: list, audio_path: 'Path | None', out_path: str,
           fps: int = 30, size: tuple = (1080, 1920)) -> None:
    """Concatenate VideoClips, add optional audio, write MP4.

    clips     — list of moviepy VideoClip (already have .fps set)
    audio_path — Path to an MP3/WAV file, or None for silent
    out_path  — output file path (string)
    """
    from moviepy.editor import concatenate_videoclips

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
```

- [ ] **Step 4: Run — expect PASS** (requires ffmpeg)

```
python -m pytest instagram/tests/test_reels.py::test_render_creates_mp4 -v
```

Expected: PASS, `test.mp4` created in temp dir

- [ ] **Step 5: Commit**

```bash
git add instagram/reels/render.py
git commit -m "feat: add reels/render.py - MoviePy composition + ffmpeg export"
```

---

## Task 5: `scenes.py` — Intro + Daily + Weekly + Trust

**Files:**
- Create: `instagram/reels/scenes.py`
- Test: `instagram/tests/test_reels.py`

Each scene composer returns a `list[VideoClip]` — the 4 scenes (intro, hero, data, cta).

- [ ] **Step 1: Write failing tests**

Append to `instagram/tests/test_reels.py`:

```python
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
    assert 9.0 < total_dur < 11.0   # ~10s


def test_make_weekly_reel_returns_four_clips():
    from reels.scenes import make_weekly_reel
    clips = make_weekly_reel({'account': SAMPLE_ACCOUNT}, recovery_day=5)
    assert len(clips) == 4
    total_dur = sum(c.duration for c in clips)
    assert 11.0 < total_dur < 13.0  # ~12s


def test_make_trust_reel_returns_four_clips():
    from reels.scenes import make_trust_reel
    clips = make_trust_reel({'account': SAMPLE_ACCOUNT})
    assert len(clips) == 4
    total_dur = sum(c.duration for c in clips)
    assert 11.0 < total_dur < 13.0  # ~12s
```

- [ ] **Step 2: Run — expect FAIL**

```
python -m pytest instagram/tests/test_reels.py -k "daily_reel or weekly_reel or trust_reel" -v
```

- [ ] **Step 3: Implement `scenes.py` — intro helper + daily + weekly + trust**

Create `instagram/reels/scenes.py`:

```python
from __future__ import annotations
from moviepy.editor import VideoClip
from reels.animator import (
    W, H, GOLD, WHITE, GREEN, RED, MUTED, CREAM, AMBER,
    logo_fade_frame, countup_frame, cascade_text_frame,
    fade_in_frame, typewriter_frame, cta_fade_frame,
)

FPS = 30
_VERIFY_CTA = 'Myfxbook #12044019'
_IB_CTA     = 'icmarkets.com/?camp=91936'


def _clip(make_frame_fn, duration: float) -> VideoClip:
    """Wrap a make_frame function as a MoviePy VideoClip."""
    clip = VideoClip(make_frame_fn, duration=duration)
    return clip.set_fps(FPS)


def _intro_clip() -> VideoClip:
    """1.5s branded intro — logo + gold bar sweep."""
    return _clip(logo_fade_frame, 1.5)


# ── Daily (10s) ──────────────────────────────────────────────────────────────

def make_daily_reel(data: dict, recovery_day: int = 0) -> list:
    """Returns [intro, hero, data, cta] VideoClips for daily post (~10s)."""
    acct        = data.get('account', {})
    open_trades = data.get('openTrades', [])[:5]

    balance   = float(acct.get('balance') or 0)
    daily_pct = float(acct.get('daily')   or 0)
    win_rate  = float(acct.get('winRate') or 0)
    pips      = int(acct.get('pips')   or 0)
    trades    = int(acct.get('trades') or 0)
    pf        = float(acct.get('profitFactor') or 0)
    pnl_color = GREEN if daily_pct >= 0 else RED
    sign      = '+' if daily_pct >= 0 else ''

    # ── Intro ─────────────────────────────────────────────────────────────────
    intro = _intro_clip()

    # ── Hero (3s): balance counts up + daily P&L slams in ────────────────────
    DUR_HERO = 3.0
    cx, cy   = W // 2, H // 2

    def hero_frame(t):
        # Balance counts up in first 2s
        f = countup_frame(t, 0, balance, 2.0, '${:,.0f}', WHITE, 110, (cx, cy - 80))
        from PIL import Image, ImageDraw
        import numpy as np
        img = Image.fromarray(f)
        # Daily P&L slams in after 1.5s
        if t > 1.5:
            from reels.animator import _draw_alpha_text, _load_font
            alp = min(int(255 * (t - 1.5) / 0.5), 255)
            pnl_text = f'{sign}{daily_pct:.2f}%'
            img = _draw_alpha_text(img, (cx, cy + 80), pnl_text,
                                   _load_font(72, bold=True), pnl_color, alp)
        return np.array(img)

    hero = _clip(hero_frame, DUR_HERO)

    # ── Data (3.5s): open positions cascade up ────────────────────────────────
    lines = []
    if recovery_day > 0:
        lines.append(f'Recovery Day {recovery_day}')
    for t in open_trades:
        sym    = t.get('symbol', '')
        action = t.get('action', '').upper()
        profit = t.get('profit', 0)
        icon   = '+ ' if profit >= 0 else '- '
        lines.append(f'{sym}  {action}  {icon}${abs(profit):.2f}')
    if not lines:
        lines = ['No open positions']
    lines += [f'Win Rate: {win_rate:.0f}%  PF: {pf:.2f}  Pips: +{pips:,}']

    def data_frame(t):
        return cascade_text_frame(t, lines, 3.5, 0.3, WHITE, 38, 700)

    data_clip = _clip(data_frame, 3.5)

    # ── CTA (2s) ──────────────────────────────────────────────────────────────
    def cta_frame(t):
        return cta_fade_frame(t, 'Verify my live account', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta]


# ── Weekly (12s) ─────────────────────────────────────────────────────────────

def make_weekly_reel(data: dict, recovery_day: int = 0) -> list:
    """Returns [intro, hero, data, cta] VideoClips for weekly post (~12s)."""
    acct   = data.get('account', {})
    gain   = float(acct.get('gain')         or 0)
    wr     = float(acct.get('winRate')       or 0)
    pf     = float(acct.get('profitFactor')  or 0)
    pips   = int(acct.get('pips')            or 0)
    trades = int(acct.get('trades')          or 0)
    bal    = float(acct.get('balance')       or 0)

    gain_color = GREEN if gain >= 0 else RED
    sign       = '+' if gain >= 0 else ''

    # ── Intro ─────────────────────────────────────────────────────────────────
    intro = _intro_clip()

    # ── Hero (4s): total gain % counts up ─────────────────────────────────────
    def hero_frame(t):
        return countup_frame(t, 0, gain, 4.0, f'{sign}{{:.1f}}%', gain_color, 120, (W // 2, H // 2))

    hero = _clip(hero_frame, 4.0)

    # ── Data (4.5s): stats cascade ────────────────────────────────────────────
    lines = []
    if recovery_day > 0:
        lines.append(f'Recovery Day {recovery_day}  |  Rebuild is live')
    lines += [
        f'Balance:  ${bal:,.0f}',
        f'Win Rate: {wr:.0f}%  across {trades:,} trades',
        f'Profit Factor:  {pf:.2f}',
        f'Total Pips:     +{pips:,}',
        'All verified on Myfxbook',
    ]

    def data_frame(t):
        return cascade_text_frame(t, lines, 4.5, 0.4, WHITE, 680, )

    # cascade_text_frame needs top_y positional arg — fix call:
    def data_frame(t):  # noqa: F811
        return cascade_text_frame(t, lines, 4.5, 0.4, WHITE, 42, 680)

    data_clip = _clip(data_frame, 4.5)

    # ── CTA (2s) ──────────────────────────────────────────────────────────────
    def cta_frame(t):
        return cta_fade_frame(t, 'Full track record:', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta]


# ── Trust (12s) ───────────────────────────────────────────────────────────────

def make_trust_reel(data: dict) -> list:
    """Returns [intro, hero, data, cta] VideoClips for trust post (~12s)."""
    acct   = data.get('account', {})
    wr     = float(acct.get('winRate')       or 0)
    pf     = float(acct.get('profitFactor')  or 0)
    gain   = float(acct.get('gain')          or 0)
    trades = int(acct.get('trades')          or 0)
    pips   = int(acct.get('pips')            or 0)
    sign   = '+' if gain >= 0 else ''

    intro = _intro_clip()

    # Hero: win rate % counts up in giant font
    def hero_frame(t):
        return countup_frame(t, 0, wr, 4.0, '{:.0f}%', GOLD, 160, (W // 2, H // 2 - 40))

    hero = _clip(hero_frame, 4.0)

    lines = [
        'Win Rate — verified',
        f'{trades:,} trades  |  Myfxbook #12044019',
        f'Profit Factor: {pf:.2f}',
        f'Total Pips:    +{pips:,}',
        f'Total Gain:    {sign}{gain:.1f}%',
        'Not a screenshot. Not a demo.',
        'Live IC Markets. ASIC regulated.',
    ]

    def data_frame(t):
        return cascade_text_frame(t, lines, 4.5, 0.35, WHITE, 40, 640)

    data_clip = _clip(data_frame, 4.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Search "Vera Level" on Myfxbook', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta]
```

- [ ] **Step 4: Run tests — expect PASS**

```
python -m pytest instagram/tests/test_reels.py -k "daily_reel or weekly_reel or trust_reel" -v
```

Expected: all 3 PASS

- [ ] **Step 5: Commit**

```bash
git add instagram/reels/scenes.py
git commit -m "feat: add scenes.py - daily, weekly, trust Reel composers"
```

---

## Task 6: `scenes.py` — Monthly + Transparency + Recovery Plan + Edu

**Files:**
- Modify: `instagram/reels/scenes.py`
- Test: `instagram/tests/test_reels.py`

- [ ] **Step 1: Write failing tests**

Append to `instagram/tests/test_reels.py`:

```python
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
    assert 26.0 < total_dur < 30.0   # ~28s


def test_make_transparency_reel_returns_four_clips():
    from reels.scenes import make_transparency_reel
    clips = make_transparency_reel({'account': SAMPLE_ACCOUNT})
    assert len(clips) == 4
    total_dur = sum(c.duration for c in clips)
    assert 23.0 < total_dur < 27.0   # ~25s


def test_make_recovery_plan_reel_returns_four_clips():
    from reels.scenes import make_recovery_plan_reel
    clips = make_recovery_plan_reel()
    assert len(clips) == 4
    total_dur = sum(c.duration for c in clips)
    assert 26.0 < total_dur < 30.0   # ~28s


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
    assert 20.0 < total_dur < 24.0   # ~22s
```

- [ ] **Step 2: Run — expect FAIL**

```
python -m pytest instagram/tests/test_reels.py -k "monthly_reel or transparency_reel or recovery_plan_reel or edu_reel" -v
```

- [ ] **Step 3: Append to `scenes.py`**

Append the following to the end of `instagram/reels/scenes.py`:

```python
# ── Monthly (28s) ─────────────────────────────────────────────────────────────

def make_monthly_reel(data: dict) -> list:
    """Returns [intro, hero, data, cta] VideoClips for monthly post (~28s)."""
    from datetime import datetime as _dt

    acct = data.get('account', {})
    gain = float(acct.get('gain') or 0)

    # Build monthly P&L from dailyGain
    monthly_pnl: dict[str, float] = {}
    for item in data.get('dailyGain', []):
        ds  = item[0] if isinstance(item, list) else item.get('date', '')
        val = item[1] if isinstance(item, list) else item.get('value', 0)
        try:
            key = _dt.fromisoformat(str(ds)[:10]).strftime('%b %y')
            monthly_pnl[key] = monthly_pnl.get(key, 0) + float(val)
        except Exception:
            pass

    months = list(monthly_pnl.items())[-6:]  # last 6 months
    sign   = '+' if gain >= 0 else ''

    intro = _intro_clip()

    # Hero (3s): "Monthly P&L" title fades in
    month_name = _dt.now().strftime('%B %Y')

    def hero_frame(t):
        return fade_in_frame(t, f'Monthly P&L\n{month_name}', 3.0, GOLD, 72, (W // 2, H // 2))

    hero = _clip(hero_frame, 3.0)

    # Data (21.5s): bars draw left to right, one per 3s
    DUR_DATA   = max(21.5, len(months) * 3.0 + 2.5)
    bar_dur    = 2.0    # seconds per bar animation
    bar_gap    = 1.5    # gap between bars starting
    start_y    = 550
    bar_h      = 120
    bar_spacing = bar_h + 40

    def data_frame(t):
        from reels.animator import _bg_frame, _draw_alpha_text, _load_font
        from PIL import Image, ImageDraw
        import numpy as np

        img  = Image.fromarray(_bg_frame(t))
        draw = ImageDraw.Draw(img)
        font_label = _load_font(34)
        font_val   = _load_font(32, bold=True)

        for i, (month, val) in enumerate(months):
            bar_start_t = i * bar_gap
            elapsed     = max(t - bar_start_t, 0)
            progress    = min(elapsed / bar_dur, 1.0)
            color       = GREEN if val >= 0 else RED

            y_top  = start_y + i * bar_spacing
            max_bw = 700
            bar_w  = int(max_bw * progress)

            # Bar
            draw.rectangle([180, y_top, 180 + bar_w, y_top + 60], fill=color)

            # Month label (always visible)
            draw.text((160, y_top + 30), month, fill=WHITE, font=font_label, anchor='rm')

            # Value label (fades in when bar is drawn)
            if progress > 0.9:
                val_alpha = int(255 * min((progress - 0.9) / 0.1, 1.0))
                sign_c    = '+' if val >= 0 else ''
                img = _draw_alpha_text(img, (180 + max_bw + 80, y_top + 30),
                                       f'{sign_c}{val:.1f}%', font_val, color, val_alpha)

        # Total gain (fades in at the end)
        if t > len(months) * bar_gap + bar_dur:
            elapsed_end = t - (len(months) * bar_gap + bar_dur)
            alp = min(int(255 * elapsed_end / 1.0), 255)
            img = _draw_alpha_text(img, (W // 2, start_y + len(months) * bar_spacing + 60),
                                   f'Total: {sign}{gain:.1f}%', font_val, GOLD, alp)
        return np.array(img)

    data_clip = _clip(data_frame, DUR_DATA)

    def cta_frame(t):
        return cta_fade_frame(t, 'Open IC Markets', _IB_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta]


# ── Transparency (25s) ────────────────────────────────────────────────────────

def make_transparency_reel(data: dict) -> list:
    """Returns [intro, hero, data, cta] VideoClips for transparency post (~25s)."""
    acct = data.get('account', {})
    gain = float(acct.get('gain') or 0)
    dd   = float(acct.get('drawdown') or 0)
    bal  = float(acct.get('balance') or 0)

    intro = _intro_clip()

    # Hero (4s): loss % smashes in red, holds
    def hero_frame(t):
        return countup_frame(t, 0, gain, 2.0, '{:.1f}%', RED, 140, (W // 2, H // 2))

    hero = _clip(hero_frame, 4.0)

    # Data (17.5s): two-part cascade — WHAT HAPPENED + WHAT CHANGED
    happened_lines = [
        'WHAT HAPPENED',
        'Position sizing errors compounded',
        'during a volatile XAUUSD run.',
        'Entry frequency was too high.',
        'Capital eroded faster than wins recovered.',
    ]
    changed_lines = [
        'WHAT CHANGED',
        'Reduced trade frequency.',
        'Tightened session filters.',
        'London/NY overlap only.',
        f'Balance: ${bal:,.0f}  |  Max DD: {dd:.1f}%',
    ]

    def data_frame(t):
        from reels.animator import _bg_frame, _draw_alpha_text, _load_font
        import numpy as np
        from PIL import Image

        img = Image.fromarray(_bg_frame(t))

        # First section: 0–8s
        for i, line in enumerate(happened_lines):
            bold  = (line == 'WHAT HAPPENED')
            color = AMBER if bold else WHITE
            fs    = 44 if bold else 36
            s_t   = i * 0.6
            elapsed = max(t - s_t, 0)
            alp   = min(int(255 * elapsed / 0.4), 255)
            img   = _draw_alpha_text(img, (W // 2, 600 + i * 70), line,
                                     _load_font(fs, bold=bold), color, alp)

        # Second section starts at 9s
        for i, line in enumerate(changed_lines):
            bold  = (line == 'WHAT CHANGED')
            color = GOLD if bold else WHITE
            fs    = 44 if bold else 36
            s_t   = 9.0 + i * 0.6
            elapsed = max(t - s_t, 0)
            alp   = min(int(255 * elapsed / 0.4), 255)
            img   = _draw_alpha_text(img, (W // 2, 1150 + i * 70), line,
                                     _load_font(fs, bold=bold), color, alp)

        import numpy as np
        return np.array(img)

    data_clip = _clip(data_frame, 17.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Full history on Myfxbook', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta]


# ── Recovery Plan (28s) ───────────────────────────────────────────────────────

_RECOVERY_MONTHS = [
    ('July',      1000, 1500.00),
    ('August',    1000, 3750.00),
    ('September', 1000, 7125.00),
    ('October',   1000, 12187.50),
    ('November',  1000, 19781.25),
    ('December',  1000, 31171.88),
]


def make_recovery_plan_reel() -> list:
    """Returns [intro, hero, data, cta] VideoClips for recovery-plan (~28s)."""
    from datetime import datetime as _dt
    now_month = _dt.now().strftime('%B')

    intro = _intro_clip()

    # Hero (3s): title + subtitle
    def hero_frame(t):
        return fade_in_frame(t, 'Recovery Plan\n$1,000/month  ·  50% target', 3.0,
                             GOLD, 60, (W // 2, H // 2))

    hero = _clip(hero_frame, 3.0)

    # Data (21.5s): table rows appear one by one, balance counts up per row
    ROW_DUR = 3.0
    GAP     = 0.4
    DUR_DATA = len(_RECOVERY_MONTHS) * (ROW_DUR + GAP) + 2.5

    def data_frame(t):
        from reels.animator import _bg_frame, _draw_alpha_text, _load_font
        from PIL import Image, ImageDraw
        import numpy as np

        img   = Image.fromarray(_bg_frame(t))
        draw  = ImageDraw.Draw(img)
        font  = _load_font(36)
        fontb = _load_font(36, bold=True)
        start_y = 460

        # Header
        header_alp = min(int(255 * t / 0.5), 255)
        img = _draw_alpha_text(img, (W // 2, start_y - 60), 'Month · +$1K · Balance',
                               font, MUTED, header_alp)
        img = _draw_alpha_text(img, (W // 2, start_y - 100), '_' * 40,
                               _load_font(20), GOLD, header_alp)

        for i, (month, topup, end_bal) in enumerate(_RECOVERY_MONTHS):
            row_start = i * (ROW_DUR + GAP)
            elapsed   = max(t - row_start, 0)
            progress  = min(elapsed / ROW_DUR, 1.0)

            if progress <= 0:
                continue

            is_now = (month == now_month)
            prefix = '> ' if is_now else '  '
            color  = GOLD if is_now else WHITE

            # Balance counts up during this row's window
            current_bal = end_bal * _ease_out(elapsed, ROW_DUR)
            row_text    = f'{prefix}{month}  +${topup:,}  →  ${current_bal:,.0f}'
            y           = start_y + i * 70

            alp = min(int(255 * elapsed / 0.3), 255)
            img = _draw_alpha_text(img, (W // 2, y), row_text,
                                   fontb if is_now else font, color, alp)

        # Projected total slams in at the end
        end_t = len(_RECOVERY_MONTHS) * (ROW_DUR + GAP) + 0.5
        if t > end_t:
            proj_alp = min(int(255 * (t - end_t) / 0.5), 255)
            img = _draw_alpha_text(img, (W // 2, start_y + len(_RECOVERY_MONTHS) * 70 + 60),
                                   'Projected: $31,171', _load_font(48, bold=True), GOLD, proj_alp)

        return np.array(img)

    data_clip = _clip(data_frame, DUR_DATA)

    def cta_frame(t):
        return cta_fade_frame(t, 'Open IC Markets', _IB_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta]


# ── Edu (22s) ─────────────────────────────────────────────────────────────────

def make_edu_reel(edu_type: str, content: dict) -> list:
    """Returns [intro, hero, data, cta] VideoClips for edu post (~22s)."""
    intro = _intro_clip()

    if edu_type == 'risk':
        title     = f"Rule #{content['rule_num']} — {content['title']}"
        body_text = content.get('body', '')
        example   = (f"${content['example_account']:,} account\n"
                     f"→ max ${content['example_risk']:,} per trade\n"
                     f"at {content['example_rr']}")

        # Hero (5s): title types onto screen
        def hero_frame(t):
            return typewriter_frame(t, title, 5.0, GOLD, 56, (W // 2, H // 2))

        hero = _clip(hero_frame, 5.0)

        # Data (13.5s): body fades in, example animates
        body_lines = [body_text[i:i+42] for i in range(0, len(body_text), 42)]
        ex_lines   = example.split('\n')

        def data_frame(t):
            return cascade_text_frame(
                t,
                body_lines + [''] + ex_lines,
                13.5, 0.8, WHITE, 38, 620)

        data_clip = _clip(data_frame, 13.5)

    elif edu_type == 'pairs':
        pair  = content.get('pair', 'XAUUSD')
        title = f"Pair Spotlight — {pair}"

        def hero_frame(t):
            return typewriter_frame(t, title, 5.0, GOLD, 60, (W // 2, H // 2))

        hero = _clip(hero_frame, 5.0)

        info_lines = [
            f"Best session: {content.get('best_session', '')}",
            f"Avg spread (IC Markets Raw): {content.get('avg_spread', '')}",
            f"Daily volatility: {content.get('volatility', '')}",
            '',
            f"My edge: {content.get('my_edge', '')}",
        ]

        def data_frame(t):
            return cascade_text_frame(t, info_lines, 13.5, 0.8, WHITE, 36, 640)

        data_clip = _clip(data_frame, 13.5)

    else:  # setup
        pair  = content.get('pair', 'XAUUSD')
        title = f"Setup — {pair} {content.get('direction', 'LONG')}"

        def hero_frame(t):
            return typewriter_frame(t, title, 5.0, GOLD, 58, (W // 2, H // 2))

        hero = _clip(hero_frame, 5.0)

        steps = content.get('steps', [])
        step_lines = [f"{i+1}. {s[0]}" for i, s in enumerate(steps)]
        step_detail = []
        for s in steps:
            step_detail.append(f'   {s[1]}')

        def data_frame(t):
            return cascade_text_frame(t, step_lines + step_detail, 13.5, 0.6, WHITE, 36, 640)

        data_clip = _clip(data_frame, 13.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Open IC Markets', _IB_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta]
```

- [ ] **Step 4: Fix `_ease_out` reference in scenes.py**

`_ease_out` is in `animator.py`. Add to the imports at the top of `scenes.py` (after the existing imports):

```python
from reels.animator import _ease_out
```

- [ ] **Step 5: Run tests — expect PASS**

```
python -m pytest instagram/tests/test_reels.py -k "monthly_reel or transparency_reel or recovery_plan_reel or edu_reel" -v
```

Expected: all 4 PASS

- [ ] **Step 6: Run full test suite**

```
python -m pytest instagram/tests/test_reels.py -v
```

Expected: all tests PASS (skip render test if no ffmpeg)

- [ ] **Step 7: Commit**

```bash
git add instagram/reels/scenes.py
git commit -m "feat: add scenes.py - monthly, transparency, recovery_plan, edu Reel composers"
```

---

## Task 7: `post.py` — Add `publish_reel()`

**Files:**
- Modify: `instagram/post.py`

- [ ] **Step 1: Write failing test**

Append to `instagram/tests/test_reels.py`:

```python
def test_publish_reel_function_exists():
    from post import publish_reel
    import inspect
    sig = inspect.signature(publish_reel)
    assert 'video_url' in sig.parameters
    assert 'caption' in sig.parameters
```

- [ ] **Step 2: Run — expect FAIL**

```
python -m pytest instagram/tests/test_reels.py::test_publish_reel_function_exists -v
```

- [ ] **Step 3: Append `publish_reel` to `instagram/post.py`**

Append after the existing `publish()` function:

```python

def publish_reel(video_url: str, caption: str) -> str:
    """Publish a video as an Instagram Reel.

    Two-step Meta Graph API: create container → poll until FINISHED → publish.
    Poll timeout is 5 minutes (video encoding is slower than images).
    """
    data = _check(requests.post(
        f'{GRAPH}/{IG_ID}/media',
        params={
            'media_type':   'REELS',
            'video_url':    video_url,
            'caption':      caption,
            'access_token': TOKEN,
        }
    ))
    container_id = data['id']
    print(f'  reel container created: {container_id}')

    for attempt in range(30):          # 30 × 10s = 5 minutes
        time.sleep(10)
        status = _check(requests.get(
            f'{GRAPH}/{container_id}',
            params={'fields': 'status_code', 'access_token': TOKEN}
        ))
        code = status.get('status_code')
        if code == 'FINISHED':
            break
        print(f'  encoding… ({code}) attempt {attempt + 1}/30')
    else:
        raise TimeoutError('Reel container did not finish processing within 5 minutes')

    result = _check(requests.post(
        f'{GRAPH}/{IG_ID}/media_publish',
        params={
            'creation_id':  container_id,
            'access_token': TOKEN,
        }
    ))
    post_id = result['id']
    print(f'  reel published: {post_id}')
    return post_id
```

- [ ] **Step 4: Run — expect PASS**

```
python -m pytest instagram/tests/test_reels.py::test_publish_reel_function_exists -v
```

- [ ] **Step 5: Commit**

```bash
git add instagram/post.py instagram/tests/test_reels.py
git commit -m "feat: add publish_reel() to post.py - REELS API with 5-min polling"
```

---

## Task 8: `run_reel.py` — Entry Point

**Files:**
- Create: `instagram/run_reel.py`

- [ ] **Step 1: Implement `run_reel.py`**

Create `instagram/run_reel.py`:

```python
"""
Entry point for the Instagram Reels automation workflow.

Env vars (same secrets as insta-post.yml plus):
  POST_TYPE         — weekly|monthly|daily|trust|edu|transparency|recovery-plan
  POST_LANG         — en|tamil (default en)
  RECOVERY_START    — YYYY-MM-DD (secret, optional)
  IG_USER_ID        — Instagram Business account numeric ID
  META_ACCESS_TOKEN — long-lived Page Access Token
  GITHUB_TOKEN      — automatically provided
  GITHUB_REPOSITORY — automatically provided (owner/repo)
"""

import json, os, subprocess, sys, time
from datetime import date, datetime
from pathlib import Path

ROOT      = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / 'data' / 'vera-snapshot.json'
REEL_DIR  = ROOT / 'instagram' / 'reels'


def load_data() -> dict:
    with open(DATA_FILE) as f:
        return json.load(f)


def commit_and_push(video_path: Path) -> str:
    """Commit MP4 and return its raw GitHub URL."""
    repo   = os.environ.get('GITHUB_REPOSITORY', '')
    branch = 'master'
    rel    = video_path.relative_to(ROOT).as_posix()

    cmds = [
        ['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'],
        ['git', 'config', 'user.name',  'github-actions[bot]'],
        ['git', 'add',    str(video_path)],
        ['git', 'commit', '-m', f'auto: instagram reel {date.today()} [skip ci]'],
        ['git', 'pull',   '--rebase', 'origin', branch],
        ['git', 'push',   'origin', branch],
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0 and 'nothing to commit' not in r.stdout:
            print(r.stderr, file=sys.stderr)

    return f'https://raw.githubusercontent.com/{repo}/{branch}/{rel}'


def main():
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / 'instagram'))

    from reels.scenes import (
        make_daily_reel, make_weekly_reel, make_trust_reel,
        make_monthly_reel, make_transparency_reel,
        make_recovery_plan_reel, make_edu_reel,
    )
    from reels.audio  import get_track
    from reels.render import render
    from captions     import (weekly, monthly, trust, daily_status,
                              transparency, recovery_plan, edu as edu_caption)
    from post         import publish_reel

    data      = load_data()
    account   = data.get('account', {})
    today     = date.today()
    post_type = os.environ.get('POST_TYPE', 'weekly')
    lang      = os.environ.get('POST_LANG', 'en')

    # Recovery day counter
    recovery_day = 0
    rs = os.environ.get('RECOVERY_START', '')
    if rs and account.get('gain', 0) < 0:
        try:
            _start       = datetime.strptime(rs, '%Y-%m-%d').date()
            recovery_day = max(1, (today - _start).days + 1)
        except Exception:
            pass

    print(f'Generating Reel: {post_type} ({today}) lang={lang} recovery_day={recovery_day}')

    REEL_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REEL_DIR / f'{today.isoformat()}-{post_type}.mp4'

    # ── Select clips + caption ────────────────────────────────────────────────
    if post_type == 'daily':
        clips   = make_daily_reel(data, recovery_day=recovery_day)
        caption = daily_status(account, data.get('openTrades', []),
                               lang=lang, recovery_day=recovery_day)

    elif post_type == 'weekly':
        clips   = make_weekly_reel(data, recovery_day=recovery_day)
        caption = weekly(account, lang=lang, recovery_day=recovery_day)

    elif post_type == 'monthly':
        clips   = make_monthly_reel(data)
        # monthly_pnl for caption
        monthly_pnl: dict = {}
        for item in data.get('dailyGain', []):
            ds  = item[0] if isinstance(item, list) else item.get('date', '')
            val = item[1] if isinstance(item, list) else item.get('value', 0)
            try:
                key = datetime.fromisoformat(str(ds)[:10]).strftime('%b %y')
                monthly_pnl[key] = monthly_pnl.get(key, 0) + float(val)
            except Exception:
                pass
        caption = monthly(account, monthly_pnl, lang=lang)

    elif post_type == 'transparency':
        clips   = make_transparency_reel(data)
        caption = transparency(account, lang=lang)

    elif post_type == 'recovery-plan':
        clips   = make_recovery_plan_reel()
        caption = recovery_plan(lang=lang)

    elif post_type == 'edu':
        from edu_content  import get_edu_content
        from run          import read_counter, write_and_commit_counter
        idx               = read_counter()
        edu_type, content = get_edu_content(idx)
        next_idx          = (idx + 1) % 12
        clips             = make_edu_reel(edu_type, content)
        caption           = edu_caption(edu_type, content, lang=lang)
        write_and_commit_counter(next_idx)

    else:  # trust
        clips   = make_trust_reel(data)
        caption = trust(account, lang=lang)

    # ── Render ────────────────────────────────────────────────────────────────
    audio_path = get_track(post_type)
    render(clips, audio_path, str(out_path))
    print(f'  rendered: {out_path}  ({out_path.stat().st_size // 1024} KB)')

    # ── Publish ───────────────────────────────────────────────────────────────
    video_url = commit_and_push(out_path)
    print(f'  url: {video_url}')

    print('  waiting 60s for GitHub CDN...')
    time.sleep(60)

    publish_reel(video_url, caption)
    print(f'Done — {post_type} Reel published.')


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Verify imports don't crash**

```bash
cd vera-level-fx
python -c "import sys; sys.path.insert(0,'instagram'); import run_reel; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add instagram/run_reel.py
git commit -m "feat: add run_reel.py - Reels entry point mirroring run.py"
```

---

## Task 9: `insta-reel.yml` — GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/insta-reel.yml`

- [ ] **Step 1: Create the workflow**

Create `.github/workflows/insta-reel.yml`:

```yaml
name: Instagram Reel Auto-Post

on:
  schedule:
    # Mon/Wed/Fri 07:00 SGT = 23:00 UTC Sun/Tue/Thu
    - cron: '0 23 * * 0,2,4'
  workflow_dispatch:
    inputs:
      post_type:
        description: 'weekly|monthly|daily|trust|edu|transparency|recovery-plan'
        required: false
        default: 'weekly'
      post_lang:
        description: 'Caption language (en|tamil)'
        required: false
        default: 'en'

permissions:
  contents: write

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  reel:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip
          cache-dependency-path: instagram/requirements.txt

      - name: Install dependencies
        run: pip install -r instagram/requirements.txt

      - name: Generate Reel & post to Instagram
        env:
          IG_USER_ID:        ${{ secrets.IG_USER_ID }}
          META_ACCESS_TOKEN: ${{ secrets.META_ACCESS_TOKEN }}
          GITHUB_TOKEN:      ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          POST_TYPE:         ${{ github.event.inputs.post_type }}
          POST_LANG:         ${{ github.event.inputs.post_lang }}
          RECOVERY_START:    ${{ secrets.RECOVERY_START }}
          BRAND_IB_URL:      ${{ secrets.BRAND_IB_URL }}
        run: python instagram/run_reel.py

      - name: Upload reel artifact
        uses: actions/upload-artifact@v4
        with:
          name: instagram-reel-${{ github.run_id }}
          path: instagram/reels/
          retention-days: 14
```

- [ ] **Step 2: Validate YAML syntax**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/insta-reel.yml'))); print('YAML OK')"
```

Expected: `YAML OK`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/insta-reel.yml
git commit -m "feat: add insta-reel.yml - Mon/Wed/Fri scheduled Reels workflow"
```

---

## Task 10: Audio Assets — User Action

**Files:** `instagram/assets/audio/*.mp3` (6 tracks, sourced by user)

This task is performed by the user — no code changes.

- [ ] **Step 1: Source 6 CC0 tracks**

Visit pixabay.com/music and search for each mood. Download as MP3 (≥35s).

| File to save | Search term on Pixabay |
|---|---|
| `instagram/assets/audio/pulse.mp3` | "upbeat electronic energetic" |
| `instagram/assets/audio/momentum.mp3` | "driving confident corporate" |
| `instagram/assets/audio/reflect.mp3` | "thoughtful piano ambient" |
| `instagram/assets/audio/tension.mp3` | "dark atmospheric tension" |
| `instagram/assets/audio/rise.mp3` | "hopeful inspirational building" |
| `instagram/assets/audio/calm.mp3` | "calm clean minimal focus" |

All tracks on Pixabay are free for commercial use with no attribution required.

- [ ] **Step 2: Commit the tracks**

```bash
git add instagram/assets/audio/*.mp3
git commit -m "assets: add 6 CC0 background music tracks for Reels"
```

> **Note:** audio.py gracefully returns `None` when tracks are missing — Reels will render as silent until this task is complete. All other tasks can proceed first.

---

## Task 11: End-to-End Dry Run

Verify the full pipeline works locally before the first scheduled run.

- [ ] **Step 1: Install dependencies locally**

```bash
pip install -r instagram/requirements.txt
```

Verify ffmpeg is available:
```bash
ffmpeg -version
```

If not installed on Windows: `winget install Gyan.FFmpeg`

- [ ] **Step 2: Run a daily Reel locally (no Meta publish)**

```bash
cd vera-level-fx
python -c "
import sys, os, json
sys.path.insert(0,'instagram')
os.environ['POST_TYPE'] = 'daily'
os.environ['GITHUB_REPOSITORY'] = 'test/test'

from reels.scenes import make_daily_reel
from reels.audio  import get_track
from reels.render import render

with open('data/vera-snapshot.json') as f:
    data = json.load(f)

clips     = make_daily_reel(data)
audio     = get_track('daily')
render(clips, audio, 'instagram/reels/test-daily.mp4')
print('Done — check instagram/reels/test-daily.mp4')
"
```

Expected: `test-daily.mp4` created (~5–15 MB)

- [ ] **Step 3: Verify the MP4 plays**

Open `instagram/reels/test-daily.mp4` in VLC or Windows Media Player. Confirm:
- Duration ~10 seconds
- 1080×1920 resolution
- Background animations visible
- Text legible
- Audio playing (if track available)

- [ ] **Step 4: Trigger a live run via CLI**

```bash
gh workflow run insta-reel.yml -f post_type=trust -f post_lang=en
gh run watch
```

Expected: workflow completes, Reel appears on @veralevel.fx

- [ ] **Step 5: Clean up test file**

```bash
git rm instagram/reels/test-daily.mp4
git commit -m "chore: remove test reel file"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] 7 post types: daily, weekly, monthly, trust, edu, transparency, recovery-plan — all in scenes.py
- [x] 4-scene structure (intro/hero/data/cta) — all composers follow it
- [x] Durations: daily≈10s, weekly≈12s, monthly≈28s, trust≈12s, transparency≈25s, recovery-plan≈28s, edu≈22s
- [x] Animation primitives: countup, cascade_text, fade_in, typewriter, slide_bar, particle_drift, radial_bg
- [x] Audio: 6 CC0 tracks, 0.15 volume, 0.5s fade-in, 1.0s fade-out — audio.py
- [x] Meta REELS API, 5-min poll timeout — publish_reel() in post.py
- [x] Entry point with RECOVERY_START + POST_LANG env vars — run_reel.py
- [x] GitHub Actions Mon/Wed/Fri schedule + manual trigger — insta-reel.yml
- [x] Static pipeline (`run.py`, `generate.py`) untouched

**Placeholder scan:** No TBD/TODO found.

**Type consistency:**
- `make_frame(t)` → `np.ndarray (H, W, 3)` throughout animator.py and scenes.py
- `get_track(post_type)` → `Path | None` — audio.py
- `build_audio_clip(path, dur)` → AudioFileClip | None — audio.py
- `render(clips, audio_path, out_path)` — render.py
- `publish_reel(video_url, caption)` → str — post.py
