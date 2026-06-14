"""
generate_status.py — Daily live-positions card for Vera Level FX.
1080×1080 @ 100 DPI. Mobile-first font sizing.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime

NAVY   = '#010E1F'
NAVY_S = '#051830'
NAVY_L = '#0A2545'
GOLD   = '#F0C040'
WHITE  = '#FFFFFF'
CREAM  = '#F0EEE8'
MUTED  = '#B8CFEA'
DIM    = '#6A8EB8'
GREEN  = '#00E096'
RED    = '#FF6B6B'
AMBER  = '#FFA040'

SIZE = (10.8, 10.8)
DPI  = 100

_STRIP = ['tol langit', 'tol-langit', 'toklangit']


def _hline(ax, y, x0=0.06, x1=0.94, color=GOLD, alpha=0.4, lw=1.5):
    ax.plot([x0, x1], [y, y], color=color, linewidth=lw,
            alpha=alpha, transform=ax.transAxes, zorder=4)


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
            fontsize=20, color=GOLD, va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold')
    ax.text(0.94, 0.065, 'IC MARKETS · ASIC',
            fontsize=20, color=MUTED, va='center', ha='right',
            transform=ax.transAxes, fontfamily='monospace')
    ax.text(0.5, 0.030, 'Not financial advice  ·  vera-level-forex.vercel.app',
            fontsize=18, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')


def make_daily_card(data: dict):
    account     = data.get('account', {})
    open_trades = data.get('openTrades', [])

    balance   = account.get('balance', 0)
    equity    = account.get('equity', balance)
    daily_pct = account.get('daily', 0)
    daily_usd = round(equity * daily_pct / 100, 2)
    win_rate  = account.get('winRate', 0)
    pips      = int(account.get('pips', 0))
    trades    = int(account.get('trades', 0))
    pf        = account.get('profitFactor', 0)

    # Deduplicate + strip brand names
    seen, rows = set(), []
    for t in open_trades:
        key = (t.get('symbol', ''), t.get('openTime', ''), t.get('action', ''))
        if key not in seen:
            seen.add(key)
            rows.append(t)
    rows = rows[:5]

    fig, ax = plt.subplots(figsize=SIZE, facecolor=NAVY)
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

    _header(ax)

    # ── Title ────────────────────────────────────────────────────
    ax.text(0.5, 0.854, 'Live Position Update',
            fontsize=44, fontweight='bold', color=WHITE,
            ha='center', va='center', transform=ax.transAxes, fontstyle='italic')
    ax.text(0.5, 0.820, datetime.now().strftime('%d %B %Y  ·  %H:%M SGT').upper(),
            fontsize=20, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    _hline(ax, 0.800)

    # ── Equity / balance / daily pills ───────────────────────────
    d_color = GREEN if daily_pct >= 0 else RED
    pill_data = [
        ('EQUITY',    f'${equity:,.2f}', GOLD),
        ('BALANCE',   f'${balance:,.2f}', CREAM),
        ('DAILY P&L', f'{daily_pct:+.2f}%', d_color),
    ]
    for i, (label, value, color) in enumerate(pill_data):
        px, pw, ph = 0.06 + i * 0.313, 0.295, 0.090
        ax.add_patch(patches.FancyBboxPatch(
            (px, 0.700), pw, ph, boxstyle='round,pad=0.006',
            facecolor=NAVY_S, edgecolor=color, linewidth=1.3,
            transform=ax.transAxes, zorder=2
        ))
        ax.text(px + pw / 2, 0.700 + ph - 0.020, label,
                fontsize=18, color=MUTED, ha='center', va='top',
                transform=ax.transAxes, fontfamily='monospace', fontweight='bold')
        ax.text(px + pw / 2, 0.700 + 0.018, value,
                fontsize=30, color=color, ha='center', va='bottom',
                transform=ax.transAxes, fontweight='bold', fontfamily='monospace')

    # ── Positions table ───────────────────────────────────────────
    _hline(ax, 0.692, alpha=0.3)

    # Column headers
    cols = [
        ('PAIR',  0.110), ('DIR', 0.248), ('LOTS', 0.355),
        ('P&L $', 0.490), ('PIPS', 0.622), ('SINCE', 0.820),
    ]
    hdr_y = 0.660
    for hdr, cx in cols:
        ax.text(cx, hdr_y, hdr,
                fontsize=18, color=GOLD, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace', fontweight='bold')
    _hline(ax, hdr_y - 0.022, alpha=0.2)

    row_h = 0.098
    if rows:
        for r, trade in enumerate(rows):
            ry = hdr_y - 0.026 - (r + 1) * row_h

            pair   = trade.get('symbol', '—')
            action = trade.get('action', '').upper()
            lots   = trade.get('sizing', {}).get('value', '—')
            profit = trade.get('profit', 0)
            t_pips = trade.get('pips', 0)
            open_t = trade.get('openTime', '')
            try:
                open_str = datetime.strptime(open_t, '%m/%d/%Y %H:%M').strftime('%m/%d')
            except Exception:
                open_str = open_t[:5]

            p_color = GREEN if profit >= 0 else RED
            d_color2 = GREEN if 'BUY' in action else RED

            if r % 2 == 0:
                ax.add_patch(patches.Rectangle(
                    (0.04, ry - 0.008), 0.92, row_h - 0.010,
                    facecolor=NAVY_L, alpha=0.55,
                    transform=ax.transAxes, zorder=1
                ))

            cy = ry + (row_h - 0.018) / 2
            row_vals = [
                (pair,              0.110, WHITE,   24, 'bold'),
                (action,            0.248, d_color2, 22, 'bold'),
                (f'{lots}L',        0.355, MUTED,   20, 'normal'),
                (f'${profit:+.2f}', 0.490, p_color, 24, 'bold'),
                (f'{t_pips:+.0f}',  0.622, p_color, 22, 'normal'),
                (open_str,          0.820, DIM,     20, 'normal'),
            ]
            for text, cx, color, fs, fw in row_vals:
                ax.text(cx, cy, text,
                        fontsize=fs, color=color, ha='center', va='center',
                        transform=ax.transAxes, fontweight=fw,
                        fontfamily='monospace')
    else:
        ax.text(0.5, hdr_y - 2 * row_h,
                'No open positions',
                fontsize=28, color=DIM, ha='center', va='center',
                transform=ax.transAxes, fontstyle='italic')

    # ── Running stats row ─────────────────────────────────────────
    stats_y = 0.158
    _hline(ax, stats_y + 0.068, alpha=0.3)

    stat_items = [
        ('WIN RATE',      f'{win_rate:.0f}%',  GOLD),
        ('PROFIT FACTOR', f'{pf:.2f}',         WHITE),
        ('TOTAL PIPS',    f'+{pips:,}',         GREEN),
        ('TRADES',        f'{trades:,}',         MUTED),
    ]
    for i, (label, value, color) in enumerate(stat_items):
        sx = 0.06 + i * 0.235
        ax.text(sx + 0.100, stats_y + 0.048, label,
                fontsize=16, color=DIM, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace')
        ax.text(sx + 0.100, stats_y + 0.012, value,
                fontsize=26, color=color, ha='center', va='bottom',
                transform=ax.transAxes, fontweight='bold', fontfamily='monospace')

    _footer(ax)
    return fig
