"""
generate_status.py — Daily / live-positions Instagram card for Vera Level FX.

Produces a terminal-style "positions dashboard" post showing:
  • Account equity + daily P&L
  • Open positions table (pair, direction, lots, P&L, pips)
  • Running stats (win rate, pips, trades since inception)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime

# ── Re-use brand tokens from generate.py ─────────────────────────
NAVY   = '#060F24'
NAVY_S = '#0A1630'
NAVY_L = '#0E1E3C'
GOLD   = '#D4AF37'
GOLD_B = '#EAC84A'
WHITE  = '#EDF2FA'
MUTED  = '#8BADD4'
DIM    = '#4A6A9B'
GREEN  = '#10B981'
RED    = '#FC8585'
AMBER  = '#F59E0B'

SIZE = (10.8, 10.8)
DPI  = 100

_STRIP_KEYWORDS = ['tol langit', 'tol-langit', 'toklangit']


def _clean_comment(comment: str) -> str:
    """Remove any third-party system names from trade comments."""
    lower = comment.lower()
    for kw in _STRIP_KEYWORDS:
        if kw in lower:
            return ''
    return comment


def _header(ax):
    ax.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026,
        facecolor=GOLD, transform=ax.transAxes, zorder=5
    ))
    ax.text(0.5, 0.933, 'VERA LEVEL FX',
            fontsize=15, fontweight='bold', color=GOLD, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    ax.text(0.5, 0.904, 'INSTITUTIONAL FOREX PORTFOLIO  ·  MYFXBOOK VERIFIED',
            fontsize=7.5, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    ax.plot([0.06, 0.94], [0.885, 0.885], color=GOLD, linewidth=1.2,
            alpha=0.45, transform=ax.transAxes)


def _footer(ax):
    ax.plot([0.06, 0.94], [0.082, 0.082], color=GOLD, linewidth=1.2,
            alpha=0.45, transform=ax.transAxes)
    ax.text(0.5, 0.052, 'IC MARKETS  ·  ASIC REGULATED  ·  @veralevel.fx',
            fontsize=8, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    ax.text(0.5, 0.022, 'Not financial advice  ·  veralevel-fx.github.io',
            fontsize=7, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')


def make_daily_card(data: dict):
    """
    Build a 1080×1080 live-positions dashboard card.

    Sections (top → bottom):
      1. Brand header
      2. Title row — "Live Position Update" + date
      3. Three equity/daily metric pills
      4. Open positions table (up to 6 rows)
      5. Running performance row
      6. Footer
    """
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

    # Deduplicate + clean open trades (strip brand names from comments)
    seen, rows = set(), []
    for t in open_trades:
        key = (t.get('symbol', ''), t.get('openTime', ''), t.get('action', ''))
        if key not in seen:
            seen.add(key)
            rows.append(t)
    rows = rows[:6]  # max 6 rows to fit the card

    fig, ax = plt.subplots(figsize=SIZE, facecolor=NAVY)
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    _header(ax)

    # ── Title ────────────────────────────────────────────────────
    ax.text(0.5, 0.850, 'Live Position Update',
            fontsize=26, fontweight='bold', color=WHITE,
            ha='center', va='center', transform=ax.transAxes, fontstyle='italic')
    ax.text(0.5, 0.814, datetime.now().strftime('%d %B %Y  ·  %H:%M SGT').upper(),
            fontsize=8.5, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    ax.plot([0.06, 0.94], [0.796, 0.796], color=GOLD, linewidth=1.0,
            alpha=0.55, transform=ax.transAxes)

    # ── Top metric pills ─────────────────────────────────────────
    pill_data = [
        ('EQUITY',    f'${equity:,.2f}',  GOLD),
        ('BALANCE',   f'${balance:,.2f}', WHITE),
        ('DAILY P&L', f'{daily_pct:+.2f}%  (${daily_usd:+.2f})',
         GREEN if daily_pct >= 0 else RED),
    ]
    pill_y, pill_h = 0.715, 0.066
    for i, (label, value, color) in enumerate(pill_data):
        px = 0.06 + i * 0.313
        pw = 0.295
        ax.add_patch(patches.FancyBboxPatch(
            (px, pill_y), pw, pill_h,
            boxstyle='round,pad=0.005',
            facecolor=NAVY_S, edgecolor=color, linewidth=0.9,
            transform=ax.transAxes, zorder=2
        ))
        ax.text(px + pw / 2, pill_y + pill_h - 0.014, label,
                fontsize=7, color=MUTED, ha='center', va='top',
                transform=ax.transAxes, fontfamily='monospace', fontweight='bold')
        ax.text(px + pw / 2, pill_y + 0.012, value,
                fontsize=12.5, color=color, ha='center', va='bottom',
                transform=ax.transAxes, fontweight='bold', fontfamily='monospace')

    # ── Open positions table ─────────────────────────────────────
    table_top = 0.696
    ax.plot([0.04, 0.96], [table_top, table_top], color=GOLD, linewidth=0.6,
            alpha=0.35, transform=ax.transAxes)

    # Column definitions: (header, x_center, align)
    cols = [
        ('PAIR',  0.115, 'center'),
        ('DIR',   0.240, 'center'),
        ('LOTS',  0.340, 'center'),
        ('P&L',   0.490, 'center'),
        ('PIPS',  0.625, 'center'),
        ('OPEN',  0.830, 'center'),
    ]

    hdr_y = table_top - 0.030
    for hdr, cx, align in cols:
        ax.text(cx, hdr_y, hdr,
                fontsize=7, color=GOLD, ha=align, va='center',
                transform=ax.transAxes, fontfamily='monospace', fontweight='bold')

    ax.plot([0.04, 0.96], [hdr_y - 0.018, hdr_y - 0.018], color=GOLD,
            linewidth=0.5, alpha=0.25, transform=ax.transAxes)

    row_height = 0.073
    if rows:
        for r_idx, trade in enumerate(rows):
            ry = hdr_y - 0.022 - (r_idx + 1) * row_height

            pair    = trade.get('symbol', '—')
            action  = trade.get('action', '').upper()
            lots    = trade.get('sizing', {}).get('value', '—')
            profit  = trade.get('profit', 0)
            t_pips  = trade.get('pips', 0)
            open_t  = trade.get('openTime', '')
            # Shorten open time to MM/DD HH:MM
            try:
                dt_open = datetime.strptime(open_t, '%m/%d/%Y %H:%M')
                open_str = dt_open.strftime('%m/%d %H:%M')
            except Exception:
                open_str = open_t[:10]

            p_color = GREEN if profit >= 0 else RED
            d_color = GREEN if action == 'BUY' else RED

            # Alternating row bg
            if r_idx % 2 == 0:
                ax.add_patch(patches.Rectangle(
                    (0.04, ry - 0.01), 0.92, row_height - 0.008,
                    facecolor=NAVY_L, alpha=0.5,
                    transform=ax.transAxes, zorder=1
                ))

            row_cy = ry + (row_height - 0.018) / 2
            values = [
                (pair,              cols[0][1], WHITE,   10.5, 'bold'),
                (action,            cols[1][1], d_color,  9,   'bold'),
                (f'{lots}L',        cols[2][1], MUTED,    9,   'normal'),
                (f'${profit:+.2f}', cols[3][1], p_color, 10,   'bold'),
                (f'{t_pips:+.0f}',  cols[4][1], p_color,  9,   'normal'),
                (open_str,          cols[5][1], DIM,      8,   'normal'),
            ]
            for text, cx, color, fsize, fw in values:
                ax.text(cx, row_cy, text,
                        fontsize=fsize, color=color, ha='center', va='center',
                        transform=ax.transAxes, fontweight=fw,
                        fontfamily='monospace')
    else:
        mid_y = hdr_y - 0.022 - 2 * row_height
        ax.text(0.5, mid_y, 'No open positions',
                fontsize=11, color=DIM, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace', fontstyle='italic')

    # ── Running stats bar ────────────────────────────────────────
    stats_y = 0.165
    ax.plot([0.04, 0.96], [stats_y + 0.055, stats_y + 0.055], color=GOLD,
            linewidth=0.5, alpha=0.3, transform=ax.transAxes)

    stat_items = [
        ('WIN RATE', f'{win_rate:.0f}%',   GOLD),
        ('PROFIT FACTOR', f'{pf:.2f}',    WHITE),
        ('TOTAL PIPS', f'+{pips:,}',       GREEN),
        ('TRADES', f'{trades:,}',          MUTED),
    ]
    sw = 0.22
    for i, (label, value, color) in enumerate(stat_items):
        sx = 0.04 + i * 0.24
        ax.text(sx + sw / 2, stats_y + 0.038, label,
                fontsize=6.5, color=DIM, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace')
        ax.text(sx + sw / 2, stats_y + 0.010, value,
                fontsize=13, color=color, ha='center', va='bottom',
                transform=ax.transAxes, fontweight='bold', fontfamily='monospace')

    _footer(ax)
    plt.tight_layout(pad=0)
    return fig
