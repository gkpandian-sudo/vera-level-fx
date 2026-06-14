# Instagram Rotating Content Library — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 2 fully-automated educational Instagram posts per week (Tue/Thu 9am SGT) to the existing pipeline, rotating across a 6-week content library of Risk Management, Pair Spotlight, and Trade Setup posts.

**Architecture:** A new `edu_content.py` holds all 13 content variants and the 12-slot rotation sequence. `generate_edu.py` renders each variant to a 1080×1080 matplotlib figure with a Unsplash photo background (navy overlay + grain). `run.py` reads/increments `data/edu-counter.json` to pick the next variant, generates the image, commits the counter, and publishes.

**Tech Stack:** Python 3.11, matplotlib 3.8, Pillow 10.3, requests 2.31, GitHub Actions, Meta Graph API v19.0

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `instagram/edu_content.py` | All content data + 12-slot rotation sequence |
| Create | `instagram/generate_edu.py` | Matplotlib renderers for risk/pairs/setup post types |
| Create | `data/edu-counter.json` | Rotation position (single int, committed to repo) |
| Create | `instagram/tests/test_edu.py` | Unit tests for content library + counter logic |
| Modify | `instagram/run.py` | Add edu routing, counter read/increment/commit |
| Modify | `.github/workflows/insta-post.yml` | Add Tue/Thu cron + edu dispatch option |

---

## Task 1 — Content library (`edu_content.py`)

**Files:**
- Create: `instagram/edu_content.py`

- [ ] **Step 1: Create `instagram/edu_content.py` with full content library**

