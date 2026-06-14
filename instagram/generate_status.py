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

# Notepad paper tilt: measured from photo corners — 1.76° counter-clockwise
_ROT      = 1.76
_ROT_TAN  = math.tan(math.radians(_ROT))
_X_REF    = 0.190   # left edge of notepad text area (reference x for tilt calc)

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


def make_daily_card(data: dict):
    account     = data.get('account', {})
    open_trades = data.get('openTrades', [])

    balance   = account.get('balance', 0)
    equity    = account.get('equity', balance)
    daily_pct = account.get('daily', 0)
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

    bg = _load_notepad_bg()

    fig = plt.figure(figsize=SIZE, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

    # ── Background photo ─────────────────────────────────────────
    if bg is not None:
        ax.imshow(bg, extent=[0, 1, 0, 1], aspect='auto', zorder=0)
    else:
        ax.set_facecolor(NAVY)

    # Dark overlay on monitor/top area for readability (y > 0.55)
    ax.add_patch(patches.Rectangle(
        (0, 0.555), 1, 0.445,
        facecolor='black', alpha=0.58,
        transform=ax.transAxes, zorder=1
    ))

    # ── Top branding band ────────────────────────────────────────
    ax.add_patch(patches.Rectangle(
        (0, 0.960), 1, 0.040,
        facecolor=GOLD, transform=ax.transAxes, zorder=2
    ))
    ax.text(0.5, 0.979, 'VERA LEVEL FX',
            fontsize=19, fontweight='bold', color=NAVY,
            ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=3)

    ax.text(0.5, 0.930, 'LIVE POSITION UPDATE  ·  ' + datetime.now().strftime('%d %B %Y  %H:%M SGT').upper(),
            fontsize=13, color=WHITE, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=3)

    # ── Equity / Balance / Daily (on darkened monitor area) ──────
    d_color = GREEN if daily_pct >= 0 else RED
    metrics = [
        ('EQUITY',  f'USD {equity:,.0f}',   GOLD),
        ('BALANCE', f'USD {balance:,.0f}',  CREAM),
        ('DAILY',   f'{daily_pct:+.2f}%',   d_color),
    ]
    for i, (label, value, color) in enumerate(metrics):
        mx = 0.08 + i * 0.315
        ax.text(mx + 0.115, 0.882, label,
                fontsize=13, color=DIM, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=3)
        ax.text(mx + 0.115, 0.848, value,
                fontsize=20, color=color, ha='center', va='center',
                transform=ax.transAxes, fontweight='bold',
                fontfamily='monospace', zorder=3)

    ax.plot([0.06, 0.94], [0.816, 0.816], color=GOLD, linewidth=0.8, alpha=0.35,
            transform=ax.transAxes, zorder=3)
    ax.text(0.5, 0.793, 'ALGORITHMIC FOREX  ·  IC MARKETS  ·  MYFXBOOK VERIFIED',
            fontsize=11, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=3)

    # ── NOTEPAD AREA: ink text on white paper, tilted to match paper angle ──
    def _ty(x, y_base):
        """y at position x on a line whose left end (x=_X_REF) is at y_base."""
        return y_base + (x - _X_REF) * _ROT_TAN

    def _tline(y_base, x0=_X_REF, x1=0.710, **kw):
        ax.plot([x0, x1], [_ty(x0, y_base), _ty(x1, y_base)],
                transform=ax.transAxes, **kw)

    def _ttext(x, y_base, label, **kw):
        ax.text(x, _ty(x, y_base), label,
                rotation=_ROT, rotation_mode='anchor',
                transform=ax.transAxes, **kw)

    # "OPEN TRADES" header
    _ttext(0.245, 0.548, 'OPEN TRADES',
           fontsize=19, color=INK, ha='left', va='center',
           fontfamily='monospace', fontweight='bold', zorder=4)
    _tline(0.524, color=INK, linewidth=0.9, alpha=0.28, zorder=4)

    # Column headers
    col_defs = [
        ('PAIR', 0.268), ('DIR', 0.385), ('P&L', 0.470),
        ('PIPS', 0.548), ('SINCE', 0.628),
    ]
    for label, cx in col_defs:
        _ttext(cx, 0.502, label,
               fontsize=13, color=INK, ha='center', va='center', alpha=0.52,
               fontfamily='monospace', fontweight='bold', zorder=4)
    _tline(0.484, color=INK, linewidth=0.5, alpha=0.18, zorder=4)

    # Trade rows
    row_gap = 0.066
    if rows:
        for r, trade in enumerate(rows):
            ry = 0.458 - r * row_gap

            pair   = trade.get('symbol', '—')
            action = trade.get('action', '').upper()
            profit = trade.get('profit', 0)
            t_pips = trade.get('pips', 0)
            open_t = trade.get('openTime', '')
            try:
                open_str = datetime.strptime(open_t, '%m/%d/%Y %H:%M').strftime('%m/%d')
            except Exception:
                open_str = open_t[:5]

            row_data = [
                (pair,              0.268, 'bold',   16),
                (action[:3],        0.385, 'bold',   15),
                (f'{profit:+.0f}',  0.470, 'normal', 14),
                (f'{t_pips:+.0f}p', 0.548, 'normal', 14),
                (open_str,          0.628, 'normal', 14),
            ]
            for text, cx, fw, fs in row_data:
                _ttext(cx, ry, text,
                       fontsize=fs, color=INK, ha='center', va='center',
                       fontfamily='monospace', fontweight=fw, zorder=4)

            if r < len(rows) - 1:
                _tline(ry - 0.028, color=INK, linewidth=0.4, alpha=0.13, zorder=4)
    else:
        _ttext(0.44, 0.420, 'no open positions',
               fontsize=15, color=INK, ha='center', va='center', alpha=0.42,
               fontstyle='italic', zorder=4)

    # Stats footer on notepad
    stats_y = 0.245 if not rows else 0.458 - len(rows) * row_gap - 0.050
    _tline(stats_y + 0.032, color=INK, linewidth=0.7, alpha=0.22, zorder=4)
    _ttext(0.450, stats_y,
           f'WR {win_rate:.0f}%  ·  PF {pf:.2f}  ·  +{pips:,} pips',
           fontsize=12, color=INK, ha='center', va='center', alpha=0.58,
           fontfamily='monospace', zorder=4)

    # Footer watermark (very bottom of image, below notepad leather frame)
    ax.text(0.5, 0.028, '@veralevel.fx  ·  Not financial advice',
            fontsize=12, color=WHITE, ha='center', va='center', alpha=0.72,
            transform=ax.transAxes, fontfamily='monospace', zorder=3)

    return fig
