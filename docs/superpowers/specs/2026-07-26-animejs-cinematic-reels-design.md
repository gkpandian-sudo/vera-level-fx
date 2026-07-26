# anime.js Cinematic Hero Reels — Design Spec (v2)

**Date:** 2026-07-26 (revised after Fable 5 review)
**Branch:** `worktree-feat+animejs-cinematic-reels`
**Author:** Pandian / Vera Level FX

---

## Goal

Upgrade the automated Instagram reels pipeline to produce cinematic, broadcast-quality hero cards using anime.js running in a headless Playwright browser. Data scenes (equity curve, cascade text, CTA, broker) receive a matching Direction C aesthetic upgrade in pure Python — no additional browser overhead.

---

## Critical Clarification — Which Workflow Is Modified

`ai-reel.yml` (03:30 SGT) runs `instagram/higgsfield/pipeline.py` → matplotlib Path E. It **never** imports `reels/scenes.py`.

`reels/scenes.py` is executed by `instagram/run_reel.py`, called by **`insta-reel.yml`** (07:00 + 20:00 SGT).

**This spec modifies `insta-reel.yml` + `reels/scenes.py`.** `ai-reel.yml` and Path E are **out of scope and untouched.**

---

## Visual Direction: Direction C — Cinematic / Broadcast Impact

- **Letterbox bars**: 4px emerald strips (native 1080px scale) sweep in at top and bottom on every scene
- **6-zone canvas layout**: content distributed across the full 9:16 frame — no central clustering
- **Typography**: oversized, weight-900, tight letter-spacing — broadcast stat aesthetic; requires bundled WOFF2 font
- **Palette**: NAVY `#001835` (= `animator.py` NAVY `(0,24,53)`), EMERALD `#059669`, WHITE `#FFFFFF`, RED `#EF4444`, MUTED `#6B7280` — pinned to `animator.py` constants to ensure visual continuity across hero and data scenes
- **Easing**: anime.js v3.2.2 spring, `easeOutBack`, `easeOutExpo` — snappy with controlled overshoot
- **Background parity**: HTML templates replicate `animated_bg_frame` — CSS radial gradient from `#001835` (centre) to `#010912` (edges) + SVG/canvas noise overlay to match Python film grain (prevents H.264 banding after IG re-encode, matches adjacent Python scenes visually)

---

## Architecture

### Hero card (all 4 reel types) — Playwright + anime.js

```
Python: build_hero_html(post_type, data, duration) → Path
  Loads instagram/reels/templates/hero_{post_type}.html
  Coerces all numeric fields: float(data.get('balance') or 0)
  Escapes string fields with json.dumps() before f-string injection
  Inlines anime.min.js + WOFF2 fonts as base64 → fully self-contained HTML
  Writes to tempfile.mkdtemp() → returns absolute Path

Python: capture_frames(html_path, duration, fps=30, timeout_s=120) → list[Path]
  Playwright Chromium via channel='chrome' (pre-installed on ubuntu-latest, zero download)
  viewport={'width': 1080, 'height': 1920}, device_scale_factor=1
  page.goto(f"file://{html_path}")
  page.evaluate("document.fonts.ready")     ← await WOFF2 font load
  for ms in range(0, int(duration*1000), int(1000/fps)):
      page.evaluate(f"seekFrame({ms})")     ← resolves after 2× rAF paint
      page.screenshot(path=frame_png_path)  ← write PNG to same temp dir
  Browser always closed in finally block. Raises RuntimeError if > timeout_s.
  Returns list[Path] — PNGs on disk, not in-memory arrays (~930 MB peak avoided)

Python: frames_to_clip(frame_paths, fps=30) → VideoClip
  MoviePy ImageSequenceClip(frame_paths, fps=fps).set_fps(fps)
  Drop-in for existing _clip() result; .set_fps() required for _with_stinger compat
```

### anime.js seekable timeline (in every HTML template)

```javascript
// anime.js v3.2.2 IIFE — inlined into HTML, no external src= reference
// ZERO CSS transitions / @keyframes — only anime.js drives motion
// (CSS-native animation is not frozen by .seek() → frame drift)
let tl = null;
function buildTimeline(data) {
  tl = anime.timeline({ autoplay: false });
  tl.add({ ... });  // all animations chained here
}
window.seekFrame = function(ms) {
  return new Promise(resolve => {
    if (tl) tl.seek(ms);
    requestAnimationFrame(() => requestAnimationFrame(resolve));
  });
};
// page.evaluate("seekFrame(ms)") awaits the Promise → screenshot after paint
window.addEventListener('DOMContentLoaded', () => buildTimeline(INJECTED_DATA));
```

### Data scenes — enhanced Python (no browser)

Equity curve, cascade text, CTA, and broker card upgraded in `animator.py`, `effects.py`, `scenes.py`.

---

## CI Wiring — `insta-reel.yml` Changes Only