```python
# instagram/edu_content.py

RISK_RULES = [
    {
        "rule_num": "01",
        "title": "The 1% Rule",
        "body": "Never risk more than 1% of your account on a single trade. One bad trade should never wipe your week.",
        "example_account": 10000,
        "example_risk": 100,
        "example_rr": "1:2.5",
        "example_target": 250,
        "tag": "ESSENTIAL",
    },
    {
        "rule_num": "02",
        "title": "Daily Drawdown Limit",
        "body": "If you're down 3% in a single day, close everything and stop trading. Protect the week, not the session.",
        "example_account": 10000,
        "example_risk": 300,
        "example_rr": "Daily limit",
        "example_target": 0,
        "tag": "PROTECTION",
    },
    {
        "rule_num": "03",
        "title": "ATR-Based Position Sizing",
        "body": "Let the market's volatility decide your lot size — not your gut. High ATR = smaller lots. Low ATR = larger lots.",
        "example_account": 10000,
        "example_risk": 100,
        "example_rr": "ATR × multiplier",
        "example_target": 0,
        "tag": "SIZING",
    },
    {
        "rule_num": "04",
        "title": "Minimum Risk:Reward",
        "body": "Only take trades offering at least 1:2 RR. If the reward doesn't justify the risk, skip the trade. Always.",
        "example_account": 10000,
        "example_risk": 100,
        "example_rr": "1:2 minimum",
        "example_target": 200,
        "tag": "SELECTION",
    },
    {
        "rule_num": "05",
        "title": "No News Trading",
        "body": "High-impact news (NFP, CPI, FOMC) creates random spikes that invalidate technical setups. Sit out or close early.",
        "example_account": 10000,
        "example_risk": 0,
        "example_rr": "Skip the trade",
        "example_target": 0,
        "tag": "DISCIPLINE",
    },
]

PAIRS = [
    {
        "pair": "EURUSD",
        "full_name": "Euro / US Dollar",
        "best_session": "London/NY",
        "avg_spread": "0.1 pip",
        "volatility": "Medium",
        "my_edge": "H4 Trend",
        "quote": "Most liquid pair in the world. Clean structure, respects levels — my bread and butter.",
    },
    {
        "pair": "GBPJPY",
        "full_name": "British Pound / Japanese Yen",
        "best_session": "London Open",
        "avg_spread": "1.2 pips",
        "volatility": "Very High",
        "my_edge": "Breakout",
        "quote": "The Dragon. Volatile, aggressive, and rewarding when you read the momentum right.",
    },
    {
        "pair": "XAUUSD",
        "full_name": "Gold / US Dollar",
        "best_session": "NY Open",
        "avg_spread": "0.3 pip",
        "volatility": "High",
        "my_edge": "S&R Levels",
        "quote": "Gold rewards patience. Wait for the key level — then strike with full conviction.",
    },
    {
        "pair": "USDJPY",
        "full_name": "US Dollar / Japanese Yen",
        "best_session": "Asian Session",
        "avg_spread": "0.2 pip",
        "volatility": "Low-Med",
        "my_edge": "Range Play",
        "quote": "The Asian session king. Predictable ranges when Tokyo is in control.",
    },
]

SETUPS = [
    {
        "pair": "GBPJPY",
        "direction": "LONG",
        "setup_type": "Trend Continuation",
        "timeframe": "H4 · H1 · M15",
        "rr": "1:2.5",
        "steps": [
            ("H4 Bias — Bullish",  "Price above 20 EMA, higher highs structure confirmed"),
            ("H1 Entry Zone",       "Pullback to key support + bullish engulfing candle"),
            ("M15 Trigger",         "Momentum entry — SL below swing low, TP next H4 resistance"),
        ],
    },
    {
        "pair": "XAUUSD",
        "direction": "SHORT",
        "setup_type": "S&R Reversal",
        "timeframe": "H4 · H1 · M15",
        "rr": "1:2.0",
        "steps": [
            ("H4 Key Resistance",  "Price rejected from major resistance zone — bearish wick"),
            ("H1 Confirmation",     "Lower high formed + bearish engulfing below zone"),
            ("M15 Entry",           "Momentum entry short — SL above wick, TP next S1 level"),
        ],
    },
    {
        "pair": "EURUSD",
        "direction": "LONG",
        "setup_type": "London Breakout",
        "timeframe": "H1 · M15 · M5",
        "rr": "1:2.5",
        "steps": [
            ("Pre-London Range",   "Identify Asia session high/low — mark both levels"),
            ("Breakout Candle",     "London open breaks Asia high with strong momentum candle"),
            ("Retest Entry",        "Wait for pullback to broken level — enter on M5 confirmation"),
        ],
    },
    {
        "pair": "USDJPY",
        "direction": "SHORT",
        "setup_type": "Asian Range Break",
        "timeframe": "H1 · M15",
        "rr": "1:2.0",
        "steps": [
            ("Define Range",       "Mark Asian session high and low (typically 30–60 pip range)"),
            ("False Break Check",   "Price spikes above range then reverses — bearish signal"),
            ("Short on Retest",     "Enter short on retest of range low — SL above range high"),
        ],
    },
]

# 12-slot rotation sequence: (type, index_into_type_list)
# Maps to 6-week Tue/Thu schedule
ROTATION_SEQUENCE = [
    ("risk",  0),   # Week 1 Tue  — Risk: 1% Rule
    ("pairs", 0),   # Week 1 Thu  — Pair: EURUSD
    ("setup", 0),   # Week 2 Tue  — Setup: GBPJPY Trend
    ("risk",  1),   # Week 2 Thu  — Risk: Daily DD Limit
    ("pairs", 2),   # Week 3 Tue  — Pair: XAUUSD
    ("setup", 1),   # Week 3 Thu  — Setup: XAUUSD S&R
    ("risk",  2),   # Week 4 Tue  — Risk: ATR Sizing
    ("pairs", 1),   # Week 4 Thu  — Pair: GBPJPY
    ("setup", 2),   # Week 5 Tue  — Setup: EURUSD Breakout
    ("risk",  3),   # Week 5 Thu  — Risk: RR Minimum
    ("pairs", 3),   # Week 6 Tue  — Pair: USDJPY
    ("setup", 3),   # Week 6 Thu  — Setup: USDJPY Range
]


def get_edu_content(index: int) -> tuple[str, dict]:
    """Return (post_type, content_dict) for the given rotation index."""
    slot = ROTATION_SEQUENCE[index % len(ROTATION_SEQUENCE)]
    post_type, content_index = slot
    if post_type == "risk":
        return post_type, RISK_RULES[content_index]
    if post_type == "pairs":
        return post_type, PAIRS[content_index]
    return post_type, SETUPS[content_index]
```

- [ ] **Step 2: Commit**

```bash
git add instagram/edu_content.py
git commit -m "feat: add educational content library (13 variants, 12-slot rotation)"
```

---

## Task 2 — Unit tests (`tests/test_edu.py`)

**Files:**
- Create: `instagram/tests/__init__.py`
- Create: `instagram/tests/test_edu.py`

- [ ] **Step 1: Create test package init**

```bash
mkdir -p "C:\Users\USER\Downloads\04 - FX Trading\vera-level-fx\instagram\tests"
```

Create `instagram/tests/__init__.py` as an empty file.

- [ ] **Step 2: Write tests**

