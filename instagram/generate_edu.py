# instagram/generate_edu.py
"""
Educational post renderers — Vera Level FX.
1080×1080 px @ 100 DPI.

Mobile-first font scale (image shown at ~35% on phone screen):
  footer    20pt → 7pt on phone  (acceptable for disclaimers)
  label     26pt → 9pt           (secondary info)
  body      34pt → 12pt          (comfortable reading)
  sub-head  48pt → 17pt          (clear hierarchy)
  headline  72pt → 25pt          (dominant)
  display   96pt → 33pt          (pair names, big numbers)
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

# ── Brand palette ─────────────────────────────────────────────────
NAVY   = '#010E1F'   # deepened for better contrast
NAVY_S = '#051830'
NAVY_L = '#0A2545'
GOLD   = '#F0C040'   # brighter gold — more visible on mobile
WHITE  = '#FFFFFF'
CREAM  = '#F0EEE8'
MUTED  = '#B8CFEA'   # lightened — was too dim at 8BADD4
DIM    = '#6A8EB8'
GREEN  = '#00E096'   # vivid green
RED    = '#FF6B6B'   # vivid red
AMBER  = '#FFA040'

SIZE = (10.8, 10.8)
DPI  = 100

ASSETS_DIR = Path(__file__).resolve().parent / 'assets'
BG_FILES = {
    'risk':  ASSETS_DIR / 'bg-risk.png',
    'pairs': ASSETS_DIR / 'bg-pairs.png',
    'setup': ASSETS_DIR / 'bg-setup.png',
}


_NAVY_RGB = np.array([0.004, 0.055, 0.122])  # NAVY colour for pre-blend

def _load_bg(post_type: str):
    """Return a pre-blended RGB array: 5% Canva texture + 95% navy.

    Pre-blending in numpy avoids matplotlib alpha-compositing quirks that
    allow Canva template text to bleed through even with overlay patches.
    """
    try:
        from PIL import Image
        path = BG_FILES.get(post_type, BG_FILES['risk'])
        img  = Image.open(path).convert('RGB')        # drop alpha channel
        img  = img.resize((1080, 1080), Image.LANCZOS)
        arr  = np.array(img, dtype=np.float32) / 255.0
        # Blend: 5% Canva content (too dark to read) + 95% navy
        blended = arr * 0.05 + _NAVY_RGB * 0.95
        return np.clip(blended, 0, 1)
    except Exception:
        return None


def _base_fig(post_type: str):
    """Figure with Canva texture + deep navy gradient + grain overlay."""
    fig = plt.figure(figsize=SIZE, facecolor=NAVY, dpi=DPI)

    ax_bg = fig.add_axes([0, 0, 1, 1])
    ax_bg.set_xlim(0, 1); ax_bg.set_ylim(0, 1); ax_bg.axis('off')

    bg = _load_bg(post_type)
    if bg is not None:
        ax_bg.imshow(bg, extent=[0, 1, 0, 1], aspect='auto',
                     origin='upper', zorder=0)

    # Deep navy gradient overlay (ensures readability)
    grad = np.linspace(0, 1, 512).reshape(512, 1)
    cmap = LinearSegmentedColormap.from_list('fade', [
        (0.00, (0.004, 0.055, 0.122, 0.97)),
        (0.40, (0.005, 0.09,  0.196, 0.93)),
        (1.00, (0.002, 0.04,  0.09,  0.88)),
    ])
    ax_bg.imshow(grad, extent=[0, 1, 0, 1], aspect='auto',
                 origin='upper', cmap=cmap, zorder=2)

    # Subtle grain
    rng = np.random.default_rng(7)
    ax_bg.scatter(rng.uniform(0, 1, 8000), rng.uniform(0, 1, 8000),
                  s=0.1, color='white', alpha=0.03, linewidths=0, zorder=2)

    # Fine grid lines (barely visible — adds depth)
    for v in np.arange(0.1, 1.0, 0.1):
        ax_bg.plot([0, 1], [v, v], color=GOLD, alpha=0.018, linewidth=0.5, zorder=2)
        ax_bg.plot([v, v], [0, 1], color=GOLD, alpha=0.018, linewidth=0.5, zorder=2)

    # Top gold bar
    ax_bg.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026, facecolor=GOLD,
        transform=ax_bg.transAxes, zorder=3
    ))

    # Content axes
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off'); ax.set_facecolor('none')
    return fig, ax


def _hline(ax, y, x0=0.06, x1=0.94, color=GOLD, alpha=0.45, lw=1.2):
    ax.plot([x0, x1], [y, y], color=color, linewidth=lw,
            alpha=alpha, transform=ax.transAxes, zorder=4)


def _brand_header(ax):
    """Brand strip just below the gold bar."""
    ax.text(0.5, 0.946, 'VERA LEVEL FX',
            fontsize=22, fontweight='bold', color=GOLD,
            ha='center', va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)
    ax.text(0.5, 0.916, 'ALGORITHMIC FOREX  ·  IC MARKETS  ·  MYFXBOOK VERIFIED',
            fontsize=15, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)
    _hline(ax, 0.898, alpha=0.4)


def _footer(ax):
    _hline(ax, 0.095, alpha=0.4)
    ax.text(0.06, 0.065, '@veralevel.fx  ·  VERA LEVEL FX',
            fontsize=15, color=GOLD, va='center',
            transform=ax.transAxes, fontfamily='monospace',
            fontweight='bold', zorder=5)
    ax.text(0.94, 0.065, 'IC MARKETS · ASIC',
            fontsize=15, color=MUTED, va='center', ha='right',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)
    ax.text(0.5, 0.030, 'Not financial advice  ·  vera-level-forex.vercel.app',
            fontsize=18, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)


def _pill(ax, x, y, w, h, label, border_color):
    ax.add_patch(patches.FancyBboxPatch(
        (x, y), w, h, boxstyle='round,pad=0.008',
        facecolor=(0.0, 0.08, 0.18, 0.55),
        edgecolor=border_color, linewidth=1.2,
        transform=ax.transAxes, zorder=5
    ))
    ax.text(x + w / 2, y + h / 2, label,
            fontsize=22, color=border_color, fontweight='bold',
            ha='center', va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)


def _glass_card(ax, x, y, w, h, label, value, val_color, sub=''):
    """Metric card: label on top, large value, optional sub-label."""
    ax.add_patch(patches.FancyBboxPatch(
        (x, y), w, h, boxstyle='round,pad=0.008',
        facecolor=(0.02, 0.10, 0.22, 0.65),
        edgecolor=val_color, linewidth=1.0,
        transform=ax.transAxes, zorder=5
    ))
    # left accent bar
    ax.add_patch(patches.Rectangle(
        (x, y), 0.005, h, facecolor=val_color, alpha=0.8,
        transform=ax.transAxes, zorder=6
    ))
    pad = 0.022
    ax.text(x + pad, y + h - 0.018, label,
            fontsize=21, color=MUTED, fontweight='bold', va='top',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)
    ax.text(x + pad, y + h * 0.4, value,
            fontsize=34, color=val_color, fontweight='bold', va='center',
            transform=ax.transAxes, zorder=6)
    if sub:
        ax.text(x + pad, y + 0.014, sub,
                fontsize=20, color=DIM, va='bottom',
                transform=ax.transAxes, fontfamily='monospace', zorder=6)


def _wrap(text: str, width: int) -> list[str]:
    words, lines, cur = text.split(), [], ''
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + ' ' + w).strip()
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines


# ═══════════════════════════════════════════════════════════════════
# Post 1 — Risk Management
# ═══════════════════════════════════════════════════════════════════

def make_risk_post(content: dict):
    fig, ax = _base_fig('risk')
    _brand_header(ax)

    # Huge watermark number
    ax.text(0.92, 0.55, content['rule_num'],
            fontsize=260, color='white', alpha=0.03,
            ha='right', va='center', transform=ax.transAxes,
            fontweight='bold', zorder=3)

    # Section label + tag pill
    ax.text(0.06, 0.876, '⚠  RISK MANAGEMENT RULE ' + content['rule_num'],
            fontsize=22, color=RED, fontweight='bold', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)
    _pill(ax, 0.71, 0.856, 0.23, 0.038, content['tag'], RED)

    _hline(ax, 0.848, alpha=0.35)

    # Rule title
    ax.text(0.06, 0.830, content['title'],
            fontsize=58, fontweight='black', color=WHITE,
            va='top', transform=ax.transAxes, zorder=5,
            linespacing=1.05)

    _hline(ax, 0.710, alpha=0.25, color=WHITE)

    # Body text — wrap at 40 chars, max 4 lines
    body_lines = _wrap(content['body'], 40)
    for i, line in enumerate(body_lines[:4]):
        ax.text(0.06, 0.695 - i * 0.072, line,
                fontsize=32, color=CREAM, va='top',
                transform=ax.transAxes, zorder=5, linespacing=1.5)

    # Stat cards
    _glass_card(ax, 0.06, 0.305, 0.415, 0.140,
                'ACCOUNT SIZE', f'${content["example_account"]:,}',
                GOLD, 'example capital')
    _glass_card(ax, 0.525, 0.305, 0.415, 0.140,
                'MAX RISK / TRADE', f'${content["example_risk"]:,}',
                RED, f'RR → {content["example_rr"]}')

    _hline(ax, 0.295, alpha=0.3)

    # CTA
    ax.text(0.06, 0.242,
            os.environ.get('BRAND_SIGNAL_CTA', '>>  join our live signals channel'),
            fontsize=26, color=MUTED, va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)

    _footer(ax)
    return fig


# ═══════════════════════════════════════════════════════════════════
# Post 2 — Pair Spotlight
# ═══════════════════════════════════════════════════════════════════

def make_pairs_post(content: dict):
    fig, ax = _base_fig('pairs')
    _brand_header(ax)

    # Section label
    ax.text(0.06, 0.876, 'PAIR SPOTLIGHT',
            fontsize=24, color=GOLD, fontweight='bold', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5, alpha=0.9)
    _hline(ax, 0.858, x0=0.06, x1=0.35, alpha=0.6)

    # Pair name (huge display)
    ax.text(0.06, 0.840, content['pair'],
            fontsize=96, fontweight='black', color=WHITE,
            va='top', transform=ax.transAxes, zorder=5, linespacing=1.0)

    ax.text(0.06, 0.735, content['full_name'].upper(),
            fontsize=26, color=GOLD, fontweight='bold', va='top',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)

    _hline(ax, 0.710, alpha=0.4)

    # Stat cards — 2 columns × 2 rows
    stat_data = [
        ('BEST SESSION', content['best_session'],  GOLD),
        ('AVG SPREAD',   content['avg_spread'],    GREEN),
        ('VOLATILITY',   content['volatility'],    AMBER),
        ('MY EDGE',      _wrap(content['my_edge'], 18)[0],  WHITE),
    ]
    cw, ch = 0.425, 0.120
    xs = [0.06, 0.515]
    ys = [0.570, 0.430]

    for i, (label, value, color) in enumerate(stat_data):
        cx, cy = xs[i % 2], ys[i // 2]
        ax.add_patch(patches.FancyBboxPatch(
            (cx, cy), cw, ch, boxstyle='round,pad=0.008',
            facecolor=(0.02, 0.10, 0.22, 0.70),
            edgecolor=color, linewidth=1.2,
            transform=ax.transAxes, zorder=5
        ))
        ax.add_patch(patches.Rectangle(
            (cx, cy + ch - 0.006), cw, 0.006,
            facecolor=color, alpha=0.9,
            transform=ax.transAxes, zorder=6
        ))
        ax.text(cx + 0.018, cy + ch - 0.022, label,
                fontsize=20, color=MUTED, fontweight='bold', va='top',
                transform=ax.transAxes, fontfamily='monospace', zorder=6)
        ax.text(cx + 0.018, cy + 0.016, value,
                fontsize=22, color=color, fontweight='bold', va='bottom',
                transform=ax.transAxes, zorder=6)

    _hline(ax, 0.415, alpha=0.35)

    # Quote
    ax.plot([0.06, 0.06], [0.220, 0.395], color=GOLD,
            linewidth=3, alpha=0.5, transform=ax.transAxes, zorder=4)
    quote_lines = _wrap(f'"{content["quote"]}"', 46)
    for i, line in enumerate(quote_lines[:3]):
        ax.text(0.092, 0.388 - i * 0.058, line,
                fontsize=28, color=CREAM, va='top', style='italic',
                transform=ax.transAxes, zorder=5, linespacing=1.4)
    ax.text(0.092, 0.210, f'— {os.environ.get("BRAND_AUTHOR", "Vera Level FX")}',
            fontsize=24, color=DIM, va='top',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)

    _footer(ax)
    return fig


# ═══════════════════════════════════════════════════════════════════
# Post 3 — Trade Setup
# ═══════════════════════════════════════════════════════════════════

def make_setup_post(content: dict):
    fig, ax = _base_fig('setup')
    _brand_header(ax)

    dir_color = GREEN if content['direction'] == 'LONG' else RED
    dir_icon  = '▲' if content['direction'] == 'LONG' else '▼'

    # Direction badge
    _pill(ax, 0.06, 0.856, 0.245, 0.038,
          f'{dir_icon}  {content["direction"]} SETUP', dir_color)

    # Pair + timeframe + RR
    ax.text(0.06, 0.843, content['pair'],
            fontsize=82, fontweight='black', color=WHITE,
            va='top', transform=ax.transAxes, zorder=5)

    ax.text(0.06, 0.755, content['setup_type'],
            fontsize=28, color=MUTED, va='top', style='italic',
            transform=ax.transAxes, zorder=5)

    ax.text(0.06, 0.722,
            content['timeframe'] + '  ·  RR ' + content['rr'],
            fontsize=24, color=dir_color, fontweight='bold', va='top',
            transform=ax.transAxes, fontfamily='monospace', zorder=5, alpha=0.9)

    _hline(ax, 0.708, alpha=0.4)

    # Steps — evenly space 4 steps in the content zone
    steps = content['steps']
    n = len(steps)
    zone_top, zone_bot = 0.698, 0.175
    step_h = (zone_top - zone_bot) / n

    for i, (title, desc) in enumerate(steps):
        cy = zone_top - (i + 0.5) * step_h  # centre of this step slot

        # Circle number
        circle = plt.Circle(
            (0.082, cy + 0.02), 0.032,
            facecolor=(0.04, 0.15, 0.30, 0.75),
            edgecolor=GOLD, linewidth=1.5,
            transform=ax.transAxes, zorder=6
        )
        ax.add_patch(circle)
        ax.text(0.082, cy + 0.02, str(i + 1),
                fontsize=26, fontweight='bold', color=GOLD,
                ha='center', va='center', transform=ax.transAxes, zorder=7)

        # Connector line between circles
        if i < n - 1:
            ax.plot([0.082, 0.082],
                    [cy + 0.02 - 0.032, cy + 0.02 - step_h + 0.032],
                    color=GOLD, alpha=0.22, linewidth=1.2,
                    transform=ax.transAxes, zorder=5)

        # Step title + description
        ax.text(0.133, cy + 0.048, title,
                fontsize=30, fontweight='bold', color=WHITE,
                va='center', transform=ax.transAxes, zorder=5)
        desc_lines = _wrap(desc, 44)
        for j, dl in enumerate(desc_lines[:2]):
            ax.text(0.133, cy - 0.003 - j * 0.042, dl,
                    fontsize=24, color=MUTED, va='top',
                    transform=ax.transAxes, zorder=5, linespacing=1.3)

    # Bottom pills
    _hline(ax, 0.168, alpha=0.3)
    pill_items = [
        ('RISK 1%',           RED,      0.06),
        ('RR ' + content['rr'], dir_color, 0.24),
        ('IC MARKETS',        GOLD,     0.42),
    ]
    for label, color, px in pill_items:
        _pill(ax, px, 0.115, 0.165, 0.042, label, color)

    _footer(ax)
    return fig
