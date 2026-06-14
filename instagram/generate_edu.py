# instagram/generate_edu.py
"""
Matplotlib renderers for the 3 educational Instagram post types.
Each returns a matplotlib Figure at 1080x1080 px (10.8in x 10.8in @ 100 DPI).

Background system:
  - Downloads a thematic Unsplash photo per post type
  - Applies navy gradient + grain overlay
  - Falls back to solid navy #001835 if download fails
"""

import io
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

# Brand palette
NAVY       = '#001835'
NAVY_DEEP  = '#000e20'
NAVY_MID   = '#002a54'
GOLD       = '#D4AF37'
GOLD_B     = '#EAC84A'
WHITE      = '#f0eee8'
MUTED      = '#8BADD4'
DIM        = '#4A6A9B'
GREEN      = '#4ade80'
RED        = '#fca5a5'

SIZE = (10.8, 10.8)
DPI  = 100

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / 'assets'

BG_FILES = {
    'risk':  ASSETS_DIR / 'bg-risk.png',
    'pairs': ASSETS_DIR / 'bg-pairs.png',
    'setup': ASSETS_DIR / 'bg-setup.png',
}


def _fetch_bg(post_type: str):
    """Load Canva background PNG, return numpy RGBA array (1080,1080,4) 0-1, or None."""
    try:
        from PIL import Image
        path = BG_FILES.get(post_type, BG_FILES['risk'])
        img  = Image.open(path).convert('RGBA')
        img  = img.resize((1080, 1080), Image.LANCZOS)
        arr  = np.array(img) / 255.0
        # Darken slightly so the Canva geometry shows as subtle texture,
        # then the navy gradient overlay (zorder=1) sits cleanly on top.
        arr[..., :3] *= 0.55
        return arr
    except Exception:
        return None


def _base_fig(post_type: str):
    """Create figure with background image + navy gradient + grain overlay."""
    fig = plt.figure(figsize=SIZE, facecolor=NAVY_DEEP, dpi=DPI)

    ax_bg = fig.add_axes([0, 0, 1, 1])
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')

    bg_arr = _fetch_bg(post_type)
    if bg_arr is not None:
        ax_bg.imshow(bg_arr, extent=[0, 1, 0, 1], aspect='auto', origin='upper',
                     zorder=0, alpha=0.7)

    grad = np.linspace(0, 1, 256).reshape(256, 1)
    cmap = LinearSegmentedColormap.from_list('navy_fade', [
        (0.00, (0.000, 0.055, 0.125, 0.95)),
        (0.45, (0.000, 0.098, 0.196, 0.87)),
        (1.00, (0.000, 0.035, 0.078, 0.75)),
    ])
    ax_bg.imshow(grad, extent=[0, 1, 0, 1], aspect='auto', origin='upper',
                 cmap=cmap, alpha=1.0, zorder=1)

    rng = np.random.default_rng(42)
    gx  = rng.uniform(0, 1, 12000)
    gy  = rng.uniform(0, 1, 12000)
    ax_bg.scatter(gx, gy, s=0.12, color='white', alpha=0.035, linewidths=0, zorder=2)

    for v in np.arange(0, 1, 0.08):
        ax_bg.axhline(v, color=GOLD, alpha=0.025, linewidth=0.5, zorder=2)
        ax_bg.axvline(v, color=GOLD, alpha=0.025, linewidth=0.5, zorder=2)

    ax_bg.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026,
        facecolor=GOLD, transform=ax_bg.transAxes, zorder=3
    ))

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor('none')

    return fig, ax


def _brand_header(ax):
    ax.add_patch(patches.FancyBboxPatch(
        (0.06, 0.922), 0.27, 0.034,
        boxstyle='round,pad=0.005',
        facecolor=(0.0, 0.094, 0.208, 0.6), edgecolor=GOLD,
        linewidth=0.8, transform=ax.transAxes, zorder=5
    ))
    ax.text(0.195, 0.939, 'VERA LEVEL FX',
            fontsize=7, fontweight='bold', color=GOLD,
            ha='center', va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)
    ax.scatter([0.915], [0.939], s=28, color=GREEN, zorder=6,
               transform=ax.transAxes)
    ax.text(0.93, 0.939, 'LIVE',
            fontsize=7, color=GREEN, fontweight='bold',
            va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)


def _footer(ax):
    ax.plot([0.06, 0.94], [0.082, 0.082], color=GOLD, linewidth=0.8,
            alpha=0.4, transform=ax.transAxes, zorder=4)
    ax.text(0.06, 0.052, 'VERA LEVEL FX · @veralevel.fx',
            fontsize=7.5, color=GOLD, va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)
    ax.text(0.94, 0.052, 'IC MARKETS · ASIC',
            fontsize=7.5, color=DIM, va='center', ha='right',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)
    ax.text(0.5, 0.022, 'Not financial advice · vera-level-forex.vercel.app',
            fontsize=6.5, color=DIM, ha='center', va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)