```python
# instagram/tests/test_edu.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'instagram'))

from edu_content import (
    ROTATION_SEQUENCE, RISK_RULES, PAIRS, SETUPS,
    get_edu_content,
)


def test_rotation_sequence_length():
    assert len(ROTATION_SEQUENCE) == 12


def test_get_edu_content_risk():
    post_type, content = get_edu_content(0)
    assert post_type == "risk"
    assert content["rule_num"] == "01"
    assert "title" in content
    assert "body" in content


def test_get_edu_content_pairs():
    post_type, content = get_edu_content(1)
    assert post_type == "pairs"
    assert content["pair"] == "EURUSD"
    assert "quote" in content


def test_get_edu_content_setup():
    post_type, content = get_edu_content(2)
    assert post_type == "setup"
    assert content["pair"] == "GBPJPY"
    assert len(content["steps"]) == 3


def test_rotation_wraps_at_12():
    type_a, content_a = get_edu_content(0)
    type_b, content_b = get_edu_content(12)
    assert type_a == type_b
    assert content_a == content_b


def test_all_rotation_slots_valid():
    for i in range(12):
        post_type, content = get_edu_content(i)
        assert post_type in ("risk", "pairs", "setup")
        assert isinstance(content, dict)
        assert len(content) > 0


def test_risk_rules_have_required_fields():
    for rule in RISK_RULES:
        for field in ("rule_num", "title", "body", "tag"):
            assert field in rule, f"Missing field '{field}' in rule {rule}"


def test_pairs_have_required_fields():
    for pair in PAIRS:
        for field in ("pair", "full_name", "best_session", "avg_spread", "volatility", "my_edge", "quote"):
            assert field in pair, f"Missing field '{field}' in pair {pair}"


def test_setups_have_required_fields():
    for setup in SETUPS:
        for field in ("pair", "direction", "setup_type", "rr", "steps"):
            assert field in setup, f"Missing field '{field}' in setup {setup}"
        assert len(setup["steps"]) == 3
```

- [ ] **Step 3: Run tests — expect all pass**

```bash
cd "C:\Users\USER\Downloads\04 - FX Trading\vera-level-fx"
pip install pytest -q
pytest instagram/tests/test_edu.py -v
```

Expected output:
```
PASSED test_rotation_sequence_length
PASSED test_get_edu_content_risk
PASSED test_get_edu_content_pairs
PASSED test_get_edu_content_setup
PASSED test_rotation_wraps_at_12
PASSED test_all_rotation_slots_valid
PASSED test_risk_rules_have_required_fields
PASSED test_pairs_have_required_fields
PASSED test_setups_have_required_fields
9 passed in 0.XX s
```

- [ ] **Step 4: Commit**

```bash
git add instagram/tests/__init__.py instagram/tests/test_edu.py
git commit -m "test: add unit tests for educational content library"
```

---

## Task 3 — Visual renderer (`generate_edu.py`)

**Files:**
- Create: `instagram/generate_edu.py`

The renderer downloads a background photo from Unsplash (with a silent fallback to solid navy if unavailable), composites a navy gradient overlay, draws grain via a tiled noise pattern, then renders post content using matplotlib text/patch primitives. Output is always 1080×1080 px (10.8 in × 10.8 in at 100 DPI).

- [ ] **Step 1: Create `instagram/generate_edu.py`**

