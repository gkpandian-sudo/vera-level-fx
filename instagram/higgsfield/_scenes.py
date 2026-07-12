# instagram/higgsfield/_scenes.py
"""Three animated portrait-format Ken Burns clips for the reel background.

Each function returns a local MP4 path. Clips are 1080x1920 matplotlib figures
at full portrait aspect ratio — no external assets required, only vera-snapshot.json.

Approach:
  1. Render a 1080x1920 matplotlib figure to a numpy array (once per clip).
  2. Apply Ken Burns slow-zoom animation via moviepy VideoClip.
  3. Overlay PIL text/chart elements per-frame where animation is needed.
"""
import io
import json
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image, ImageDraw
from moviepy.editor import VideoClip

ROOT = Path(__file__).resolve().parent.parent.parent

# ── Brand palette ─────────────────────────────────────────────────────────────
NAVY    = '#010E1F'
NAVY_S  = '#051830'
NAVY_L  = '#0A2545'
EMERALD = '#059669'
WHITE   = '#FFFFFF'
MUTED   = '#B8CFEA'
DIM     = '#6A8EB8'
RED     = '#EF4444'

# PIL colours
_EMERALD = (5, 150, 105)
_RED     = (239, 68, 68)
_WHITE   = (255, 255, 255)
_NAVY    = (1, 14, 31)
_MUTED   = (184, 207, 234)

_W, _H = 1080, 1920


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_snapshot() -> dict:
    return json.loads((ROOT / 'data' / 'vera-snapshot.json').read_text())


def _fig_to_arr(fig, w: int = _W, h: int = _H) -> np.ndarray:
    """Save matplotlib figure to numpy RGB array at target size."""
    buf = io.BytesIO()
    fig.savefig(buf, dpi=100, bbox_inches=None, facecolor=NAVY, format='png')
    plt.close(fig)
    buf.seek(0)
    return np.array(Image.open(buf).convert('RGB').resize((w, h), Image.LANCZOS))


def _ken_burns_arr(base_arr: np.ndarray, t: float, duration: float,
                   zoom_start: float = 1.0, zoom_end: float = 1.12) -> np.ndarray:
    """Return a zoomed numpy frame at time t from base_arr (Ken Burns effect)."""
    z = zoom_start + (zoom_end - zoom_start) * (t / duration)
    h, w = base_arr.shape[:2]
    cw, ch = int(w / z), int(h / z)
    x0, y0 = (w - cw) // 2, (h - ch) // 2
    return np.array(
        Image.fromarray(base_arr[y0:y0 + ch, x0:x0 + cw]).resize((w, h), Image.LANCZOS)
    )


def _pil_font():
    """Return a large PIL-compatible font from matplotlib's bundled DejaVu Sans."""
    from PIL import ImageFont
    try:
        import matplotlib.font_manager as fm
        path = fm.findfont(fm.FontProperties(family='DejaVu Sans', weight='bold'))
        return {
            'xl':  ImageFont.truetype(path, 160),
            'lg':  ImageFont.truetype(path, 72),
            'md':  ImageFont.truetype(path, 48),
            'sm':  ImageFont.truetype(path, 32),
            'xs':  ImageFont.truetype(path, 22),
        }
    except Exception:
        default = ImageFont.load_default()
        return {k: default for k in ('xl', 'lg', 'md', 'sm', 'xs')}


def _write_to_mp4(make_frame_fn, duration: float, fps: int = 24) -> str:
    clip = VideoClip(make_frame_fn, duration=duration).set_fps(fps)
    tmp = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    tmp.close()
    clip.write_videofile(tmp.name, codec='libx264', audio=False, logger=None)
    clip.close()
    return tmp.name


def _monthly_pnl(daily_gain: list) -> dict[str, float]:
    """Compute month→total-gain-% from dailyGain list (MM/DD/YYYY format)."""
    totals: dict[str, list] = {}
    for d in daily_gain:
        date_str = d.get('date', '')
        try:
            parts = date_str.split('/')
            key = f"{parts[2]}-{parts[0].zfill(2)}"  # YYYY-MM
        except Exception:
            continue
        try:
            totals.setdefault(key, []).append(float(d.get('value', 0)))
        except ValueError:
            pass
    # Use the last value per month as the month-end cumulative gain
    monthly = {}
    prev = 0.0
    for k in sorted(totals):
        last = totals[k][-1] if totals[k] else prev
        monthly[k] = round(last - prev, 2)
        prev = last
    return monthly


