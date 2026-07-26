"""
hero_browser.py — Playwright frame-capture bridge for anime.js hero reel templates.

Public API:
    build_hero_html(post_type, data, duration) -> Path
    capture_frames(html_path, duration, fps, timeout_s) -> list[Path]
    frames_to_clip(frame_paths, fps) -> VideoClip
"""
from __future__ import annotations

import base64
import json
import tempfile
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_REELS_DIR = Path(__file__).parent
_TEMPLATES_DIR = _REELS_DIR / 'templates'
_VENDOR_DIR = _TEMPLATES_DIR / 'vendor'


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _coerce_data(post_type: str, data: dict) -> dict:
    """Coerce all snapshot fields to safe types for JSON injection into HTML.

    Handles missing/None fields gracefully. Returns a flat dict of type-safe
    values suitable for json.dumps() injection into an HTML template.
    """
    acct = data.get('account', {}) or {}
    open_trades = data.get('openTrades', []) or []
    daily_gain = data.get('dailyGain', []) or []

    # --- Numeric account fields ---
    balance = float(acct.get('balance') or 0)
    balance_fmt = f'${balance:,.0f}'

    today_daily_raw = acct.get('todayDaily')
    if today_daily_raw is None:
        today_daily_raw = acct.get('daily')
    today_daily = float(today_daily_raw or 0)
    today_daily_sign = '+' if today_daily >= 0 else ''

    win_rate = float(acct.get('winRate') or 0)
    profit_factor = float(acct.get('profitFactor') or 0)
    pips = int(acct.get('pips') or 0)
    trades = int(acct.get('trades') or 0)
    gain = float(acct.get('gain') or 0)
    gain_sign = '+' if gain >= 0 else ''
    drawdown = float(acct.get('drawdown') or 0)

    # --- Weekly gain ---
    if 'weekly_gain' in data and data['weekly_gain'] is not None:
        weekly_gain = float(data['weekly_gain'])
    else:
        weekly_gain = gain
    weekly_gain_sign = '+' if weekly_gain >= 0 else ''

    # --- Open pairs (up to 5) ---
    open_pairs = [
        str(t.get('symbol', ''))
        for t in open_trades[:5]
        if t.get('symbol')
    ]
    open_pairs_str = ' · '.join(open_pairs) if open_pairs else 'No open positions'

    # --- Sparkline points: normalise dailyGain cumulative values to [0, 1] ---
    sparkline_points = _build_sparkline(daily_gain)

    # --- Monthly items: last 6 months from monthly_pnl_from_daily ---
    monthly_items = _build_monthly_items(daily_gain)

    # --- This month ---
    this_month = float(monthly_items[-1][1]) if monthly_items else 0.0
    this_month_sign = '+' if this_month >= 0 else ''

    # --- Month name ---
    month_name = datetime.now().strftime('%B %Y')

    return {
        'balance': balance,
        'balance_fmt': balance_fmt,
        'today_daily': today_daily,
        'today_daily_sign': today_daily_sign,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'pips': pips,
        'trades': trades,
        'gain': gain,
        'gain_sign': gain_sign,
        'drawdown': drawdown,
        'weekly_gain': weekly_gain,
        'weekly_gain_sign': weekly_gain_sign,
        'open_pairs': open_pairs,
        'open_pairs_str': open_pairs_str,
        'sparkline_points': sparkline_points,
        'monthly_items': monthly_items,
        'month_name': month_name,
        'this_month': this_month,
        'this_month_sign': this_month_sign,
    }


def _build_sparkline(daily_gain: list) -> list:
    """Parse dailyGain rows and normalise cumulative values to [[x_frac, y_frac], ...]."""
    values: list[float] = []
    for row in daily_gain:
        if isinstance(row, list) and len(row) >= 2:
            try:
                values.append(float(row[1]))
            except (ValueError, TypeError):
                continue
        elif isinstance(row, dict):
            try:
                values.append(float(row.get('value', 0)))
            except (ValueError, TypeError):
                continue

    if len(values) < 2:
        return [[0.0, 0.5], [1.0, 0.5]]

    min_v = min(values)
    max_v = max(values)
    v_range = max_v - min_v

    points = []
    n = len(values)
    for i, v in enumerate(values):
        x = i / (n - 1)
        if v_range == 0:
            y = 0.5
        else:
            y = (v - min_v) / v_range
        points.append([round(x, 6), round(y, 6)])

    return points