```python
# instagram/generate_edu.py
"""
Matplotlib renderers for the 3 educational Instagram post types.
Each returns a matplotlib Figure at 1080x1080 px (10.8in × 10.8in @ 100 DPI).

Background system:
  - Downloads a thematic Unsplash photo per post type
  - Applies navy gradient + grain overlay
  - Falls back to solid navy #001835 if download fails
"""

import io
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

# ── Brand palette ─────────────────────────────────────────────────
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
RED_DIM    = '#7f2d2d'

SIZE = (10.8, 10.8)
DPI  = 100

# Unsplash background URLs per post type (w=1200 for quality)
BG_URLS = {
    'risk':  'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=85',
    'pairs': 'https://images.unsplash.com/photo-1642790106117-e829e14a795f?w=1200&q=85',
    'setup': 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&q=85',
}


def _fetch_bg(post_type: str):
    """Return numpy RGBA array (1080,1080,4) or None on failure."""
    try:
        import requests
        from PIL import Image
        url = BG_URLS.get(post_type, BG_URLS['risk'])
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert('RGB')
        img = img.resize((1080, 1080), Image.LANCZOS)
        arr = np.array(img) / 255.0
        # Darken + desaturate to simulate CSS filter(saturate 0.6 brightness 0.5)
        gray = arr.mean(axis=2, keepdims=True)
        arr  = arr * 0.6 + gray * 0.4   # desaturate
        arr  = arr * 0.5                 # darken
        return arr
    except Exception:
        return None


def _base_fig(post_type: str):
    """Create figure with background image + navy gradient + grain overlay."""
    fig = plt.figure(figsize=SIZE, facecolor=NAVY_DEEP, dpi=DPI)

    # Full-canvas axes for bg image
    ax_bg = fig.add_axes([0, 0, 1, 1])
    ax_bg.set_xlim(0, 1)
    ax_bg.set_ylim(0, 1)
    ax_bg.axis('off')

    bg_arr = _fetch_bg(post_type)
    if bg_arr is not None:
        ax_bg.imshow(bg_arr, extent=[0, 1, 0, 1], aspect='auto', origin='upper', zorder=0)

    # Navy gradient overlay
    grad = np.linspace(0, 1, 256).reshape(256, 1)
    cmap = LinearSegmentedColormap.from_list('navy_fade', [
        (0.00, (0.000, 0.055, 0.125, 0.95)),
        (0.45, (0.000, 0.098, 0.196, 0.87)),
        (1.00, (0.000, 0.035, 0.078, 0.75)),
    ])
    ax_bg.imshow(grad, extent=[0, 1, 0, 1], aspect='auto', origin='upper',
                 cmap=cmap, alpha=1.0, zorder=1)

    # Grain texture (tiled dots)
    rng = np.random.default_rng(42)
    gx  = rng.uniform(0, 1, 12000)
    gy  = rng.uniform(0, 1, 12000)
    ax_bg.scatter(gx, gy, s=0.12, color='white', alpha=0.035, linewidths=0, zorder=2)

    # Subtle grid lines
    for v in np.arange(0, 1, 0.08):
        ax_bg.axhline(v, color=GOLD, alpha=0.025, linewidth=0.5, zorder=2)
        ax_bg.axvline(v, color=GOLD, alpha=0.025, linewidth=0.5, zorder=2)

    # Gold top accent bar
    ax_bg.add_patch(patches.Rectangle(
        (0, 0.974), 1, 0.026,
        facecolor=GOLD, transform=ax_bg.transAxes, zorder=3
    ))

    # Content axes (sits on top)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor('none')

    return fig, ax


def _brand_header(ax):
    """VERA LEVEL FX brand chip (top-left) + live dot (top-right)."""
    # Brand chip
    ax.add_patch(patches.FancyBboxPatch(
        (0.06, 0.922), 0.27, 0.034,
        boxstyle='round,pad=0.005',
        facecolor='rgba(0,24,53,0.6)', edgecolor=GOLD,
        linewidth=0.8, transform=ax.transAxes, zorder=5
    ))
    ax.text(0.195, 0.939, 'VERA LEVEL FX',
            fontsize=7, fontweight='bold', color=GOLD,
            ha='center', va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)

    # Live dot
    ax.scatter([0.915], [0.939], s=28, color=GREEN, zorder=6,
               transform=ax.transAxes)
    ax.text(0.93, 0.939, 'LIVE',
            fontsize=7, color=GREEN, fontweight='bold',
            va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)


def _footer(ax):
    """Shared footer: gold divider + brand/handle."""
    ax.axhline(y=0.082, xmin=0.06, xmax=0.94, color=GOLD, linewidth=0.8,
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
    """Frosted glass card rectangle."""
    ax.add_patch(patches.FancyBboxPatch(
        (x, y), w, h, boxstyle='round,pad=0.008',
        facecolor=(0.0, 0.09, 0.2, 0.55),
        edgecolor=accent_color, linewidth=0.7,
        transform=ax.transAxes, zorder=4
    ))
    # Left accent stripe
    ax.add_patch(patches.Rectangle(
        (x, y), 0.004, h,
        facecolor=accent_color, alpha=0.7,
        transform=ax.transAxes, zorder=5
    ))


# ── Renderer 1: Risk Management ──────────────────────────────────

def make_risk_post(content: dict):
    """
    content keys: rule_num, title, body, example_account,
                  example_risk, example_rr, example_target, tag
    """
    fig, ax = _base_fig('risk')
    _brand_header(ax)

    # Giant ghost rule number
    ax.text(0.95, 0.62, content['rule_num'],
            fontsize=180, color='white', alpha=0.04,
            ha='right', va='center', transform=ax.transAxes,
            fontweight='bold', zorder=3)

    # Series label
    ax.text(0.06, 0.895,
            f'⚠  RISK MANAGEMENT · RULE {content["rule_num"]}',
            fontsize=8, color=RED, fontweight='bold',
            va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=5, alpha=0.9)

    # Tag pill
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

    # Headline
    ax.text(0.06, 0.81, content['title'],
            fontsize=32, fontweight='black', color=WHITE,
            va='top', transform=ax.transAxes, zorder=5,
            linespacing=1.1)

    # Body text
    body_lines = _wrap(content['body'], 48)
    for i, line in enumerate(body_lines[:3]):
        ax.text(0.06, 0.71 - i * 0.055, line,
                fontsize=10.5, color=MUTED, va='top',
                transform=ax.transAxes, zorder=5, linespacing=1.6)

    # Example cards
    card_y = 0.44
    card_h = 0.10

    _glass_card(ax, 0.06, card_y, 0.40, card_h, RED)
    ax.text(0.085, card_y + card_h - 0.015, '💰  ACCOUNT',
            fontsize=7.5, color=RED, fontweight='bold',
            va='top', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)
    ax.text(0.085, card_y + 0.018,
            f'${content["example_account"]:,} → ${content["example_risk"]:,} max risk',
            fontsize=10, color=WHITE, fontweight='bold',
            va='bottom', transform=ax.transAxes, zorder=6)

    _glass_card(ax, 0.54, card_y, 0.40, card_h, GOLD)
    ax.text(0.565, card_y + card_h - 0.015, '🎯  RATIO',
            fontsize=7.5, color=GOLD, fontweight='bold',
            va='top', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)
    rr_text = (f'${content["example_target"]:,} target'
               if content["example_target"] else content["example_rr"])
    ax.text(0.565, card_y + 0.018, rr_text,
            fontsize=10, color=WHITE, fontweight='bold',
            va='bottom', transform=ax.transAxes, zorder=6)

    # CTA
    ax.text(0.06, 0.30,
            '📲 t.me/pandiangk  ·  Join for live signals',
            fontsize=9, color=MUTED, va='center',
            transform=ax.transAxes, fontfamily='monospace', zorder=5)

    _footer(ax)
    plt.tight_layout(pad=0)
    return fig


# ── Renderer 2: Pair Spotlight ────────────────────────────────────

def make_pairs_post(content: dict):
    """
    content keys: pair, full_name, best_session, avg_spread,
                  volatility, my_edge, quote
    """
    fig, ax = _base_fig('pairs')
    _brand_header(ax)

    # Series label
    ax.text(0.06, 0.895, '● PAIR SPOTLIGHT · WEEKLY',
            fontsize=8, color=GOLD, fontweight='bold',
            va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=5, alpha=0.8)

    # Gold accent bar
    ax.add_patch(patches.Rectangle(
        (0.06, 0.860), 0.06, 0.003,
        facecolor=GOLD, transform=ax.transAxes, zorder=5
    ))

    # Big pair name
    ax.text(0.06, 0.845, content['pair'],
            fontsize=68, fontweight='black', color=WHITE,
            va='top', transform=ax.transAxes, zorder=5,
            linespacing=1.0)

    # Full name
    ax.text(0.06, 0.72, content['full_name'].upper(),
            fontsize=9, color=GOLD, fontweight='bold',
            va='top', transform=ax.transAxes,
            fontfamily='monospace', zorder=5, alpha=0.8,
            letter_spacing=0.12 if False else None)

    # Divider
    ax.axhline(y=0.69, xmin=0.06, xmax=0.94, color=GOLD,
               linewidth=0.8, alpha=0.3, transform=ax.transAxes, zorder=4)

    # Stat grid (2×2)
    stat_data = [
        ('BEST SESSION',  content['best_session'], WHITE),
        ('AVG SPREAD',    content['avg_spread'],   GOLD),
        ('VOLATILITY',    content['volatility'],   GOLD),
        ('MY EDGE',       content['my_edge'],      GREEN),
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

    # Quote
    ax.axvline(x=0.06, ymin=0.21, ymax=0.30, color=GOLD,
               linewidth=2, alpha=0.45, transform=ax.transAxes, zorder=4)
    quote_lines = _wrap(f'"{content["quote"]}"', 52)
    for i, line in enumerate(quote_lines[:3]):
        ax.text(0.085, 0.295 - i * 0.042, line,
                fontsize=10, color=MUTED, va='top',
                transform=ax.transAxes, zorder=5,
                style='italic', linespacing=1.5)
    ax.text(0.085, 0.175, f'— Pandian, Vera Level FX',
            fontsize=8.5, color=DIM, va='top',
            transform=ax.transAxes, zorder=5)

    _footer(ax)
    plt.tight_layout(pad=0)
    return fig


# ── Renderer 3: Trade Setup ───────────────────────────────────────

def make_setup_post(content: dict):
    """
    content keys: pair, direction, setup_type, timeframe, rr,
                  steps (list of (title, desc) tuples)
    """
    fig, ax = _base_fig('setup')
    _brand_header(ax)

    direction_color = GREEN if content['direction'] == 'LONG' else RED
    direction_arrow = '▲' if content['direction'] == 'LONG' else '▼'

    # Direction badge
    ax.add_patch(patches.FancyBboxPatch(
        (0.06, 0.882), 0.18, 0.030,
        boxstyle='round,pad=0.005',
        facecolor=(0.1, 0.42, 0.22, 0.15) if content['direction'] == 'LONG'
                  else (0.42, 0.1, 0.1, 0.15),
        edgecolor=direction_color, linewidth=0.8,
        transform=ax.transAxes, zorder=5
    ))
    ax.text(0.15, 0.897,
            f'{direction_arrow}  {content["direction"]} SETUP',
            fontsize=8, color=direction_color, fontweight='bold',
            ha='center', va='center', transform=ax.transAxes,
            fontfamily='monospace', zorder=6)

    # Pair + setup type
    ax.text(0.06, 0.875, content['pair'],
            fontsize=52, fontweight='black', color=WHITE,
            va='top', transform=ax.transAxes, zorder=5)
    ax.text(0.06, 0.77, content['setup_type'],
            fontsize=16, color=MUTED, va='top',
            transform=ax.transAxes, style='italic', zorder=5)

    # Timeframe line
    ax.text(0.06, 0.735, content['timeframe'] + '  ·  RR ' + content['rr'],
            fontsize=8, color=direction_color, va='top',
            transform=ax.transAxes, fontfamily='monospace',
            fontweight='bold', zorder=5, alpha=0.8)

    # Step-by-step
    step_top = 0.660
    circle_r  = 0.022
    step_gap  = 0.155

    for i, (title, desc) in enumerate(content['steps']):
        cy = step_top - i * step_gap

        # Circle
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

        # Connector line (not after last step)
        if i < len(content['steps']) - 1:
            ax.plot([0.085, 0.085],
                    [cy - circle_r, cy - step_gap + circle_r],
                    color=GOLD, alpha=0.2, linewidth=0.8,
                    transform=ax.transAxes, zorder=4)

        # Text
        ax.text(0.125, cy + 0.012, title,
                fontsize=11, fontweight='bold', color=WHITE,
                va='center', transform=ax.transAxes, zorder=5)
        ax.text(0.125, cy - 0.022, desc,
                fontsize=9, color=MUTED, va='top',
                transform=ax.transAxes, zorder=5, linespacing=1.4)

    # RR pills row
    pill_data = [
        (f'RISK 1%',          RED,            (0.59,0.18,0.18,0.15)),
        (f'RR {content["rr"]}', direction_color, (0.1,0.42,0.22,0.15)),
        ('IC MARKETS',         GOLD,           (0.12,0.10,0.02,0.15)),
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


# ── Shared utility ────────────────────────────────────────────────

def _wrap(text: str, width: int) -> list[str]:
    """Naive word-wrap returning list of lines."""
    words  = text.split()
    lines  = []
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
```