def _glass_card(ax, x, y, w, h, accent_color=GOLD):
    ax.add_patch(patches.FancyBboxPatch(
        (x, y), w, h, boxstyle='round,pad=0.008',
        facecolor=(0.0, 0.09, 0.2, 0.55),
        edgecolor=accent_color, linewidth=0.7,
        transform=ax.transAxes, zorder=4
    ))
    ax.add_patch(patches.Rectangle(
        (x, y), 0.004, h,
        facecolor=accent_color, alpha=0.7,
        transform=ax.transAxes, zorder=5
    ))


def _wrap(text: str, width: int) -> list:
    words   = text.split()
    lines   = []
    current = ''
    for word in words:
        if len(current) + len(word) + 1 <= width:
            current = (current + ' ' + word).strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_risk_post(content: dict):
    fig, ax = _base_fig('risk')
    _brand_header(ax)

    ax.text(0.95, 0.62, content['rule_num'],
            fontsize=180, color='white', alpha=0.04,
            ha='right', va='center', transform=ax.transAxes,
            fontweight='bold', zorder=3)

    ax.text(0.06, 0.895,
            'WARNING  RISK MANAGEMENT · RULE ' + content['rule_num'],
            fontsize=8, color=RED, fontweight='bold',
            va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=5, alpha=0.9)

    ax.add_patch(patches.FancyBboxPatch(
        (0.06, 0.844), 0.13, 0.030,
        boxstyle='round,pad=0.006',
        facecolor=(0.59, 0.2, 0.2, 0.18),
        edgecolor=(0.99, 0.64, 0.64, 0.4),
        linewidth=0.8, transform=ax.transAxes, zorder=5
    ))
    ax.text(0.125, 0.859, content['tag'],
            fontsize=7, color=RED, fontweight='bold',
            ha='center', va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)

    ax.text(0.06, 0.81, content['title'],
            fontsize=32, fontweight='black', color=WHITE,
            va='top', transform=ax.transAxes, zorder=5,
            linespacing=1.1)

    body_lines = _wrap(content['body'], 48)
    for i, line in enumerate(body_lines[:3]):
        ax.text(0.06, 0.71 - i * 0.055, line,
                fontsize=10.5, color=MUTED, va='top',
                transform=ax.transAxes, zorder=5, linespacing=1.6)

    card_y = 0.44
    card_h = 0.10

    _glass_card(ax, 0.06, card_y, 0.40, card_h, RED)
    ax.text(0.085, card_y + card_h - 0.015, 'ACCOUNT',
            fontsize=7.5, color=RED, fontweight='bold',
            va='top', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)
    ax.text(0.085, card_y + 0.018,
            f'${content["example_account"]:,} -> ${content["example_risk"]:,} max risk',
            fontsize=10, color=WHITE, fontweight='bold',
            va='bottom', transform=ax.transAxes, zorder=6)

    _glass_card(ax, 0.54, card_y, 0.40, card_h, GOLD)
    ax.text(0.565, card_y + card_h - 0.015, 'RATIO',
            fontsize=7.5, color=GOLD, fontweight='bold',
            va='top', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)
    rr_text = (f'${content["example_target"]:,} target'
               if content['example_target'] else content['example_rr'])
    ax.text(0.565, card_y + 0.018, rr_text,
            fontsize=10, color=WHITE, fontweight='bold',
            va='bottom', transform=ax.transAxes, zorder=6)

    ax.text(0.06, 0.30,
            't.me/pandiangk  Join for live signals',
            fontsize=9, color=MUTED, va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)

    _footer(ax)
    plt.tight_layout(pad=0)
    return fig


