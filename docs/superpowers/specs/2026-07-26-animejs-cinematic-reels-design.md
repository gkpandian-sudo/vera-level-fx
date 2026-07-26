# anime.js Cinematic Hero Reels — Design Spec

**Date:** 2026-07-26
**Branch:** `worktree-feat+animejs-cinematic-reels`
**Author:** Pandian / Vera Level FX

---

## Goal

Upgrade the automated Instagram reels pipeline to produce cinematic, broadcast-quality hero cards using anime.js running in a headless Playwright browser. Data scenes (equity curve, cascade, CTA, broker) receive a matching Direction C aesthetic upgrade in pure Python — no additional browser overhead.

---

## Visual Direction: Direction C — Cinematic / Broadcast Impact

- **Letterbox bars**: 3px emerald strips sweep in at top and bottom on every scene
- **6-zone canvas layout**: content is distributed across the full 9:16 frame — no central clustering
- **Typography**: oversized, weight-900, tight letter-spacing — broadcast stat aesthetic
- **Palette**: unchanged — NAVY `#010E1F`, EMERALD `#059669`, WHITE, RED `#EF4444`, MUTED `#6B7280`
- **Easing**: anime.js spring, `easeOutBack`, `easeOutExpo` — snappy with controlled overshoot

---

## Architecture

### Hero card (all 4 reel types) — Playwright + anime.js

```
Python: build_hero_html(post_type, data, duration)
  → f-string template (no Jinja2) → /tmp/hero-{type}-{ts}.html

Python: capture_frames(html_path, duration, fps=30)
  → Playwright Chromium 1080×1920
  → for each frame: page.evaluate("seekFrame(ms)") + page.screenshot()
  → returns list[np.ndarray]  shape (1920, 1080, 3)

Python: frames_to_clip(frames, fps=30)
  → MoviePy ImageSequenceClip
  → returns VideoClip (drop-in for existing _clip() result)
```

The HTML templates expose `window.seekFrame(ms)` — a function that seeks the anime.js timeline to the given millisecond. Playwright calls this deterministically for each frame, producing the same output on every run. No real-time recording, no timing jitter.

### Data scenes — enhanced Python (no browser)

Equity curve, cascade text, CTA, and broker card are upgraded in-place inside the existing `animator.py` / `effects.py` / `scenes.py` Python pipeline.

---

## 9:16 Canvas Zone Map

Applies to all 4 hero HTML templates and the broker card. At 1080×1920 (4× the preview scale):

| Zone | Pixel range (1920px tall) | % of canvas | Content |
|------|--------------------------|-------------|---------|
| A | 0–249px | 0–13% | Brand pill — `Vera Level FX · Live Account` |
| B | 249–538px | 13–28% | Context / eyebrow — broker, session type, LIVE badge |
| C | 538–1344px | 28–70% | **Hero metric** — balance, weekly %, win-rate ring, or bar chart |
| D | 1344–1536px | 70–80% | Divider line + secondary sentence |
| E | 1536–1747px | 80–91% | 3-stat row — win rate · profit factor · pips |
| F | 1747–1920px | 91–100% | Myfxbook verify text + @veralevel.fx handle |

Zone C is subdivided for Daily and Weekly:

- **C1**: label + giant primary metric (balance / weekly %)
- **C2**: sparkline (Daily) or giant `%` number (Weekly) — fills the visual centre
- **C3**: secondary metric (daily P&L / total return)

---

## Hero Templates — Per Reel Type

### Daily (`hero_daily.html`) — 4 seconds, 120 frames

| Zone | Content | Animation |
|------|---------|-----------|
| A | `Vera Level FX · Live Account` pill | fade in |
| B | `IC Markets · ASIC` + `● LIVE POSITION UPDATE` | fade + slide up 8px |
| C1 | `Account Balance` label + `$24,813` | odometer spring `spring(1,80,10,0)` |
| C2 | Equity sparkline (L→R draw) | `easeInOutQuad` over 800ms |
| C3 | `+2.14%` + `Today's P&L` | `easeOutBack(1.8)` snap |
| D | Divider sweep + `Open: XAUUSD · EURUSD · AUDCAD` | `easeOutQuart` |
| E | Win rate · PF · Pips | fade + slide up |
| F | Myfxbook verify + handle | fade |

Data injected: `balance`, `todayDaily`, `winRate`, `profitFactor`, `pips`, open pairs.

### Weekly (`hero_weekly.html`) — 4 seconds, 120 frames

| Zone | Content | Animation |
|------|---------|-----------|
| A | `Weekly Performance` pill | fade in |
| B | Handle + week-end date | fade + slide |
| C1 | `This Week` label | fade |
| C2 | `+2.34%` at 3.4em bold | `easeOutBack(2.5)` — overshoots, snaps |
| C3 | `Total return: +12.4%` | `easeOutQuart` count-up |
| D | Divider + `847 trades · All verified` | sweep |
| E | Win rate · PF · Pips | fade + slide |
| F | Track record + handle | fade |

Data injected: `weekly_gain`, `gain` (total), `winRate`, `trades`, `profitFactor`, `pips`.

### Trust (`hero_trust.html`) — 5 seconds, 150 frames