- [ ] **Step 2: Smoke-test the renderer locally**

```bash
cd "C:\Users\USER\Downloads\04 - FX Trading\vera-level-fx"
python - <<'EOF'
import sys; sys.path.insert(0, 'instagram')
from edu_content import get_edu_content
from generate_edu import make_risk_post, make_pairs_post, make_setup_post
import matplotlib.pyplot as plt

_, risk  = get_edu_content(0)
_, pair  = get_edu_content(1)
_, setup = get_edu_content(2)

make_risk_post(risk).savefig('test_risk.png',  dpi=100, bbox_inches='tight')
make_pairs_post(pair).savefig('test_pair.png', dpi=100, bbox_inches='tight')
make_setup_post(setup).savefig('test_setup.png', dpi=100, bbox_inches='tight')
plt.close('all')
print('OK — check test_risk.png, test_pair.png, test_setup.png')
EOF
```

Expected: Three PNG files created. Open them and verify they look correct — background photo with navy overlay, brand header, post content, gold footer.

- [ ] **Step 3: Clean up test images, commit**

```bash
del test_risk.png test_pair.png test_setup.png
git add instagram/generate_edu.py
git commit -m "feat: add educational post visual renderers (risk/pairs/setup)"
```

---

## Task 4 — Counter + edu routing in `run.py`

