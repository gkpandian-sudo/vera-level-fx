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
NAVY    = '#010E1F'
NAVY_S  = '#051830'
NAVY_L  = '#0A2545'
EMERALD = '#059669'
WHITE   = '#FFFFFF'
CREAM   = '#F0EEE8'
MUTED   = '#B8CFEA'
DIM     = '#6A8EB8'
GREEN   = '#059669'
RED     = '#EF4444'

SIZE = (10.8, 10.8)
DPI  = 100


def _base(nrows=1, ncols=1):
    fig = plt.figure(figsize=SIZE, facecolor=NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    return fig, ax


def _hline(ax, y, x0=0.06, x1=0.94, color=EMERALD, alpha=0.45, lw=1.5):
    ax.plot([x0, x1], [y, y], color=color, linewidth=lw,
            alpha=alpha, transform=ax.transAxes)


def _header(ax):
    ax.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026, facecolor=EMERALD, transform=ax.transAxes, zorder=5
    ))
    ax.text(0.5, 0.946, 'VERA LEVEL FX',
            fontsize=22, fontweight='bold', color=EMERALD, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    ax.text(0.5, 0.916, 'ALGORITHMIC FOREX  ·  IC MARKETS  ·  MYFXBOOK VERIFIED',
            fontsize=15, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    _hline(ax, 0.898, alpha=0.4)


def _footer(ax):
    _hline(ax, 0.095, alpha=0.4)
    ax.text(0.06, 0.065, '@veralevel.fx  ·  VERA LEVEL FX',
            fontsize=15, color=EMERALD, va='center',
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

def make_weekly_card(data, recovery_day: int = 0, recovery_total: int = 180):
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

    # Verified badge
    ax.add_patch(patches.Circle((0.075, 0.960), 0.007,
        facecolor=GREEN, transform=ax.transAxes, zorder=6))
    ax.text(0.090, 0.960, 'IC Markets Verified  ·  ASIC Regulated',
            fontsize=14, color=EMERALD, ha='left', va='center',
            transform=ax.transAxes, zorder=6)

    # Post type label
    ax.text(0.06, 0.923,
            f'WEEKLY PERFORMANCE  ·  {datetime.now().strftime("%d %B %Y").upper()}',
            fontsize=16, color=MUTED, ha='left', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Recovery day badge — only when active
    if recovery_day > 0:
        badge_text = f'DAY {recovery_day}/{recovery_total}'
        ax.add_patch(patches.FancyBboxPatch(
            (0.64, 0.906), 0.30, 0.032,
            boxstyle='round,pad=0.005',
            facecolor=NAVY_S, edgecolor=RED, linewidth=1.2,
            transform=ax.transAxes, zorder=7
        ))
        ax.text(0.79, 0.922, badge_text,
                fontsize=14, fontweight='bold', color=RED, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=8)

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
    pips_sign  = '+' if pips >= 0 else ''
    pips_color = GREEN if pips >= 0 else RED

    stats = [
        (f'${balance:,.0f}',        'BALANCE',  EMERALD),
        (f'{win_rate:.0f}%',        'WIN RATE', WHITE),
        (f'{pips_sign}{pips:,}',    'PIPS',     pips_color),
        (f'{trades:,}',             'TRADES',   MUTED),
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
    ax.text(0.06, 0.568, 'Verify every trade on Myfxbook',
            fontsize=17, color=MUTED, ha='left', va='center',
            transform=ax.transAxes, zorder=6)
    ax.text(0.06, 0.542, 'Account #12044019',
            fontsize=19, fontweight='bold', color=EMERALD,
            ha='left', va='center', transform=ax.transAxes, zorder=6)

    # Footer
    _hline(ax, 0.095, alpha=0.3)
    ax.text(0.94, 0.065, '@veralevel.fx',
            fontsize=15, color=EMERALD, va='center', ha='right',
            transform=ax.transAxes, fontweight='bold', zorder=6)
    ax.text(0.94, 0.030, 'Not financial advice',
            fontsize=14, color=DIM, ha='right', va='center',
            transform=ax.transAxes, zorder=6)

    return fig


# ── Monthly P&L Chart ────────────────────────────────────────────

def make_monthly_chart(data):
    daily = data.get('dailyGain', [])

    # Use the same time-weighted formula as captions.py to keep image and caption consistent
    from captions import monthly_pnl_from_daily

    monthly_pnl = monthly_pnl_from_daily(daily)

    keys = list(monthly_pnl.keys())[-12:]
    vals = [monthly_pnl[k] for k in keys]

    fig = plt.figure(figsize=SIZE, facecolor=NAVY)
    ax_bg = fig.add_axes([0, 0, 1, 1], facecolor=NAVY)
    ax_bg.set_xlim(0, 1); ax_bg.set_ylim(0, 1); ax_bg.axis('off')

    # Verified badge
    ax_bg.add_patch(patches.Circle(
        (0.36, 0.960), 0.007, facecolor=GREEN, transform=ax_bg.transAxes, zorder=6
    ))
    ax_bg.text(0.5, 0.960, 'IC Markets Verified  ·  ASIC Regulated',
               fontsize=13, color=EMERALD, ha='center', va='center',
               transform=ax_bg.transAxes, zorder=6)
    ax_bg.text(0.5, 0.912, 'Monthly P&L',
               fontsize=48, fontweight='bold', color=WHITE,
               ha='center', va='center', transform=ax_bg.transAxes, fontstyle='italic')
    ax_bg.text(0.5, 0.874, '12-MONTH ROLLING BREAKDOWN',
               fontsize=18, color=MUTED, ha='center', va='center',
               transform=ax_bg.transAxes, fontfamily='monospace')
    ax_bg.plot([0.06, 0.94], [0.854, 0.854], color=EMERALD, linewidth=1.5,
               alpha=0.4, transform=ax_bg.transAxes)

    ax = fig.add_axes([0.06, 0.130, 0.88, 0.700], facecolor=NAVY_L)
    for spine in ax.spines.values():
        spine.set_color(EMERALD); spine.set_alpha(0.3)
    ax.tick_params(colors=MUTED, labelsize=16)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=EMERALD, alpha=0.08, linewidth=0.6)
    ax.xaxis.grid(False)

    x      = np.arange(len(keys))
    colors = [GREEN if v >= 0 else RED for v in vals]
    bars   = ax.bar(x, vals, color=colors, width=0.64, alpha=0.88, zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(keys, fontsize=15, color=MUTED, fontfamily='monospace')
    ax.tick_params(axis='y', labelcolor=MUTED, labelsize=15)
    ax.axhline(y=0, color=EMERALD, linewidth=1.0, alpha=0.5)

    vmax = max(abs(v) for v in vals) if vals else 1
    for bar_r, val in zip(bars, vals):
        offset = vmax * 0.05
        ypos   = bar_r.get_height() + (offset if val >= 0 else -offset)
        ax.text(bar_r.get_x() + bar_r.get_width() / 2, ypos,
                f'{val:+.1f}%',
                ha='center', va='bottom' if val >= 0 else 'top',
                fontsize=13, color=GREEN if val >= 0 else RED,
                fontweight='bold', fontfamily='monospace')

    ax_bg.plot([0.06, 0.94], [0.095, 0.095], color=EMERALD, linewidth=1.2,
               alpha=0.3, transform=ax_bg.transAxes, zorder=5)
    ax_bg.text(0.94, 0.065, '@veralevel.fx',
               fontsize=15, color=EMERALD, va='center', ha='right',
               transform=ax_bg.transAxes, fontweight='bold', zorder=5)
    ax_bg.text(0.5, 0.065, 'icmarkets.com/global/en/?camp=91936',
               fontsize=14, color=MUTED, ha='center', va='center',
               transform=ax_bg.transAxes, zorder=5)
    ax_bg.text(0.5, 0.030, 'Not financial advice  ·  vera-level-forex.vercel.app',
               fontsize=14, color=DIM, ha='center', va='center',
               transform=ax_bg.transAxes, zorder=5)
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

    # IC Markets Verified (no box)
    ax.add_patch(patches.Circle(
        (0.275, 0.932), 0.008,
        facecolor=GREEN, transform=ax.transAxes, zorder=6
    ))
    ax.text(0.5, 0.932, 'IC Markets Verified  ·  ASIC Regulated',
            fontsize=16, color=EMERALD, fontweight='bold',
            ha='center', va='center', transform=ax.transAxes, zorder=7)

    # Post type label (no box)
    ax.text(0.5, 0.875, 'LIVE TRACK RECORD',
            fontsize=14, fontweight='black', color=EMERALD,
            ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Hero: win rate %
    ax.text(0.5, 0.690, f'{win_rate:.0f}%',
            fontsize=110, fontweight='black', color=WHITE,
            ha='center', va='center', transform=ax.transAxes, zorder=6)
    ax.text(0.5, 0.590, f'WIN RATE  ·  {trades:,} TRADES',
            fontsize=20, color=CREAM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Stats row (no boxes — plain labeled text like weekly card)
    stats_row = [
        (f'${balance:,.0f}',        'BALANCE', EMERALD,                        0.20),
        (f'{gain_sign}{gain:.1f}%', 'GAIN',    GREEN if gain >= 0 else RED, 0.50),
        (f'+{pips:,}',              'PIPS',    WHITE,                       0.78),
    ]
    for val, lbl, color, px in stats_row:
        ax.text(px, 0.548, val,
                fontsize=26, fontweight='black', color=color,
                ha='center', va='center', transform=ax.transAxes, zorder=6)
        ax.text(px, 0.514, lbl,
                fontsize=13, color=MUTED, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Profit factor
    ax.text(0.5, 0.462,
            f'Profit Factor {pf:.2f}  ·  1% max risk per trade',
            fontsize=17, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # CTAs
    _hline(ax, 0.420, alpha=0.2)
    ax.text(0.5, 0.388,
            'Verify every trade yourself  →  Myfxbook.com',
            fontsize=17, color=CREAM, ha='center', va='center',
            transform=ax.transAxes, zorder=6)
    ax.text(0.5, 0.355,
            'Myfxbook account #12044019  ·  All trades verified',
            fontsize=18, fontweight='bold', color=EMERALD,
            ha='center', va='center', transform=ax.transAxes, zorder=6)

    # Footer
    ax.text(0.5, 0.040, '@veralevel.fx  ·  Not financial advice',
            fontsize=14, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    return fig


# ── Transparency / Recovery Card ─────────────────────────────────

def make_transparency_card(data):
    account  = data.get('account', {})
    gain     = account.get('gain', 0)
    dd       = account.get('drawdown', 0)
    balance  = account.get('balance', 0)
    trades   = int(account.get('trades', 0))
    win_rate = account.get('winRate', 0)

    fig = plt.figure(figsize=SIZE, facecolor=NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.set_facecolor(NAVY)

    # Top gold bar
    ax.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026, facecolor=EMERALD, transform=ax.transAxes, zorder=5
    ))

    # Brand name
    ax.text(0.5, 0.946, 'VERA LEVEL FX',
            fontsize=22, fontweight='bold', color=EMERALD, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    ax.text(0.5, 0.916, 'FULL TRANSPARENCY  ·  NOTHING HIDDEN',
            fontsize=15, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    _hline(ax, 0.898, alpha=0.35)

    # Hero: loss number — intentionally RED and large
    gain_sign = '+' if gain >= 0 else ''
    ax.text(0.5, 0.790,
            f'{gain_sign}{gain:.1f}%',
            fontsize=100, fontweight='black', color=RED,
            ha='center', va='center', transform=ax.transAxes, zorder=6)
    ax.text(0.5, 0.730, 'TOTAL GAIN SINCE INCEPTION',
            fontsize=16, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')

    _hline(ax, 0.706, alpha=0.25)

    # What changed section
    ax.text(0.06, 0.672, 'WHAT HAPPENED',
            fontsize=14, color=RED, ha='left', va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold')
    ax.text(0.06, 0.642,
            'Entry frequency too high during volatile XAUUSD run.',
            fontsize=17, color=CREAM, ha='left', va='center',
            transform=ax.transAxes)
    ax.text(0.06, 0.614,
            'Capital eroded faster than wins could recover.',
            fontsize=17, color=CREAM, ha='left', va='center',
            transform=ax.transAxes)

    _hline(ax, 0.592, alpha=0.20)

    ax.text(0.06, 0.562, 'WHAT CHANGED',
            fontsize=14, color=GREEN, ha='left', va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold')
    ax.text(0.06, 0.532,
            'Reduced frequency · tighter session filters',
            fontsize=17, color=CREAM, ha='left', va='center',
            transform=ax.transAxes)
    ax.text(0.06, 0.504,
            'London/NY overlap only · 1% risk rule unchanged',
            fontsize=17, color=CREAM, ha='left', va='center',
            transform=ax.transAxes)

    _hline(ax, 0.480, alpha=0.20)

    # Stats row: balance · drawdown · trades · win rate
    stats = [
        (f'${balance:,.0f}',  'BALANCE',   EMERALD,  0.14),
        (f'{dd:.1f}%',        'DRAWDOWN',  RED,   0.38),
        (f'{trades:,}',       'TRADES',    WHITE, 0.62),
        (f'{win_rate:.0f}%',  'WIN RATE',  GREEN, 0.86),
    ]
    for val, lbl, color, px in stats:
        ax.text(px, 0.444, val,
                fontsize=28, fontweight='black', color=color,
                ha='center', va='center', transform=ax.transAxes, zorder=6)
        ax.text(px, 0.410, lbl,
                fontsize=13, color=DIM, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=6)

    _hline(ax, 0.382, alpha=0.20)

    # CTA
    ax.text(0.5, 0.348,
            'Verify every trade · Myfxbook account #12044019',
            fontsize=17, color=MUTED, ha='center', va='center',
            transform=ax.transAxes)
    ax.text(0.5, 0.316,
            'Live alerts as recovery unfolds  →  t.me/pandiangk',
            fontsize=19, fontweight='bold', color=EMERALD,
            ha='center', va='center', transform=ax.transAxes)

    # Recovery journey callout box
    ax.add_patch(patches.FancyBboxPatch(
        (0.06, 0.200), 0.88, 0.096,
        boxstyle='round,pad=0.006',
        facecolor=NAVY_S, edgecolor=RED, linewidth=1.4,
        transform=ax.transAxes, zorder=2
    ))
    ax.text(0.5, 0.260,
            'Any account showing only winning months is lying to you.',
            fontsize=17, color=CREAM, ha='center', va='center',
            transform=ax.transAxes, zorder=3)
    ax.text(0.5, 0.224,
            'This is what real trading looks like. The recovery starts now.',
            fontsize=17, color=RED, ha='center', va='center',
            transform=ax.transAxes, fontweight='bold', zorder=3)

    # Footer
    _hline(ax, 0.095, alpha=0.35)
    ax.text(0.06, 0.065, '@veralevel.fx  ·  IC MARKETS  ·  ASIC REGULATED',
            fontsize=14, color=EMERALD, va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold')
    ax.text(0.94, 0.030, 'Not financial advice',
            fontsize=14, color=DIM, ha='right', va='center',
            transform=ax.transAxes, fontfamily='monospace')

    return fig


# ── Recovery Plan Card (actuals-based) ───────────────────────────

def make_recovery_plan_card(data=None, recovery_day: int = 0, recovery_total: int = 180,
                             recovery_start_str: str = ''):
    account = (data or {}).get('account', {})
    balance = account.get('balance', 0)
    pf      = account.get('profitFactor', 0)
    gain    = account.get('gain', 0)
    daily   = account.get('daily', 0)

    fig = plt.figure(figsize=SIZE, facecolor=NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.set_facecolor(NAVY)

    # Top emerald bar
    ax.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026, facecolor=EMERALD, transform=ax.transAxes, zorder=5
    ))

    # Header
    ax.text(0.5, 0.946, 'VERA LEVEL FX  ·  RECOVERY PLAN',
            fontsize=20, fontweight='bold', color=EMERALD, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    ax.text(0.5, 0.916, '180-DAY PUBLIC REBUILD  ·  EVERY TRADE VERIFIED',
            fontsize=13, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    _hline(ax, 0.898, alpha=0.35)

    # Day counter hero
    if recovery_day > 0:
        ax.text(0.5, 0.842,
                f'DAY {recovery_day} / {recovery_total}',
                fontsize=64, fontweight='black', color=RED,
                ha='center', va='center', transform=ax.transAxes, linespacing=1.0)

        filled   = round((recovery_day / recovery_total) * 24)
        bar_text = '▓' * filled + '░' * (24 - filled)
        pct      = recovery_day / recovery_total * 100
        ax.text(0.5, 0.790, f'{bar_text}  {pct:.0f}%',
                fontsize=13, color=EMERALD, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace')
    else:
        ax.text(0.5, 0.836, 'RECOVERY PLAN · 180 DAYS',
                fontsize=36, fontweight='black', color=RED,
                ha='center', va='center', transform=ax.transAxes)

    _hline(ax, 0.765, alpha=0.25)

    # Actuals row: Balance · Total Return · Profit Factor
    gain_sign = '+' if gain >= 0 else ''
    actuals = [
        (f'${balance:,.0f}',             'BALANCE',      EMERALD, 0.18),
        (f'{gain_sign}{gain:.1f}%',       'TOTAL RTN',   RED if gain < 0 else GREEN, 0.50),
        (f'{pf:.2f}',                     'PROF.FACTOR', WHITE, 0.82),
    ]
    for val, lbl, color, px in actuals:
        ax.text(px, 0.730, val,
                fontsize=26, fontweight='black', color=color,
                ha='center', va='center', transform=ax.transAxes, zorder=6)
        ax.text(px, 0.696, lbl,
                fontsize=12, color=DIM, ha='center', va='center',
                transform=ax.transAxes, fontfamily='monospace', zorder=6)

    _hline(ax, 0.672, alpha=0.20)

    # Milestone checklist — auto-computed from live data
    def _ms(done: bool, label: str) -> str:
        return f"{'☑' if done else '☐'} {label}"

    milestones = [
        _ms(pf >= 1.0,  'Profit Factor above 1.0'),
        _ms(pf >= 1.2,  'Profit Factor 1.2+ (target)'),
        _ms(gain >= 0,  'Total return back to breakeven'),
        _ms(gain > 5,   'New equity high'),
    ]

    ax.text(0.06, 0.648, 'MILESTONES (reported when hit — not before)',
            fontsize=12, color=DIM, ha='left', va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold')

    for i, ms in enumerate(milestones):
        done  = ms.startswith('☑')
        color = EMERALD if done else MUTED
        ax.text(0.06, 0.618 - i * 0.044, ms,
                fontsize=14, color=color, ha='left', va='center',
                transform=ax.transAxes, fontfamily='monospace')

    _hline(ax, 0.430, alpha=0.20)

    # End-date commitment line
    if recovery_start_str and recovery_total > 0:
        try:
            from datetime import timedelta as _td
            end_dt  = datetime.strptime(recovery_start_str, '%Y-%m-%d') + _td(days=recovery_total - 1)
            end_str = end_dt.strftime('%d %b %Y')
            commit  = f'Day 180 is {end_str}. Final result posted — green or not.'
        except Exception:
            commit = f'Day {recovery_total} · Final result posted — green or not.'
    else:
        commit = f'Day {recovery_total} · Final result posted — green or not.'

    ax.add_patch(patches.FancyBboxPatch(
        (0.06, 0.370), 0.88, 0.046,
        boxstyle='round,pad=0.005',
        facecolor=NAVY_S, edgecolor=RED, linewidth=1.2,
        transform=ax.transAxes, zorder=2
    ))
    ax.text(0.5, 0.393, commit,
            fontsize=14, fontweight='bold', color=RED,
            ha='center', va='center', transform=ax.transAxes, zorder=3)

    # CTA
    ax.text(0.5, 0.326,
            'Every trade · Myfxbook account #12044019',
            fontsize=15, color=MUTED, ha='center', va='center',
            transform=ax.transAxes)
    ax.text(0.5, 0.292,
            'Live alerts as rebuild unfolds  →  t.me/pandiangk',
            fontsize=17, fontweight='bold', color=EMERALD,
            ha='center', va='center', transform=ax.transAxes)

    # Footer
    _hline(ax, 0.248, alpha=0.20)
    ax.text(0.5, 0.218, '#180dayrebuild  ·  Nothing projected. Nothing hidden.',
            fontsize=13, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    _hline(ax, 0.095, alpha=0.35)
    ax.text(0.06, 0.065, '@veralevel.fx  ·  IC MARKETS  ·  ASIC REGULATED',
            fontsize=13, color=EMERALD, va='center',
            transform=ax.transAxes, fontfamily='monospace', fontweight='bold')
    ax.text(0.94, 0.030, 'Not financial advice',
            fontsize=13, color=DIM, ha='right', va='center',
            transform=ax.transAxes, fontfamily='monospace')

    return fig