# ── Scene 0: Performance ──────────────────────────────────────────────────────

def make_performance_clip(duration: float = 12.0) -> str:
    """Portrait card: hero gain %, balance, win rate, profit factor, monthly bars."""
    print('  [scenes] rendering performance clip…')
    snap = _load_snapshot()
    acct = snap.get('account', {})
    daily = snap.get('dailyGain', [])

    gain   = float(acct.get('gain', 0))
    bal    = float(acct.get('balance', 0))
    wr     = float(acct.get('winRate', 0))
    pf     = float(acct.get('profitFactor', 0))
    dd     = float(acct.get('drawdown', 0))
    trades = int(acct.get('trades', 0))

    gain_color = EMERALD if gain >= 0 else RED
    gain_sign  = '+' if gain >= 0 else ''

    # Monthly bars
    monthly = _monthly_pnl(daily)
    months  = sorted(monthly)[-9:]
    mvals   = [monthly[m] for m in months]
    mlabels = [m[5:] for m in months]   # "MM"

    # ── Build static matplotlib portrait ──────────────────────────────────────
    fig = plt.figure(figsize=(10.8, 19.2), dpi=100, facecolor=NAVY)
    ax  = fig.add_axes([0, 0, 1, 1], facecolor=NAVY)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

    # Emerald accent bars
    ax.add_patch(patches.Rectangle((0, 0.979), 1, 0.021, fc=EMERALD, transform=ax.transAxes, zorder=10))
    ax.add_patch(patches.Rectangle((0, 0),     1, 0.008, fc=EMERALD, transform=ax.transAxes, zorder=10))

    # Header
    ax.add_patch(patches.Circle((0.065, 0.962), 0.006, fc=EMERALD, transform=ax.transAxes, zorder=11))
    ax.text(0.085, 0.962, 'IC Markets Verified  ·  ASIC Regulated  ·  Myfxbook #12044019',
            fontsize=13, color=EMERALD, va='center', transform=ax.transAxes, fontfamily='monospace', zorder=11)
    ax.text(0.06, 0.942, '@veralevel.fx  ·  LIVE PERFORMANCE CARD',
            fontsize=18, color=MUTED, va='center', transform=ax.transAxes,
            fontfamily='monospace', fontweight='bold', zorder=11)
    ax.plot([0.06, 0.94], [0.928, 0.928], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)

    # Label for hero
    ax.text(0.06, 0.900, 'TOTAL GAIN SINCE INCEPTION',
            fontsize=19, color=MUTED, va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=11)

    # ← Hero gain % will be drawn in PIL overlay (counted animation) ←
    # Placeholder region: y=0.72–0.88
    ax.add_patch(patches.Rectangle((0.06, 0.720), 0.88, 0.168,
        fc='#051830', ec='none', transform=ax.transAxes, zorder=5))

    # Sub-metrics strip
    ax.plot([0.06, 0.94], [0.714, 0.714], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)
    sub = [('WIN RATE', f'{wr:.1f}%', 0.18), ('PROF.FACTOR', f'{pf:.2f}', 0.45),
           ('BALANCE', f'${bal:,.0f}', 0.72), ('DRAWDOWN', f'{dd:.1f}%', 0.91)]
    for lbl, val, px in sub:
        col = RED if lbl == 'DRAWDOWN' else WHITE
        ax.text(px, 0.688, val,  fontsize=22, fontweight='black', color=col,
                ha='center', va='center', transform=ax.transAxes, zorder=11)
        ax.text(px, 0.663, lbl, fontsize=11, color=MUTED, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=11)

    ax.plot([0.06, 0.94], [0.648, 0.648], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)
    ax.text(0.5, 0.628, 'MONTHLY P&L BREAKDOWN', fontsize=17, color=MUTED, ha='center',
            va='center', transform=ax.transAxes, fontfamily='monospace', zorder=11)

    # Monthly bar chart
    if mvals:
        chart_ax = fig.add_axes([0.07, 0.30, 0.86, 0.29])
        bar_cols = [EMERALD if v >= 0 else RED for v in mvals]
        xs = np.arange(len(mvals))
        chart_ax.bar(xs, mvals, color=bar_cols, width=0.65)
        chart_ax.axhline(0, color=MUTED, linewidth=0.7, alpha=0.5)
        chart_ax.set_xticks(xs)
        chart_ax.set_xticklabels(mlabels, color=MUTED, fontsize=11, fontfamily='monospace')
        chart_ax.set_facecolor(NAVY_S)
        for spine in chart_ax.spines.values():
            spine.set_color(EMERALD); spine.set_alpha(0.3)
        chart_ax.tick_params(colors=MUTED, length=3)
        chart_ax.yaxis.set_tick_params(labelcolor=MUTED, labelsize=11)

    # Trades + disclaimer
    ax.text(0.5, 0.278, f'{trades:,} trades  ·  All live  ·  Nothing hidden',
            fontsize=16, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)
    ax.plot([0.06, 0.94], [0.032, 0.032], color=EMERALD, alpha=0.25, lw=1.0, transform=ax.transAxes)
    ax.text(0.5, 0.017, 'Not financial advice. Past performance does not guarantee future results.',
            fontsize=11, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)

    bg = _fig_to_arr(fig)
    fonts = _pil_font()

    def make_frame(t: float) -> np.ndarray:
        # Ken Burns slow zoom into the card
        frame = _ken_burns_arr(bg, t, duration, zoom_start=1.0, zoom_end=1.10)
        # Animated gain% counter over the placeholder region (y ~780–940px from top)
        progress = min(t / (duration * 0.72), 1.0)
        eased = progress * progress * (3 - 2 * progress)
        current = gain * eased
        sign  = '+' if current >= 0 else ''
        color = _EMERALD if current >= 0 else _RED
        text  = f'{sign}{current:.1f}%'
        img   = Image.fromarray(frame)
        draw  = ImageDraw.Draw(img)
        draw.text((540, 860), text, fill=color, font=fonts['xl'], anchor='mm')
        return np.array(img)

    return _write_to_mp4(make_frame, duration)