**Files:**
- Create: `data/edu-counter.json`
- Modify: `instagram/run.py`

- [ ] **Step 1: Create `data/edu-counter.json`**

```json
{"index": 0}
```

```bash
git add data/edu-counter.json
git commit -m "feat: add educational post rotation counter (starts at 0)"
```

- [ ] **Step 2: Modify `instagram/run.py` — add edu counter functions and routing**

Add these imports at the top of `run.py` (after the existing imports):

```python
import json
```

Add these two functions after the `save_image` function:

```python
COUNTER_FILE = ROOT / 'data' / 'edu-counter.json'


def read_counter() -> int:
    with open(COUNTER_FILE) as f:
        return json.load(f)['index']


def write_and_commit_counter(index: int):
    with open(COUNTER_FILE, 'w') as f:
        json.dump({'index': index}, f)
    cmds = [
        ['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'],
        ['git', 'config', 'user.name',  'github-actions[bot]'],
        ['git', 'add', str(COUNTER_FILE)],
        ['git', 'commit', '-m', f'chore: advance edu counter to {index} [skip ci]'],
        ['git', 'push',   'origin', 'master'],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if result.returncode != 0 and 'nothing to commit' not in result.stdout:
            print(result.stderr, file=sys.stderr)
```

Extend `decide_post_type` to recognise Tue/Thu:

