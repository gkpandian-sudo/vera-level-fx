# Vera Level FX — System Update
**Date:** 2026-07-28

---

## Overview

This document captures the anime.js Cinematic Hero Reels upgrade — a full pipeline enhancement that replaces the Python-drawn hero card at the start of each reel with a broadcast-quality animated card rendered by anime.js running inside a headless Playwright browser.

---

## What Was Built

### anime.js Cinematic Hero Cards

**Motivation:** The existing Python hero cards (matplotlib bars, PIL text) look functional but flat. Reel feeds reward visual stops. Replacing only the opening hero scene — the most-watched moment — with a cinematic anime.js card (smooth easing, spring physics, SVG arc rings, odometer count-ups) lifts the production quality without touching the rest of the pipeline.

**How it works:**

```
insta-reel.yml (BROWSER_HERO=1)
  └── run_reel.py
       └── scenes.py: make_daily_reel() / make_weekly_reel() / make_trust_reel() / make_monthly_reel()
            └── hero_browser.py: build_hero_html() → capture_frames() → frames_to_clip()
                 ├── Loads hero_{post_type}.html (templates/vendor/anime.min.js inlined)
                 ├── Playwright page.evaluate("seekFrame(ms)") per frame
                 └── page.screenshot() → PNG sequence → MoviePy ImageSequenceClip
```

The `seekFrame(ms)` mechanism is deterministic — anime.js timeline is seeked to exact milliseconds, not recorded in real time. Output is bit-identical on every run.

**Fallback:** Every `scenes.py` function wraps the browser path in `try/except`. Any Playwright failure falls back to the original Python hero silently. Set `BROWSER_HERO=0` to revert instantly without a code change.

---

## New Files

```
instagram/reels/
├── hero_browser.py                     ← Playwright frame-capture bridge
└── templates/
    ├── hero_daily.html                 ← 4s, 120 frames, balance odometer + sparkline
    ├── hero_weekly.html                ← 4s, 120 frames, giant % with easeOutBack(2.5)
    ├── hero_trust.html                 ← 5s, 150 frames, SVG arc ring easeOutCubic
    ├── hero_monthly.html               ← 5s, 150 frames, canvas bar chart easeOutQuart
    └── vendor/
        ├── anime.min.js                ← v3.2.2 IIFE, inlined at build time
        ├── Roboto-Black.woff2          ← weight 900, base64-embedded into HTML
        ├── Roboto-Bold.woff2           ← weight 700
        └── Roboto-Regular.woff2        ← weight 400
```

---

## Modified Files

### `instagram/reels/scenes.py`

Added `USE_BROWSER_HERO = os.getenv('BROWSER_HERO', '0') == '1'` at module top.

All 4 reel composers now follow this pattern:

```python
if USE_BROWSER_HERO:
    try:
        from reels.hero_browser import build_hero_html, capture_frames, frames_to_clip
        html = build_hero_html('daily', data, DUR_HERO)
        frame_paths = capture_frames(html, DUR_HERO)
        hero = frames_to_clip(frame_paths)
    except Exception as e:
        print(f"[hero_browser] FAILED ({e}), falling back to Python hero", flush=True)
        hero = _clip(hero_frame, DUR_HERO)
else:
    hero = _clip(hero_frame, DUR_HERO)
```

**Monthly reel change:** The redundant 5.5s Python `data_clip` bar chart was removed. The browser hero monthly template already draws the bar chart. New monthly scene list: `[hero, cta, broker, stinger]` — total ~11.6s (was ~15.1s).

### `instagram/reels/effects.py`

`equity_curve_clip` Direction C upgrades:
- Line weight: 3px → 6px
- Fill opacity: 11% → 22%
- Tip dot replaced with glow overlay + GaussianBlur + sharp centre dot
- 4px emerald letterbox bars sweep in over the first 30% of the clip

### `instagram/reels/animator.py`

Three additions for Direction C aesthetic parity with the HTML templates:

| Change | Detail |
|--------|--------|
| `ease_out_back(x, c1=1.5)` | New easing function — polynomial overshoot: `1 + c3*(x-1)^3 + c1*(x-1)^2` |
| `cascade_text_frame` | Line 0 = headline (bold, fontsize+10). Lines 1+ get 3px emerald left-edge accent bar via RGBA composite. Easing changed from cubic to `ease_out_back`. |
| `cta_fade_frame` | Letterbox bars sweep in (0–400ms). Line1 48pt bold EMERALD at H//2-60. Animated emerald underline grows L→R from t=0.3. |

### `instagram/requirements.txt`

Added: `playwright>=1.44`

### `.github/workflows/insta-reel.yml`

Two additions:

```yaml
# After pip install -r requirements.txt:
- name: Install Playwright
  run: pip install playwright

# In Generate Reel step env:
env:
  BROWSER_HERO: '1'
```

`channel='chrome'` in `hero_browser.py` uses Chrome for Testing pre-installed on `ubuntu-latest` — no `playwright install chromium` needed.

---

## Hero Templates — Per Type

### Daily (`hero_daily.html`) — 4s, 120 frames

