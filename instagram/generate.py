"""
generate.py — Weekly, Monthly and Trust card renderers.
1080×1080 @ 100 DPI.  Mobile-first font sizing.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime

# ── Brand palette ─────────────────────────────────────────────────
NAVY   = '#010E1F'
NAVY_S = '#051830'
NAVY_L = '#0A2545'
GOLD   = '#F0C040'
GOLD_B = '#FFD060'
WHITE  = '#FFFFFF'
CREAM  = '#F0EEE8'
MUTED  = '#B8CFEA'
DIM    = '#6A8EB8'
GREEN  = '#00E096'
RED    = '#FF6B6B'
AMBER  = '#FFA040'

SIZE = (10.8, 10.8)
DPI  = 100


def _base(nrows=1, ncols=1):
    fig = plt.figure(figsize=SIZE, facecolor=NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    return fig, ax


def _hline(ax, y, x0=0.06, x1=0.94, color=GOLD, alpha=0.45, lw=1.5):
    ax.plot([x0, x1], [y, y], color=color, linewidth=lw,
            alpha=alpha, transform=ax.transAxes)


def _header(ax):
    ax.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026, facecolor=GOLD, transform=ax.transAxes, zorder=5
    ))
    ax.text(0.5, 0.946, 'VERA LEVEL FX',
            fontsize=22, fontweight='bold', color=GOLD, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    ax.text(0.5, 0.916, 'ALGORITHMIC FOREX  ·  IC MARKETS  ·  MYFXBOOK VERIFIED',
            fontsize=15, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    _hline(ax, 0.898, alpha=0.4)


def _footer(ax):
    _hline(ax, 0.095, alpha=0.4)
    ax.text(0.06, 0.065, '@veralevel.fx  ·  VERA LEVEL FX',
            fontsize=15, color=GOLD, va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold')
    ax.text(0.94, 0.065, 'IC MARKETS · ASIC',
            fontsize=15, color=MUTED, va='center', ha='right',
            transform=ax.transAxes, fontfamily='monospace')
    ax.text(0.5, 0.030, f'Not financial advice  ·  {os.environ.get("BRAND_DOMAIN", "veralevelFX")}',
            fontsize=18, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')


def _metric_card(ax, x, y, w, h, label, value, color, sub=''):
    ax.add_patch(patches.FancyBboxPatch(
        (x, y), w, h, boxstyle='round,pad=0.006',
        facecolor=NAVY_S, edgecolor=color, linewidth=1.2,
        transform=ax.transAxes, zorder=2
    ))
    ax.add_patch(patches.Rectangle(
        (x, y + h - 0.005), w, 0.005,
        facecolor=color, transform=ax.transAxes, zorder=3
    ))
    pad = 0.020
    ax.text(x + pad, y + h - 0.022, label,
            fontsize=20, color=MUTED, va='top', transform=ax.transAxes,
            fontfamily='monospace', fontweight='bold')
    ax.text(x + pad, y + h * 0.42, value,
            fontsize=36, color=color, va='center', transform=ax.transAxes,
            fontweight='bold')
    if sub:
        ax.text(x + pad, y + 0.016, sub,
                fontsize=18, color=DIM, va='bottom', transform=ax.transAxes,
                fontfamily='monospace')


# ── Weekly Performance Card ──────────────────────────────────────

def make_weekly_card(data):
    from instagram.composer import load_background, gradient_panel
    from pathlib import Path

    account  = data.get('account', {})
    balance  = account.get('balance', 0)
    gain     = account.get('gain', 0)
    monthly  = account.get('monthly', 0)
    win_rate = account.get('winRate', 0)
    pf       = account.get('profitFactor', 0)
    dd       = account.get('drawdown', 0)
    pips     = int(account.get('pips', 0))
    trades   = int(account.get('trades', 0))

    bg_path = Path(__file__).parent / 'assets' / 'bg-weekly.jpg'
    bg = gradient_panel(load_background(bg_path), height_frac=0.52)

    fig = plt.figure(figsize=SIZE, facecolor=NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.imshow(bg, extent=[0, 1, 0, 1], aspect='auto', zorder=0)

    gain_color = GREEN if gain >= 0 else RED
    gain_sign  = '+' if gain >= 0 else ''

    # Gold top bar
    ax.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026, facecolor=GOLD, transform=ax.transAxes, zorder=5
    ))

    # Account name
    ax.text(0.06, 0.946, 'VERA LEVEL FX',
            fontsize=20, fontweight='bold', color=GOLD,
            ha='left', va='center', transform=ax.transAxes, zorder=6)

    # Verified badge
    ax.add_patch(patches.FancyBboxPatch(
        (0.06, 0.910), 0.50, 0.026, boxstyle='round,pad=0.004',
        facecolor=(240/255, 192/255, 64/255, 0.12),
        edgecolor=(240/255, 192/255, 64/255, 0.4), linewidth=0.8,
        transform=ax.transAxes, zorder=5
    ))
    ax.add_patch(patches.Circle((0.075, 0.923), 0.007,
        facecolor=GREEN, transform=ax.transAxes, zorder=6))
    ax.text(0.090, 0.923, 'IC Markets Verified  ·  ASIC Regulated',
            fontsize=14, color=GOLD, ha='left', va='center',
            transform=ax.transAxes, zorder=6)

    # Post type label
    ax.text(0.06, 0.868,
            f'WEEKLY PERFORMANCE  ·  {datetime.now().strftime("%d %B %Y").upper()}',
            fontsize=16, color=MUTED, ha='left', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Hero: gain %
    ax.text(0.06, 0.810, f'{gain_sign}{gain:.1f}%',
            fontsize=88, fontweight='black', color=gain_color,
            ha='left', va='center', transform=ax.transAxes,
            linespacing=1.0, zorder=6)
    ax.text(0.06, 0.760, 'Total gain since inception',
            fontsize=20, color=MUTED, ha='left', va='center',
            transform=ax.transAxes, zorder=6)

    _hline(ax, 0.740, alpha=0.3)

    # 4-stat row
    stats = [
        (f'${balance:,.0f}',   'BALANCE',   GOLD),
        (f'{win_rate:.0f}%',   'WIN RATE',  WHITE),
        (f'+{pips:,}',         'PIPS',      GREEN),
        (f'{trades:,}',        'TRADES',    MUTED),
    ]
    col_w = 0.22
    for i, (val, lbl, color) in enumerate(stats):
        cx = 0.06 + i * col_w
        ax.text(cx, 0.700, val,
                fontsize=30, fontweight='black', color=color,
                ha='left', va='center', transform=ax.transAxes, zorder=6)
        ax.text(cx, 0.668, lbl,
                fontsize=14, color=DIM, ha='left', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Risk row
    ax.text(0.06, 0.630,
            f'Profit Factor {pf:.2f}  ·  Drawdown {dd:.1f}%  ·  1% max risk per trade',
            fontsize=16, color=DIM, ha='left', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # CTA
    _hline(ax, 0.595, alpha=0.25)
    ax.text(0.06, 0.568, 'Open your IC Markets account — same broker I use:',
            fontsize=17, color=MUTED, ha='left', va='center',
            transform=ax.transAxes, zorder=6)
    ax.text(0.06, 0.542, 'icmarkets.com/?camp=91936',
            fontsize=19, fontweight='bold', color=GOLD,
            ha='left', va='center', transform=ax.transAxes, zorder=6)

    # Footer
    _hline(ax, 0.095, alpha=0.3)
    ax.text(0.94, 0.065, '@veralevel.fx  ·  VERA LEVEL FX',
            fontsize=15, color=GOLD, va='center', ha='right',
            transform=ax.transAxes, fontweight='bold', zorder=6)
    ax.text(0.94, 0.030, 'Not financial advice',
            fontsize=14, color=DIM, ha='right', va='center',
            transform=ax.transAxes, zorder=6)

    return fig


# ── Monthly P&L Chart ────────────────────────────────────────────

def make_monthly_chart(data):
    daily = data.get('dailyGain', [])

    monthly_pnl = {}
    for item in daily:
        date_s = item[0] if isinstance(item, list) else item.get('date', '')
        val    = item[1] if isinstance(item, list) else item.get('value', 0)
        try:
            dt  = datetime.fromisoformat(str(date_s)[:10])
            key = dt.strftime('%b %y')
            monthly_pnl[key] = monthly_pnl.get(key, 0) + float(val)
        except Exception:
            pass

    keys = list(monthly_pnl.keys())[-12:]
    vals = [monthly_pnl[k] for k in keys]

    fig = plt.figure(figsize=SIZE, facecolor=NAVY)
    ax_bg = fig.add_axes([0, 0, 1, 1], facecolor=NAVY)
    ax_bg.set_xlim(0, 1); ax_bg.set_ylim(0, 1); ax_bg.axis('off')

    _header(ax_bg)
    ax_bg.text(0.5, 0.848, 'Monthly P&L',
               fontsize=48, fontweight='bold', color=WHITE,
               ha='center', va='center', transform=ax_bg.transAxes, fontstyle='italic')
    ax_bg.text(0.5, 0.812, '12-MONTH ROLLING BREAKDOWN',
               fontsize=22, color=MUTED, ha='center', va='center',
               transform=ax_bg.transAxes, fontfamily='monospace')
    ax_bg.plot([0.06, 0.94], [0.792, 0.792], color=GOLD, linewidth=1.5,
               alpha=0.45, transform=ax_bg.transAxes)

    ax = fig.add_axes([0.06, 0.130, 0.88, 0.645], facecolor=NAVY_L)
    for spine in ax.spines.values():
        spine.set_color(GOLD); spine.set_alpha(0.3)
    ax.tick_params(colors=MUTED, labelsize=16)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GOLD, alpha=0.08, linewidth=0.6)
    ax.xaxis.grid(False)

    x      = np.arange(len(keys))
    colors = [GREEN if v >= 0 else RED for v in vals]
    bars   = ax.bar(x, vals, color=colors, width=0.64, alpha=0.88, zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(keys, fontsize=15, color=MUTED, fontfamily='monospace')
    ax.tick_params(axis='y', labelcolor=MUTED, labelsize=15)
    ax.axhline(y=0, color=GOLD, linewidth=1.0, alpha=0.5)

    vmax = max(abs(v) for v in vals) if vals else 1
    for bar_r, val in zip(bars, vals):
        offset = vmax * 0.05
        ypos   = bar_r.get_height() + (offset if val >= 0 else -offset)
        ax.text(bar_r.get_x() + bar_r.get_width() / 2, ypos,
                f'{val:+.1f}%',
                ha='center', va='bottom' if val >= 0 else 'top',
                fontsize=13, color=GREEN if val >= 0 else RED,
                fontweight='bold', fontfamily='monospace')

    _footer(ax_bg)
    return fig


# ── Win Rate / Trust Card ────────────────────────────────────────

def make_winrate_card(data):
    from instagram.composer import load_background, vignette
    from pathlib import Path

    account  = data.get('account', {})
    win_rate = account.get('winRate', 0)
    pf       = account.get('profitFactor', 0)
    gain     = account.get('gain', 0)
    trades   = int(account.get('trades', 0))
    pips     = int(account.get('pips', 0))
    balance  = account.get('balance', 0)
    gain_sign = '+' if gain >= 0 else ''

    # Full-bleed background with vignette
    bg_path = Path(__file__).parent / 'assets' / 'bg-trust.jpg'
    bg = vignette(load_background(bg_path), strength=0.68)

    fig = plt.figure(figsize=SIZE, facecolor=NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.imshow(bg, extent=[0, 1, 0, 1], aspect='auto', zorder=0)

    # IC Markets Verified badge (top-centre)
    ax.add_patch(patches.FancyBboxPatch(
        (0.22, 0.915), 0.56, 0.034, boxstyle='round,pad=0.010',
        facecolor=(240/255, 192/255, 64/255, 0.10),
        edgecolor=(240/255, 192/255, 64/255, 0.35), linewidth=1.0,
        transform=ax.transAxes, zorder=5
    ))
    ax.add_patch(patches.Circle(
        (0.285, 0.932), 0.008,
        facecolor=GREEN, transform=ax.transAxes, zorder=6
    ))
    ax.text(0.5, 0.932, 'IC Markets Verified  ·  ASIC Regulated',
            fontsize=16, color=GOLD, fontweight='bold',
            ha='center', va='center', transform=ax.transAxes, zorder=7)

    # Post type label (gold pill)
    ax.add_patch(patches.FancyBboxPatch(
        (0.32, 0.858), 0.36, 0.034, boxstyle='round,pad=0.010',
        facecolor=(240/255, 192/255, 64/255, 0.85), edgecolor='none',
        transform=ax.transAxes, zorder=5
    ))
    ax.text(0.5, 0.875, 'LIVE TRACK RECORD',
            fontsize=14, fontweight='black', color=NAVY,
            ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Hero: win rate %
    ax.text(0.5, 0.690, f'{win_rate:.0f}%',
            fontsize=110, fontweight='black', color=WHITE,
            ha='center', va='center', transform=ax.transAxes, zorder=6)
    ax.text(0.5, 0.590, f'WIN RATE  ·  {trades:,} TRADES',
            fontsize=20, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Pill stats row
    pills = [
        (f'${balance:,.0f} Balance', 0.14),
        (f'{gain_sign}{gain:.1f}% Gain', 0.40),
        (f'+{pips:,} Pips', 0.66),
    ]
    pill_y = 0.515
    pill_w = 0.22
    for label, px in pills:
        ax.add_patch(patches.FancyBboxPatch(
            (px, pill_y), pill_w, 0.034, boxstyle='round,pad=0.008',
            facecolor=(1, 1, 1, 0.08), edgecolor=(1, 1, 1, 0.18), linewidth=0.8,
            transform=ax.transAxes, zorder=5
        ))
        ax.text(px + pill_w / 2, pill_y + 0.017, label,
                fontsize=15, color=WHITE, ha='center', va='center',
                transform=ax.transAxes, zorder=6)

    # Profit factor
    ax.text(0.5, 0.462,
            f'Profit Factor {pf:.2f}  ·  1% max risk per trade',
            fontsize=17, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # CTAs
    _hline(ax, 0.420, alpha=0.2)
    ax.text(0.5, 0.388,
            'Verify every trade yourself  →  Myfxbook.com',
            fontsize=17, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, zorder=6)
    ax.text(0.5, 0.355,
            'Open IC Markets  →  icmarkets.com/?camp=91936',
            fontsize=18, fontweight='bold', color=GOLD,
            ha='center', va='center', transform=ax.transAxes, zorder=6)

    # Footer
    ax.text(0.5, 0.040, '@veralevel.fx  ·  VERA LEVEL FX  ·  Not financial advice',
            fontsize=14, color=WHITE, ha='center', va='center',
            alpha=0.45, transform=ax.transAxes,
            fontfamily='monospace', zorder=6)

    return fig