```python
def decide_post_type(today: date) -> str:
    if today.day <= 2:
        return 'monthly'
    weekday = today.weekday()   # 0=Mon … 6=Sun
    if weekday == 0:
        return 'weekly'
    if weekday in (1, 3):       # Tuesday, Thursday
        return 'edu'
    return 'trust'
```

Extend `main()` — add the `edu` branch inside the `if/elif/else` block (before the `else` clause):

```python
    elif post_type == 'edu':
        sys.path.insert(0, str(ROOT / 'instagram'))
        from edu_content  import get_edu_content
        from generate_edu import make_risk_post, make_pairs_post, make_setup_post
        from captions     import edu as edu_caption   # added in Task 5

        idx           = read_counter()
        edu_type, content = get_edu_content(idx)
        next_idx      = (idx + 1) % 12

        if edu_type == 'risk':
            fig = make_risk_post(content)
        elif edu_type == 'pairs':
            fig = make_pairs_post(content)
        else:
            fig = make_setup_post(content)

        caption = edu_caption(edu_type, content)

        image_path = save_image(fig, f'edu-{edu_type}')
        plt.close('all')
        print(f'  saved: {image_path}')

        image_url = commit_and_push(image_path)
        print(f'  url:   {image_url}')

        write_and_commit_counter(next_idx)
        print(f'  counter: {idx} → {next_idx}')

        print('  waiting for CDN…')
        time.sleep(20)
        publish(image_url, caption)
        print(f'Done — edu/{edu_type} post published.')
        return
```

- [ ] **Step 3: Commit**

```bash
git add instagram/run.py data/edu-counter.json
git commit -m "feat: wire edu post routing and counter into run.py"
```

---

## Task 5 — Captions for edu posts (`captions.py`)

**Files:**
- Modify: `instagram/captions.py`

- [ ] **Step 1: Append `edu()` function to `instagram/captions.py`**

```python
def edu(edu_type: str, content: dict) -> str:
    base_tags = (
        "#forex #forextrader #forexsingapore #icmarkets #xauusd "
        "#veralevelFX #tradingstrategy #singaporetrader #pandian "
        "#forexeducation #fxtrading #priceaction"
    )
    cta = (
        "\n\n📲 Live signals → t.me/pandiangk"
        "\n📊 Live results → vera-level-forex.vercel.app"
        "\n🏦 Open IC Markets (IB #91936) → icmarkets.com/?camp=91936"
    )

    if edu_type == 'risk':
        return (
            f"⚠️ Risk Management Rule #{content['rule_num']} — {content['title']}\n\n"
            f"{content['body']}\n\n"
            f"💰 Example: ${content['example_account']:,} account → "
            f"${content['example_risk']:,} max risk per trade\n"
            f"🎯 At {content['example_rr']} — that's the professional way."
            f"{cta}\n\n{base_tags}"
        )

    if edu_type == 'pairs':
        return (
            f"🌍 Pair Spotlight — {content['pair']} ({content['full_name']})\n\n"
            f"Best session: {content['best_session']}\n"
            f"Avg spread: {content['avg_spread']}\n"
            f"Volatility: {content['volatility']}\n"
            f"My edge: {content['my_edge']}\n\n"
            f'"{content["quote"]}"\n\n'
            f"— Pandian, Vera Level FX"
            f"{cta}\n\n{base_tags}"
        )

    # setup
    steps_text = '\n'.join(
        f"{i+1}. {title} — {desc}"
        for i, (title, desc) in enumerate(content['steps'])
    )
    return (
        f"📈 Setup Breakdown — {content['pair']} {content['direction']} "
        f"({content['setup_type']})\n\n"
        f"Timeframe: {content['timeframe']}\n"
        f"Risk:Reward: {content['rr']}\n\n"
        f"{steps_text}\n\n"
        f"This is exactly how I structure every trade — no guessing, no emotion."
        f"{cta}\n\n{base_tags}"
    )
```

