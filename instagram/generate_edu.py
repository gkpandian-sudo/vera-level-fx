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
    from instagram.composer import load_background, gradient_panel

    bg = gradient_panel(load_background(ASSETS_DIR / 'bg-daily.jpg'), height_frac=0.62)

    fig = plt.figure(figsize=SIZE, facecolor=NAVY, dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.imshow(bg, extent=[0, 1, 0, 1], aspect='auto', zorder=0)

    # Gold top bar
    ax.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026, facecolor=GOLD, transform=ax.transAxes, zorder=5
    ))

    # Brand
    ax.text(0.06, 0.946, 'VERA LEVEL FX',
            fontsize=20, fontweight='bold', color=GOLD,
            ha='left', va='center', transform=ax.transAxes, zorder=6)
    ax.add_patch(patches.Circle((0.075, 0.923), 0.007,
        facecolor=GREEN, transform=ax.transAxes, zorder=6))
    ax.text(0.090, 0.923, 'IC Markets Verified  ·  ASIC Regulated',
            fontsize=14, color=GOLD, ha='left', va='center',
            transform=ax.transAxes, zorder=6)

    # Section label + tag (plain text, no box)
    ax.text(0.06, 0.876, 'RISK MANAGEMENT RULE ' + content['rule_num'],
            fontsize=16, color=RED, fontweight='bold', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)
    ax.text(0.94, 0.876, content['tag'],
            fontsize=16, color=RED, fontweight='bold', va='center', ha='right',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)

    _hline(ax, 0.858, alpha=0.30)

    # Rule title — wrap to 2 lines if long so nothing clips at right edge
    title_lines = _wrap(content['title'], 16)
    for ti, tl in enumerate(title_lines[:2]):
        ax.text(0.06, 0.840 - ti * 0.072, tl,
                fontsize=56, fontweight='black', color=WHITE,
                va='top', transform=ax.transAxes, zorder=5, clip_on=True)

    _hline(ax, 0.720, alpha=0.22, color=WHITE)

    # Body text
    body_lines = _wrap(content['body'], 40)
    for i, line in enumerate(body_lines[:4]):
        ax.text(0.06, 0.705 - i * 0.072, line,
                fontsize=32, color=CREAM, va='top',
                transform=ax.transAxes, zorder=5, linespacing=1.5, clip_on=True)

    # Stats — plain text, no boxes
    _hline(ax, 0.315, alpha=0.25)
    ax.text(0.06, 0.292, 'ACCOUNT SIZE',
            fontsize=14, color=DIM, va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)
    ax.text(0.06, 0.258, f'${content["example_account"]:,}',
            fontsize=36, fontweight='bold', color=GOLD, va='center',
            transform=ax.transAxes, zorder=5)

    ax.text(0.52, 0.292, 'MAX RISK / TRADE',
            fontsize=14, color=DIM, va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)
    ax.text(0.52, 0.258, f'${content["example_risk"]:,}',
            fontsize=36, fontweight='bold', color=RED, va='center',
            transform=ax.transAxes, zorder=5)

    ax.text(0.06, 0.215, f'RR  →  {content["example_rr"]}',
            fontsize=18, color=MUTED, va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)

    # CTA
    _hline(ax, 0.196, alpha=0.25)
    ax.text(0.06, 0.162,
            os.environ.get('BRAND_SIGNAL_CTA', '>>  join our live signals channel'),
            fontsize=20, color=MUTED, va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)

    # Footer
    _hline(ax, 0.098, alpha=0.3)
    ax.text(0.94, 0.065, '@veralevel.fx  ·  VERA LEVEL FX',
            fontsize=15, color=GOLD, va='center', ha='right',
            transform=ax.transAxes, fontweight='bold', zorder=5)
    ax.text(0.94, 0.030, 'Not financial advice  ·  IC MARKETS · ASIC',
            fontsize=12, color=DIM, ha='right', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)

    return fig


# ═══════════════════════════════════════════════════════════════════
# Post 2 — Pair Spotlight
# ═══════════════════════════════════════════════════════════════════

