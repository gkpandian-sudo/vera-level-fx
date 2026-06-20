"""
generate_status.py — Daily live-positions card for Vera Level FX.
1080×1080 @ 100 DPI. Notepad photo background with ink-style text overlay.
"""

import os
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime

# Flat open notebook — table spans full image width, centred at x=0.5
_ROT      = 0.0
_ROT_TAN  = 0.0
_X_REF    = 0.05    # left edge of table area

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
INK    = '#0A1628'

SIZE = (10.8, 10.8)
DPI  = 100

_STRIP = ['tol langit', 'tol-langit', 'toklangit']

_BG_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'bg-daily-notepad.jpg')


def _load_notepad_bg():
    try:
        from PIL import Image
        img = Image.open(_BG_PATH).convert('RGB')
        w, h = img.size
        # Center-crop to square
        if h > w:
            top = (h - w) // 2
            img = img.crop((0, top, w, top + w))
        else:
            left = (w - h) // 2
            img = img.crop((left, 0, left + h, h))
        img = img.resize((1080, 1080), Image.LANCZOS)
        return np.array(img, dtype=np.float32) / 255.0
    except Exception:
        return None


def _fmt_pips(p: float) -> str:
    """Format pip value — abbreviate to 1 decimal + k suffix above ±999."""
    if abs(p) >= 1000:
        return f'{p/1000:+.1f}k'
    return f'{p:+.0f}p'


def _fmt_price(p: float) -> str:
    """Format entry price: 2dp for instruments >= 10 (gold, JPY), 4dp otherwise."""
    if p == 0:
        return '—'
    return f'{p:.2f}' if p >= 10 else f'{p:.4f}'