- [ ] **Step 2: Commit**

```bash
git add instagram/captions.py
git commit -m "feat: add edu caption generator for risk/pairs/setup post types"
```

---

## Task 6 — GitHub Actions workflow

**Files:**
- Modify: `.github/workflows/insta-post.yml`

- [ ] **Step 1: Add Tue/Thu cron triggers and edu dispatch option**

Replace the `on:` block in `.github/workflows/insta-post.yml`:

```yaml
on:
  schedule:
    # Monday  09:00 SGT = 01:00 UTC → weekly performance card
    - cron: '0 1 * * 1'
    # Tuesday 09:00 SGT = 01:00 UTC → educational post (rotating)
    - cron: '0 1 * * 2'
    # Wednesday 09:00 SGT = 01:00 UTC → trust card
    - cron: '0 1 * * 3'
    # Thursday 09:00 SGT = 01:00 UTC → educational post (rotating)
    - cron: '0 1 * * 4'
    # Friday 09:00 SGT = 01:00 UTC → trust card
    - cron: '0 1 * * 5'
    # 1st of every month 09:00 SGT → monthly P&L chart
    - cron: '0 1 1 * *'
  workflow_dispatch:
    inputs:
      post_type:
        description: 'Post type (weekly | monthly | trust | edu)'
        required: false
        default: 'weekly'
```

- [ ] **Step 2: Commit and push everything**

```bash
git add .github/workflows/insta-post.yml
git commit -m "feat: add Tue/Thu educational post cron triggers to GitHub Actions"
git push origin master
```

---

## Task 7 — End-to-end smoke test

- [ ] **Step 1: Trigger manually via GitHub Actions**

Go to: `https://github.com/gkpandian-sudo/vera-level-fx/actions/workflows/insta-post.yml`

Click **Run workflow** → set `post_type` to `edu` → Run.

- [ ] **Step 2: Verify in GitHub Actions logs**

Expected log output:
```
Generating post: edu (2026-xx-xx)
  saved: instagram/posts/2026-xx-xx-edu-risk.png
  url:   https://raw.githubusercontent.com/.../edu-risk.png
  counter: 0 → 1
  waiting for CDN…
  container created: XXXXXXX
  processing… (IN_PROGRESS)
  published: XXXXXXX
Done — edu/risk post published.
```

- [ ] **Step 3: Check Instagram page**

Visit `https://www.instagram.com/veralevel.fx/` — the new risk management post should appear in the feed with the correct caption and `@veralevel.fx` footer.

- [ ] **Step 4: Verify counter advanced**

```bash
git pull origin master
cat data/edu-counter.json
```

Expected: `{"index": 1}`

---

## Self-Review

**Spec coverage check:**
- ✅ 3 post types implemented (risk, pairs, setup)
- ✅ 6-week / 12-slot rotation via counter
- ✅ All 13 content variants written in `edu_content.py`
- ✅ Counter commits to repo and advances on each run
- ✅ Tue/Thu 09:00 SGT crons added
- ✅ `@veralevel.fx` in footer of every post
- ✅ Photo backgrounds (Unsplash) with navy overlay + grain
- ✅ Captions include Telegram, website, IC Markets IB CTA
- ✅ Existing Mon/Wed/Fri pipeline untouched
- ✅ `workflow_dispatch` updated to accept `edu`

**Placeholder scan:** No TBDs, TODOs, or "similar to above" references found.

**Type consistency:**
- `get_edu_content(index)` → `(str, dict)` — used consistently in `run.py` Task 4
- `make_risk_post(content)` / `make_pairs_post(content)` / `make_setup_post(content)` — all accept `dict`, return `Figure`
- `edu_caption(edu_type, content)` in `captions.py` matches call in `run.py`
- `write_and_commit_counter(next_idx)` defined and called with correct int
