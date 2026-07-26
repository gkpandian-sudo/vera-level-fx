# anime.js Cinematic Hero Reels — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade automated Instagram reels with cinematic anime.js hero cards rendered via Playwright + 4 self-contained HTML templates, plus Direction C Python aesthetic upgrades to equity, cascade text, and CTA scenes.

**Architecture:** `hero_browser.py` builds self-contained HTML (anime.js v3.2.2 + Roboto WOFF2 base64-embedded) and captures frames via `sync_playwright` with `channel='chrome'` (pre-installed on ubuntu-latest) — one PNG per frame → `ImageSequenceClip`. Gated behind `BROWSER_HERO=os.getenv('BROWSER_HERO','0')=='1'` with try/except auto-fallback to Python hero. Python scenes upgraded in-place for equity curve, cascade text, and CTA.

**Tech Stack:** anime.js v3.2.2 (inlined), Playwright 1.44+ sync API, `channel='chrome'` (zero download), MoviePy 1.0.3 (v2.x with v1 compat shim), PIL/Pillow, NumPy, Roboto WOFF2 fonts (base64-embedded into HTML).

**Workflow target:** `insta-reel.yml` only — NOT `ai-reel.yml` (which runs Path E matplotlib pipeline and never imports `reels/scenes.py`).

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `instagram/reels/templates/vendor/anime.min.js` | **Create** | anime.js v3.2.2 IIFE pinned |
| `instagram/reels/templates/vendor/Roboto-Black.woff2` | **Create** | Weight 900 font |
| `instagram/reels/templates/vendor/Roboto-Bold.woff2` | **Create** | Weight 700 font |
| `instagram/reels/templates/vendor/Roboto-Regular.woff2` | **Create** | Weight 400 font |
| `instagram/reels/hero_browser.py` | **Create** | `build_hero_html`, `capture_frames`, `frames_to_clip` |
| `instagram/reels/templates/hero_daily.html` | **Create** | Daily hero — 4s, 120 frames |
| `instagram/reels/templates/hero_weekly.html` | **Create** | Weekly hero — 4s, 120 frames |
| `instagram/reels/templates/hero_trust.html` | **Create** | Trust hero — 5s, 150 frames |
| `instagram/reels/templates/hero_monthly.html` | **Create** | Monthly hero — 5s, 150 frames |
| `instagram/reels/scenes.py` | **Modify** | `USE_BROWSER_HERO` guard in 4 functions; remove monthly `data_clip` |
| `instagram/reels/effects.py` | **Modify** | `equity_curve_clip` Direction C upgrades |
| `instagram/reels/animator.py` | **Modify** | `ease_out_back` + `cascade_text_frame` + `cta_fade_frame` Direction C |
| `instagram/requirements.txt` | **Modify** | Add `playwright>=1.44` |
| `.github/workflows/insta-reel.yml` | **Modify** | Add pip install playwright + `BROWSER_HERO: '1'` env |
| `instagram/tests/test_hero_browser.py` | **Create** | Smoke tests for hero_browser.py |

---

## Task 1: Vendor assets — anime.js + Roboto WOFF2

**Files:**
- Create: `instagram/reels/templates/vendor/anime.min.js`
- Create: `instagram/reels/templates/vendor/Roboto-Black.woff2`
- Create: `instagram/reels/templates/vendor/Roboto-Bold.woff2`
- Create: `instagram/reels/templates/vendor/Roboto-Regular.woff2`

- [ ] **Step 1: Create vendor directory**

```bash
mkdir -p instagram/reels/templates/vendor
```

- [ ] **Step 2: Download anime.min.js v3.2.2 from npm registry (pinned, not CDN)**

```bash
curl -L "https://unpkg.com/animejs@3.2.2/lib/anime.min.js" \
  -o instagram/reels/templates/vendor/anime.min.js
# Verify: file must be ~17KB, must contain "var anime="
wc -c instagram/reels/templates/vendor/anime.min.js
grep -c "var anime=" instagram/reels/templates/vendor/anime.min.js
```

Expected: size ~17000 bytes, grep returns `1`.

- [ ] **Step 3: Download Roboto WOFF2 fonts**

```bash
# Weight 900 (Black)
curl -L "https://fonts.gstatic.com/s/roboto/v47/KFOMCnqEu92Fr1ME7kSn66aGLdTylUAMQXC89YmC2DfNTo7OIcpBFCXIoA.woff2" \
  -o instagram/reels/templates/vendor/Roboto-Black.woff2
# Weight 700 (Bold)
curl -L "https://fonts.gstatic.com/s/roboto/v47/KFOMCnqEu92Fr1ME7kSn66aGLdTylUAMQXC89YmC2DfNTo7OIcpBFCXGoA.woff2" \
  -o instagram/reels/templates/vendor/Roboto-Bold.woff2
# Weight 400 (Regular)
curl -L "https://fonts.gstatic.com/s/roboto/v47/KFOMCnqEu92Fr1ME7kSn66aGLdTylUAMQXC89YmC2DfNTo7OIcpBFCXMoA.woff2" \
  -o instagram/reels/templates/vendor/Roboto-Regular.woff2
```

If Google Fonts URLs are unreachable (they change periodically), use the Ubuntu fonts already on the CI runner as WOFF2 alternatives:
```bash
# Fallback: generate WOFF2 from TTF using fonttools
pip install fonttools brotli
python3 -c "
from pathlib import Path
import subprocess
for name in ['Roboto-Black','Roboto-Bold','Roboto-Regular']:
    ttf = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    out = Path(f'instagram/reels/templates/vendor/{name}.woff2')
    subprocess.run(['python3','-m','fonttools','ttLib.woff2','compress',str(ttf),'-o',str(out)])
print('Done')
"
```

- [ ] **Step 4: Verify all 4 vendor files exist and are non-empty**

```bash
ls -lh instagram/reels/templates/vendor/
```

Expected output: 4 files, each > 10KB.

- [ ] **Step 5: Commit**

```bash
git add instagram/reels/templates/vendor/
git commit -m "feat: add vendor assets — anime.js v3.2.2 + Roboto WOFF2 fonts"
```

---

## Task 2: hero_browser.py — Playwright frame-capture bridge

**Files:**
- Create: `instagram/reels/hero_browser.py`
- Create: `instagram/tests/test_hero_browser.py`

- [ ] **Step 1: Write the failing test for `_coerce_data`**

Create `instagram/tests/test_hero_browser.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

SAMPLE_DATA = {
    'account': {
        'balance': 24813, 'todayDaily': 2.14, 'daily': 2.14,
        'winRate': 68.5, 'profitFactor': 1.82,
        'pips': 3420, 'trades': 847,
        'gain': 12.4, 'drawdown': 8.3,
    },
    'openTrades': [
        {'symbol': 'XAUUSD', 'action': 'buy', 'profit': 42.50},
        {'symbol': 'EURUSD', 'action': 'sell', 'profit': -12.30},
    ],
    'dailyGain': [
        ['01/01/2026', '0.5', '200'],
        ['01/15/2026', '1.2', '480'],
        ['02/01/2026', '0.8', '320'],
        ['02/15/2026', '2.1', '840'],
        ['03/01/2026', '-0.4', '-160'],
        ['03/15/2026', '3.0', '1200'],
    ],
    'weekly_gain': 2.34,
}


def test_coerce_data_types():
    from reels.hero_browser import _coerce_data
    d = _coerce_data('daily', SAMPLE_DATA)
    assert isinstance(d['balance'], float)
    assert isinstance(d['balance_fmt'], str)
    assert d['balance_fmt'].startswith('$')
    assert isinstance(d['win_rate'], float)
    assert isinstance(d['pips'], int)
    assert isinstance(d['open_pairs'], list)
    assert isinstance(d['sparkline_points'], list)
    assert len(d['sparkline_points']) == 6
    for pt in d['sparkline_points']:
        assert 0.0 <= pt[0] <= 1.0
        assert 0.0 <= pt[1] <= 1.0


def test_coerce_data_weekly_gain_fallback():
    from reels.hero_browser import _coerce_data
    data_no_wg = {**SAMPLE_DATA}
    data_no_wg.pop('weekly_gain', None)
    d = _coerce_data('weekly', data_no_wg)
    assert d['weekly_gain'] == d['gain']  # falls back to total gain


def test_coerce_data_monthly_items():
    from reels.hero_browser import _coerce_data
    d = _coerce_data('monthly', SAMPLE_DATA)
    assert isinstance(d['monthly_items'], list)
    assert len(d['monthly_items']) <= 6
    for item in d['monthly_items']:
        assert len(item) == 2
        assert isinstance(item[1], float)


def test_coerce_data_trust_fallback():
    from reels.hero_browser import _coerce_data
    d = _coerce_data('trust', {
        'account': {'winRate': 0, 'profitFactor': 0, 'gain': 0, 'trades': 0, 'pips': 0},
        'dailyGain': [],
    })
    assert d['win_rate'] == 0.0
    assert d['sparkline_points'] == [[0.0, 0.5], [1.0, 0.5]]  # flat line fallback


def test_build_hero_html_creates_file(tmp_path, monkeypatch):
    """build_hero_html writes a temp HTML file with all markers replaced."""
    import os
    from reels.hero_browser import build_hero_html

    vendor = Path(__file__).parent.parent / 'reels' / 'templates' / 'vendor'
    if not vendor.exists() or not (vendor / 'anime.min.js').exists():
        import pytest
        pytest.skip('vendor assets not present')

    template_dir = Path(__file__).parent.parent / 'reels' / 'templates'
    if not (template_dir / 'hero_daily.html').exists():
        import pytest
        pytest.skip('hero_daily.html template not present')

    html_path = build_hero_html('daily', SAMPLE_DATA, 4.0)
    assert html_path.exists()
    content = html_path.read_text(encoding='utf-8')
    assert '__ANIME_JS__' not in content
    assert '__FONTS_CSS__' not in content
    assert '__DATA_JSON__' not in content
    assert '__DURATION_MS__' not in content
    assert 'const DATA =' in content
    assert 'seekFrame' in content
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd instagram && python -m pytest tests/test_hero_browser.py::test_coerce_data_types -v
```

Expected: `FAILED` with `ModuleNotFoundError: No module named 'reels.hero_browser'`.

- [ ] **Step 3: Create `instagram/reels/hero_browser.py`**