| Zone | Content | Animation |
|------|---------|-----------|
| A | `Verified Track Record` pill | fade |
| B | Myfxbook ID + IC Markets | fade + slide |
| C (full) | SVG arc ring — 168px diameter | `easeOutCubic` arc to win rate %, count-up inside |
| D | Divider + `68% win rate · 847 verified trades` | sweep |
| E | PF · Total Return · Max DD | fade + slide |
| F | `No screenshots. Raw data only.` + handle | fade |

Data injected: `winRate`, `trades`, `profitFactor`, `gain`, `drawdown`.

### Monthly (`hero_monthly.html`) — 5 seconds, 150 frames

| Zone | Content | Animation |
|------|---------|-----------|
| A | `Monthly P&L · {month}` pill | fade |
| B | Handle + `+2.3% this month` | fade + slide |
| C+D | 6-month bar chart, staggered L→R | `easeOutQuart`, 130ms stagger per bar |
| E | Total return · WR · PF | fade + slide |
| F | Myfxbook verify + handle | fade |

Data injected: last 6 entries from `daily_gain` → monthly buckets, current month name.

---

## New Files

```
instagram/reels/hero_browser.py          ← Playwright frame-capture bridge
instagram/reels/templates/
  hero_daily.html
  hero_weekly.html
  hero_trust.html
  hero_monthly.html
  vendor/anime.min.js                    ← bundled locally (not CDN) for CI reliability
docs/superpowers/specs/
  2026-07-26-animejs-cinematic-reels-design.md   ← this file
```

## Modified Files

```
instagram/reels/scenes.py        ← hero call wrapped in USE_BROWSER_HERO if/else
instagram/requirements.txt       ← add: playwright>=1.44
.github/workflows/ai-reel.yml    ← add: playwright install chromium + install-deps
```

Everything else — `animator.py`, `effects.py`, `render.py`, `audio.py`, `run_reel.py`, `captions.py`, `post.py`, `generate.py`, `insta-post.yml`, `insta-reel.yml` — is **untouched**.

---

## scenes.py Change Pattern

For each of the 4 reel types, the hero creation block changes from:

```python
# Before
def hero_frame(t):
    ...
hero = _clip(hero_frame, duration)
```

to:

```python
# After
USE_BROWSER_HERO = os.getenv('BROWSER_HERO', '1') == '1'

if USE_BROWSER_HERO:
    from reels.hero_browser import build_hero_html, capture_frames, frames_to_clip
    html = build_hero_html('daily', data, duration)
    frames = capture_frames(html, duration)
    hero = frames_to_clip(frames)
else:
    def hero_frame(t):
        ...
    hero = _clip(hero_frame, duration)
```

The `else` branch preserves the original Python hero exactly — set `BROWSER_HERO=0` in the workflow env to revert instantly without any code change.

---

## GitHub Actions — ai-reel.yml Changes

Add one step after `pip install -r requirements.txt`:

```yaml
- name: Install Playwright Chromium
  run: |
    playwright install chromium
    playwright install-deps chromium
```

Chromium is cached by the Actions runner after the first install (~90s cold, ~10s cached).

### CI Timing Impact

| Stage | Before | After |
|-------|--------|-------|
| Chromium install | — | +90s cold / +10s cached |
| Hero capture (daily/weekly) | — | +18s |
| Hero capture (trust/monthly) | — | +22s |
| Existing Python scenes | ~45s | ~45s unchanged |
| **Total per reel** | **~45s** | **~2–3 min** |

---

## Python Data Scene Upgrades (Direction C, no Playwright)

### equity_curve_clip — `effects.py`
- Line weight: 3px → 6px
- Fill opacity: 0.11 → 0.22
- Glowing dot pulses at curve tip (matches `draw_pulsing_dot`)
- Top + bottom 4px emerald bars (same as hero letterbox, via `PIL.ImageDraw.rectangle`)

### cascade_text_frame — `animator.py`
- Emerald 3px left-edge accent bar drawn per line before text
- First line treated as headline: 48pt bold, no accent bar
- Stagger tightened: 0.3s → 0.22s per line
- Easing: `ease_out` cubic → `ease_out_back` (port of `easeOutBack(1.5)`)

### cta_fade_frame — `animator.py`
- Letterbox bars sweep in (same pattern as hero — PIL `scaleX` approximated via rectangle width)
- Line 1: 48pt bold, emerald
- Animated underline: emerald rect grows L→R under line 1 over 0.4s

### make_broker_card_clip — `scenes.py`
- Adopts 6-zone layout: brand pill at top, IC Markets giant centred, emerald pill for IB URL, verify + handle at bottom
- Letterbox bars sweep in

---

## Rollback

1. **Instant** (no deploy): Set `BROWSER_HERO: '0'` in `ai-reel.yml` env → all hero types revert to original Python path.
2. **Full revert**: Switch back to `master` branch — worktree branch is isolated, master is never modified.
3. **Per-reel-type**: The `if USE_BROWSER_HERO` guard can be applied per reel type independently.

---

## Out of Scope

- motion.dev — anime.js covers all use cases; motion.dev adds no value for headless frame capture
- Playwright for data/equity/CTA scenes — Python is faster and sufficient for these
- Changes to caption functions, `run.py`, `run_reel.py`, posting logic, or static image pipeline
- Changes to `insta-post.yml` or `insta-reel.yml` (only `ai-reel.yml` is modified)