def make_pairs_post(content: dict):
    from instagram.composer import load_background, split_layout

    pair = content.get('pair', 'EURUSD').upper()
    bg_key = {
        'EURUSD': 'bg-pairs-eurusd.jpg',
        'XAUUSD': 'bg-pairs-xauusd.jpg',
        'AUDCAD': 'bg-pairs-audcad.jpg',
    }.get(pair, 'bg-pairs-eurusd.jpg')

    # Split: photo top 52%, black panel bottom 48%
    bg, split_y = split_layout(load_background(ASSETS_DIR / bg_key), split_frac=0.52)

    fig = plt.figure(figsize=SIZE, facecolor=NAVY, dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.imshow(bg, extent=[0, 1, 0, 1], aspect='auto', zorder=0)

    # Gold top bar
    ax.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026, facecolor=GOLD, transform=ax.transAxes, zorder=5
    ))
    ax.text(0.5, 0.946, 'VERA LEVEL FX',
            fontsize=18, fontweight='bold', color=GOLD,
            ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)
    ax.text(0.5, 0.916, 'ALGORITHMIC FOREX  ·  IC MARKETS  ·  MYFXBOOK VERIFIED',
            fontsize=13, color=MUTED, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # PAIR SPOTLIGHT label (at top of black panel)
    ax.text(0.06, split_y - 0.028, 'PAIR SPOTLIGHT',
            fontsize=17, color=GOLD, fontweight='bold',
            ha='left', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Pair name hero
    ax.text(0.06, split_y - 0.105, pair,
            fontsize=80, fontweight='black', color=WHITE,
            ha='left', va='center', transform=ax.transAxes, zorder=6)
    ax.text(0.06, split_y - 0.160, content.get('full_name', '').upper(),
            fontsize=18, color=GOLD, fontweight='bold',
            ha='left', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    _hline(ax, split_y - 0.175, alpha=0.3)

    # Stat 2x2 grid
    stats = [
        ('BEST SESSION', content.get('best_session', ''),  GOLD),
        ('AVG SPREAD',   content.get('avg_spread', ''),    GREEN),
        ('VOLATILITY',   content.get('volatility', ''),    AMBER),
        ('MY EDGE',      content.get('my_edge', ''),       WHITE),
    ]
    grid_top = split_y - 0.195
    cw, ch = 0.425, 0.095
    xs = [0.06, 0.515]
    ys = [grid_top, grid_top - 0.108]

    for i, (label, value, color) in enumerate(stats):
        cx, cy = xs[i % 2], ys[i // 2]
        # Label
        ax.text(cx, cy + ch - 0.004, label,
                fontsize=13, color=DIM, fontweight='bold', va='top',
                transform=ax.transAxes, fontfamily='monospace', zorder=6)
        # Value (wrapped, no box)
        val_lines = _wrap(str(value), 38)[:2]
        line_gap = 0.028
        for k, vl in enumerate(val_lines):
            ax.text(cx, cy + ch * 0.52 - k * line_gap, vl,
                    fontsize=14, color=color, fontweight='bold', va='top',
                    transform=ax.transAxes, zorder=6, clip_on=True)
        # Thin separator line below each cell
        ax.plot([cx, cx + cw], [cy, cy], color=color, linewidth=0.5, alpha=0.20,
                transform=ax.transAxes, zorder=5)

    # CTA
    cta_y = ys[1] - 0.055
    _hline(ax, cta_y + 0.025, alpha=0.2)
    ax.text(0.06, cta_y, 'Trade with raw spreads  →  icmarkets.com/?camp=91936',
            fontsize=16, fontweight='bold', color=GOLD,
            ha='left', va='center', transform=ax.transAxes, zorder=6)

    # Footer
    ax.text(0.94, 0.032, '@veralevel.fx  ·  Not financial advice',
            fontsize=13, color=DIM, ha='right', va='center',
            transform=ax.transAxes, zorder=6)

    return fig


# ═══════════════════════════════════════════════════════════════════
# Post 3 — Trade Setup
# ═══════════════════════════════════════════════════════════════════

def make_setup_post(content: dict):
    from instagram.composer import load_background, split_layout

    # Photo top 42%, dark step panel bottom 58%
    bg, split_y = split_layout(
        load_background(ASSETS_DIR / 'bg-setup.jpg'),
        split_frac=0.42,
    )

    fig = plt.figure(figsize=SIZE, facecolor=NAVY, dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    ax.imshow(bg, extent=[0, 1, 0, 1], aspect='auto', zorder=0)

    direction = content.get('direction', 'LONG')
    dir_color = GREEN if direction == 'LONG' else RED
    dir_icon  = '▲' if direction == 'LONG' else '▼'
    pair      = content.get('pair', '')
    rr        = content.get('rr', '1:2')
    steps     = content.get('steps', [])

    # Gold top bar
    ax.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026, facecolor=GOLD, transform=ax.transAxes, zorder=5
    ))
    ax.text(0.5, 0.946, 'VERA LEVEL FX',
            fontsize=18, fontweight='bold', color=GOLD,
            ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Direction label (no box)
    ax.text(0.06, split_y + 0.027, f'{dir_icon}  {direction} SETUP',
            fontsize=18, fontweight='bold', color=dir_color,
            ha='left', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=6)

    # Pair + setup type label
    ax.text(0.40, split_y + 0.028, f'{pair}  ·  {content.get("setup_type", "")}',
            fontsize=17, color=WHITE, ha='left', va='center',
            transform=ax.transAxes, zorder=6)

    # Steps in black panel
    panel_bottom = 0.130
    usable_h     = split_y - panel_bottom
    step_h       = usable_h / max(len(steps), 1)

    for i, (title, desc) in enumerate(steps[:4]):
        cy = split_y - (i + 0.5) * step_h

        # Circle number
        circ = plt.Circle(
            (0.088, cy + 0.010), 0.030,
            facecolor=(0.04, 0.14, 0.28, 0.85),
            edgecolor=GOLD, linewidth=1.4,
            transform=ax.transAxes, zorder=6
        )
        ax.add_patch(circ)
        ax.text(0.088, cy + 0.010, str(i + 1),
                fontsize=22, fontweight='bold', color=GOLD,
                ha='center', va='center', transform=ax.transAxes, zorder=7)

        # Connector line
        if i < len(steps) - 1:
            ax.plot([0.088, 0.088],
                    [cy + 0.010 - 0.030, cy + 0.010 - step_h + 0.030],
                    color=GOLD, alpha=0.20, linewidth=1.2,
                    transform=ax.transAxes, zorder=5)

        # Title + description
        ax.text(0.136, cy + 0.030, title,
                fontsize=24, fontweight='bold', color=WHITE,
                va='center', transform=ax.transAxes, zorder=6)
        desc_lines = _wrap(desc, 46)
        for j, dl in enumerate(desc_lines[:2]):
            ax.text(0.136, cy - 0.008 - j * 0.038, dl,
                    fontsize=18, color=MUTED, va='top',
                    transform=ax.transAxes, zorder=6, linespacing=1.3)

    # Bottom info (no boxes)
    _hline(ax, panel_bottom + 0.005, alpha=0.25)
    ax.text(0.06, 0.078, 'RISK 1%',
            fontsize=16, fontweight='bold', color=RED,
            va='center', transform=ax.transAxes, fontfamily='monospace', zorder=5)
    ax.text(0.26, 0.078, f'RR {rr}',
            fontsize=16, fontweight='bold', color=dir_color,
            va='center', transform=ax.transAxes, fontfamily='monospace', zorder=5)
    ax.text(0.42, 0.078, 'IC MARKETS',
            fontsize=16, fontweight='bold', color=GOLD,
            va='center', transform=ax.transAxes, fontfamily='monospace', zorder=5)

    # CTA
    ax.text(0.66, 0.078, 'Alerts → t.me/pandiangk',
            fontsize=16, fontweight='bold', color=GOLD,
            ha='left', va='center', transform=ax.transAxes, zorder=6)

    # Footer
    ax.text(0.94, 0.024, '@veralevel.fx  ·  Not financial advice',
            fontsize=12, color=DIM, ha='right', va='center',
            transform=ax.transAxes, zorder=6)

    return fig
