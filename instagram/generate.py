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
    account  = data.get('account', {})
    balance  = account.get('balance', 0)
    gain     = account.get('gain', 0)
    monthly  = account.get('monthly', 0)
    win_rate = account.get('winRate', 0)
    pf       = account.get('profitFactor', 0)
    dd       = account.get('drawdown', 0)
    pips     = int(account.get('pips', 0))
    trades   = int(account.get('trades', 0))

    fig, ax = _base()
    _header(ax)

    ax.text(0.5, 0.848, 'Weekly Performance',
            fontsize=48, fontweight='bold', color=WHITE,
            ha='center', va='center', transform=ax.transAxes, fontstyle='italic')
    ax.text(0.5, 0.812, datetime.now().strftime('%d %B %Y').upper(),
            fontsize=22, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    _hline(ax, 0.792)

    gain_color  = GREEN if gain >= 0  else RED
    month_color = GREEN if monthly >= 0 else RED
    gain_sign   = '+' if gain >= 0 else ''
    month_sign  = '+' if monthly >= 0 else ''

    metrics = [
        ('ACCOUNT BALANCE', f'${balance:,.0f}',             GOLD,        ''),
        ('TOTAL GAIN',      f'{gain_sign}{gain:.2f}%',      gain_color,  'since inception'),
        ('MONTHLY AVG',     f'{month_sign}{monthly:.2f}%',  month_color, '30-day rolling'),
        ('WIN RATE',        f'{win_rate:.0f}%',             WHITE,       f'{trades:,} trades'),
        ('PROFIT FACTOR',   f'{pf:.2f}',                    GOLD,        'benchmark > 1.5'),
        ('DRAWDOWN',        f'{dd:.1f}%',                   AMBER,       'balance drawdown'),
    ]

    xs = [0.06, 0.53]
    ys = [0.596, 0.390, 0.184]
    cw, ch = 0.41, 0.185

    for i, (label, value, color, sub) in enumerate(metrics):
        _metric_card(ax, xs[i % 2], ys[i // 2], cw, ch, label, value, color, sub)

    ax.text(0.5, 0.138, f'+{pips:,} PIPS  ·  {trades:,} TOTAL TRADES',
            fontsize=26, color=GOLD_B, ha='center', va='center',
            transform=ax.transAxes, fontweight='bold', fontfamily='monospace')

    _footer(ax)
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
    account  = data.get('account', {})
    win_rate = account.get('winRate', 0)
    pf       = account.get('profitFactor', 0)
    gain     = account.get('gain', 0)
    trades   = int(account.get('trades', 0))
    pips     = int(account.get('pips', 0))

    fig, ax = _base()
    _header(ax)

    ax.text(0.5, 0.848, 'Live Track Record',
            fontsize=48, fontweight='bold', color=WHITE,
            ha='center', va='center', transform=ax.transAxes, fontstyle='italic')
    ax.text(0.5, 0.812, 'VERIFIED  ·  LIVE ACCOUNT  ·  NOT DEMO',
            fontsize=22, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    _hline(ax, 0.792)

    # Donut chart
    ax_d = fig.add_axes([0.25, 0.44, 0.50, 0.36], aspect='equal')
    ax_d.set_facecolor('none')
    wins = max(0, min(win_rate / 100, 1))
    ax_d.pie([wins, 1 - wins], colors=[GOLD, NAVY_L], startangle=90,
             counterclock=False,
             wedgeprops={'width': 0.38, 'edgecolor': NAVY, 'linewidth': 3})
    ax_d.text(0, 0.12, f'{win_rate:.0f}%',
              fontsize=68, fontweight='bold', color=WHITE,
              ha='center', va='center')
    ax_d.text(0, -0.34, 'WIN RATE',
              fontsize=20, color=MUTED, ha='center', va='center',
              fontfamily='monospace', fontweight='bold')

    # Stat cards
    stat_items = [
        ('PROFIT FACTOR', f'{pf:.2f}',    GOLD),
        ('TOTAL GAIN',    f'{gain:+.1f}%', GREEN),
        ('TRADES',        f'{trades:,}',   WHITE),
    ]
    cw, ch = 0.27, 0.118
    cy     = 0.290
    for i, (label, value, color) in enumerate(stat_items):
        cx = 0.06 + i * 0.323
        ax.add_patch(patches.FancyBboxPatch(
            (cx, cy), cw, ch, boxstyle='round,pad=0.006',
            facecolor=NAVY_S, edgecolor=color, linewidth=1.2,
            transform=ax.transAxes, zorder=2
        ))
        ax.add_patch(patches.Rectangle(
            (cx, cy + ch - 0.005), cw, 0.005,
            facecolor=color, transform=ax.transAxes, zorder=3
        ))
        ax.text(cx + cw / 2, cy + ch - 0.025, label,
                fontsize=18, color=MUTED, ha='center', va='top',
                transform=ax.transAxes, fontfamily='monospace', fontweight='bold')
        ax.text(cx + cw / 2, cy + 0.022, value,
                fontsize=30, color=color, ha='center', va='bottom',
                transform=ax.transAxes, fontweight='bold')

    ax.text(0.5, 0.226,
            f'+{pips:,} pips  ·  every trade live-verified on Myfxbook',
            fontsize=22, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')

    ax.text(0.5, 0.172,
            '"Consistent. Algorithmic. Transparent."',
            fontsize=28, color=WHITE, ha='center', va='center',
            transform=ax.transAxes, fontstyle='italic')

    _footer(ax)
    return fig