# ── Scene 1: Equity Curve ─────────────────────────────────────────────────────

def make_equity_clip(duration: float = 12.0) -> str:
    """Equity curve drawing itself across the screen using live dailyGain data."""
    print('  [scenes] rendering equity curve clip…')
    snap  = _load_snapshot()
    daily = snap.get('dailyGain', [])
    acct  = snap.get('account', {})
    gain  = float(acct.get('gain', 0))

    # Build cumulative gain series
    cumulative = []
    total = 0.0
    for d in daily:
        try:
            total += float(d.get('value', 0))
        except ValueError:
            pass
        cumulative.append(total)
    if not cumulative:
        cumulative = [0.0, gain]
    n = len(cumulative)
    min_v, max_v = min(cumulative), max(cumulative)
    val_range = max(max_v - min_v, 0.1)

    # ── Background ────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(10.8, 19.2), dpi=100, facecolor=NAVY)
    ax  = fig.add_axes([0, 0, 1, 1], facecolor=NAVY)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

    ax.add_patch(patches.Rectangle((0, 0.979), 1, 0.021, fc=EMERALD, transform=ax.transAxes, zorder=10))
    ax.add_patch(patches.Rectangle((0, 0),     1, 0.008, fc=EMERALD, transform=ax.transAxes, zorder=10))
    ax.add_patch(patches.Circle((0.065, 0.962), 0.006, fc=EMERALD, transform=ax.transAxes, zorder=11))
    ax.text(0.085, 0.962, 'IC Markets Verified  ·  ASIC Regulated  ·  Myfxbook #12044019',
            fontsize=13, color=EMERALD, va='center', transform=ax.transAxes, fontfamily='monospace', zorder=11)

    ax.text(0.5, 0.928, 'EQUITY CURVE', fontsize=42, color=WHITE, ha='center', va='center',
            transform=ax.transAxes, fontweight='black', zorder=11)
    ax.text(0.5, 0.900, 'LIVE ACCOUNT  ·  EVERY TRADE  ·  FULL HISTORY',
            fontsize=17, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold', zorder=11)
    ax.plot([0.06, 0.94], [0.886, 0.886], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)

    # Chart area background box
    ax.add_patch(patches.FancyBboxPatch((0.04, 0.068), 0.92, 0.79,
        boxstyle='square', fc=NAVY_S, ec=EMERALD, lw=0.8,
        transform=ax.transAxes, zorder=4))

    # Y-axis labels
    gain_label  = f'{gain:+.1f}%'
    gain_color  = EMERALD if gain >= 0 else RED
    ax.text(0.96, 0.854, gain_label, fontsize=18, color=gain_color, ha='right', va='center',
            transform=ax.transAxes, fontweight='black', zorder=11)
    ax.text(0.96, 0.075, '0.0%', fontsize=14, color=MUTED, ha='right', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)
    # X-axis labels
    ax.text(0.06, 0.050, 'Start', fontsize=12, color=MUTED, va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)
    ax.text(0.94, 0.050, f'Day {n}', fontsize=12, color=MUTED, ha='right', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)

    # Horizontal grid lines
    for frac in (0.25, 0.5, 0.75):
        y = 0.068 + frac * 0.79
        ax.plot([0.04, 0.96], [y, y], color=MUTED, alpha=0.10, lw=0.8, transform=ax.transAxes)

    # Disclaimer
    ax.plot([0.06, 0.94], [0.032, 0.032], color=EMERALD, alpha=0.25, lw=1.0, transform=ax.transAxes)
    ax.text(0.5, 0.017, 'Not financial advice. Past performance does not guarantee future results.',
            fontsize=11, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)

    bg = _fig_to_arr(fig)

    # Chart pixel bounds (matching the matplotlib axes above)
    cx0  = int(0.04 * _W)
    cx1  = int(0.96 * _W)
    cy0  = int((1 - 0.858) * _H)   # top of chart (high values)
    cy1  = int((1 - 0.068) * _H)   # bottom of chart (low values)
    cw   = cx1 - cx0
    ch   = cy1 - cy0

    def _val_to_px(v):
        frac = (v - min_v) / val_range
        return int(cy1 - frac * ch)

    def make_frame(t: float) -> np.ndarray:
        progress = min(t / (duration * 0.88), 1.0)
        n_show   = max(2, int(n * progress))

        frame = bg.copy()
        img   = Image.fromarray(frame)
        draw  = ImageDraw.Draw(img)

        # Draw revealed portion of equity curve
        pts = []
        for i in range(n_show):
            x = cx0 + int(i / max(n - 1, 1) * cw)
            y = _val_to_px(cumulative[i])
            y = max(cy0, min(cy1, y))
            pts.append((x, y))

        if len(pts) >= 2:
            last_val = cumulative[n_show - 1]
            col = _EMERALD if last_val >= 0 else _RED
            draw.line(pts, fill=col, width=5)
            # Leading dot
            lx, ly = pts[-1]
            draw.ellipse([(lx - 9, ly - 9), (lx + 9, ly + 9)], fill=col)

        return np.array(img)

    return _write_to_mp4(make_frame, duration)


# ── Scene 2: Trust Metrics ────────────────────────────────────────────────────

def make_trust_clip(duration: float = 12.0) -> str:
    """Win rate, profit factor, drawdown, trade count — metrics appear one by one."""
    print('  [scenes] rendering trust metrics clip…')
    snap  = _load_snapshot()
    acct  = snap.get('account', {})

    wr     = float(acct.get('winRate', 0))
    pf     = float(acct.get('profitFactor', 0))
    dd     = float(acct.get('drawdown', 0))
    trades = int(acct.get('trades', 0))
    pips   = int(acct.get('pips', 0))
    bal    = float(acct.get('balance', 0))

    # ── Static portrait matplotlib card ───────────────────────────────────────
    fig = plt.figure(figsize=(10.8, 19.2), dpi=100, facecolor=NAVY)
    ax  = fig.add_axes([0, 0, 1, 1], facecolor=NAVY)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

    ax.add_patch(patches.Rectangle((0, 0.979), 1, 0.021, fc=EMERALD, transform=ax.transAxes, zorder=10))
    ax.add_patch(patches.Rectangle((0, 0),     1, 0.008, fc=EMERALD, transform=ax.transAxes, zorder=10))
    ax.add_patch(patches.Circle((0.065, 0.962), 0.006, fc=EMERALD, transform=ax.transAxes, zorder=11))
    ax.text(0.085, 0.962, 'IC Markets Verified  ·  ASIC Regulated  ·  Myfxbook #12044019',
            fontsize=13, color=EMERALD, va='center', transform=ax.transAxes, fontfamily='monospace', zorder=11)

    ax.text(0.5, 0.930, 'TRUST METRICS', fontsize=42, color=WHITE, ha='center', va='center',
            transform=ax.transAxes, fontweight='black', zorder=11)
    ax.text(0.5, 0.900, 'VERIFIED LIVE  ·  NO FILTERS  ·  FULL DRAWDOWN SHOWN',
            fontsize=15, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold', zorder=11)
    ax.plot([0.06, 0.94], [0.886, 0.886], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)

    # ── Win rate big circle ───────────────────────────────────────────────────
    theta = np.linspace(np.pi / 2, np.pi / 2 - 2 * np.pi * (wr / 100), 200)
    ax.plot(0.5 + 0.26 * np.cos(np.linspace(0, 2 * np.pi, 100)),
            0.73 + 0.22 * np.sin(np.linspace(0, 2 * np.pi, 100)),
            color=NAVY_L, lw=18, solid_capstyle='round', transform=ax.transAxes, zorder=5)
    ax.plot(0.5 + 0.26 * np.cos(theta),
            0.73 + 0.22 * np.sin(theta),
            color=EMERALD, lw=18, solid_capstyle='round', transform=ax.transAxes, zorder=6)
    ax.text(0.5, 0.748, f'{wr:.1f}%', fontsize=58, fontweight='black', color=EMERALD,
            ha='center', va='center', transform=ax.transAxes, zorder=11)
    ax.text(0.5, 0.688, 'WIN RATE', fontsize=22, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold', zorder=11)

    ax.plot([0.06, 0.94], [0.656, 0.656], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)

    # ── 4 metric boxes ────────────────────────────────────────────────────────
    box_metrics = [
        ('PROFIT FACTOR', f'{pf:.2f}',     WHITE,   0.06, 0.576),
        ('DRAWDOWN',      f'{dd:.1f}%',    RED,     0.53, 0.576),
        ('TOTAL TRADES',  f'{trades:,}',   WHITE,   0.06, 0.452),
        ('TOTAL PIPS',    f'+{pips:,}',    EMERALD, 0.53, 0.452),
    ]
    for lbl, val, col, bx, by in box_metrics:
        ax.add_patch(patches.FancyBboxPatch((bx, by), 0.41, 0.106,
            boxstyle='round,pad=0.008', fc=NAVY_S, ec=EMERALD, lw=0.8,
            transform=ax.transAxes, zorder=7))
        ax.text(bx + 0.205, by + 0.072, val, fontsize=32, fontweight='black', color=col,
                ha='center', va='center', transform=ax.transAxes, zorder=11)
        ax.text(bx + 0.205, by + 0.024, lbl, fontsize=13, color=MUTED,
                ha='center', va='center', transform=ax.transAxes,
                fontfamily='monospace', zorder=11)

    ax.plot([0.06, 0.94], [0.432, 0.432], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)

    # Balance + CTA
    ax.text(0.5, 0.408, f'Current Balance: ${bal:,.0f}', fontsize=22, color=WHITE,
            ha='center', va='center', transform=ax.transAxes, fontweight='bold', zorder=11)
    ax.add_patch(patches.FancyBboxPatch((0.06, 0.34), 0.88, 0.054,
        boxstyle='round,pad=0.008', fc=EMERALD, ec='none',
        transform=ax.transAxes, zorder=7))
    ax.text(0.5, 0.367, 'Open a live account → icmarkets.com/?camp=91936',
            fontsize=15, color='#010E1F', ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold', zorder=11)

    ax.text(0.5, 0.310, 'Join Telegram for live alerts  →  t.me/pandiangk',
            fontsize=16, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, zorder=11)
    ax.text(0.5, 0.280, 'Follow @veralevel.fx for every trade update',
            fontsize=16, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, zorder=11)

    # Disclaimer
    ax.plot([0.06, 0.94], [0.032, 0.032], color=EMERALD, alpha=0.25, lw=1.0, transform=ax.transAxes)
    ax.text(0.5, 0.017, 'Not financial advice. Past performance does not guarantee future results.',
            fontsize=11, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)

    bg = _fig_to_arr(fig)

    def make_frame(t: float) -> np.ndarray:
        return _ken_burns_arr(bg, t, duration, zoom_start=1.05, zoom_end=1.0)

    return _write_to_mp4(make_frame, duration)