```python
"""
hero_browser.py — Playwright frame-capture bridge for anime.js hero cards.

Three public functions:
  build_hero_html  → Path  (self-contained HTML from template + vendor assets)
  capture_frames   → list[Path]  (PNG frames via headless Chrome seekFrame loop)
  frames_to_clip   → VideoClip  (MoviePy ImageSequenceClip drop-in)
"""
from __future__ import annotations

import base64
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path

_VENDOR_DIR = Path(__file__).parent / 'templates' / 'vendor'
_TEMPLATE_DIR = Path(__file__).parent / 'templates'


# ── Data coercion ─────────────────────────────────────────────────────────────

def _coerce_data(post_type: str, data: dict) -> dict:
    """Coerce all snapshot fields to safe types for JSON injection."""
    acct = data.get('account', {})
    daily_gain = data.get('dailyGain', [])

    # Sparkline points: normalised (x_frac, y_frac) in [0,1]
    values = []
    for row in daily_gain:
        try:
            values.append(float(row[1] if isinstance(row, list) else row.get('value', 0)))
        except (IndexError, TypeError, ValueError):
            continue
    if len(values) < 2:
        values = [0.0, 0.0]
    v_min, v_max = min(values), max(values)
    v_range = max(v_max - v_min, 0.01)
    sparkline_points = [
        [i / (len(values) - 1), 1.0 - (v - v_min) / v_range]
        for i, v in enumerate(values)
    ]

    # Monthly P&L (last 6 months)
    try:
        from captions import monthly_pnl_from_daily
        monthly_pnl = monthly_pnl_from_daily(daily_gain)
    except ImportError:
        monthly_pnl = {}
    monthly_items = [[m, float(v)] for m, v in list(monthly_pnl.items())[-6:]]

    balance = float(acct.get('balance') or 0)
    today_daily = float(acct.get('todayDaily') or acct.get('daily') or 0)
    win_rate = float(acct.get('winRate') or 0)
    profit_factor = float(acct.get('profitFactor') or 0)
    pips = int(acct.get('pips') or 0)
    trades = int(acct.get('trades') or 0)
    gain = float(acct.get('gain') or 0)
    drawdown = float(acct.get('drawdown') or 0)
    weekly_gain = float(data.get('weekly_gain') or gain)
    open_pairs = [str(t.get('symbol', '')) for t in data.get('openTrades', [])[:5]]
    this_month = monthly_items[-1][1] if monthly_items else 0.0

    return {
        'balance': balance,
        'balance_fmt': f'${balance:,.0f}',
        'today_daily': today_daily,
        'today_daily_sign': '+' if today_daily >= 0 else '',
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'pips': pips,
        'trades': trades,
        'gain': gain,
        'gain_sign': '+' if gain >= 0 else '',
        'drawdown': drawdown,
        'weekly_gain': weekly_gain,
        'weekly_gain_sign': '+' if weekly_gain >= 0 else '',
        'open_pairs': open_pairs,
        'open_pairs_str': ' · '.join(open_pairs) if open_pairs else 'No open positions',
        'sparkline_points': sparkline_points,
        'monthly_items': monthly_items,
        'month_name': datetime.now().strftime('%B %Y'),
        'this_month': this_month,
        'this_month_sign': '+' if this_month >= 0 else '',
    }


# ── Font embedding ─────────────────────────────────────────────────────────────

def _build_fonts_css() -> str:
    """@font-face CSS with base64-encoded WOFF2 for each Roboto weight."""
    css_blocks = []
    for weight, filename in [
        ('900', 'Roboto-Black.woff2'),
        ('700', 'Roboto-Bold.woff2'),
        ('400', 'Roboto-Regular.woff2'),
    ]:
        woff_path = _VENDOR_DIR / filename
        b64 = base64.b64encode(woff_path.read_bytes()).decode('ascii')
        css_blocks.append(
            f"@font-face {{\n"
            f"  font-family: 'Roboto';\n"
            f"  font-weight: {weight};\n"
            f"  src: url('data:font/woff2;base64,{b64}') format('woff2');\n"
            f"}}"
        )
    return '\n'.join(css_blocks)


# ── HTML builder ───────────────────────────────────────────────────────────────

def build_hero_html(post_type: str, data: dict, duration: float) -> Path:
    """Build self-contained HTML for the hero card.

    Loads template, coerces data, inlines anime.min.js + WOFF2 fonts as
    base64, writes to a temp file. Returns absolute Path to the temp file.
    """
    template_path = _TEMPLATE_DIR / f'hero_{post_type}.html'
    template = template_path.read_text(encoding='utf-8')

    coerced = _coerce_data(post_type, data)
    anime_js = (_VENDOR_DIR / 'anime.min.js').read_text(encoding='utf-8')
    fonts_css = _build_fonts_css()

    html = template
    html = html.replace('__ANIME_JS__', anime_js)
    html = html.replace('__FONTS_CSS__', fonts_css)
    html = html.replace('__DATA_JSON__', json.dumps(coerced))
    html = html.replace('__DURATION_MS__', str(int(duration * 1000)))

    tmp_dir = Path(tempfile.mkdtemp())
    out_path = tmp_dir / f'hero_{post_type}_{int(time.time())}.html'
    out_path.write_text(html, encoding='utf-8')
    return out_path


# ── Frame capture ──────────────────────────────────────────────────────────────

def capture_frames(html_path: Path, duration: float,
                   fps: int = 30, timeout_s: int = 120) -> list[Path]:
    """Capture animation frames from the HTML template via Playwright.

    Uses channel='chrome' (pre-installed on ubuntu-latest — zero download).
    Returns list[Path] to PNG files on disk (avoids 930MB in-memory arrays).
    Raises RuntimeError if capture exceeds timeout_s.
    """
    from playwright.sync_api import sync_playwright
    import time as _time

    n_frames = int(duration * fps)
    tmp_dir = html_path.parent
    frame_paths: list[Path] = []
    start = _time.time()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome')
        try:
            page = browser.new_page(
                viewport={'width': 1080, 'height': 1920},
                device_scale_factor=1,
            )
            page.goto(f'file://{html_path.as_posix()}')
            page.evaluate('document.fonts.ready')  # await WOFF2 load

            for frame_idx in range(n_frames):
                if _time.time() - start > timeout_s:
                    raise RuntimeError(
                        f'[hero_browser] capture_frames timed out after '
                        f'{timeout_s}s at frame {frame_idx}/{n_frames}'
                    )
                ms = int(frame_idx * 1000 / fps)
                page.evaluate(f'seekFrame({ms})')
                frame_path = tmp_dir / f'frame_{frame_idx:04d}.png'
                page.screenshot(path=str(frame_path))
                frame_paths.append(frame_path)
        finally:
            browser.close()

    return frame_paths


# ── Clip builder ───────────────────────────────────────────────────────────────

def frames_to_clip(frame_paths: list[Path], fps: int = 30):
    """Convert frame PNG paths to a MoviePy VideoClip.

    Returns an ImageSequenceClip with .set_fps(fps) — required for
    _with_stinger compatibility in scenes.py.
    """
    from moviepy.editor import ImageSequenceClip
    str_paths = [str(p) for p in frame_paths]
    return ImageSequenceClip(str_paths, fps=fps).set_fps(fps)
```

- [ ] **Step 4: Run all tests in test_hero_browser.py**

```bash
cd instagram && python -m pytest tests/test_hero_browser.py -v
```