def _build_monthly_items(daily_gain: list) -> list:
    """Return last 6 months as [[month_str, float], ...] pairs."""
    try:
        from captions import monthly_pnl_from_daily
        monthly_pnl = monthly_pnl_from_daily(daily_gain)
    except Exception:
        monthly_pnl = {}

    items = [[k, float(v)] for k, v in monthly_pnl.items()]
    return items[-6:]


def _build_fonts_css() -> str:
    """Read WOFF2 files, base64-encode them, return @font-face CSS string."""
    fonts = [
        ('Roboto-Black.woff2', 900),
        ('Roboto-Bold.woff2', 700),
        ('Roboto-Regular.woff2', 400),
    ]
    css_blocks = []
    for filename, weight in fonts:
        font_path = _VENDOR_DIR / filename
        raw = font_path.read_bytes()
        b64 = base64.b64encode(raw).decode('ascii')
        css_blocks.append(
            f"@font-face {{\n"
            f"  font-family: 'Roboto';\n"
            f"  font-weight: {weight};\n"
            f"  font-style: normal;\n"
            f"  src: url('data:font/woff2;base64,{b64}') format('woff2');\n"
            f"}}"
        )
    return '\n'.join(css_blocks)


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def build_hero_html(post_type: str, data: dict, duration: float) -> Path:
    """Build the hero HTML from template, inject data/assets, write to temp file.

    Returns the Path to the written HTML file.
    """
    template_path = _TEMPLATES_DIR / f'hero_{post_type}.html'
    template_html = template_path.read_text(encoding='utf-8')

    coerced = _coerce_data(post_type, data)
    fonts_css = _build_fonts_css()
    anime_js = (_VENDOR_DIR / 'anime.min.js').read_text(encoding='utf-8')
    data_json = json.dumps(coerced, ensure_ascii=False)
    duration_ms = str(int(duration * 1000))

    html = template_html
    html = html.replace('__ANIME_JS__', anime_js)
    html = html.replace('__FONTS_CSS__', fonts_css)
    html = html.replace('__DATA_JSON__', data_json)
    html = html.replace('__DURATION_MS__', duration_ms)

    tmp_dir = Path(tempfile.mkdtemp())
    out_path = tmp_dir / f'hero_{post_type}_{int(time.time())}.html'
    out_path.write_text(html, encoding='utf-8')
    return out_path


def capture_frames(
    html_path: Path,
    duration: float,
    fps: int = 30,
    timeout_s: int = 120,
) -> list[Path]:
    """Render anime.js template frame-by-frame via Playwright, returning PNG paths.

    playwright is imported inside this function so the module can be imported
    without playwright installed.
    """
    from playwright.sync_api import sync_playwright  # noqa: PLC0415

    tmp_dir = Path(tempfile.mkdtemp())
    n_frames = int(duration * fps)
    frame_paths: list[Path] = []
    start = time.time()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='chrome')
        try:
            page = browser.new_page(
                viewport={'width': 1080, 'height': 1920},
                device_scale_factor=1,
            )
            page.goto(f'file://{html_path.as_posix()}')
            # Wait for WOFF2 fonts to load
            page.evaluate('document.fonts.ready')

            for frame_idx in range(n_frames):
                if time.time() - start > timeout_s:
                    raise RuntimeError(
                        f'capture_frames timed out after {timeout_s}s '
                        f'at frame {frame_idx}/{n_frames}'
                    )
                ms = int(frame_idx * 1000 / fps)
                page.evaluate(f'seekFrame({ms})')
                frame_file = tmp_dir / f'frame_{frame_idx:04d}.png'
                page.screenshot(path=str(frame_file))
                frame_paths.append(frame_file)
        finally:
            browser.close()

    return frame_paths


def frames_to_clip(frame_paths: list[Path], fps: int = 30):
    """Convert a list of PNG frame paths to a MoviePy VideoClip.

    moviepy is imported inside this function so the module can be imported
    without moviepy installed.
    """
    from moviepy.editor import ImageSequenceClip  # noqa: PLC0415

    str_paths = [str(p) for p in frame_paths]
    return ImageSequenceClip(str_paths, fps=fps).set_fps(fps)