def make_pairs_post(content: dict):
    fig, ax = _base_fig('pairs')
    _brand_header(ax)

    ax.text(0.06, 0.895, 'PAIR SPOTLIGHT · WEEKLY',
            fontsize=8, color=GOLD, fontweight='bold',
            va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=5, alpha=0.8)

    ax.add_patch(patches.Rectangle(
        (0.06, 0.860), 0.06, 0.003,
        facecolor=GOLD, transform=ax.transAxes, zorder=5
    ))

    ax.text(0.06, 0.845, content['pair'],
            fontsize=68, fontweight='black', color=WHITE,
            va='top', transform=ax.transAxes, zorder=5)

    ax.text(0.06, 0.72, content['full_name'].upper(),
            fontsize=9, color=GOLD, fontweight='bold',
            va='top', transform=ax.transAxes,
            fontfamily='monospace', zorder=5, alpha=0.8)

    ax.plot([0.06, 0.94], [0.69, 0.69], color=GOLD,
            linewidth=0.8, alpha=0.3, transform=ax.transAxes, zorder=4)

    stat_data = [
        ('BEST SESSION', content['best_session'], WHITE),
        ('AVG SPREAD',   content['avg_spread'],   GOLD),
        ('VOLATILITY',   content['volatility'],   GOLD),
        ('MY EDGE',      content['my_edge'],      GREEN),
    ]
    xs = [0.06, 0.52]
    ys = [0.555, 0.42]
    cw, ch = 0.40, 0.115

    for i, (label, value, color) in enumerate(stat_data):
        cx = xs[i % 2]
        cy = ys[i // 2]
        _glass_card(ax, cx, cy, cw, ch, color)
        ax.text(cx + 0.025, cy + ch - 0.014, label,
                fontsize=7, color=MUTED, fontweight='bold',
                va='top', transform=ax.transAxes,
                fontfamily='monospace', zorder=6)
        ax.text(cx + 0.025, cy + 0.018, value,
                fontsize=13, color=color, fontweight='bold',
                va='bottom', transform=ax.transAxes, zorder=6)

    ax.plot([0.06, 0.06], [0.21, 0.30], color=GOLD,
            linewidth=2, alpha=0.45, transform=ax.transAxes, zorder=4)
    quote_lines = _wrap(f'"{content["quote"]}"', 52)
    for i, line in enumerate(quote_lines[:3]):
        ax.text(0.085, 0.295 - i * 0.042, line,
                fontsize=10, color=MUTED, va='top',
                transform=ax.transAxes, zorder=5,
                style='italic', linespacing=1.5)
    ax.text(0.085, 0.175, '— Pandian, Vera Level FX',
            fontsize=8.5, color=DIM, va='top',
            transform=ax.transAxes, zorder=5)

    _footer(ax)
    plt.tight_layout(pad=0)
    return fig


def make_setup_post(content: dict):
    fig, ax = _base_fig('setup')
    _brand_header(ax)

    direction_color = GREEN if content['direction'] == 'LONG' else RED
    direction_arrow = 'UP' if content['direction'] == 'LONG' else 'DOWN'

    ax.add_patch(patches.FancyBboxPatch(
        (0.06, 0.882), 0.20, 0.030,
        boxstyle='round,pad=0.005',
        facecolor=(0.1, 0.42, 0.22, 0.15) if content['direction'] == 'LONG'
                  else (0.42, 0.1, 0.1, 0.15),
        edgecolor=direction_color, linewidth=0.8,
        transform=ax.transAxes, zorder=5
    ))
    ax.text(0.16, 0.897,
            f'{direction_arrow}  {content["direction"]} SETUP',
            fontsize=8, color=direction_color, fontweight='bold',
            ha='center', va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)

    ax.text(0.06, 0.875, content['pair'],
            fontsize=52, fontweight='black', color=WHITE,
            va='top', transform=ax.transAxes, zorder=5)
    ax.text(0.06, 0.77, content['setup_type'],
            fontsize=16, color=MUTED, va='top',
            transform=ax.transAxes, style='italic', zorder=5)

    ax.text(0.06, 0.735, content['timeframe'] + '  RR ' + content['rr'],
            fontsize=8, color=direction_color, va='top',
            transform=ax.transAxes, fontfamily='monospace',
            fontweight='bold', zorder=5, alpha=0.8)

    step_top = 0.660
    circle_r  = 0.022
    step_gap  = 0.155

    for i, (title, desc) in enumerate(content['steps']):
        cy = step_top - i * step_gap
        circle = plt.Circle(
            (0.085, cy), circle_r,
            facecolor=(0.07, 0.17, 0.3, 0.7),
            edgecolor=GOLD, linewidth=1.2,
            transform=ax.transAxes, zorder=5
        )
        ax.add_patch(circle)
        ax.text(0.085, cy, str(i + 1),
                fontsize=10, fontweight='bold', color=GOLD,
                ha='center', va='center', transform=ax.transAxes, zorder=6)
        if i < len(content['steps']) - 1:
            ax.plot([0.085, 0.085],
                    [cy - circle_r, cy - step_gap + circle_r],
                    color=GOLD, alpha=0.2, linewidth=0.8,
                    transform=ax.transAxes, zorder=4)
        ax.text(0.125, cy + 0.012, title,
                fontsize=11, fontweight='bold', color=WHITE,
                va='center', transform=ax.transAxes, zorder=5)
        ax.text(0.125, cy - 0.022, desc,
                fontsize=9, color=MUTED, va='top',
                transform=ax.transAxes, zorder=5, linespacing=1.4)

    pill_data = [
        ('RISK 1%',          RED,            (0.59, 0.18, 0.18, 0.15)),
        ('RR ' + content['rr'], direction_color, (0.1, 0.42, 0.22, 0.15)),
        ('IC MARKETS',       GOLD,           (0.12, 0.10, 0.02, 0.15)),
    ]
    pill_x = 0.06
    for label, color, face in pill_data:
        w = max(0.12, len(label) * 0.012 + 0.04)
        ax.add_patch(patches.FancyBboxPatch(
            (pill_x, 0.175), w, 0.038,
            boxstyle='round,pad=0.005',
            facecolor=face, edgecolor=color, linewidth=0.8,
            transform=ax.transAxes, zorder=5
        ))
        ax.text(pill_x + w / 2, 0.194, label,
                fontsize=8, color=color, fontweight='bold',
                ha='center', va='center', transform=ax.transAxes,
                fontfamily='monospace', zorder=6)
        pill_x += w + 0.015

    _footer(ax)
    plt.tight_layout(pad=0)
    return fig