Expected: `test_coerce_data_types PASSED`, `test_coerce_data_weekly_gain_fallback PASSED`, `test_coerce_data_monthly_items PASSED`, `test_coerce_data_trust_fallback PASSED`. The `test_build_hero_html_creates_file` test will SKIP (template not yet written — that's correct for now).

- [ ] **Step 5: Commit**

```bash
git add instagram/reels/hero_browser.py instagram/tests/test_hero_browser.py
git commit -m "feat: add hero_browser.py — Playwright frame-capture bridge"
```

---

## Task 3: hero_daily.html — daily hero template (4s, 120 frames)

**Files:**
- Create: `instagram/reels/templates/hero_daily.html`

- [ ] **Step 1: Write the template**

Create `instagram/reels/templates/hero_daily.html` with the full content below. Note the 4 substitution markers (`__ANIME_JS__`, `__FONTS_CSS__`, `__DATA_JSON__`, `__DURATION_MS__`) — these are replaced literally by `build_hero_html`.

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="color-scheme" content="dark">
<style>
__FONTS_CSS__

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  width: 1080px; height: 1920px; overflow: hidden;
  background: radial-gradient(ellipse at 50% 35%, #001835 0%, #010912 100%);
  font-family: 'Roboto', 'DejaVu Sans', sans-serif;
  color: #fff;
}
/* Film grain via SVG turbulence (static — deterministic across frames) */
body::after {
  content: '';
  position: fixed; inset: 0; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  opacity: 0.5;
}
/* Letterbox bars — animated by anime.js */
.lb { position: fixed; left: 0; right: 0; height: 4px; background: #059669; transform: scaleX(0); }
#lb-t { top: 0; transform-origin: left center; }
#lb-b { bottom: 0; transform-origin: right center; }
/* Zones */
#za { position: absolute; top: 0;     left: 0; right: 0; height: 249px;  display: flex; align-items: center; justify-content: center; }
#zb { position: absolute; top: 249px; left: 0; right: 0; height: 289px;  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px; }
#zc { position: absolute; top: 538px; left: 0; right: 0; height: 806px; }
#zd { position: absolute; top: 1344px;left: 0; right: 0; height: 192px;  padding: 0 60px; display: flex; flex-direction: column; justify-content: center; gap: 14px; }
#ze { position: absolute; top: 1536px;left: 0; right: 0; height: 211px;  display: flex; align-items: center; justify-content: space-around; padding: 0 60px; }
#zf { position: absolute; top: 1747px;left: 0; right: 0; height: 173px;  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }
/* Zone C subdivisions */
#zc1 { position: absolute; top: 0;    left: 0; right: 0; height: 248px; display: flex; flex-direction: column; align-items: center; justify-content: center; }
#zc2 { position: absolute; top: 262px;left: 60px; right: 60px; height: 275px; }
#zc3 { position: absolute; top: 545px;left: 0; right: 0; height: 261px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; }
.stat { text-align: center; }
.stat-val { font-size: 44px; font-weight: 700; }
.stat-lbl { font-size: 22px; color: #6B7280; margin-top: 6px; letter-spacing: 0.05em; }
.sep { width: 1px; height: 60px; background: rgba(255,255,255,0.1); }
</style>
</head>
<body>
<div class="lb" id="lb-t"></div>
<div class="lb" id="lb-b"></div>

<!-- Zone A: Brand pill -->
<div id="za">
  <div id="brand-pill" style="opacity:0;background:rgba(5,150,105,0.12);border:1px solid rgba(5,150,105,0.35);border-radius:24px;padding:14px 36px;font-size:26px;font-weight:700;letter-spacing:0.08em;color:#059669;">
    VERA LEVEL FX &middot; LIVE ACCOUNT
  </div>
</div>

<!-- Zone B: Context -->
<div id="zb">
  <div id="broker-line" style="opacity:0;transform:translateY(16px);font-size:30px;color:#6B7280;letter-spacing:0.04em;">IC MARKETS &middot; ASIC REGULATED</div>
  <div id="live-badge" style="opacity:0;transform:translateY(16px);font-size:36px;font-weight:700;color:#EF4444;letter-spacing:0.04em;">&#9679; LIVE POSITION UPDATE</div>
</div>

<!-- Zone C -->
<div id="zc">
  <!-- C1: Balance -->
  <div id="zc1">
    <div id="bal-lbl" style="opacity:0;font-size:26px;color:#6B7280;letter-spacing:0.08em;margin-bottom:14px;">ACCOUNT BALANCE</div>
    <div id="bal-val" style="font-size:110px;font-weight:900;letter-spacing:-0.02em;line-height:1;">$0</div>
  </div>
  <!-- C2: Sparkline canvas -->
  <div id="zc2">
    <canvas id="sparkline" width="960" height="275" style="opacity:0;display:block;"></canvas>
  </div>
  <!-- C3: Daily P&L -->
  <div id="zc3">
    <div id="pnl-val" style="opacity:0;transform:scale(0.8);font-size:80px;font-weight:900;letter-spacing:-0.02em;"></div>
    <div id="pnl-lbl" style="opacity:0;font-size:28px;color:#6B7280;letter-spacing:0.06em;">TODAY&rsquo;S P&amp;L</div>
  </div>
</div>

<!-- Zone D: Divider + open pairs -->
<div id="zd">
  <div id="divider" style="height:1px;width:0;background:#059669;"></div>
  <div id="pairs-line" style="opacity:0;font-size:28px;color:#6B7280;"></div>
</div>

<!-- Zone E: 3-stat row -->
<div id="ze">
  <div class="stat" id="stat-wr" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="wr-val" style="color:#059669;"></div>
    <div class="stat-lbl">WIN RATE</div>
  </div>
  <div class="sep"></div>
  <div class="stat" id="stat-pf" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="pf-val"></div>
    <div class="stat-lbl">PROFIT FACTOR</div>
  </div>
  <div class="sep"></div>
  <div class="stat" id="stat-pip" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="pip-val"></div>
    <div class="stat-lbl">TOTAL PIPS</div>
  </div>
</div>

<!-- Zone F: Verify + handle -->
<div id="zf">
  <div id="verify-line" style="opacity:0;font-size:24px;color:#6B7280;">Myfxbook #12044019 &middot; All trades verified</div>
  <div id="handle" style="opacity:0;font-size:24px;color:#6B7280;">@veralevel.fx</div>
</div>

<script>__ANIME_JS__</script>
<script>
const DATA = __DATA_JSON__;
const DURATION_MS = __DURATION_MS__;

/* ── Sparkline drawing ─────────────────────────────────────────────── */
function drawSparkline(progress) {
  const canvas = document.getElementById('sparkline');
  const ctx = canvas.getContext('2d');
  const pts = DATA.sparkline_points;  // [[x_frac, y_frac], ...]
  const W = canvas.width, H = canvas.height;
  const isPos = DATA.today_daily >= 0;
  const lineCol = isPos ? '#059669' : '#EF4444';
  const n = Math.max(2, Math.round(progress * pts.length));
  const vis = pts.slice(0, n).map(p => [p[0] * W, p[1] * H]);

  ctx.clearRect(0, 0, W, H);

  // Fill area
  ctx.beginPath();
  ctx.moveTo(vis[0][0], vis[0][1]);
  for (let i = 1; i < vis.length; i++) ctx.lineTo(vis[i][0], vis[i][1]);
  ctx.lineTo(vis[vis.length-1][0], H);
  ctx.lineTo(vis[0][0], H);
  ctx.closePath();
  const r = isPos ? 5 : 239, g = isPos ? 150 : 68, b = isPos ? 105 : 68;
  ctx.fillStyle = `rgba(${r},${g},${b},0.22)`;
  ctx.fill();

  // Line
  ctx.beginPath();
  ctx.moveTo(vis[0][0], vis[0][1]);
  for (let i = 1; i < vis.length; i++) ctx.lineTo(vis[i][0], vis[i][1]);
  ctx.strokeStyle = lineCol;
  ctx.lineWidth = 6;
  ctx.lineJoin = 'round';
  ctx.stroke();

  // Glowing tip dot
  const last = vis[vis.length - 1];
  ctx.shadowColor = lineCol;
  ctx.shadowBlur = 16;
  ctx.beginPath();
  ctx.arc(last[0], last[1], 8, 0, Math.PI * 2);
  ctx.fillStyle = lineCol;
  ctx.fill();
  ctx.shadowBlur = 0;
}

/* ── DOM population ──────────────────────────────────────────────────── */
(function populateDOM() {
  const isPos = DATA.today_daily >= 0;
  const pnlColor = isPos ? '#059669' : '#EF4444';
  document.getElementById('pnl-val').textContent = DATA.today_daily_sign + DATA.today_daily.toFixed(2) + '%';
  document.getElementById('pnl-val').style.color = pnlColor;
  document.getElementById('wr-val').textContent = DATA.win_rate > 0 ? DATA.win_rate.toFixed(0) + '%' : '—';
  document.getElementById('pf-val').textContent = DATA.profit_factor.toFixed(2);
  document.getElementById('pip-val').textContent = '+' + DATA.pips.toLocaleString();
  document.getElementById('pairs-line').textContent = 'Open: ' + DATA.open_pairs_str;
})();

/* ── Timeline ────────────────────────────────────────────────────────── */
let tl = null;

function buildTimeline(data) {
  tl = anime.timeline({ autoplay: false });

  // Letterbox bars sweep in simultaneously (0–400ms)
  tl.add({ targets: '#lb-t', scaleX: [0, 1], duration: 400, easing: 'easeOutQuart' }, 0);
  tl.add({ targets: '#lb-b', scaleX: [0, 1], duration: 400, easing: 'easeOutQuart' }, 0);

  // Zone A: brand pill (200–600ms)
  tl.add({ targets: '#brand-pill', opacity: [0, 1], duration: 400, easing: 'easeOutCubic' }, 200);

  // Zone B: broker + live badge (300–750ms)
  tl.add({ targets: '#broker-line', opacity: [0, 1], translateY: [16, 0], duration: 400, easing: 'easeOutCubic' }, 300);
  tl.add({ targets: '#live-badge',  opacity: [0, 1], translateY: [16, 0], duration: 350, easing: 'easeOutCubic' }, 500);

  // Zone C1: balance label (400ms) then odometer (500–1700ms)
  tl.add({ targets: '#bal-lbl', opacity: [0, 1], duration: 300, easing: 'easeOutCubic' }, 400);
  tl.add({
    targets: { value: 0 },
    value: data.balance,
    duration: 1200,
    easing: 'spring(1, 80, 10, 0)',
    update: function(anim) {
      document.getElementById('bal-val').textContent =
        '$' + Math.round(anim.animations[0].currentValue).toLocaleString();
    }
  }, 500);

  // Zone C2: sparkline draws L→R (800–1600ms)
  tl.add({
    targets: { progress: 0 },
    progress: 1,
    duration: 800,
    easing: 'easeInOutQuad',
    begin: function() { document.getElementById('sparkline').style.opacity = '1'; },
    update: function(anim) { drawSparkline(anim.animations[0].currentValue); }
  }, 800);

  // Zone C3: P&L snaps in with overshoot (1600–2050ms)
  tl.add({ targets: '#pnl-val', opacity: [0, 1], scale: [0.8, 1], duration: 450, easing: 'easeOutBack(1.8)' }, 1600);
  tl.add({ targets: '#pnl-lbl', opacity: [0, 1], duration: 300, easing: 'easeOutCubic' }, 1850);

  // Zone D: divider sweep (2000ms) + pairs text (2250ms)
  tl.add({ targets: '#divider', width: [0, 960], duration: 400, easing: 'easeOutQuart' }, 2000);
  tl.add({ targets: '#pairs-line', opacity: [0, 1], duration: 300, easing: 'easeOutCubic' }, 2250);

  // Zone E: 3 stats stagger in (2500–3000ms)
  tl.add({ targets: ['#stat-wr', '#stat-pf', '#stat-pip'],
           opacity: [0, 1], translateY: [16, 0],
           delay: anime.stagger(150), duration: 400, easing: 'easeOutCubic' }, 2500);

  // Zone F: verify + handle (3000–3600ms)
  tl.add({ targets: ['#verify-line', '#handle'],
           opacity: [0, 1], delay: anime.stagger(150), duration: 350, easing: 'easeOutCubic' }, 3000);
}

/* ── seekFrame (called by Playwright for each frame) ─────────────────── */
window.seekFrame = function(ms) {
  return new Promise(function(resolve) {
    if (tl) tl.seek(ms);
    requestAnimationFrame(function() { requestAnimationFrame(resolve); });
  });
};

window.addEventListener('DOMContentLoaded', function() { buildTimeline(DATA); });
</script>
</body>
</html>
```

- [ ] **Step 2: Run test to verify build_hero_html works**

```bash
cd instagram && python -m pytest tests/test_hero_browser.py::test_build_hero_html_creates_file -v
```

Expected: `PASSED` (or `SKIPPED` if vendor assets not downloaded yet — go back to Task 1 if so).

- [ ] **Step 3: Commit**

```bash
git add instagram/reels/templates/hero_daily.html
git commit -m "feat: add hero_daily.html — 6-zone anime.js template (4s)"
```

---

## Task 4: hero_weekly.html — weekly hero template (4s, 120 frames)

**Files:**
- Create: `instagram/reels/templates/hero_weekly.html`

- [ ] **Step 1: Write the template**

The weekly template shares the same boilerplate as daily. Key differences:
- Zone C has no sparkline canvas
- Zone C2 shows giant weekly % with `easeOutBack(2.5)` overshoot
- Zone C3 shows total return count-up

Create `instagram/reels/templates/hero_weekly.html`:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="color-scheme" content="dark">
<style>
__FONTS_CSS__

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  width: 1080px; height: 1920px; overflow: hidden;
  background: radial-gradient(ellipse at 50% 35%, #001835 0%, #010912 100%);
  font-family: 'Roboto', 'DejaVu Sans', sans-serif; color: #fff;
}
body::after {
  content: ''; position: fixed; inset: 0; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  opacity: 0.5;
}
.lb { position: fixed; left: 0; right: 0; height: 4px; background: #059669; transform: scaleX(0); }
#lb-t { top: 0; transform-origin: left center; }
#lb-b { bottom: 0; transform-origin: right center; }
#za { position: absolute; top: 0;     left: 0; right: 0; height: 249px;  display: flex; align-items: center; justify-content: center; }
#zb { position: absolute; top: 249px; left: 0; right: 0; height: 289px;  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px; }
#zc { position: absolute; top: 538px; left: 0; right: 0; height: 806px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0; }
#zd { position: absolute; top: 1344px;left: 0; right: 0; height: 192px;  padding: 0 60px; display: flex; flex-direction: column; justify-content: center; gap: 14px; }
#ze { position: absolute; top: 1536px;left: 0; right: 0; height: 211px;  display: flex; align-items: center; justify-content: space-around; padding: 0 60px; }
#zf { position: absolute; top: 1747px;left: 0; right: 0; height: 173px;  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }
.stat { text-align: center; }
.stat-val { font-size: 44px; font-weight: 700; }
.stat-lbl { font-size: 22px; color: #6B7280; margin-top: 6px; letter-spacing: 0.05em; }
.sep { width: 1px; height: 60px; background: rgba(255,255,255,0.1); }
</style>
</head>
<body>
<div class="lb" id="lb-t"></div>
<div class="lb" id="lb-b"></div>

<div id="za">
  <div id="brand-pill" style="opacity:0;background:rgba(5,150,105,0.12);border:1px solid rgba(5,150,105,0.35);border-radius:24px;padding:14px 36px;font-size:26px;font-weight:700;letter-spacing:0.08em;color:#059669;">
    WEEKLY PERFORMANCE
  </div>
</div>

<div id="zb">
  <div id="handle-line" style="opacity:0;transform:translateY(16px);font-size:34px;font-weight:700;color:#fff;">@veralevel.fx</div>
  <div id="date-line" style="opacity:0;transform:translateY(16px);font-size:28px;color:#6B7280;" id="date-line"></div>
</div>

<div id="zc">
  <div id="week-lbl" style="opacity:0;font-size:28px;color:#6B7280;letter-spacing:0.1em;margin-bottom:24px;">THIS WEEK</div>
  <div id="week-val" style="opacity:0;transform:scale(0.85);font-size:200px;font-weight:900;letter-spacing:-0.04em;line-height:0.9;"></div>
  <div id="total-line" style="opacity:0;font-size:36px;color:#6B7280;margin-top:40px;">Total return: <span id="total-val" style="color:#fff;font-weight:700;"></span></div>
</div>

<div id="zd">
  <div id="divider" style="height:1px;width:0;background:#059669;"></div>
  <div id="trades-line" style="opacity:0;font-size:28px;color:#6B7280;"></div>
</div>

<div id="ze">
  <div class="stat" id="stat-wr" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="wr-val" style="color:#059669;"></div>
    <div class="stat-lbl">WIN RATE</div>
  </div>
  <div class="sep"></div>
  <div class="stat" id="stat-pf" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="pf-val"></div>
    <div class="stat-lbl">PROFIT FACTOR</div>
  </div>
  <div class="sep"></div>
  <div class="stat" id="stat-pip" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="pip-val"></div>
    <div class="stat-lbl">TOTAL PIPS</div>
  </div>
</div>

<div id="zf">
  <div id="verify-line" style="opacity:0;font-size:24px;color:#6B7280;">Full track record: Myfxbook #12044019</div>
  <div id="handle-f" style="opacity:0;font-size:24px;color:#6B7280;">@veralevel.fx</div>
</div>

<script>__ANIME_JS__</script>
<script>
const DATA = __DATA_JSON__;
const DURATION_MS = __DURATION_MS__;

(function populateDOM() {
  const wg = DATA.weekly_gain;
  const wgColor = wg >= 0 ? '#059669' : '#EF4444';
  document.getElementById('week-val').textContent = DATA.weekly_gain_sign + wg.toFixed(2) + '%';
  document.getElementById('week-val').style.color = wgColor;
  document.getElementById('wr-val').textContent = DATA.win_rate > 0 ? DATA.win_rate.toFixed(0) + '%' : '—';
  document.getElementById('pf-val').textContent = DATA.profit_factor.toFixed(2);
  document.getElementById('pip-val').textContent = '+' + DATA.pips.toLocaleString();
  document.getElementById('trades-line').textContent =
    DATA.trades.toLocaleString() + ' trades · All verified on Myfxbook';
  document.getElementById('total-val').textContent =
    DATA.gain_sign + DATA.gain.toFixed(2) + '%';
})();

let tl = null;

function buildTimeline(data) {
  tl = anime.timeline({ autoplay: false });

  tl.add({ targets: '#lb-t', scaleX: [0,1], duration: 400, easing: 'easeOutQuart' }, 0);
  tl.add({ targets: '#lb-b', scaleX: [0,1], duration: 400, easing: 'easeOutQuart' }, 0);
  tl.add({ targets: '#brand-pill', opacity: [0,1], duration: 400, easing: 'easeOutCubic' }, 200);
  tl.add({ targets: '#handle-line', opacity:[0,1], translateY:[16,0], duration:400, easing:'easeOutCubic' }, 300);
  tl.add({ targets: '#date-line',   opacity:[0,1], translateY:[16,0], duration:400, easing:'easeOutCubic' }, 450);
  tl.add({ targets: '#week-lbl', opacity:[0,1], duration:300, easing:'easeOutCubic' }, 600);

  // Giant weekly % snaps in with pronounced overshoot (easeOutBack 2.5)
  tl.add({ targets: '#week-val', opacity:[0,1], scale:[0.85,1], duration:700, easing:'easeOutBack(2.5)' }, 750);

  // Total return count-up
  tl.add({
    targets: { value: 0 }, value: data.gain, duration: 800, easing: 'easeOutQuart',
    update: function(anim) {
      const v = anim.animations[0].currentValue;
      const sign = v >= 0 ? '+' : '';
      document.getElementById('total-val').textContent = sign + v.toFixed(2) + '%';
    }
  }, 1600);
  tl.add({ targets: '#total-line', opacity:[0,1], duration:400, easing:'easeOutCubic' }, 1600);

  tl.add({ targets: '#divider', width:[0,960], duration:400, easing:'easeOutQuart' }, 2200);
  tl.add({ targets: '#trades-line', opacity:[0,1], duration:300, easing:'easeOutCubic' }, 2450);
  tl.add({ targets: ['#stat-wr','#stat-pf','#stat-pip'],
           opacity:[0,1], translateY:[16,0], delay:anime.stagger(150), duration:400, easing:'easeOutCubic' }, 2700);
  tl.add({ targets: ['#verify-line','#handle-f'],
           opacity:[0,1], delay:anime.stagger(150), duration:350, easing:'easeOutCubic' }, 3200);
}

window.seekFrame = function(ms) {
  return new Promise(function(resolve) {
    if (tl) tl.seek(ms);
    requestAnimationFrame(function() { requestAnimationFrame(resolve); });
  });
};

window.addEventListener('DOMContentLoaded', function() { buildTimeline(DATA); });
</script>
</body>
</html>
```

- [ ] **Step 2: Verify template has no unresolved markers**

```bash
grep -c '__ANIME_JS__\|__FONTS_CSS__\|__DATA_JSON__\|__DURATION_MS__' \
  instagram/reels/templates/hero_weekly.html
```

Expected: `4` (one of each marker present and ready for substitution).

- [ ] **Step 3: Commit**

```bash
git add instagram/reels/templates/hero_weekly.html
git commit -m "feat: add hero_weekly.html — giant % anime.js template (4s)"
```

---

## Task 5: hero_trust.html — trust hero with SVG arc ring (5s, 150 frames)

**Files:**
- Create: `instagram/reels/templates/hero_trust.html`

- [ ] **Step 1: Write the template**

The trust hero uses an SVG `stroke-dashoffset` arc for the win-rate ring. Circumference of r=316px circle = 2π×316 ≈ 1985.2px.

Create `instagram/reels/templates/hero_trust.html`:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="color-scheme" content="dark">
<style>
__FONTS_CSS__

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  width: 1080px; height: 1920px; overflow: hidden;
  background: radial-gradient(ellipse at 50% 35%, #001835 0%, #010912 100%);
  font-family: 'Roboto', 'DejaVu Sans', sans-serif; color: #fff;
}
body::after {
  content: ''; position: fixed; inset: 0; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  opacity: 0.5;
}
.lb { position: fixed; left: 0; right: 0; height: 4px; background: #059669; transform: scaleX(0); }
#lb-t { top: 0; transform-origin: left center; }
#lb-b { bottom: 0; transform-origin: right center; }
#za { position: absolute; top: 0;     left: 0; right: 0; height: 249px; display: flex; align-items: center; justify-content: center; }
#zb { position: absolute; top: 249px; left: 0; right: 0; height: 289px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px; }
/* Zone C: full 538–1344px, ring centred */
#zc { position: absolute; top: 538px; left: 0; right: 0; height: 806px; display: flex; align-items: center; justify-content: center; }
#ring-wrap { position: relative; width: 672px; height: 672px; }
#ring-wrap svg { position: absolute; top: 0; left: 0; }
#ring-centre { position: absolute; top: 0; left: 0; width: 672px; height: 672px; display: flex; flex-direction: column; align-items: center; justify-content: center; }
#wr-count { font-size: 160px; font-weight: 900; color: #059669; line-height: 1; filter: drop-shadow(0 0 24px rgba(5,150,105,0.6)); }
#wr-sub { font-size: 26px; color: #6B7280; letter-spacing: 0.06em; margin-top: 8px; }
#zd { position: absolute; top: 1344px; left: 0; right: 0; height: 192px; padding: 0 60px; display: flex; flex-direction: column; justify-content: center; gap: 14px; }
#ze { position: absolute; top: 1536px; left: 0; right: 0; height: 211px; display: flex; align-items: center; justify-content: space-around; padding: 0 60px; }
#zf { position: absolute; top: 1747px; left: 0; right: 0; height: 173px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }
.stat { text-align: center; }
.stat-val { font-size: 44px; font-weight: 700; }
.stat-lbl { font-size: 22px; color: #6B7280; margin-top: 6px; letter-spacing: 0.05em; }
.sep { width: 1px; height: 60px; background: rgba(255,255,255,0.1); }
</style>
</head>
<body>
<div class="lb" id="lb-t"></div>
<div class="lb" id="lb-b"></div>

<div id="za">
  <div id="brand-pill" style="opacity:0;background:rgba(5,150,105,0.12);border:1px solid rgba(5,150,105,0.35);border-radius:24px;padding:14px 36px;font-size:26px;font-weight:700;letter-spacing:0.08em;color:#059669;">
    VERIFIED TRACK RECORD
  </div>
</div>

<div id="zb">
  <div id="myfx-line" style="opacity:0;transform:translateY(16px);font-size:30px;color:#6B7280;">Myfxbook #12044019</div>
  <div id="broker-line" style="opacity:0;transform:translateY(16px);font-size:28px;color:#6B7280;">Live IC Markets &middot; ASIC Regulated</div>
</div>

<div id="zc">
  <div id="ring-wrap">
    <!-- SVG arc ring: r=316, cx=cy=336, circumference=1985.2 -->
    <svg width="672" height="672" viewBox="0 0 672 672">
      <!-- Track ring -->
      <circle cx="336" cy="336" r="316" fill="none" stroke="rgba(107,114,128,0.2)" stroke-width="20"/>
      <!-- Animated arc — stroke-dashoffset starts at circumference (0% fill) -->
      <circle id="arc" cx="336" cy="336" r="316" fill="none"
              stroke="#059669" stroke-width="20"
              stroke-linecap="round"
              stroke-dasharray="1985.2"
              stroke-dashoffset="1985.2"
              transform="rotate(-90 336 336)"
              filter="url(#arc-glow)"/>
      <defs>
        <filter id="arc-glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="6" result="glow"/>
          <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>
    </svg>
    <div id="ring-centre">
      <div id="wr-count" style="opacity:0;">0%</div>
      <div id="wr-sub" style="opacity:0;">WIN RATE &middot; VERIFIED</div>
    </div>
  </div>
</div>

<div id="zd">
  <div id="divider" style="height:1px;width:0;background:#059669;"></div>
  <div id="trades-line" style="opacity:0;font-size:28px;color:#6B7280;"></div>
</div>

<div id="ze">
  <div class="stat" id="stat-pf" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="pf-val" style="color:#fff;"></div>
    <div class="stat-lbl">PROFIT FACTOR</div>
  </div>
  <div class="sep"></div>
  <div class="stat" id="stat-gain" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="gain-val" style="color:#059669;"></div>
    <div class="stat-lbl">TOTAL RETURN</div>
  </div>
  <div class="sep"></div>
  <div class="stat" id="stat-dd" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="dd-val" style="color:#EF4444;"></div>
    <div class="stat-lbl">MAX DRAWDOWN</div>
  </div>
</div>

<div id="zf">
  <div id="raw-line" style="opacity:0;font-size:24px;color:#6B7280;">No screenshots. Raw Myfxbook data only.</div>
  <div id="handle-f" style="opacity:0;font-size:24px;color:#6B7280;">@veralevel.fx</div>
</div>

<script>__ANIME_JS__</script>
<script>
const DATA = __DATA_JSON__;
const DURATION_MS = __DURATION_MS__;

(function populateDOM() {
  document.getElementById('pf-val').textContent = DATA.profit_factor.toFixed(2);
  document.getElementById('gain-val').textContent = DATA.gain_sign + DATA.gain.toFixed(1) + '%';
  document.getElementById('dd-val').textContent = '-' + DATA.drawdown.toFixed(1) + '%';
  document.getElementById('trades-line').textContent =
    DATA.win_rate > 0
      ? DATA.win_rate.toFixed(0) + '% win rate · ' + DATA.trades.toLocaleString() + ' verified trades'
      : 'Search "Vera Level" on Myfxbook to verify';
})();

let tl = null;

function buildTimeline(data) {
  const CIRC = 1985.2;
  const targetOffset = data.win_rate > 0
    ? CIRC * (1 - data.win_rate / 100)
    : CIRC;  // no-data: arc stays at 0

  tl = anime.timeline({ autoplay: false });

  tl.add({ targets: '#lb-t', scaleX:[0,1], duration:400, easing:'easeOutQuart' }, 0);
  tl.add({ targets: '#lb-b', scaleX:[0,1], duration:400, easing:'easeOutQuart' }, 0);
  tl.add({ targets: '#brand-pill', opacity:[0,1], duration:400, easing:'easeOutCubic' }, 200);
  tl.add({ targets: '#myfx-line',   opacity:[0,1], translateY:[16,0], duration:400, easing:'easeOutCubic' }, 300);
  tl.add({ targets: '#broker-line', opacity:[0,1], translateY:[16,0], duration:400, easing:'easeOutCubic' }, 450);

  // Arc sweeps from 0 to win_rate% (easeOutCubic, 3000ms)
  if (data.win_rate > 0) {
    tl.add({
      targets: '#arc',
      strokeDashoffset: [CIRC, targetOffset],
      duration: 3000, easing: 'easeOutCubic'
    }, 600);
    // Count-up inside ring, synced to arc
    tl.add({
      targets: { v: 0 }, v: data.win_rate, duration: 3000, easing: 'easeOutCubic',
      update: function(anim) {
        document.getElementById('wr-count').textContent =
          Math.round(anim.animations[0].currentValue) + '%';
      }
    }, 600);
    tl.add({ targets: '#wr-count', opacity:[0,1], duration:300, easing:'easeOutCubic' }, 600);
    tl.add({ targets: '#wr-sub',   opacity:[0,1], duration:300, easing:'easeOutCubic' }, 900);
  } else {
    // No data: show verify text instead
    tl.add({ targets: '#wr-count', opacity:[0,1], duration:400, easing:'easeOutCubic',
             begin: function() { document.getElementById('wr-count').style.fontSize='60px'; document.getElementById('wr-count').textContent='Myfxbook #12044019'; } }, 600);
    tl.add({ targets: '#wr-sub', opacity:[0,1], duration:300, easing:'easeOutCubic',
             begin: function() { document.getElementById('wr-sub').textContent='Search "Vera Level" to verify'; } }, 900);
  }

  tl.add({ targets: '#divider',    width:[0,960], duration:400, easing:'easeOutQuart' }, 3700);
  tl.add({ targets: '#trades-line', opacity:[0,1], duration:300, easing:'easeOutCubic' }, 3950);
  tl.add({ targets: ['#stat-pf','#stat-gain','#stat-dd'],
           opacity:[0,1], translateY:[16,0], delay:anime.stagger(150), duration:400, easing:'easeOutCubic' }, 4200);
  tl.add({ targets: ['#raw-line','#handle-f'],
           opacity:[0,1], delay:anime.stagger(150), duration:350, easing:'easeOutCubic' }, 4600);
}

window.seekFrame = function(ms) {
  return new Promise(function(resolve) {
    if (tl) tl.seek(ms);
    requestAnimationFrame(function() { requestAnimationFrame(resolve); });
  });
};

window.addEventListener('DOMContentLoaded', function() { buildTimeline(DATA); });
</script>
</body>
</html>
```

- [ ] **Step 2: Verify marker count**

```bash
grep -c '__ANIME_JS__\|__FONTS_CSS__\|__DATA_JSON__\|__DURATION_MS__' \
  instagram/reels/templates/hero_trust.html
```

Expected: `4`.

- [ ] **Step 3: Commit**

```bash
git add instagram/reels/templates/hero_trust.html
git commit -m "feat: add hero_trust.html — SVG arc ring anime.js template (5s)"
```

---

## Task 6: hero_monthly.html — monthly bar chart template (5s, 150 frames)

**Files:**
- Create: `instagram/reels/templates/hero_monthly.html`

- [ ] **Step 1: Write the template**

The monthly hero draws 6 horizontal bars on a canvas, staggered 130ms each. Bars grow left→right via `easeOutQuart`. Zone C+D combined (538–1536px = 998px) holds the chart canvas.

Create `instagram/reels/templates/hero_monthly.html`:

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="color-scheme" content="dark">
<style>
__FONTS_CSS__

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  width: 1080px; height: 1920px; overflow: hidden;
  background: radial-gradient(ellipse at 50% 35%, #001835 0%, #010912 100%);
  font-family: 'Roboto', 'DejaVu Sans', sans-serif; color: #fff;
}
body::after {
  content: ''; position: fixed; inset: 0; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  opacity: 0.5;
}
.lb { position: fixed; left: 0; right: 0; height: 4px; background: #059669; transform: scaleX(0); }
#lb-t { top: 0; transform-origin: left center; }
#lb-b { bottom: 0; transform-origin: right center; }
#za { position: absolute; top: 0;     left: 0; right: 0; height: 249px; display: flex; align-items: center; justify-content: center; }
#zb { position: absolute; top: 249px; left: 0; right: 0; height: 289px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 18px; }
/* C+D combined: 538–1536px = 998px chart area */
#chart-area { position: absolute; top: 538px; left: 0; right: 0; height: 998px; padding: 40px 60px; }
#chart-canvas { display: block; }
#ze { position: absolute; top: 1536px; left: 0; right: 0; height: 211px; display: flex; align-items: center; justify-content: space-around; padding: 0 60px; }
#zf { position: absolute; top: 1747px; left: 0; right: 0; height: 173px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }
.stat { text-align: center; }
.stat-val { font-size: 44px; font-weight: 700; }
.stat-lbl { font-size: 22px; color: #6B7280; margin-top: 6px; letter-spacing: 0.05em; }
.sep { width: 1px; height: 60px; background: rgba(255,255,255,0.1); }
</style>
</head>
<body>
<div class="lb" id="lb-t"></div>
<div class="lb" id="lb-b"></div>

<div id="za">
  <div id="brand-pill" style="opacity:0;background:rgba(5,150,105,0.12);border:1px solid rgba(5,150,105,0.35);border-radius:24px;padding:14px 36px;font-size:26px;font-weight:700;letter-spacing:0.08em;color:#059669;">
    MONTHLY P&amp;L &middot; <span id="month-name-pill"></span>
  </div>
</div>

<div id="zb">
  <div id="handle-line" style="opacity:0;transform:translateY(16px);font-size:34px;font-weight:700;color:#fff;">@veralevel.fx</div>
  <div id="this-month" style="opacity:0;transform:translateY(16px);font-size:36px;font-weight:700;" id="this-month"></div>
</div>

<div id="chart-area">
  <canvas id="chart-canvas" width="960" height="918"></canvas>
</div>

<div id="ze">
  <div class="stat" id="stat-gain" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="gain-val" style="color:#059669;"></div>
    <div class="stat-lbl">TOTAL RETURN</div>
  </div>
  <div class="sep"></div>
  <div class="stat" id="stat-wr" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="wr-val" style="color:#fff;"></div>
    <div class="stat-lbl">WIN RATE</div>
  </div>
  <div class="sep"></div>
  <div class="stat" id="stat-pf" style="opacity:0;transform:translateY(16px);">
    <div class="stat-val" id="pf-val"></div>
    <div class="stat-lbl">PROFIT FACTOR</div>
  </div>
</div>

<div id="zf">
  <div id="verify-line" style="opacity:0;font-size:24px;color:#6B7280;">Myfxbook #12044019 &middot; Verify every month</div>
  <div id="handle-f" style="opacity:0;font-size:24px;color:#6B7280;">@veralevel.fx</div>
</div>

<script>__ANIME_JS__</script>
<script>
const DATA = __DATA_JSON__;
const DURATION_MS = __DURATION_MS__;

// bar_widths[i] = current drawn width (0..700px), updated by anime.js
const bar_widths = new Array(DATA.monthly_items.length).fill(0);
const LABEL_ALPHA = new Array(DATA.monthly_items.length).fill(0);

(function populateDOM() {
  document.getElementById('month-name-pill').textContent = DATA.month_name;
  const tm = DATA.this_month, tmSign = DATA.this_month_sign;
  const tmColor = tm >= 0 ? '#059669' : '#EF4444';
  const el = document.getElementById('this-month');
  el.textContent = tmSign + tm.toFixed(2) + '% this month';
  el.style.color = tmColor;
  document.getElementById('gain-val').textContent = DATA.gain_sign + DATA.gain.toFixed(1) + '%';
  document.getElementById('wr-val').textContent = DATA.win_rate > 0 ? DATA.win_rate.toFixed(0) + '%' : '—';
  document.getElementById('pf-val').textContent = DATA.profit_factor.toFixed(2);
})();

function redrawChart() {
  const canvas = document.getElementById('chart-canvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const items = DATA.monthly_items;
  const n = items.length;
  if (n === 0) return;

  const barH = 60, gap = 40;
  const totalH = n * (barH + gap);
  const startY = (H - totalH) / 2;
  const MAX_W = 700, LABEL_X = 170, BAR_X = LABEL_X + 10;

  ctx.clearRect(0, 0, W, H);
  ctx.font = '700 34px Roboto, sans-serif';

  for (let i = 0; i < n; i++) {
    const [month, val] = items[i];
    const isPos = val >= 0;
    const color = isPos ? '#059669' : '#EF4444';
    const y = startY + i * (barH + gap);
    const bw = bar_widths[i];

    // Month label (right-aligned at LABEL_X)
    ctx.fillStyle = 'rgba(255,255,255,0.7)';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText(month, LABEL_X, y + barH / 2);

    // Bar
    if (bw > 0) {
      ctx.fillStyle = color;
      ctx.fillRect(BAR_X, y, bw, barH);
    }

    // Value label appears after bar is 90% drawn
    if (LABEL_ALPHA[i] > 0.01) {
      const sign = val >= 0 ? '+' : '';
      ctx.fillStyle = color;
      ctx.globalAlpha = LABEL_ALPHA[i];
      ctx.textAlign = 'left';
      ctx.fillText(sign + val.toFixed(1) + '%', BAR_X + MAX_W + 16, y + barH / 2);
      ctx.globalAlpha = 1;
    }
  }
}

let tl = null;

function buildTimeline(data) {
  tl = anime.timeline({ autoplay: false });

  tl.add({ targets: '#lb-t', scaleX:[0,1], duration:400, easing:'easeOutQuart' }, 0);
  tl.add({ targets: '#lb-b', scaleX:[0,1], duration:400, easing:'easeOutQuart' }, 0);
  tl.add({ targets: '#brand-pill', opacity:[0,1], duration:400, easing:'easeOutCubic' }, 200);
  tl.add({ targets: '#handle-line', opacity:[0,1], translateY:[16,0], duration:400, easing:'easeOutCubic' }, 300);
  tl.add({ targets: '#this-month',  opacity:[0,1], translateY:[16,0], duration:400, easing:'easeOutCubic' }, 450);

  // Bars grow staggered 130ms apart, 600ms each
  const n = data.monthly_items.length;
  for (let i = 0; i < n; i++) {
    const barStart = 700 + i * 130;
    const MAX_W = 700;
    // Use closure to capture i
    (function(idx) {
      tl.add({
        targets: { w: 0 }, w: MAX_W, duration: 600, easing: 'easeOutQuart',
        update: function(anim) {
          bar_widths[idx] = anim.animations[0].currentValue;
          redrawChart();
        }
      }, barStart);
      // Value label fades in near bar end
      tl.add({
        targets: { a: 0 }, a: 1, duration: 200, easing: 'easeOutCubic',
        update: function(anim) {
          LABEL_ALPHA[idx] = anim.animations[0].currentValue;
          redrawChart();
        }
      }, barStart + 480);
    })(i);
  }

  const allBarsEnd = 700 + (n - 1) * 130 + 600;
  tl.add({ targets: ['#stat-gain','#stat-wr','#stat-pf'],
           opacity:[0,1], translateY:[16,0], delay:anime.stagger(150), duration:400, easing:'easeOutCubic' }, allBarsEnd + 100);
  tl.add({ targets: ['#verify-line','#handle-f'],
           opacity:[0,1], delay:anime.stagger(150), duration:350, easing:'easeOutCubic' }, allBarsEnd + 500);
}

window.seekFrame = function(ms) {
  return new Promise(function(resolve) {
    if (tl) tl.seek(ms);
    requestAnimationFrame(function() { requestAnimationFrame(resolve); });
  });
};

window.addEventListener('DOMContentLoaded', function() { buildTimeline(DATA); });
</script>
</body>
</html>
```

- [ ] **Step 2: Verify marker count**

```bash
grep -c '__ANIME_JS__\|__FONTS_CSS__\|__DATA_JSON__\|__DURATION_MS__' \
  instagram/reels/templates/hero_monthly.html
```

Expected: `4`.

- [ ] **Step 3: Commit**

```bash
git add instagram/reels/templates/hero_monthly.html
git commit -m "feat: add hero_monthly.html — 6-bar chart anime.js template (5s)"
```

---

## Task 7: scenes.py — USE_BROWSER_HERO guard + monthly fix

**Files:**
- Modify: `instagram/reels/scenes.py`

The spec removes the Python `data_clip` bar chart from `make_monthly_reel` (it would duplicate the monthly bar chart now in `hero_monthly.html`). The new monthly scene list for both paths: `[hero, cta, broker, stinger]`.

- [ ] **Step 1: Verify existing test suite passes before changes**

```bash
cd instagram && BROWSER_HERO=0 python -m pytest tests/test_reels.py -v 2>&1 | tail -20
```

Expected: all tests pass. Note: `test_monthly_reel_total_duration_under_14s` may already be failing (monthly is 15.1s before the fix) — that's expected. Continue.

- [ ] **Step 2: Add `USE_BROWSER_HERO` and import at top of `scenes.py`**

At line 1 of `instagram/reels/scenes.py`, after the existing imports, add:

```python
import os

USE_BROWSER_HERO = os.getenv('BROWSER_HERO', '0') == '1'
```

The `import os` line goes right after `from __future__ import annotations` (line 1).

- [ ] **Step 3: Wrap `make_daily_reel` hero creation**

In `make_daily_reel` (lines ~119–139), replace:

```python
    hero = _clip(hero_frame, DUR_HERO)
```

with:

```python
    if USE_BROWSER_HERO:
        try:
            from reels.hero_browser import build_hero_html, capture_frames, frames_to_clip
            _data_with_meta = data  # daily needs no extra meta
            _html = build_hero_html('daily', _data_with_meta, DUR_HERO)
            _frame_paths = capture_frames(_html, DUR_HERO)
            hero = frames_to_clip(_frame_paths)
        except Exception as _e:
            print(f'[hero_browser] daily FAILED ({_e}), falling back to Python hero', flush=True)
            hero = _clip(hero_frame, DUR_HERO)
    else:
        hero = _clip(hero_frame, DUR_HERO)
```

- [ ] **Step 4: Wrap `make_weekly_reel` hero creation**

In `make_weekly_reel`, replace:

```python
    hero = _clip(hero_frame, 4.0)
```

with:

```python
    if USE_BROWSER_HERO:
        try:
            from reels.hero_browser import build_hero_html, capture_frames, frames_to_clip
            _data_with_meta = {**data, 'weekly_gain': hero_val}
            _html = build_hero_html('weekly', _data_with_meta, 4.0)
            _frame_paths = capture_frames(_html, 4.0)
            hero = frames_to_clip(_frame_paths)
        except Exception as _e:
            print(f'[hero_browser] weekly FAILED ({_e}), falling back to Python hero', flush=True)
            hero = _clip(hero_frame, 4.0)
    else:
        hero = _clip(hero_frame, 4.0)
```

- [ ] **Step 5: Wrap `make_trust_reel` hero creation**

In `make_trust_reel`, replace both branches that assign `ring_clip`:

```python
    # Hero: animated win-rate ring (5s) — only if we have real data
    if wr > 0:
        ring_clip = progress_ring_clip(win_rate=wr, duration=5.0)
    else:
        ...
        ring_clip = _clip(verify_frame, 5.0)
```

Add the BROWSER_HERO guard after both branches:

```python
    if USE_BROWSER_HERO:
        try:
            from reels.hero_browser import build_hero_html, capture_frames, frames_to_clip
            _html = build_hero_html('trust', data, 5.0)
            _frame_paths = capture_frames(_html, 5.0)
            ring_clip = frames_to_clip(_frame_paths)
        except Exception as _e:
            print(f'[hero_browser] trust FAILED ({_e}), falling back to Python hero', flush=True)
            # ring_clip already assigned above (Python path)
```

So the full block becomes:

```python
    # Hero: animated win-rate ring (5s) — only if we have real data
    if wr > 0:
        ring_clip = progress_ring_clip(win_rate=wr, duration=5.0)
    else:
        def verify_frame(t):
            img = bg_frame(t)
            alp = min(t * 1.5, 1.0)
            img = draw_alpha_text(img, (W // 2, H // 2 - 120),
                                   'WIN RATE', load_font(72, bold=True), EMERALD, alp)
            img = draw_alpha_text(img, (W // 2, H // 2 + 20),
                                   'Myfxbook #12044019', load_font(52), WHITE, alp)
            img = draw_alpha_text(img, (W // 2, H // 2 + 130),
                                   'Search "Vera Level" to verify', load_font(36), MUTED, alp)
            img = _brand_watermark(img)
            return np.array(img)
        ring_clip = _clip(verify_frame, 5.0)

    if USE_BROWSER_HERO:
        try:
            from reels.hero_browser import build_hero_html, capture_frames, frames_to_clip
            _html = build_hero_html('trust', data, 5.0)
            _frame_paths = capture_frames(_html, 5.0)
            ring_clip = frames_to_clip(_frame_paths)
        except Exception as _e:
            print(f'[hero_browser] trust FAILED ({_e}), falling back to Python hero', flush=True)
```

- [ ] **Step 6: Fix `make_monthly_reel` — replace Python hero + remove data_clip**

The Python-path hero in `make_monthly_reel` (currently a 3s fade_in) stays for `BROWSER_HERO=0`. The 5.5s `data_clip` bar chart is removed entirely (the monthly HTML template replaces it when BROWSER_HERO=1; in Python path the bar chart is gone to keep reel under 14s).

Replace the entire hero + data_clip block and the return statement in `make_monthly_reel`:

```python
    # Hero: fade-in title (Python path) OR browser hero (anime.js bar chart)
    def hero_frame(t):
        return fade_in_frame(t, f'Monthly P&L\n{month_name}', 3.0, EMERALD, 72, (W // 2, H // 2))

    hero = _clip(hero_frame, 3.0)

    if USE_BROWSER_HERO:
        try:
            from reels.hero_browser import build_hero_html, capture_frames, frames_to_clip
            _html = build_hero_html('monthly', data, 5.0)
            _frame_paths = capture_frames(_html, 5.0)
            hero = frames_to_clip(_frame_paths)
        except Exception as _e:
            print(f'[hero_browser] monthly FAILED ({_e}), falling back to Python hero', flush=True)

    # data_clip removed — bar chart now lives in hero_monthly.html (BROWSER_HERO=1)
    # or omitted (BROWSER_HERO=0) to keep reel under 14s

    def cta_frame(t):
        return cta_fade_frame(t, 'Verify every month yourself:', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)
    return _with_stinger([hero, cta, make_broker_card_clip()])
```

- [ ] **Step 7: Run full test suite with BROWSER_HERO=0**

```bash
cd instagram && BROWSER_HERO=0 python -m pytest tests/test_reels.py -v 2>&1 | tail -30
```

Expected: all tests PASS. Specifically:
- `test_make_monthly_reel_returns_clips`: `len(clips) >= 4` → passes (4 clips: hero+cta+broker+stinger)
- `test_monthly_reel_total_duration_under_14s`: total = 3.0+2.0+4.0+0.6 = 9.6s < 14s → PASSES

- [ ] **Step 8: Commit**

```bash
git add instagram/reels/scenes.py
git commit -m "feat: add USE_BROWSER_HERO guard to all 4 reel types; remove monthly data_clip"
```

---

## Task 8: effects.py — equity_curve_clip Direction C upgrades

**Files:**
- Modify: `instagram/reels/effects.py`

Direction C changes: line weight 3→6px, fill opacity 28→56, glowing dot at tip, 4px emerald letterbox bars.

- [ ] **Step 1: Write the failing test**

Add to `instagram/tests/test_reels.py` (append at end):

```python
def test_equity_curve_clip_direction_c_line_weight():
    """Direction C upgrade: line should be visually heavier (more saturated pixels)."""
    from reels.effects import equity_curve_clip
    import numpy as np
    daily_gain = [
        ['01/01/2026', 0.0, 0], ['02/01/2026', 2.1, 210],
        ['03/01/2026', -1.5, -150], ['04/01/2026', 3.2, 320],
        ['05/01/2026', -0.8, -80], ['06/01/2026', 1.9, 190],
    ]
    clip = equity_curve_clip(daily_gain, duration=3.0)
    # Frame at t=2.0 (80% drawn) should have emerald pixels visible
    frame = clip.get_frame(2.0)
    assert frame.shape == (1920, 1080, 3)
    # Emerald pixels: high G channel, low R, low B
    emerald_mask = (frame[:,:,1] > 100) & (frame[:,:,0] < 80) & (frame[:,:,2] < 80)
    assert emerald_mask.sum() > 20, "Expected visible emerald line pixels in equity curve"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd instagram && python -m pytest tests/test_reels.py::test_equity_curve_clip_direction_c_line_weight -v
```

Expected: `FAILED` (test may actually pass if existing emerald line has some pixels — re-run after changes to see visual improvement).

- [ ] **Step 3: Apply Direction C changes to `equity_curve_clip` in `effects.py`**

In `equity_curve_clip`, locate the drawing section (around line 70–82 in effects.py) and make these changes:

**Change 1** — Fill opacity 28 → 56 (≈22%):
```python
# Before:
draw.polygon(poly, fill=(r, g, b, 28))
# After:
draw.polygon(poly, fill=(r, g, b, 56))
```

**Change 2** — Line weight 3 → 6px:
```python
# Before:
draw.line(visible, fill=(*line_color, 220), width=3)
# After:
draw.line(visible, fill=(*line_color, 220), width=6)
```

**Change 3** — Replace simple tip dot with glowing dot. Replace:
```python
            tx, ty = visible[-1]
            draw.ellipse([tx - 6, ty - 6, tx + 6, ty + 6],
                         fill=(*line_color, 255))
```
with:
```python
            tx, ty = visible[-1]
            # Glowing tip dot: glow layer + sharp dot
            glow_overlay = Image.new('RGBA', overlay.size, (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow_overlay)
            gd.ellipse([tx - 18, ty - 18, tx + 18, ty + 18],
                       fill=(*line_color, 80))
            glow_overlay = glow_overlay.filter(ImageFilter.GaussianBlur(radius=10))
            overlay = Image.alpha_composite(overlay, glow_overlay)
            draw = ImageDraw.Draw(overlay)  # rebind after composite
            draw.ellipse([tx - 8, ty - 8, tx + 8, ty + 8],
                         fill=(*line_color, 255))
```

**Change 4** — Add 4px letterbox bars at top and bottom of the overlay. Add after the `overlay` image is built but before the `glow = overlay.filter(...)` line:
```python
        # 4px emerald letterbox bars (sweep in over first 30% of progress)
        bar_alpha = int(220 * min(progress * 3.0, 1.0))
        if bar_alpha > 0:
            draw.rectangle([0, 0, x1, 4], fill=(*EMERALD, bar_alpha))
            draw.rectangle([x0, H - 4, W, H], fill=(*EMERALD, bar_alpha))
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd instagram && python -m pytest tests/test_reels.py::test_equity_curve_clip_direction_c_line_weight \
  tests/test_reels.py::test_equity_curve_clip_shape -v
```

Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add instagram/reels/effects.py
git commit -m "feat: equity_curve_clip Direction C — 6px line, 22% fill, glow dot, letterbox bars"
```

---

## Task 9: animator.py — Direction C for cascade text and CTA

**Files:**
- Modify: `instagram/reels/animator.py`

Adds `ease_out_back`, upgrades `cascade_text_frame` (headline treatment + emerald accent bars + easeOutBack), and upgrades `cta_fade_frame` (letterbox bars + 48pt bold line1 + underline animation).

- [ ] **Step 1: Write failing tests**

Add to `instagram/tests/test_reels.py`:

```python
def test_ease_out_back_overshoots():
    """ease_out_back(c1=1.5) must overshoot 1.0 before settling."""
    from reels.animator import ease_out_back
    values = [ease_out_back(i * 0.05) for i in range(1, 20)]
    assert max(values) > 1.0, "ease_out_back must overshoot"


def test_ease_out_back_settles_at_one():
    """ease_out_back at x=1.0 must equal exactly 1.0."""
    from reels.animator import ease_out_back
    assert ease_out_back(1.0) == 1.0


def test_cascade_text_frame_direction_c_shape():
    """cascade_text_frame still returns (1920, 1080, 3) after Direction C changes."""
    from reels.animator import cascade_text_frame
    import numpy as np
    frame = cascade_text_frame(t=1.0, lines=['Headline', 'Detail line'],
                               dur=3.0, stagger=0.3,
                               color=(255, 255, 255), fontsize=38, top_y=700)
    assert frame.shape == (1920, 1080, 3)


def test_cta_fade_frame_direction_c_shape():
    """cta_fade_frame still returns (1920, 1080, 3) after Direction C changes."""
    from reels.animator import cta_fade_frame
    import numpy as np
    frame = cta_fade_frame(t=1.0, line1='Verify my live account',
                           line2='Myfxbook #12044019')
    assert frame.shape == (1920, 1080, 3)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd instagram && python -m pytest tests/test_reels.py::test_ease_out_back_overshoots \
  tests/test_reels.py::test_ease_out_back_settles_at_one -v
```

Expected: `FAILED` with `AttributeError: module 'reels.animator' has no attribute 'ease_out_back'`.

- [ ] **Step 3: Add `ease_out_back` to `animator.py`**

In `instagram/reels/animator.py`, after the `ease_spring` function (around line 104), add:

```python
def ease_out_back(x: float, c1: float = 1.5) -> float:
    """Ease-out with overshoot. c1 controls overshoot amount (1.5 = mild)."""
    x = min(max(x, 0.0), 1.0)
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
```

- [ ] **Step 4: Upgrade `cascade_text_frame` in `animator.py`**

Replace the entire `cascade_text_frame` function body:

```python
def cascade_text_frame(t: float, lines, dur: float, stagger: float,
                       color, fontsize: int, top_y: int) -> np.ndarray:
    """
    Lines slide up 20px + fade in sequentially with Direction C aesthetic.

    Line 0 is the headline: bold, slightly larger, no accent bar.
    Lines 1+ get a 3px emerald left-edge accent bar before text.
    Easing: ease_out_back(1.5) — mild overshoot.
    """
    img = bg_frame(t)
    font = load_font(fontsize)
    font_headline = load_font(fontsize + 10, bold=True)
    line_height = fontsize + 24

    for i, line in enumerate(lines):
        line_t = t - i * stagger
        if line_t <= 0:
            continue
        x = min(line_t / dur, 1.0)
        progress = ease_out_back(x, c1=1.5)
        alpha = min(max(progress, 0.0), 1.0)
        y_offset = int(20 * (1.0 - min(progress, 1.0)))
        y = top_y + i * line_height + y_offset

        if i == 0:
            img = draw_alpha_text(img, (W // 2, y), line, font_headline, color, alpha)
        else:
            if alpha > 0.05:
                draw = ImageDraw.Draw(img)
                bar_x = 80
                bar_y = y - fontsize // 2
                bar_alpha_int = int(alpha * 220)
                draw.rectangle([bar_x, bar_y, bar_x + 3, bar_y + fontsize],
                               fill=(*EMERALD, bar_alpha_int))
            img = draw_alpha_text(img, (W // 2, y), line, font, color, alpha)

    return np.array(img)
```

- [ ] **Step 5: Upgrade `cta_fade_frame` in `animator.py`**

Replace the entire `cta_fade_frame` function body:

```python
def cta_fade_frame(t: float, line1: str, line2: str = '') -> np.ndarray:
    """
    Two-line call-to-action with Direction C aesthetic.

    Letterbox bars sweep in (0–400ms).
    line1: 48pt bold EMERALD, centred at H//2 - 60. Animated underline grows L→R.
    line2: 30pt MUTED, centred at H//2 + 60.
    """
    img = bg_frame(t)

    # Letterbox bars sweep in from 0 → full width over 400ms
    bar_progress = ease_out(t, 0.4)
    bar_w = int(W * bar_progress)
    if bar_w > 0:
        draw0 = ImageDraw.Draw(img)
        draw0.rectangle([0, 0, bar_w, 4], fill=EMERALD)
        draw0.rectangle([W - bar_w, H - 4, W, H], fill=EMERALD)

    # line1: 48pt bold EMERALD
    alpha1 = ease_out(t, 1.0)
    font1 = load_font(48, bold=True)
    img = draw_alpha_text(img, (W // 2, H // 2 - 60), line1, font1, EMERALD, alpha1)

    # Animated underline: emerald rect grows L→R under line1 starting at t=0.3
    if t > 0.3:
        ul_progress = ease_out(t - 0.3, 0.4)
        ul_w = int(600 * ul_progress)
        ul_x = W // 2 - 300
        ul_y = H // 2 - 20
        draw1 = ImageDraw.Draw(img)
        draw1.rectangle([ul_x, ul_y, ul_x + ul_w, ul_y + 3], fill=EMERALD)

    # line2: 30pt MUTED
    if line2 and t > 0.4:
        alpha2 = ease_out(t - 0.4, 1.0)
        font2 = load_font(30)
        img = draw_alpha_text(img, (W // 2, H // 2 + 60), line2, font2, MUTED, alpha2)

    return np.array(img)
```

- [ ] **Step 6: Run all Direction C tests**

```bash
cd instagram && python -m pytest tests/test_reels.py \
  -k "ease_out_back or cascade_text_frame_direction or cta_fade_frame_direction" -v
```

Expected: all 4 new tests PASS.

- [ ] **Step 7: Run full test suite to check no regressions**

```bash
cd instagram && BROWSER_HERO=0 python -m pytest tests/test_reels.py -v 2>&1 | tail -30
```

Expected: all tests PASS.

- [ ] **Step 8: Commit**

```bash
git add instagram/reels/animator.py
git commit -m "feat: animator.py Direction C — ease_out_back, cascade accent bars, cta letterbox + underline"
```

---

## Task 10: CI wiring — requirements.txt + insta-reel.yml

**Files:**
- Modify: `instagram/requirements.txt`
- Modify: `.github/workflows/insta-reel.yml`

- [ ] **Step 1: Add `playwright>=1.44` to requirements.txt**

Append to `instagram/requirements.txt`:
```
playwright>=1.44
```

Full resulting file:
```
matplotlib==3.8.4
numpy==1.26.4
requests==2.31.0
Pillow==10.3.0
moviepy==1.0.3
google-genai>=1.0.0
edge-tts>=6.1.0
deep-translator>=1.11.4
higgsfield-client
gradio-client>=1.3
playwright>=1.44
```

- [ ] **Step 2: Add playwright install step to `insta-reel.yml`**

In `.github/workflows/insta-reel.yml`, after the `Install dependencies` step (line 55), add:

```yaml
      - name: Install Playwright (Chrome pre-installed via channel=chrome)
        run: pip install playwright
        # No 'playwright install chromium' — channel='chrome' uses
        # Chrome for Testing already present on ubuntu-latest (zero download)
```

- [ ] **Step 3: Add `BROWSER_HERO: '1'` to the `Generate Reel` step env block**

In the `Generate Reel & post to Instagram` step (around line 97), add `BROWSER_HERO` to the `env:` block:

```yaml
      - name: Generate Reel & post to Instagram
        env:
          IG_USER_ID:        ${{ secrets.IG_USER_ID }}
          META_ACCESS_TOKEN: ${{ secrets.META_ACCESS_TOKEN }}
          GITHUB_TOKEN:      ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          POST_TYPE:         ${{ steps.post_type.outputs.type }}
          POST_LANG:         ${{ github.event.inputs.post_lang || 'en' }}
          RECOVERY_START:    ${{ secrets.RECOVERY_START }}
          BRAND_IB_URL:      ${{ secrets.BRAND_IB_URL }}
          BROWSER_HERO:      '1'
        run: python instagram/run_reel.py
```

- [ ] **Step 4: Verify YAML is valid**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/insta-reel.yml'))" && echo "YAML OK"
```

Expected: `YAML OK`.

- [ ] **Step 5: Commit**

```bash
git add instagram/requirements.txt .github/workflows/insta-reel.yml
git commit -m "feat: CI wiring — playwright>=1.44 in requirements, BROWSER_HERO=1 in insta-reel.yml"
```

---

## Task 11: End-to-end smoke test and merge-readiness check

**Files:**
- No new files (runs existing tests)

- [ ] **Step 1: Run full test suite with BROWSER_HERO=0 (must pass before merge)**

```bash
cd instagram && BROWSER_HERO=0 python -m pytest tests/test_reels.py tests/test_hero_browser.py -v 2>&1
```

Expected: all tests PASS. Zero failures permitted.

- [ ] **Step 2: Verify effects.py and animator.py imports haven't broken**

```bash
cd instagram && python -c "
from reels import animator, effects, scenes, hero_browser
from reels.animator import ease_out_back, cascade_text_frame, cta_fade_frame
from reels.effects import equity_curve_clip
from reels.hero_browser import build_hero_html, capture_frames, frames_to_clip, _coerce_data
print('All imports OK')
"
```

Expected: `All imports OK`.

- [ ] **Step 3: Smoke-test a daily reel frame locally (Python path)**

```bash
cd instagram && BROWSER_HERO=0 python -c "
import json
from pathlib import Path
data = json.loads(Path('data/vera-snapshot.json').read_text())
from reels.scenes import make_daily_reel
clips = make_daily_reel(data)
print(f'Daily reel clips: {len(clips)}, durations: {[round(c.duration,1) for c in clips]}')
assert len(clips) == 5
"
```

Expected: `Daily reel clips: 5, durations: [4.0, 3.0, 3.5, 2.0, 0.6]` (approximate).

- [ ] **Step 4: Confirm git status is clean**

```bash
git status
git log --oneline -8
```

Expected: no untracked or modified files (everything committed). Log shows 8+ commits for this feature.

- [ ] **Step 5: Force-add plan and spec docs to worktree branch**

```bash
git add -f docs/superpowers/plans/2026-07-26-animejs-cinematic-reels.md
git add -f docs/superpowers/specs/2026-07-26-animejs-cinematic-reels-design.md
git commit -m "docs: add implementation plan for animejs cinematic reels"
```

- [ ] **Step 6: Final commit summary**

```bash
git log --oneline worktree-feat+animejs-cinematic-reels 2>/dev/null | head -15
```

Expected: shows all feature commits. Branch is ready for review / PR against master.

---

## Rollback Reference

| Tier | Action | Effect |
|------|--------|--------|
| Automatic | `try/except` in `scenes.py` catches Playwright failure | Python hero used, post goes out |
| Instant (no code) | Remove `BROWSER_HERO: '1'` from `insta-reel.yml` | All reels use Python hero |
| Full | `git checkout master` | Entire feature branch isolated |
| Per-type | Add `post_type == 'daily'` check inside `if USE_BROWSER_HERO:` | Opt-out per reel type |

---

## Self-Review Checklist

**Spec coverage:**
- ✅ 4 HTML templates (hero_daily, weekly, trust, monthly) — Tasks 3–6
- ✅ hero_browser.py with 3 public functions — Task 2
- ✅ vendor assets (anime.min.js + 3 WOFF2) — Task 1
- ✅ `USE_BROWSER_HERO` guard in all 4 reel types — Task 7
- ✅ Monthly data_clip removed — Task 7, Step 6
- ✅ equity_curve_clip Direction C (line 6px, fill 22%, glow dot, letterbox) — Task 8
- ✅ cascade_text_frame Direction C (headline, accent bars, ease_out_back) — Task 9
- ✅ cta_fade_frame Direction C (letterbox, 48pt, underline) — Task 9
- ✅ playwright>=1.44 in requirements — Task 10
- ✅ BROWSER_HERO=1 in insta-reel.yml only — Task 10
- ✅ channel='chrome' (no download) — in hero_browser.py Task 2
- ✅ try/except auto-fallback — Task 7
- ✅ Data coercion (float/int/json.dumps) — _coerce_data Task 2
- ✅ Trust winRate==0 fallback (no ring) — hero_trust.html Task 5
- ✅ Fonts base64-embedded, await document.fonts.ready — hero_browser.py + all templates
- ✅ NAVY = #001835 in CSS backgrounds — all templates
- ✅ seekFrame 2×rAF guard — all templates
- ✅ PNGs to disk (not in-memory) — capture_frames returns list[Path] Task 2

**No placeholders found.**

**Type consistency:** `capture_frames` returns `list[Path]` → `frames_to_clip(list[Path])` ✅. `build_hero_html` returns `Path` → `capture_frames(Path, ...)` ✅. `frames_to_clip` returns `VideoClip` with `.set_fps()` ✅ (required for `_with_stinger`).