```yaml
# Add after existing 'pip install -r requirements.txt' step:
- name: Install Playwright
  run: pip install playwright
  # channel='chrome' uses Chrome for Testing pre-installed on ubuntu-latest
  # No 'playwright install chromium' step — zero download, zero install time

# Add to workflow-level env:
env:
  BROWSER_HERO: '1'   # explicit opt-in — only set here, nowhere else
```

### CI Timing Impact

| Stage | Before | After |
|-------|--------|-------|
| Chromium download/install | — | 0s (pre-installed `channel='chrome'`) |
| Hero capture (daily/weekly, 120 frames) | — | +30–40s |
| Hero capture (trust/monthly, 150 frames) | — | +38–50s |
| Existing Python scenes | ~45s | ~45s unchanged |
| **Total per reel** | **~45s** | **~90–100s** |

---

## 9:16 Canvas Zone Map

Templates authored at native **1080×1920px** (`viewport={'width':1080,'height':1920}`, `device_scale_factor=1`, `body{overflow:hidden}`).

| Zone | px (1920px height) | % | Content |
|------|-------------------|---|---------|
| A | 0–249px | 0–13% | Brand pill |
| B | 249–538px | 13–28% | Context / eyebrow / LIVE badge |
| C | 538–1344px | 28–70% | **Hero metric** (subdivided for Daily/Weekly) |
| D | 1344–1536px | 70–80% | Divider + secondary sentence |
| E | 1536–1747px | 80–91% | 3-stat row |
| F | 1747–1920px | 91–100% | Myfxbook verify + handle |

Zone C subdivisions for Daily and Weekly:
- **C1** (538–786px): label + giant primary metric
- **C2** (800–1075px): sparkline (Daily) or giant % number (Weekly)
- **C3** (1080–1344px): secondary metric

---

## Data Contract for `build_hero_html`

All fields coerced before injection. String fields use `json.dumps()`.

| Field | Source key | Coercion | Default |
|-------|-----------|----------|---------|
| balance | `acct['balance']` | `float(... or 0)` → `f"${v:,.0f}"` | `$0` |
| todayDaily | `acct['todayDaily'] or acct['daily']` | `float(... or 0)` | `0.00` |
| winRate | `acct['winRate']` | `float(... or 0)` | `0` (show `—` if 0) |
| profitFactor | `acct['profitFactor']` | `float(... or 0)` | `0.00` |
| pips | `acct['pips']` | `int(... or 0)` | `0` |
| trades | `acct['trades']` | `int(... or 0)` | `0` |
| gain | `acct['gain']` | `float(... or 0)` | `0.0` |
| drawdown | `acct['drawdown']` | `float(... or 0)` | `0.0` |
| weekly_gain | caller arg | `float(... or 0)` | `0.0` |
| open_pairs | `openTrades[:5]` → symbols | `json.dumps(list)` | `[]` |
| monthly_pnl | `monthly_pnl_from_daily(data['dailyGain'])` | reuse `captions.py` function | `{}` |

**Trust hero special case**: `winRate == 0` → render verification-only layout (no ring), matching existing `scenes.py:260–272` fallback.

---

## Font Strategy

Bundle locally — no web fonts, no CDN:

```
instagram/reels/templates/vendor/
  anime.min.js        ← v3.2.2 IIFE, inlined as <script> block in HTML output
  Roboto-Black.woff2  ← weight 900, base64-embedded in @font-face in HTML output
  Roboto-Bold.woff2   ← weight 700
  Roboto-Regular.woff2← weight 400
```

`build_hero_html` reads these files once, base64-encodes them, and inlines them into the generated HTML so each output file is fully self-contained at the `file://` path. `capture_frames` awaits `document.fonts.ready` before starting the frame loop.

---

## Hero Templates — Per Reel Type

### Daily (`hero_daily.html`) — 4 seconds, 120 frames

| Zone | Content | Animation |
|------|---------|-----------|
| A | `Vera Level FX · Live Account` pill | fade in |
| B | `IC Markets · ASIC` + `● LIVE POSITION UPDATE` | fade + slide up 16px |
| C1 | `Account Balance` + `$24,813` | odometer: `spring(1,80,10,0)` |
| C2 | Equity sparkline, L→R canvas draw | `easeInOutQuad` 800ms |
| C3 | `+2.14%` + `Today's P&L` | `easeOutBack(1.8)` snap |
| D | Divider sweep + open pairs | `easeOutQuart` |
| E | Win rate · Profit Factor · Pips | fade + slide 16px |
| F | `Myfxbook #12044019 · All trades verified` + handle | fade |

Data: `balance`, `todayDaily`, `winRate`, `profitFactor`, `pips`, `open_pairs`.

### Weekly (`hero_weekly.html`) — 4 seconds, 120 frames

| Zone | Content | Animation |
|------|---------|-----------|
| A | `Weekly Performance` pill | fade |
| B | `@veralevel.fx` + week-end date | fade + slide |
| C1 | `This Week` label | fade |
| C2 | `+2.34%` weight-900, ~340px font-size | `easeOutBack(2.5)` |
| C3 | `Total return: +12.4%` count-up | `easeOutQuart` |
| D | Divider + `{trades} trades · All verified` | sweep |
| E | Win rate · Profit Factor · Pips | fade + slide |
| F | `Full track record: Myfxbook #12044019` + handle | fade |

