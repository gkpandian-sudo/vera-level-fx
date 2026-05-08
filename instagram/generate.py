import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime

# ── Brand palette ────────────────────────────────────────────────
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


# ── Shared helpers ───────────────────────────────────────────────

def _base(nrows=1, ncols=1):
    fig, ax = plt.subplots(figsize=SIZE, facecolor=NAVY)
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    return fig, ax


def _gold_line(ax, y, x0=0.06, x1=0.94, lw=1.5, alpha=0.85):
    ax.axhline(y=y, xmin=x0, xmax=x1, color=GOLD, linewidth=lw, alpha=alpha,
               transform=ax.transAxes)


def _header(ax):
    ax.add_patch(patches.Rectangle((0, 0.974), 1, 0.026,
                                    facecolor=GOLD, transform=ax.transAxes, zorder=5))
    ax.text(0.5, 0.933, 'VERA LEVEL FX',
            fontsize=15, fontweight='bold', color=GOLD, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    ax.text(0.5, 0.904, 'INSTITUTIONAL FOREX PORTFOLIO  ·  MYFXBOOK VERIFIED',
            fontsize=7.5, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    _gold_line(ax, 0.885, alpha=0.5)


def _footer(ax):
    _gold_line(ax, 0.082, alpha=0.5)
    ax.text(0.5, 0.052, 'IC MARKETS  ·  ASIC REGULATED  ·  @veralevel.fx',
            fontsize=8, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    ax.text(0.5, 0.022, 'Not financial advice  ·  veralevel-fx.github.io',
            fontsize=7, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')


def _metric_card(ax, x, y, w, h, label, value, color, sub=''):
    ax.add_patch(patches.FancyBboxPatch(
        (x, y), w, h, boxstyle='round,pad=0.004',
        facecolor=NAVY_S, edgecolor=GOLD, linewidth=0.7,
        transform=ax.transAxes, zorder=2
    ))
    # top colour accent
    ax.add_patch(patches.Rectangle(
        (x, y + h - 0.003), w, 0.003,
        facecolor=color, transform=ax.transAxes, zorder=3
    ))
    pad = 0.018
    ax.text(x + pad, y + h - 0.028, label,
            fontsize=7.5, color=MUTED, va='top', transform=ax.transAxes,
            fontfamily='monospace', fontweight='bold')
    ax.text(x + pad, y + h - 0.085, value,
            fontsize=22, color=color, va='top', transform=ax.transAxes,
            fontweight='bold')
    if sub:
        ax.text(x + pad, y + 0.018, sub,
                fontsize=7, color=DIM, va='bottom', transform=ax.transAxes,
                fontfamily='monospace')


# ── Post 1: Weekly Performance Card ─────────────────────────────

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

    ax.text(0.5, 0.845, 'Weekly Performance',
            fontsize=28, fontweight='bold', color=WHITE,
            ha='center', va='center', transform=ax.transAxes, fontstyle='italic')
    ax.text(0.5, 0.808, datetime.now().strftime('%d %B %Y').upper(),
            fontsize=9, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    _gold_line(ax, 0.788)

    metrics = [
        ('ACCOUNT BALANCE', f'${balance:,.2f}', GOLD,  ''),
        ('TOTAL GAIN',      f'+{gain:.2f}%',     GREEN, 'since inception'),
        ('MONTHLY RETURN',  f'+{monthly:.2f}%',  GREEN, '30-day rolling avg'),
        ('WIN RATE',        f'{win_rate:.0f}%',  WHITE, f'{trades:,} total trades'),
        ('PROFIT FACTOR',   f'{pf:.2f}',         GOLD,  'benchmark > 1.5'),
        ('MAX DRAWDOWN',    f'{dd:.1f}%',        AMBER, 'controlled risk'),
    ]

    xs = [0.06, 0.53]
    ys = [0.598, 0.395, 0.192]
    card_w, card_h = 0.41, 0.185

    for i, (label, value, color, sub) in enumerate(metrics):
        _metric_card(ax, xs[i % 2], ys[i // 2], card_w, card_h, label, value, color, sub)

    ax.text(0.5, 0.140, f'+{pips:,} PIPS TOTAL',
            fontsize=14, color=GOLD_B, ha='center', va='center',
            transform=ax.transAxes, fontweight='bold', fontfamily='monospace')

    _footer(ax)
    plt.tight_layout(pad=0)
    return fig


# ── Post 2: Monthly P&L Chart ────────────────────────────────────

def make_monthly_chart(data):
    account   = data.get('account', {})
    daily     = data.get('dailyGain', [])

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
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')

    _header(ax_bg)
    ax_bg.text(0.5, 0.845, 'Monthly P&L',
               fontsize=28, fontweight='bold', color=WHITE,
               ha='center', va='center', transform=ax_bg.transAxes, fontstyle='italic')
    ax_bg.text(0.5, 0.808, '12-MONTH BREAKDOWN  ·  DAILY GAIN DATA',
               fontsize=9, color=MUTED, ha='center', va='center',
               transform=ax_bg.transAxes, fontfamily='monospace')
    _gold_line(ax_bg, 0.788)

    # Chart subplot inset
    ax = fig.add_axes([0.08, 0.13, 0.84, 0.635], facecolor=NAVY_L)
    for spine in ax.spines.values():
        spine.set_color(GOLD)
        spine.set_alpha(0.25)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GOLD, alpha=0.07, linewidth=0.5)
    ax.xaxis.grid(False)

    x      = np.arange(len(keys))
    colors = [GREEN if v >= 0 else RED for v in vals]
    bars   = ax.bar(x, vals, color=colors, width=0.62, alpha=0.88, zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(keys, fontsize=7.5, color=MUTED, fontfamily='monospace')
    ax.tick_params(axis='y', labelcolor=MUTED, labelsize=8)
    ax.axhline(y=0, color=GOLD, linewidth=0.8, alpha=0.45)

    # Value labels on bars
    vmax = max(abs(v) for v in vals) if vals else 1
    for bar_r, val in zip(bars, vals):
        offset = vmax * 0.04
        ypos   = bar_r.get_height() + (offset if val >= 0 else -offset)
        ax.text(bar_r.get_x() + bar_r.get_width() / 2, ypos,
                f'{val:+.1f}%',
                ha='center', va='bottom' if val >= 0 else 'top',
                fontsize=6.5, color=GREEN if val >= 0 else RED,
                fontweight='bold', fontfamily='monospace')

    _footer(ax_bg)
    plt.tight_layout(pad=0)
    return fig


# ── Post 3: Win Rate / Trust Card ───────────────────────────────

def make_winrate_card(data):
    account  = data.get('account', {})
    win_rate = account.get('winRate', 0)
    pf       = account.get('profitFactor', 0)
    gain     = account.get('gain', 0)
    trades   = int(account.get('trades', 0))
    pips     = int(account.get('pips', 0))

    fig, ax = _base()
    _header(ax)

    ax.text(0.5, 0.845, 'Live Track Record',
            fontsize=28, fontweight='bold', color=WHITE,
            ha='center', va='center', transform=ax.transAxes, fontstyle='italic')
    ax.text(0.5, 0.808, 'VERIFIED PERFORMANCE  ·  LIVE ACCOUNT  ·  NOT DEMO',
            fontsize=9, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')
    _gold_line(ax, 0.788)

    # Donut
    ax_d = fig.add_axes([0.28, 0.42, 0.44, 0.36], aspect='equal')
    ax_d.set_facecolor(NAVY)
    wins = max(0, min(win_rate / 100, 1))
    ax_d.pie([wins, 1 - wins], colors=[GOLD, NAVY_L], startangle=90,
             counterclock=False,
             wedgeprops={'width': 0.36, 'edgecolor': NAVY, 'linewidth': 2.5})
    ax_d.text(0, 0.12, f'{win_rate:.0f}%',
              fontsize=42, fontweight='bold', color=WHITE, ha='center', va='center')
    ax_d.text(0, -0.28, 'WIN RATE',
              fontsize=10, color=MUTED, ha='center', va='center',
              fontfamily='monospace', fontweight='bold')

    # Three stat cards
    stat_items = [
        ('PROFIT FACTOR', f'{pf:.2f}',          GOLD),
        ('TOTAL GAIN',    f'+{gain:.2f}%',        GREEN),
        ('TOTAL TRADES',  f'{trades:,}',           WHITE),
    ]
    cw, ch = 0.26, 0.10
    cy     = 0.285
    for i, (label, value, color) in enumerate(stat_items):
        cx = 0.06 + i * 0.32
        ax.add_patch(patches.FancyBboxPatch(
            (cx, cy), cw, ch, boxstyle='round,pad=0.005',
            facecolor=NAVY_S, edgecolor=GOLD, linewidth=0.7,
            transform=ax.transAxes, zorder=2
        ))
        ax.add_patch(patches.Rectangle(
            (cx, cy + ch - 0.003), cw, 0.003,
            facecolor=color, transform=ax.transAxes, zorder=3
        ))
        ax.text(cx + cw / 2, cy + ch - 0.022, label,
                fontsize=7.5, color=MUTED, ha='center', va='top',
                transform=ax.transAxes, fontfamily='monospace', fontweight='bold')
        ax.text(cx + cw / 2, cy + 0.022, value,
                fontsize=17, color=color, ha='center', va='bottom',
                transform=ax.transAxes, fontweight='bold')

    ax.text(0.5, 0.215,
            f'+{pips:,} pips total  ·  every trade live-verified on Myfxbook',
            fontsize=9, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace')

    ax.text(0.5, 0.162,
            '"Consistent. Algorithmic. Transparent."',
            fontsize=12, color=WHITE, ha='center', va='center',
            transform=ax.transAxes, fontstyle='italic')

    _footer(ax)
    plt.tight_layout(pad=0)
    return fig