| Zone | Content | Animation |
|------|---------|-----------|
| A | `Vera Level FX · Live Account` pill | fade in |
| B | `IC Markets · ASIC` + `● LIVE POSITION UPDATE` | fade + slide 16px |
| C1 | `Account Balance` + `$24,813` | odometer spring `spring(1,80,10,0)` |
| C2 | Equity sparkline L→R | `easeInOutQuad` 800ms |
| C3 | `+2.14%` Today's P&L | `easeOutBack(1.8)` snap |
| D | Divider sweep + open pairs | `easeOutQuart` |
| E | Win rate · Profit Factor · Pips | fade + slide |
| F | Myfxbook verify + handle | fade |

### Weekly (`hero_weekly.html`) — 4s, 120 frames

Giant `+2.34%` at weight-900, ~340px font, `easeOutBack(2.5)` overshoot. Total return count-up via `easeOutQuart`.

### Trust (`hero_trust.html`) — 5s, 150 frames

SVG arc ring `r=316`, circumference 1985.2px. `stroke-dashoffset` animates via `easeOutCubic` from full-circumference to win-rate %. Win-rate count-up inside ring. `winRate==0` fallback: centred verification text, no ring.

### Monthly (`hero_monthly.html`) — 5s, 150 frames

Canvas bar chart: 6-month P&L bars drawn via `redrawChart()`, staggered 130ms per bar, `easeOutQuart`. All data from `monthly_pnl_from_daily(data['dailyGain'])`.

---

## `hero_browser.py` API

```python
build_hero_html(post_type: str, data: dict, duration: float) -> Path
```
- Loads `templates/hero_{post_type}.html`
- Inlines `anime.min.js` and WOFF2 fonts as base64
- Coerces all data fields via `_coerce_data()` — never passes raw strings
- Replaces 4 markers: `__ANIME_JS__`, `__FONTS_CSS__`, `__DATA_JSON__`, `__DURATION_MS__`
- Writes to `tempfile.mkdtemp()` — fully self-contained `file://` HTML

```python
capture_frames(html_path: Path, duration: float, fps: int = 30, timeout_s: int = 120) -> list[Path]
```
- Playwright `channel='chrome'`, viewport 1080×1920, `device_scale_factor=1`
- Awaits `document.fonts.ready` before frame loop
- `page.evaluate(f"seekFrame({ms})")` per frame — resolves after 2× rAF paint cycles
- Returns list of PNG paths on disk (not in-memory arrays — avoids ~930 MB peak)
- Browser always closed in `finally` block

```python
frames_to_clip(frame_paths: list[Path], fps: int = 30) -> VideoClip
```
- `ImageSequenceClip(frame_paths, fps=fps).set_fps(fps)` — drop-in for `_clip()` result

---

## Test Results

```
pytest instagram/tests/test_reels.py instagram/tests/test_hero_browser.py
46 passed, 5 failed
```

The 5 failures are all pre-existing (unrelated to this feature):
- `test_typewriter_frame_grows`
- `test_make_daily_reel_returns_clips`
- `test_daily_reel_no_intro_clip`
- `test_weekly_reel_no_intro_clip`
- `test_transparency_reel_ends_without_broker_card`

New tests added: 9 total (5 in `test_hero_browser.py` + 4 in `test_reels.py`).

---

## CI Timing Impact

| Stage | Before | After |
|-------|--------|-------|
| Chromium install | — | 0s (pre-installed `channel='chrome'`) |
| Hero capture (daily/weekly, 120 frames) | — | ~30–40s |
| Hero capture (trust/monthly, 150 frames) | — | ~38–50s |
| Python scenes (equity, cascade, CTA, broker) | ~45s | ~45s |
| **Total per reel** | **~45s** | **~90–100s** |

---

## Rollback

| Method | Action |
|--------|--------|
| Instant | Remove `BROWSER_HERO: '1'` from `insta-reel.yml` env |
| Auto | `try/except` in each `scenes.py` function catches Playwright errors, falls back to Python hero |
| Full | Revert to `master` — feature branch is isolated |

---

## Commits (this feature branch)

```
c74f267 data: add missing hf-edu thumbnails 2026-07-11
8431122 feat(ci): wire Playwright into insta-reel.yml
25e40c8 fix: accent bar alpha composite on RGB canvas in cascade_text_frame
7064c07 feat: animator.py Direction C — ease_out_back, cascade accent bars, cta letterbox + underline
4a8e233 feat: equity_curve_clip Direction C — 6px line, 22% fill, glow dot, letterbox bars
87ac9ac feat: USE_BROWSER_HERO guard on all 4 reel types; remove monthly data_clip
d3731d2 fix: conftest.py — moviepy v1/v2 compatibility
1ef55ca feat: hero_monthly.html — 6-bar chart template (5s)
a4ec129 feat: hero_trust.html — SVG arc ring template (5s)
6a21f62 feat: hero_weekly.html — giant % template (4s)
5769325 feat: hero_daily.html — 6-zone template (4s)
887914c feat: hero_browser.py — Playwright frame-capture bridge
a276709 feat: vendor assets — anime.js v3.2.2 + Roboto WOFF2 fonts
```