Data: `weekly_gain`, `gain`, `winRate`, `trades`, `profitFactor`, `pips`.

### Trust (`hero_trust.html`) — 5 seconds, 150 frames

| Zone | Content | Animation |
|------|---------|-----------|
| A | `Verified Track Record` pill | fade |
| B | `Myfxbook #12044019` + `Live IC Markets · ASIC` | fade + slide |
| C (full) | SVG arc ring, 672px diameter | `easeOutCubic` arc to winRate%, count-up |
| D | Divider + `{winRate}% win rate · {trades} verified trades` | sweep |
| E | Profit Factor · Total Return · Max DD | fade + slide |
| F | `No screenshots. Raw Myfxbook data only.` + handle | fade |

winRate == 0 fallback: centred text layout, no ring.
Data: `winRate`, `trades`, `profitFactor`, `gain`, `drawdown`.

### Monthly (`hero_monthly.html`) — 5 seconds, 150 frames

| Zone | Content | Animation |
|------|---------|-----------|
| A | `Monthly P&L · {month_name}` pill | fade |
| B | `@veralevel.fx` + `+{this_month}% this month` | fade + slide |
| C+D | 6-month bar chart from `monthly_pnl_from_daily()` | `easeOutQuart`, 130ms stagger |
| E | Total return · Win rate · Profit Factor | fade + slide |
| F | `Myfxbook #12044019 · Verify every month` + handle | fade |

**Scene list change**: the existing 5.5s Python `data_clip` bar chart in `make_monthly_reel` is **removed** (it would double-render the same chart). New scene list: `[hero_browser_clip, cta, broker]`. Total monthly reel: ~9s (was ~12.5s).

Data: `monthly_pnl_from_daily(data['dailyGain'])` (reuse `captions.py`), `gain`, `winRate`, `profitFactor`.

---

## New Files

```
instagram/reels/hero_browser.py
instagram/reels/templates/
  hero_daily.html
  hero_weekly.html
  hero_trust.html
  hero_monthly.html
  vendor/
    anime.min.js          ← v3.2.2 pinned; inlined into HTML at build time
    Roboto-Black.woff2    ← base64-embedded into HTML at build time
    Roboto-Bold.woff2
    Roboto-Regular.woff2
docs/superpowers/specs/
  2026-07-26-animejs-cinematic-reels-design.md
```

## Modified Files

```
instagram/reels/scenes.py        ← hero call wrapped in USE_BROWSER_HERO if/else
                                    make_monthly_reel: old Python data_clip removed
instagram/reels/animator.py      ← cascade_text_frame, cta_fade_frame upgrades
instagram/reels/effects.py       ← equity_curve_clip upgrades
instagram/requirements.txt       ← add: playwright>=1.44
.github/workflows/insta-reel.yml ← add pip install playwright + BROWSER_HERO=1 env
```

Blast radius of `animator.py` changes: edu, broker, transparency, signup, milestone reels all call `cascade_text_frame`. The `ease_out_back` overshoot (1.5) is mild — safe for multi-line content — but `test_reels.py` must pass with `BROWSER_HERO=0` before merge.

`ai-reel.yml`, `insta-post.yml`, `run_reel.py`, `captions.py`, `post.py`, `generate*.py`, `audio.py`, `render.py` are **untouched**.

---

## `scenes.py` Change Pattern

```python
USE_BROWSER_HERO = os.getenv('BROWSER_HERO', '0') == '1'  # OFF by default

if USE_BROWSER_HERO:
    try:
        from reels.hero_browser import build_hero_html, capture_frames, frames_to_clip
        html = build_hero_html('daily', data, DUR_HERO)
        frame_paths = capture_frames(html, DUR_HERO)
        hero = frames_to_clip(frame_paths)
    except Exception as e:
        print(f"[hero_browser] FAILED ({e}), falling back to Python hero", flush=True)
        hero = _clip(hero_frame, DUR_HERO)  # original path preserved
else:
    hero = _clip(hero_frame, DUR_HERO)      # original path unchanged
```

`BROWSER_HERO` is `'0'` everywhere except `insta-reel.yml`. All other workflows never import playwright.

---

## Rollback

1. **Automatic**: `try/except` in `scenes.py` catches any Playwright failure → Python hero → post always goes out
2. **Instant**: Remove `BROWSER_HERO: '1'` from `insta-reel.yml` → Python hero across all reel types
3. **Full**: Switch to `master` — worktree is isolated, master untouched
4. **Per-type**: Guard can be narrowed by `post_type` check inside the `if` block

---

## Out of Scope

- motion.dev — anime.js v3.2.2 covers all animation needs
- `ai-reel.yml` / matplotlib Path E — different pipeline, untouched
- Playwright for data/equity/CTA scenes — Python is faster and adequate
- Caption functions, run.py, run_reel.py, posting logic, static image pipeline, insta-post.yml
- Parallel Playwright capture — sequential seek is correct; multiple pages add complexity for <2× gain
