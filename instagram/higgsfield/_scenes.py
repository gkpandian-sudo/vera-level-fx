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
import os
import tempfile
from datetime import date, datetime
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


def _recovery_day() -> int:
    """Days since RECOVERY_START (env, YYYY-MM-DD). 0 when unset/invalid."""
    rs = os.environ.get('RECOVERY_START', '')
    if not rs:
        return 0
    try:
        start = datetime.strptime(rs, '%Y-%m-%d').date()
        return max(1, (date.today() - start).days + 1)
    except Exception:
        return 0


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
    clip.write_videofile(
        tmp.name, codec='libx264', audio=False, logger=None,
        ffmpeg_params=['-pix_fmt', 'yuv420p'],
    )
    clip.close()
    return tmp.name


def _monthly_pnl(daily_gain: list) -> dict[str, float]:
    """Delegate to captions.monthly_pnl_from_daily — handles list-of-lists format."""
    from captions import monthly_pnl_from_daily
    return monthly_pnl_from_daily(daily_gain)


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

    # Recovery day badge — the rebuild story, only while the account is under water
    rec_day = _recovery_day()
    if rec_day > 0 and bal < 10000:
        ax.text(0.94, 0.900, f'REBUILD DAY {rec_day}/180',
                fontsize=17, fontweight='bold', color=RED, ha='right', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=11)

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

    # dailyGain rows are [date, cumulative_gain_%, profit_$] — d[1] is already cumulative
    cumulative = []
    for d in daily:
        try:
            cumulative.append(float(d[1] if isinstance(d, list) else d.get('value', 0)))
        except (ValueError, IndexError):
            pass
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

    # Lowest point of the curve — where the recovery story starts
    min_idx = int(np.argmin(cumulative))
    min_x   = cx0 + int(min_idx / max(n - 1, 1) * cw)
    min_y   = max(cy0, min(cy1, _val_to_px(cumulative[min_idx])))
    fonts   = _pil_font()

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

        # Subtle annotation at the lowest point once the reveal reaches it
        if n_show > min_idx and min_idx > 0:
            label, tx, anchor = 'Recovery started →', min_x - 18, 'rm'
            if tx < 360:   # too close to left edge — flip to the right side
                label, tx, anchor = '← Recovery started', min_x + 18, 'lm'
            ty = max(cy0 + 30, min_y - 28)
            draw.text((tx, ty), label, fill=_MUTED, font=fonts['xs'], anchor=anchor)

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

    ax.text(0.5, 0.310, "Comment BROKER → I'll DM you my IC Markets setup",
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


# ── Static PNG exports (used by Muapi I2V path) ───────────────────────────────

def make_performance_png() -> str:
    """Render the performance card as a static PNG with gain% at final value."""
    snap = _load_snapshot()
    acct = snap.get('account', {})
    daily = snap.get('dailyGain', [])

    gain   = float(acct.get('gain', 0))
    bal    = float(acct.get('balance', 0))
    wr     = float(acct.get('winRate', 0))
    pf     = float(acct.get('profitFactor', 0))
    dd     = float(acct.get('drawdown', 0))
    trades = int(acct.get('trades', 0))

    monthly = _monthly_pnl(daily)
    months  = sorted(monthly)[-9:]
    mvals   = [monthly[m] for m in months]
    mlabels = [m[5:] for m in months]

    fig = plt.figure(figsize=(10.8, 19.2), dpi=100, facecolor=NAVY)
    ax  = fig.add_axes([0, 0, 1, 1], facecolor=NAVY)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

    ax.add_patch(patches.Rectangle((0, 0.979), 1, 0.021, fc=EMERALD, transform=ax.transAxes, zorder=10))
    ax.add_patch(patches.Rectangle((0, 0),     1, 0.008, fc=EMERALD, transform=ax.transAxes, zorder=10))
    ax.add_patch(patches.Circle((0.065, 0.962), 0.006, fc=EMERALD, transform=ax.transAxes, zorder=11))
    ax.text(0.085, 0.962, 'IC Markets Verified  ·  ASIC Regulated  ·  Myfxbook #12044019',
            fontsize=13, color=EMERALD, va='center', transform=ax.transAxes, fontfamily='monospace', zorder=11)
    ax.text(0.06, 0.942, '@veralevel.fx  ·  LIVE PERFORMANCE CARD',
            fontsize=18, color=MUTED, va='center', transform=ax.transAxes,
            fontfamily='monospace', fontweight='bold', zorder=11)
    ax.plot([0.06, 0.94], [0.928, 0.928], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)
    ax.text(0.06, 0.900, 'TOTAL GAIN SINCE INCEPTION',
            fontsize=19, color=MUTED, va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=11)

    rec_day = _recovery_day()
    if rec_day > 0 and bal < 10000:
        ax.text(0.94, 0.900, f'REBUILD DAY {rec_day}/180',
                fontsize=17, fontweight='bold', color=RED, ha='right', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=11)

    ax.add_patch(patches.Rectangle((0.06, 0.720), 0.88, 0.168,
        fc='#051830', ec='none', transform=ax.transAxes, zorder=5))

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

    if mvals:
        chart_ax = fig.add_axes([0.07, 0.30, 0.86, 0.29])
        bar_cols = [EMERALD if v >= 0 else RED for v in mvals]
        chart_ax.bar(np.arange(len(mvals)), mvals, color=bar_cols, width=0.65)
        chart_ax.axhline(0, color=MUTED, linewidth=0.7, alpha=0.5)
        chart_ax.set_xticks(np.arange(len(mvals)))
        chart_ax.set_xticklabels(mlabels, color=MUTED, fontsize=11, fontfamily='monospace')
        chart_ax.set_facecolor(NAVY_S)
        for spine in chart_ax.spines.values():
            spine.set_color(EMERALD); spine.set_alpha(0.3)
        chart_ax.tick_params(colors=MUTED, length=3)
        chart_ax.yaxis.set_tick_params(labelcolor=MUTED, labelsize=11)

    ax.text(0.5, 0.278, f'{trades:,} trades  ·  All live  ·  Nothing hidden',
            fontsize=16, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)
    ax.plot([0.06, 0.94], [0.032, 0.032], color=EMERALD, alpha=0.25, lw=1.0, transform=ax.transAxes)
    ax.text(0.5, 0.017, 'Not financial advice. Past performance does not guarantee future results.',
            fontsize=11, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)

    bg    = _fig_to_arr(fig)
    fonts = _pil_font()

    sign  = '+' if gain >= 0 else ''
    color = _EMERALD if gain >= 0 else _RED
    img   = Image.fromarray(bg)
    draw  = ImageDraw.Draw(img)
    draw.text((540, 860), f'{sign}{gain:.1f}%', fill=color, font=fonts['xl'], anchor='mm')

    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    tmp.close()
    img.save(tmp.name, 'PNG')
    return tmp.name


def make_equity_png() -> str:
    """Render the equity curve card as a static PNG with the full curve drawn."""
    snap  = _load_snapshot()
    daily = snap.get('dailyGain', [])
    acct  = snap.get('account', {})
    gain  = float(acct.get('gain', 0))

    cumulative = []
    for d in daily:
        try:
            cumulative.append(float(d[1] if isinstance(d, list) else d.get('value', 0)))
        except (ValueError, IndexError):
            pass
    if not cumulative:
        cumulative = [0.0, gain]
    n = len(cumulative)
    min_v, max_v = min(cumulative), max(cumulative)
    val_range = max(max_v - min_v, 0.1)

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
    ax.add_patch(patches.FancyBboxPatch((0.04, 0.068), 0.92, 0.79,
        boxstyle='square', fc=NAVY_S, ec=EMERALD, lw=0.8,
        transform=ax.transAxes, zorder=4))

    gain_color = EMERALD if gain >= 0 else RED
    ax.text(0.96, 0.854, f'{gain:+.1f}%', fontsize=18, color=gain_color, ha='right', va='center',
            transform=ax.transAxes, fontweight='black', zorder=11)
    ax.text(0.96, 0.075, '0.0%', fontsize=14, color=MUTED, ha='right', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)
    ax.text(0.06, 0.050, 'Start', fontsize=12, color=MUTED, va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)
    ax.text(0.94, 0.050, f'Day {n}', fontsize=12, color=MUTED, ha='right', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)
    for frac in (0.25, 0.5, 0.75):
        y = 0.068 + frac * 0.79
        ax.plot([0.04, 0.96], [y, y], color=MUTED, alpha=0.10, lw=0.8, transform=ax.transAxes)
    ax.plot([0.06, 0.94], [0.032, 0.032], color=EMERALD, alpha=0.25, lw=1.0, transform=ax.transAxes)
    ax.text(0.5, 0.017, 'Not financial advice. Past performance does not guarantee future results.',
            fontsize=11, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)

    bg    = _fig_to_arr(fig)
    fonts = _pil_font()

    cx0 = int(0.04 * _W); cx1 = int(0.96 * _W)
    cy0 = int((1 - 0.858) * _H); cy1 = int((1 - 0.068) * _H)
    cw  = cx1 - cx0;             ch  = cy1 - cy0

    def _val_to_px(v: float) -> int:
        return int(cy1 - (v - min_v) / val_range * ch)

    img  = Image.fromarray(bg)
    draw = ImageDraw.Draw(img)

    pts = []
    for i in range(n):
        x = cx0 + int(i / max(n - 1, 1) * cw)
        y = max(cy0, min(cy1, _val_to_px(cumulative[i])))
        pts.append((x, y))

    if len(pts) >= 2:
        last_val = cumulative[-1]
        col = _EMERALD if last_val >= 0 else _RED
        draw.line(pts, fill=col, width=5)
        lx, ly = pts[-1]
        draw.ellipse([(lx - 9, ly - 9), (lx + 9, ly + 9)], fill=col)

    min_idx = int(np.argmin(cumulative))
    if min_idx > 0:
        min_x = cx0 + int(min_idx / max(n - 1, 1) * cw)
        min_y = max(cy0, min(cy1, _val_to_px(cumulative[min_idx])))
        label, tx, anchor = 'Recovery started →', min_x - 18, 'rm'
        if tx < 360:
            label, tx, anchor = '← Recovery started', min_x + 18, 'lm'
        ty = max(cy0 + 30, min_y - 28)
        draw.text((tx, ty), label, fill=_MUTED, font=fonts['xs'], anchor=anchor)

    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    tmp.close()
    img.save(tmp.name, 'PNG')
    return tmp.name


# ── Path E: Programmatic motion graphics (free, deterministic) ───────────────
#
# Animate trading data directly in PIL/NumPy — bars grow, arc sweeps, curve
# draws itself with fill — no AI service required.
# Triggered by MOTION_GRAPHICS=1 env var via _avatar_gemini.py.

def make_performance_clip_motion(duration: float = 15.0) -> str:
    """Performance card: gain% counter + sequential bar growth + sub-metric counts."""
    print('  [scenes] rendering performance clip (motion)…')
    snap  = _load_snapshot()
    acct  = snap.get('account', {})
    daily = snap.get('dailyGain', [])

    gain   = float(acct.get('gain', 0))
    bal    = float(acct.get('balance', 0))
    wr     = float(acct.get('winRate', 0))
    pf     = float(acct.get('profitFactor', 0))
    dd     = float(acct.get('drawdown', 0))
    trades = int(acct.get('trades', 0))

    monthly = _monthly_pnl(daily)
    months  = sorted(monthly)[-9:]
    mvals   = [monthly[m] for m in months]
    mlabels = [m[5:] for m in months]

    fig = plt.figure(figsize=(10.8, 19.2), dpi=100, facecolor=NAVY)
    ax  = fig.add_axes([0, 0, 1, 1], facecolor=NAVY)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

    ax.add_patch(patches.Rectangle((0, 0.979), 1, 0.021, fc=EMERALD, transform=ax.transAxes, zorder=10))
    ax.add_patch(patches.Rectangle((0, 0),     1, 0.008, fc=EMERALD, transform=ax.transAxes, zorder=10))
    ax.add_patch(patches.Circle((0.065, 0.962), 0.006, fc=EMERALD, transform=ax.transAxes, zorder=11))
    ax.text(0.085, 0.962, 'IC Markets Verified  ·  ASIC Regulated  ·  Myfxbook #12044019',
            fontsize=13, color=EMERALD, va='center', transform=ax.transAxes, fontfamily='monospace', zorder=11)
    ax.text(0.06, 0.942, '@veralevel.fx  ·  LIVE PERFORMANCE CARD',
            fontsize=18, color=MUTED, va='center', transform=ax.transAxes,
            fontfamily='monospace', fontweight='bold', zorder=11)
    ax.plot([0.06, 0.94], [0.928, 0.928], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)
    ax.text(0.06, 0.900, 'TOTAL GAIN SINCE INCEPTION',
            fontsize=19, color=MUTED, va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=11)

    rec_day = _recovery_day()
    if rec_day > 0 and bal < 10000:
        ax.text(0.94, 0.900, f'REBUILD DAY {rec_day}/180',
                fontsize=17, fontweight='bold', color=RED, ha='right', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=11)

    ax.add_patch(patches.Rectangle((0.06, 0.720), 0.88, 0.168,
        fc='#051830', ec='none', transform=ax.transAxes, zorder=5))

    ax.plot([0.06, 0.94], [0.714, 0.714], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)
    for lbl, px in [('WIN RATE', 0.18), ('PROF.FACTOR', 0.45), ('BALANCE', 0.72), ('DRAWDOWN', 0.91)]:
        ax.text(px, 0.663, lbl, fontsize=11, color=MUTED, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=11)

    ax.plot([0.06, 0.94], [0.648, 0.648], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)
    ax.text(0.5, 0.628, 'MONTHLY P&L BREAKDOWN', fontsize=17, color=MUTED, ha='center',
            va='center', transform=ax.transAxes, fontfamily='monospace', zorder=11)

    ax.add_patch(patches.FancyBboxPatch((0.06, 0.305), 0.88, 0.28,
        boxstyle='square', fc=NAVY_S, ec=EMERALD, lw=0.6,
        transform=ax.transAxes, zorder=4))

    if mvals:
        m_min0 = min(0.0, min(mvals)); m_max0 = max(0.0, max(mvals))
        pad0   = max(abs(m_min0), abs(m_max0)) * 0.15 or 1.0
        zero_f = (0 - (m_min0 - pad0)) / ((m_max0 + pad0) - (m_min0 - pad0))
        ax.plot([0.06, 0.94], [0.305 + zero_f * 0.28] * 2,
                color=MUTED, alpha=0.35, lw=0.8, transform=ax.transAxes)

    ax.text(0.5, 0.278, f'{trades:,} trades  ·  All live  ·  Nothing hidden',
            fontsize=16, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)
    ax.plot([0.06, 0.94], [0.032, 0.032], color=EMERALD, alpha=0.25, lw=1.0, transform=ax.transAxes)
    ax.text(0.5, 0.017, 'Not financial advice. Past performance does not guarantee future results.',
            fontsize=11, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)

    bg    = _fig_to_arr(fig)
    fonts = _pil_font()

    cx0 = int(0.06 * _W);  cx1 = int(0.94 * _W)
    cy0 = int((1 - 0.585) * _H);  cy1 = int((1 - 0.305) * _H)
    cw  = cx1 - cx0;  ch = cy1 - cy0

    if mvals:
        m_min = min(0.0, min(mvals)); m_max = max(0.0, max(mvals))
        pad   = max(abs(m_min), abs(m_max)) * 0.15 or 1.0
        y_lo  = m_min - pad;  y_hi = m_max + pad;  y_rng = y_hi - y_lo

        def _bpy(v):
            return int(cy1 - (v - y_lo) / y_rng * ch)

        zero_py = _bpy(0)
        n_bars  = len(mvals)
        bar_w   = max(4, int(cw / (n_bars + 1) * 0.60))
        bar_cxs = [cx0 + int((i + 0.5) / n_bars * cw) for i in range(n_bars)]
    else:
        n_bars = 0; zero_py = cy1; bar_w = 10; bar_cxs = []
        def _bpy(v): return cy1

    sub_xs = [int(p * _W) for p in (0.18, 0.45, 0.72, 0.91)]
    sub_y  = int(0.688 * _H)

    def make_frame(t: float) -> np.ndarray:
        p   = t / duration
        img = Image.fromarray(bg.copy())
        d   = ImageDraw.Draw(img)

        gp = min(p / 0.50, 1.0); ge = gp * gp * (3 - 2 * gp)
        cg = gain * ge
        d.text((540, 860), f'{"+" if cg >= 0 else ""}{cg:.1f}%',
               fill=(_EMERALD if cg >= 0 else _RED), font=fonts['xl'], anchor='mm')

        sp = max(0.0, min((p - 0.40) / 0.32, 1.0)); se = sp * sp * (3 - 2 * sp)
        for x_px, val_str, col in [
            (sub_xs[0], f'{wr * se:.1f}%',   _WHITE),
            (sub_xs[1], f'{pf * se:.2f}',     _WHITE),
            (sub_xs[2], f'${bal * se:,.0f}',  _WHITE),
            (sub_xs[3], f'{dd * se:.1f}%',    _RED),
        ]:
            d.text((x_px, sub_y), val_str, fill=col, font=fonts['sm'], anchor='mm')

        if n_bars:
            bp = max(0.0, (p - 0.62) / 0.38)
            for i, (bx, bv) in enumerate(zip(bar_cxs, mvals)):
                bl = max(0.0, min((bp - i / n_bars) * n_bars, 1.0))
                be = bl * bl * (3 - 2 * bl)
                top = _bpy(bv * be); bc = _EMERALD if bv >= 0 else _RED
                x0b = bx - bar_w // 2;  x1b = bx + bar_w // 2
                if bv >= 0:
                    d.rectangle([x0b, top, x1b, zero_py], fill=bc)
                else:
                    d.rectangle([x0b, zero_py, x1b, top], fill=bc)
                d.text((bx, cy1 + 20), mlabels[i], fill=_MUTED, font=fonts['xs'], anchor='mm')

        return np.array(img)

    return _write_to_mp4(make_frame, duration)


def make_equity_clip_motion(duration: float = 12.0) -> str:
    """Equity curve drawing itself with dimmed fill polygon and live value label."""
    print('  [scenes] rendering equity clip (motion)…')
    snap  = _load_snapshot()
    daily = snap.get('dailyGain', [])
    acct  = snap.get('account', {})
    gain  = float(acct.get('gain', 0))

    cumulative = []
    for row in daily:
        try:
            cumulative.append(float(row[1] if isinstance(row, list) else row.get('value', 0)))
        except (ValueError, IndexError):
            pass
    if not cumulative:
        cumulative = [0.0, gain]
    n     = len(cumulative)
    min_v = min(cumulative); max_v = max(cumulative)
    val_r = max(max_v - min_v, 0.1)

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
    ax.add_patch(patches.FancyBboxPatch((0.04, 0.068), 0.92, 0.79,
        boxstyle='square', fc=NAVY_S, ec=EMERALD, lw=0.8,
        transform=ax.transAxes, zorder=4))
    g_col = EMERALD if gain >= 0 else RED
    ax.text(0.96, 0.854, f'{gain:+.1f}%', fontsize=18, color=g_col, ha='right', va='center',
            transform=ax.transAxes, fontweight='black', zorder=11)
    ax.text(0.96, 0.075, '0.0%', fontsize=14, color=MUTED, ha='right', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)
    ax.text(0.06, 0.050, 'Start', fontsize=12, color=MUTED, va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)
    ax.text(0.94, 0.050, f'Day {n}', fontsize=12, color=MUTED, ha='right', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)
    for frac in (0.25, 0.5, 0.75):
        ax.plot([0.04, 0.96], [0.068 + frac * 0.79] * 2,
                color=MUTED, alpha=0.10, lw=0.8, transform=ax.transAxes)
    ax.plot([0.06, 0.94], [0.032, 0.032], color=EMERALD, alpha=0.25, lw=1.0, transform=ax.transAxes)
    ax.text(0.5, 0.017, 'Not financial advice. Past performance does not guarantee future results.',
            fontsize=11, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)

    bg = _fig_to_arr(fig)

    cx0 = int(0.04 * _W);  cx1 = int(0.96 * _W)
    cy0 = int((1 - 0.858) * _H);  cy1 = int((1 - 0.068) * _H)
    cw  = cx1 - cx0;  ch = cy1 - cy0

    def _vpx(v):
        return int(cy1 - (v - min_v) / val_r * ch)

    zero_py = max(cy0, min(cy1, _vpx(0)))
    min_idx = int(np.argmin(cumulative))
    min_x   = cx0 + int(min_idx / max(n - 1, 1) * cw)
    min_y   = max(cy0, min(cy1, _vpx(cumulative[min_idx])))
    fonts   = _pil_font()
    _FILL_POS = (3,  70, 50)
    _FILL_NEG = (90, 12, 12)

    def make_frame(t: float) -> np.ndarray:
        progress = min(t / (duration * 0.88), 1.0)
        n_show   = max(2, int(n * progress))

        img  = Image.fromarray(bg.copy())
        draw = ImageDraw.Draw(img)

        pts = []
        for i in range(n_show):
            x = cx0 + int(i / max(n - 1, 1) * cw)
            y = max(cy0, min(cy1, _vpx(cumulative[i])))
            pts.append((x, y))

        if len(pts) >= 2:
            last_val = cumulative[n_show - 1]
            lc   = _EMERALD if last_val >= 0 else _RED
            fill = _FILL_POS  if last_val >= 0 else _FILL_NEG

            fill_poly = list(pts) + [(pts[-1][0], zero_py), (pts[0][0], zero_py)]
            draw.polygon(fill_poly, fill=fill)
            draw.line(pts, fill=lc, width=5)

            lx, ly = pts[-1]
            draw.ellipse([(lx - 10, ly - 10), (lx + 10, ly + 10)], fill=lc)

            lv  = cumulative[n_show - 1]
            lbl = f'{"+" if lv >= 0 else ""}{lv:.1f}%'
            tx  = min(lx + 18, cx1 - 100)
            ty  = max(cy0 + 22, min(ly - 22, cy1 - 22))
            draw.text((tx, ty), lbl, fill=lc, font=fonts['sm'], anchor='lm')

        if n_show > min_idx and min_idx > 0:
            rlbl, tx2, anc = 'Recovery started →', min_x - 18, 'rm'
            if tx2 < 360:
                rlbl, tx2, anc = '← Recovery started', min_x + 18, 'lm'
            ty2 = max(cy0 + 30, min_y - 28)
            draw.text((tx2, ty2), rlbl, fill=_MUTED, font=fonts['xs'], anchor=anc)

        return np.array(img)

    return _write_to_mp4(make_frame, duration)


def make_trust_clip_motion(duration: float = 15.0) -> str:
    """Trust metrics: animated arc filling from 0 to win rate + sequential metric reveal."""
    print('  [scenes] rendering trust clip (motion)…')
    snap  = _load_snapshot()
    acct  = snap.get('account', {})

    wr     = float(acct.get('winRate', 0))
    pf     = float(acct.get('profitFactor', 0))
    dd     = float(acct.get('drawdown', 0))
    trades = int(acct.get('trades', 0))
    pips   = int(acct.get('pips', 0))
    bal    = float(acct.get('balance', 0))

    # Static base — header, box outlines + labels; arc and metric values in PIL per-frame
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

    # Arc area is clear (arc drawn per-frame); separator below it is static
    ax.plot([0.06, 0.94], [0.656, 0.656], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)

    for lbl, bx, by in [('PROFIT FACTOR', 0.06, 0.576), ('DRAWDOWN', 0.53, 0.576),
                         ('TOTAL TRADES',  0.06, 0.452), ('TOTAL PIPS', 0.53, 0.452)]:
        ax.add_patch(patches.FancyBboxPatch((bx, by), 0.41, 0.106,
            boxstyle='round,pad=0.008', fc=NAVY_S, ec=EMERALD, lw=0.8,
            transform=ax.transAxes, zorder=7))
        ax.text(bx + 0.205, by + 0.024, lbl, fontsize=13, color=MUTED,
                ha='center', va='center', transform=ax.transAxes,
                fontfamily='monospace', zorder=11)

    ax.plot([0.06, 0.94], [0.432, 0.432], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)
    ax.text(0.5, 0.408, f'Current Balance: ${bal:,.0f}', fontsize=22, color=WHITE,
            ha='center', va='center', transform=ax.transAxes, fontweight='bold', zorder=11)
    ax.add_patch(patches.FancyBboxPatch((0.06, 0.34), 0.88, 0.054,
        boxstyle='round,pad=0.008', fc=EMERALD, ec='none',
        transform=ax.transAxes, zorder=7))
    ax.text(0.5, 0.367, 'Open a live account → icmarkets.com/?camp=91936',
            fontsize=15, color='#010E1F', ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold', zorder=11)
    ax.text(0.5, 0.310, "Comment BROKER → I'll DM you my IC Markets setup",
            fontsize=16, color=MUTED, ha='center', va='center', transform=ax.transAxes, zorder=11)
    ax.text(0.5, 0.280, 'Follow @veralevel.fx for every trade update',
            fontsize=16, color=MUTED, ha='center', va='center', transform=ax.transAxes, zorder=11)
    ax.plot([0.06, 0.94], [0.032, 0.032], color=EMERALD, alpha=0.25, lw=1.0, transform=ax.transAxes)
    ax.text(0.5, 0.017, 'Not financial advice. Past performance does not guarantee future results.',
            fontsize=11, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)

    bg    = _fig_to_arr(fig)
    fonts = _pil_font()

    # Arc fits within the separator zone: y=0.886→218px from top to y=0.656→660px from top
    # A circular arc (rx==ry) centred in that 442px window avoids spilling into the header
    # or the metric boxes below.
    arc_cx   = 540
    arc_cy   = 439             # midpoint of 218–660 zone
    arc_rx   = 190
    arc_ry   = 190             # circle, not ellipse
    arc_bb   = [arc_cx - arc_rx, arc_cy - arc_ry, arc_cx + arc_rx, arc_cy + arc_ry]
    arc_lw   = 20
    wr_val_y = arc_cy - 20    # slightly above centre
    wr_lbl_y = arc_cy + 62    # below centre
    _NAVY_L_PIL = (10, 37, 69)

    # Metric value centres: box at (bx, by, 0.41, 0.106) → value at (bx+0.205, by+0.072)
    metric_data = [
        (pf,     lambda v: f'{v:.2f}',     _WHITE,   int((0.06+0.205)*_W), int((1-0.648)*_H), 0.42),
        (dd,     lambda v: f'{v:.1f}%',    _RED,     int((0.53+0.205)*_W), int((1-0.648)*_H), 0.55),
        (trades, lambda v: f'{int(v):,}',  _WHITE,   int((0.06+0.205)*_W), int((1-0.524)*_H), 0.68),
        (pips,   lambda v: f'+{int(v):,}', _EMERALD, int((0.53+0.205)*_W), int((1-0.524)*_H), 0.81),
    ]

    def make_frame(t: float) -> np.ndarray:
        p   = t / duration
        img = Image.fromarray(bg.copy())
        d   = ImageDraw.Draw(img)

        # Phase 1 (0–40%): arc sweeps clockwise from top
        arc_p = min(p / 0.40, 1.0);  arc_e = arc_p * arc_p * (3 - 2 * arc_p)
        wr_now = wr * arc_e
        d.arc(arc_bb, start=0, end=360, fill=_NAVY_L_PIL, width=arc_lw)
        if wr_now > 0.1:
            d.arc(arc_bb, start=270, end=int(270 + wr_now / 100 * 360), fill=_EMERALD, width=arc_lw)
        d.text((arc_cx, wr_val_y), f'{wr_now:.1f}%', fill=_EMERALD, font=fonts['lg'], anchor='mm')
        d.text((arc_cx, wr_lbl_y), 'WIN RATE',       fill=_MUTED,   font=fonts['sm'], anchor='mm')

        # Phase 2 (42–95%): metric boxes count up one by one
        for final_val, fmt_fn, col, mx, my, sf in metric_data:
            mp = max(0.0, min((p - sf) / 0.18, 1.0));  me = mp * mp * (3 - 2 * mp)
            d.text((mx, my), fmt_fn(final_val * me), fill=col, font=fonts['md'], anchor='mm')

        return np.array(img)

    return _write_to_mp4(make_frame, duration)


# ── Static PNG exports (used by Muapi I2V path) ───────────────────────────────

def make_trust_png() -> str:
    """Render the trust metrics card as a static PNG (matplotlib card is already complete)."""
    snap = _load_snapshot()
    acct = snap.get('account', {})

    wr     = float(acct.get('winRate', 0))
    pf     = float(acct.get('profitFactor', 0))
    dd     = float(acct.get('drawdown', 0))
    trades = int(acct.get('trades', 0))
    pips   = int(acct.get('pips', 0))
    bal    = float(acct.get('balance', 0))

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
                ha='center', va='center', transform=ax.transAxes, fontfamily='monospace', zorder=11)

    ax.plot([0.06, 0.94], [0.432, 0.432], color=EMERALD, alpha=0.4, lw=1.5, transform=ax.transAxes)
    ax.text(0.5, 0.408, f'Current Balance: ${bal:,.0f}', fontsize=22, color=WHITE,
            ha='center', va='center', transform=ax.transAxes, fontweight='bold', zorder=11)
    ax.add_patch(patches.FancyBboxPatch((0.06, 0.34), 0.88, 0.054,
        boxstyle='round,pad=0.008', fc=EMERALD, ec='none',
        transform=ax.transAxes, zorder=7))
    ax.text(0.5, 0.367, 'Open a live account → icmarkets.com/?camp=91936',
            fontsize=15, color='#010E1F', ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold', zorder=11)
    ax.text(0.5, 0.310, "Comment BROKER → I'll DM you my IC Markets setup",
            fontsize=16, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, zorder=11)
    ax.text(0.5, 0.280, 'Follow @veralevel.fx for every trade update',
            fontsize=16, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, zorder=11)
    ax.plot([0.06, 0.94], [0.032, 0.032], color=EMERALD, alpha=0.25, lw=1.0, transform=ax.transAxes)
    ax.text(0.5, 0.017, 'Not financial advice. Past performance does not guarantee future results.',
            fontsize=11, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=11)

    tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    tmp.close()
    Image.fromarray(_fig_to_arr(fig)).save(tmp.name, 'PNG')
    return tmp.name
