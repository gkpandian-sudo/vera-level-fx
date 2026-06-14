# Instagram Rotating Content Library — Design Spec
**Date:** 2026-06-13
**Project:** Vera Level FX (`@veralevel.fx`)
**Status:** Approved

---

## Goal

Expand the existing automated Instagram pipeline from 3 post types (Mon/Wed/Fri) to 5 posts/week by adding two educational posts every Tuesday and Thursday. Content rotates across a 6-week library with zero manual work.

---

## Weekly Schedule

| Day | Time (SGT) | Post Type | Status |
|-----|-----------|-----------|--------|
| Mon | 09:00 | Weekly Performance Card | ✅ Existing |
| **Tue** | **09:00** | **Educational (rotating)** | 🆕 New |
| Wed | 09:00 | Win Rate / Trust Card | ✅ Existing |
| **Thu** | **09:00** | **Educational (rotating)** | 🆕 New |
| Fri | 09:00 | Win Rate / Trust Card | ✅ Existing |
| 1st of month | 09:00 | Monthly P&L Chart | ✅ Existing |

---

## Educational Post Types (3 types × 6 variants = 6-week rotation)

### Type A — Risk Management (5 rules, rotates on Tue/Thu alternating)
| # | Title | Key Message |
|---|-------|-------------|
| 1 | The 1% Rule | Never risk >1% per trade. $10k → $100 max loss |
| 2 | Daily Drawdown Limit | Stop trading if down 3% in a day. Protect the week |
| 3 | ATR-Based Position Sizing | Let volatility dictate lot size, not gut feel |
| 4 | Minimum Risk:Reward | Only take trades with 1:2 RR or better |
| 5 | No News Trading | Close or avoid positions around high-impact events |

### Type B — Pair Spotlights (4 pairs, one per rotation slot)
| # | Pair | Best Session | Volatility | Pandian's Edge |
|---|------|-------------|------------|----------------|
| 1 | EURUSD | London/NY overlap | Medium | H4 trend following |
| 2 | GBPJPY | London open | Very High | Breakout momentum |
| 3 | XAUUSD | NY open | High | S&R level plays |
| 4 | USDJPY | Asian session | Low-Medium | Range trading |

### Type C — Trade Setup Breakdowns (4 setups)
| # | Pair | Direction | Setup Type | RR |
|---|------|-----------|-----------|-----|
| 1 | GBPJPY | Long | H4 trend continuation entry | 1:2.5 |
| 2 | XAUUSD | Long/Short | Support/Resistance reversal | 1:2.0 |
| 3 | EURUSD | Long | London breakout continuation | 1:2.5 |
| 4 | USDJPY | Short | Asian range break with retest | 1:2.0 |

### 6-Week Rotation Sequence
| Week | Tuesday | Thursday |
|------|---------|----------|
| 1 | Risk — 1% Rule | Pair — EURUSD |
| 2 | Setup — GBPJPY Trend | Risk — Daily DD Limit |
| 3 | Pair — XAUUSD | Setup — XAUUSD S&R |
| 4 | Risk — ATR Sizing | Pair — GBPJPY |
| 5 | Setup — EURUSD Breakout | Risk — RR Minimum |
| 6 | Pair — USDJPY | Setup — USDJPY Range |

---

## Visual Design

**Aesthetic:** Bloomberg Terminal meets luxury editorial — institutional precision with premium depth.

**Brand colours:** Navy `#001835`, Gold `#D4AF37`, White `#f0eee8`

**Typography:**
- Display: `Bebas Neue` (large headlines, pair names)
- Editorial: `DM Serif Display` (body headlines, quotes)
- Data/labels: `Space Mono` (tags, footers, metadata)

**Background system:** Real forex/trading Unsplash photos filtered with `saturate(0.6) brightness(0.55)` + navy gradient overlay. Grain texture + subtle grid-line art on every post.

**Per-type accent colours:**
- Risk Management: Red `#fca5a5` warnings + glass cards
- Pair Spotlight: Gold `#D4AF37` divider + stat grid
- Trade Setup: Green `#4ade80` direction badge + gold numbered circles

**Footer (all posts):** `VERA LEVEL FX · @veralevel.fx`

---

## Architecture

### Files to Create
```
instagram/
  edu_content.py       # Full content library (all variants, all 3 types)
  generate_edu.py      # Matplotlib post renderers for 3 edu post types
data/
  edu-counter.json     # {"index": 0}  — tracks rotation position, committed to repo
```

### Files to Modify
```
instagram/
  run.py               # Add edu post type routing + counter read/write/commit
.github/workflows/
  insta-post.yml       # Add Tue 09:00 SGT and Thu 09:00 SGT cron triggers
```

### Rotation Counter Mechanism
- `data/edu-counter.json` stores a single integer `index` (0–11 for 12 slots)
- On each Tue/Thu run: read index → pick `ROTATION_SEQUENCE[index]` → generate post → increment index → commit `edu-counter.json` → publish
- After index 11, wraps back to 0

### Counter file format
```json
{"index": 0}
```

### Rotation sequence array (12 entries, maps to 6-week table above)
```python
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
```

### GitHub Actions cron additions
```yaml
# Add to existing insta-post.yml schedule:
- cron: '0 1 * * 2'   # Tuesday  09:00 SGT (UTC+8 = 01:00 UTC)
- cron: '0 1 * * 4'   # Thursday 09:00 SGT
```
Both triggers set `POST_TYPE: edu` env var so `run.py` knows to use the educational pipeline.

---

## Caption Strategy

Every caption ends with:
```
📲 Join: t.me/pandiangk
📊 Live results: vera-level-forex.vercel.app
🏦 Open IC Markets: [IB link camp=91936]

#forex #forextrader #forexsingapore #icmarkets #xauusd
#veralevelFX #tradingstrategy #singaporetrader #pandian
```

---

## Spec Self-Review

- ✅ No TBDs or placeholders — all content fully specified
- ✅ Counter mechanism handles wrap-around at index 12
- ✅ Cron times correctly converted SGT→UTC
- ✅ Existing Mon/Wed/Fri pipeline untouched
- ✅ Image backgrounds consistent with site theme
- ✅ `@veralevel.fx` footer on all new post types
- ✅ 6 weeks of variety before any content repeats