def make_daily_card(data: dict):
    from instagram.composer import load_background, gradient_panel
    from pathlib import Path

    account     = data.get('account', {})
    open_trades = data.get('openTrades', [])

    balance   = account.get('balance', 0)
    equity    = account.get('equity', balance)
    daily_pct = account.get('daily', 0)
    win_rate  = account.get('winRate', 0)
    pips      = int(account.get('pips', 0))
    pf        = account.get('profitFactor', 0)

    # Deduplicate trades
    seen, rows = set(), []
    for t in open_trades:
        key = (t.get('symbol', ''), t.get('openTime', ''), t.get('action', ''))
        if key not in seen:
            seen.add(key)
            rows.append(t)
    rows = rows[:5]

    bg_path = Path(__file__).parent / 'assets' / 'bg-daily.jpg'
    bg = gradient_panel(load_background(bg_path), height_frac=0.58)

    fig = plt.figure(figsize=SIZE, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.imshow(bg, extent=[0, 1, 0, 1], aspect='auto', zorder=0)

    d_color = GREEN if daily_pct >= 0 else RED

    ax.text(0.5, 0.955,
            'LIVE POSITION UPDATE  ·  ' + datetime.now().strftime('%d %B %Y').upper(),
            fontsize=15, color=WHITE, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Equity / Balance / Daily metrics
    metrics = [
        ('EQUITY',  f'USD {equity:,.0f}',   GOLD),
        ('BALANCE', f'USD {balance:,.0f}',  WHITE),
        ('DAILY',   f'{daily_pct:+.2f}%',   d_color),
    ]
    for i, (label, value, color) in enumerate(metrics):
        mx = 0.08 + i * 0.305
        ax.text(mx + 0.10, 0.887, label,
                fontsize=15, color=WHITE, fontweight='bold', ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=6)
        ax.text(mx + 0.10, 0.852, value,
                fontsize=26, color=color, ha='center', va='center',
                transform=ax.transAxes, fontweight='bold', zorder=6)

    ax.plot([0.06, 0.94], [0.822, 0.822], color=GOLD, linewidth=0.8, alpha=0.3,
            transform=ax.transAxes, zorder=6)

    # LIVE indicator
    ax.text(0.94, 0.793, '● LIVE',
            fontsize=16, fontweight='bold', color=RED,
            ha='right', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Open positions header
    n_open = len(rows)
    ax.text(0.06, 0.793, f'{n_open} Open Position{"s" if n_open != 1 else ""}',
            fontsize=32, fontweight='black', color=WHITE,
            ha='left', va='center', transform=ax.transAxes, zorder=6)

    # Trade table
    col_x = {'pair': 0.06, 'dir': 0.300, 'pnl': 0.470, 'pips': 0.640, 'entry': 0.810}
    headers = [('PAIR', 'pair', 'left'), ('DIR', 'dir', 'center'),
               ('P&L', 'pnl', 'center'), ('PIPS', 'pips', 'center'),
               ('ENTRY', 'entry', 'center')]

    ax.plot([0.06, 0.94], [0.752, 0.752], color=GOLD, linewidth=0.8, alpha=0.25,
            transform=ax.transAxes, zorder=6)
    for label, key, ha in headers:
        ax.text(col_x[key], 0.737, label,
                fontsize=15, color=WHITE, fontweight='bold', ha=ha, va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=6)
    ax.plot([0.06, 0.94], [0.718, 0.718], color=GOLD, linewidth=0.8, alpha=0.18,
            transform=ax.transAxes, zorder=6)

    row_gap = 0.062
    if rows:
        for r, trade in enumerate(rows):
            ry = 0.700 - r * row_gap
            pair    = trade.get('symbol', '—')
            action  = trade.get('action', '').upper()
            profit  = trade.get('profit', 0)
            t_pips  = trade.get('pips', 0)
            entry   = trade.get('openPrice', 0)
            p_color = GREEN if profit >= 0 else RED

            ax.text(col_x['pair'],  ry, pair,              fontsize=19, fontweight='bold', color=WHITE,   ha='left',   va='center', transform=ax.transAxes, zorder=6)
            ax.text(col_x['dir'],   ry, action[:3],        fontsize=17, fontweight='bold', color=WHITE,   ha='center', va='center', transform=ax.transAxes, zorder=6)
            ax.text(col_x['pnl'],   ry, f'{profit:+.0f}',  fontsize=17, fontweight='bold', color=WHITE,   ha='center', va='center', transform=ax.transAxes, zorder=6)
            ax.text(col_x['pips'],  ry, _fmt_pips(t_pips), fontsize=17, color=WHITE,       ha='center', va='center', transform=ax.transAxes, zorder=6)
            ax.text(col_x['entry'], ry, _fmt_price(entry), fontsize=16, color=WHITE,        ha='center', va='center', transform=ax.transAxes, fontfamily='monospace', zorder=6)
            if r < len(rows) - 1:
                ax.plot([0.06, 0.94], [ry - 0.026, ry - 0.026],
                        color=GOLD, linewidth=0.5, alpha=0.15,
                        transform=ax.transAxes, zorder=6)
    else:
        ax.text(0.5, 0.630, 'No open positions',
                fontsize=20, color=MUTED, ha='center', va='center',
                fontstyle='italic', transform=ax.transAxes, zorder=6)

    # Stats bar
    bottom_y = max(0.270, 0.700 - len(rows) * row_gap - 0.050)
    ax.plot([0.06, 0.94], [bottom_y + 0.026, bottom_y + 0.026],
            color=GOLD, linewidth=0.8, alpha=0.2, transform=ax.transAxes, zorder=6)
    ax.text(0.5, bottom_y,
            f'WR {win_rate:.0f}%  ·  PF {pf:.2f}  ·  +{pips:,} pips  —  verified on Myfxbook',
            fontsize=15, fontweight='bold', color=WHITE, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # CTA
    ax.text(0.5, 0.148, 'Trade with my broker  ·  icmarkets.com/?camp=91936',
            fontsize=15, fontweight='bold', color=GOLD,
            ha='center', va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)

    # Footer
    ax.text(0.94, 0.022, '@veralevel.fx  ·  Not financial advice',
            fontsize=14, color=MUTED, ha='right', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    return fig
