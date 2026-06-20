# Vera Level FX — System Master Document

**Account:** @veralevel.fx (Instagram)  
**Broker:** IC Markets — IB referral `icmarkets.com/?camp=91936`  
**Myfxbook account ID:** 12044019  
**Repository:** `vera-level-fx` (GitHub, branch: `master`)

---

## 1. System Overview

This is a fully automated Instagram content pipeline for a live Forex trading account. It runs entirely on GitHub Actions — no server, no VPS. Every day it:

1. Fetches live account data from Myfxbook API → saves `data/vera-snapshot.json`
2. On posting days, generates a 1080×1080 PNG image using Python (matplotlib + Pillow)
3. Commits the image to the repo so it has a public raw URL
4. Publishes to Instagram via the Meta Graph API with a pre-written caption

Nothing is manual. The only human input required is updating secrets when tokens expire.

---

## 2. Repository Structure

```
vera-level-fx/
├── .github/workflows/
│   ├── fetch-snapshot.yml      # daily data pull from Myfxbook
│   └── insta-post.yml          # Mon–Fri post generation + publish
│
├── data/
│   ├── vera-snapshot.json      # live account data (auto-updated daily)
│   └── edu-counter.json        # tracks current position in edu rotation
│
├── instagram/
│   ├── run.py                  # main entry point — decides post type and orchestrates
│   ├── generate.py             # weekly card, monthly chart, winrate/trust card
│   ├── generate_status.py      # daily live-positions card
│   ├── generate_edu.py         # educational posts (risk, pairs, setup)
│   ├── composer.py             # PIL image composition utilities
│   ├── edu_content.py          # all educational content data + 12-slot rotation
│   ├── captions.py             # Instagram caption text for each post type
│   ├── post.py                 # Meta Graph API publisher
│   ├── requirements.txt        # Python dependencies
│   │
│   ├── assets/                 # Background images (AI-generated, not committed as source)
│   │   ├── bg-weekly.jpg       # trading desk — weekly card
│   │   ├── bg-trust.jpg        # charts — winrate card
│   │   ├── bg-daily.jpg        # monitor setup — daily card
│   │   ├── bg-setup.jpg        # chart closeup — trade setup posts
│   │   ├── bg-pairs-eurusd.jpg
│   │   ├── bg-pairs-xauusd.jpg
│   │   ├── bg-pairs-audcad.jpg
│   │   └── qr-icmarkets.jpg    # IC Markets IB referral QR code
│   │
│   ├── buffer/                 # Pre-made images that bypass generation (optional)
│   │   ├── daily/
│   │   ├── weekly/
│   │   ├── monthly/
│   │   ├── trust/
│   │   └── edu/{risk,pairs,setup}/
│   │
│   ├── posts/                  # All generated post images (committed, used as CDN)
│   ├── previews/               # Local preview renders for review
│   └── tests/                  # pytest test suite
│       ├── test_composer.py
│       ├── test_edu.py
│       └── test_redesign.py
│
├── fetch_snapshot.py           # Myfxbook data fetcher (called by GitHub Actions)
└── docs/
    └── SYSTEM_MASTER.md        # this document
```

---

## 3. Post Schedule

| Day | Time (SGT) | Post Type | Generator |
|-----|-----------|-----------|-----------|
| Monday | 09:00 | Weekly performance card | `make_weekly_card` |
| Tuesday | 09:00 | Educational (rotating) | `make_risk_post` / `make_pairs_post` / `make_setup_post` |
| Wednesday | 09:00 | Daily live positions | `make_daily_card` |
| Thursday | 09:00 | Educational (rotating) | same as Tuesday |
| Friday | 09:00 | Daily live positions | `make_daily_card` |
| 1st of month | 09:00 | Monthly P&L chart | `make_monthly_chart` |

GitHub Actions cron runs at `01:00 UTC` = `09:00 SGT`.

---

## 4. Data Flow

```
Myfxbook API
    │
    ▼
fetch_snapshot.py          ← runs daily at 00:01 UTC via fetch-snapshot.yml
    │  (login → get-my-accounts, get-daily-gain, get-open-trades, get-history)
    ▼
data/vera-snapshot.json    ← committed to repo automatically
    │
    ▼
instagram/run.py           ← triggered by insta-post.yml (Mon–Fri 01:00 UTC)
    │  reads snapshot → decides post type → calls generator
    ▼
generate_*.py              ← builds 1080×1080 matplotlib figure
    │
    ▼
instagram/posts/YYYY-MM-DD-{type}.png   ← committed to repo
    │  (raw GitHub URL becomes the image_url for Meta API)
    ▼
instagram/post.py          ← Meta Graph API
    │  POST /media (create container) → wait for FINISHED → POST /media_publish
    ▼
Instagram feed             ← live post at @veralevel.fx
```

---

## 5. File-by-File Reference

### `fetch_snapshot.py`
Authenticates with Myfxbook, fetches account stats, daily gain curve, open trades, and full history. Saves everything to `data/vera-snapshot.json`.

**Key fields saved in snapshot:**
- `account.balance`, `account.equity`, `account.gain`, `account.winRate`
- `account.profitFactor`, `account.pips`, `account.trades`, `account.daily`
- `openTrades[]` — list of live positions with symbol, action, profit, pips, openPrice
- `dailyGain[]` — `[date, cumulative_pct, daily_profit]` per day since 2026-01-01
- `history[]` — full closed trade history

**Env vars required:** `MYFX_EMAIL`, `MYFX_PASSWORD`

---

### `instagram/run.py`
Main orchestrator. Called by GitHub Actions.

**Post type decision logic (`decide_post_type`):**
```
day <= 2 of month  → monthly
Monday             → weekly
Tuesday/Thursday   → edu
Wednesday/Friday   → daily
```
The `POST_TYPE` env var overrides this (used for manual `workflow_dispatch` triggers).

**Buffer system (`pop_buffer`):** Checks `instagram/buffer/{type}/` for pre-made `.png` files first. If found, uses them instead of generating. This allows batching image creation ahead of time.

**QR stamp (`overlay_qr`):** After saving, stamps `qr-icmarkets.jpg` onto the bottom-left corner of every post image (corner stamp via Pillow). The daily card generates its own bottom CTA line, so the QR stamp is still applied to it.

**Edu counter:** Reads `data/edu-counter.json` → calls `get_edu_content(index)` → advances and commits counter. Ensures no repeat of the same slot.

---

### `instagram/composer.py`
PIL-based image composition utilities. All functions work with `float32 numpy arrays [0,1]` at shape `(1080, 1080, 3)`.

| Function | Purpose |
|----------|---------|
| `load_background(path)` | Load + center-crop + resize any image to 1080×1080 |
| `dark_bg()` | Fallback solid navy if image missing |
| `gradient_panel(arr, height_frac)` | Fade bottom portion to black for text overlay |
| `frosted_glass_region(arr, ...)` | Blur + darken a horizontal band (frosted glass) |
| `split_layout(arr, split_frac)` | Paint bottom fraction solid black; returns split_y in axes coords |
| `vignette(arr, strength)` | Radial darkening toward edges |

---

### `instagram/generate.py`
Generates three post types using matplotlib Agg backend at 10.8×10.8 inches, 100 DPI = **1080×1080 px**.

#### `make_weekly_card(data)`
Background: `bg-weekly.jpg` with `gradient_panel(height_frac=0.52)`.  
Content: IC Markets Verified badge → "WEEKLY PERFORMANCE · DATE" → hero gain % (fontsize=88) → 4-stat row (Balance, Win Rate, Pips, Trades) → Risk row → CTA → footer.

#### `make_monthly_chart(data)`
Pure navy background with matplotlib bar chart. IC Markets Verified badge → "Monthly P&L" italic heading → bar chart (12 months, green/red bars) → footer with IB URL.  
Data source: `dailyGain` array aggregated by month.

#### `make_winrate_card(data)`
Background: `bg-trust.jpg` with `vignette(strength=0.68)`.  
Content: IC Markets Verified badge → "LIVE TRACK RECORD" → hero win rate % (fontsize=110) → 3-stat row (Balance, Gain, Pips) → profit factor → Myfxbook CTA → IB link → footer.

---

### `instagram/generate_status.py`
Generates the **daily live-positions card**.

Background: `bg-daily.jpg` with `gradient_panel(height_frac=0.58)`.  
Layout (top to bottom):
1. "LIVE POSITION UPDATE · DATE" header
2. EQUITY / BALANCE / DAILY metrics (3-column)
3. Separator line
4. "{N} Open Positions" + "● LIVE" badge
5. Trade table: PAIR | DIR | P&L | PIPS | ENTRY (up to 5 rows)
6. Stats bar: WR / PF / pips / Myfxbook verified
7. CTA: "Trade with my broker · icmarkets.com/?camp=91936"
8. Footer: "@veralevel.fx · Not financial advice"

**Color scheme:** All text WHITE. Metric highlights: EQUITY=GOLD, DAILY=GREEN/RED. Dir/P&L columns intentionally WHITE (not colored per design decision).

---

### `instagram/generate_edu.py`
Generates three educational post types. Uses `_base_fig()` for risk posts (deep navy gradient over Canva texture), `split_layout()` for pairs and setup.

#### `make_risk_post(content)`
Background: `bg-daily.jpg` with `gradient_panel(height_frac=0.62)`.  
Layout: Section label (RED) → hline → Rule title (fontsize=56, wraps to 2 lines) → body text (CREAM, 4 lines) → Account size / Max risk stats (GOLD/RED) → CTA → footer.

#### `make_pairs_post(content)`
Background: split photo (top 52%) + black panel (bottom 48%).  
Layout: "PAIR SPOTLIGHT · {FULL NAME}" header → pair name hero (fontsize=40) → hline → 2×2 stat grid (BEST SESSION / AVG SPREAD / VOLATILITY / MY EDGE) → IB CTA → footer.

#### `make_setup_post(content)`
Background: split photo (top 42%) + black panel (bottom 58%).  
Layout: Direction label + pair/setup type → 4 numbered steps (circle + title + 2-line desc) → connector lines between circles → bottom bar (RISK 1% / RR / IC MARKETS / @veralevel.fx) → footer.

---

### `instagram/edu_content.py`
All educational content as Python data structures. No database needed.

**Content libraries:**
- `RISK_RULES` — 5 risk management rules (rule_num, title, body, example stats, tag)
- `PAIRS` — 4 pair spotlights (EURUSD, GBPJPY, XAUUSD, USDJPY)
- `SETUPS` — 4 trade setups (EURUSD long, XAUUSD short, GBPJPY long, USDJPY short)

**12-slot rotation (`ROTATION_SEQUENCE`):**
```python
[
  ("risk",  0),  # Lot Sizing By Balance
  ("pairs", 0),  # EURUSD
  ("setup", 0),  # EURUSD Liquidity Sweep Long
  ("risk",  1),  # Grid Spacing Discipline      ← current (index 3)
  ("pairs", 2),  # XAUUSD
  ("setup", 1),  # XAUUSD Premium Zone Short
  ("risk",  2),  # Balance vs Equity Drawdown
  ("pairs", 1),  # GBPJPY
  ("setup", 2),  # GBPJPY London Breakout
  ("risk",  3),  # Multi-Pair Diversification
  ("pairs", 3),  # USDJPY
  ("setup", 3),  # USDJPY Asian False Break
]
```
Current counter: `data/edu-counter.json` = `{"index": 3}`  
Cycle repeats every 6 weeks (12 posts, Tue + Thu).

---

### `instagram/captions.py`
Pre-written Instagram captions for each post type. Reads env vars for brand links at import time:
- `BRAND_TELEGRAM` → defaults to `t.me/pandiangk`
- `BRAND_WEBSITE` → defaults to `vera-level-forex.vercel.app`
- `BRAND_IB_URL` → defaults to `icmarkets.com/?camp=91936`

| Function | Post type |
|----------|-----------|
| `weekly(account)` | Weekly card |
| `monthly(account, monthly_pnl)` | Monthly chart |
| `edu(edu_type, content)` | All edu types |
| `daily_status(account, open_trades)` | Daily card |
| `trust(account)` | Winrate card |

All captions include `TAGS` block with India-targeted hashtags.

---

### `instagram/post.py`
Two-step Meta Graph API publisher.
1. `POST /{IG_USER_ID}/media` with `image_url` + `caption` → gets `container_id`
2. Polls container status every 5s (up to 60s) until `status_code == FINISHED`
3. `POST /{IG_USER_ID}/media_publish` with `container_id` → live post

**Env vars required:** `IG_USER_ID`, `META_ACCESS_TOKEN`

---

## 6. GitHub Actions Workflows

### `fetch-snapshot.yml` — Runs daily at 00:01 UTC
```
checkout → python 3.11 → pip install requests → python fetch_snapshot.py → git commit + push
```
Secrets needed: `MYFX_EMAIL`, `MYFX_PASSWORD`

### `insta-post.yml` — Runs Mon–Fri at 01:00 UTC + 1st of month
```
checkout → python 3.11 → pip install -r requirements.txt → python instagram/run.py
```
Secrets needed:

| Secret | Value |
|--------|-------|
| `IG_USER_ID` | Instagram Business account numeric ID |
| `META_ACCESS_TOKEN` | Long-lived Page Access Token (60-day, must be refreshed) |
| `MYFX_EMAIL` | Myfxbook login email |
| `MYFX_PASSWORD` | Myfxbook password |
| `BRAND_TELEGRAM` | Telegram channel link |
| `BRAND_WEBSITE` | Website URL |
| `BRAND_IB_URL` | IC Markets IB referral URL |
| `BRAND_SIGNAL_CTA` | Custom CTA line for signal posts |
| `BRAND_AUTHOR` | Author name |
| `BRAND_DOMAIN` | Domain label for footers |

Permissions: `contents: write` (to commit generated images).

---

## 7. Brand Design System

### Canvas
- **Size:** 1080×1080 px (Instagram square)
- **DPI:** 100 (matplotlib figure: 10.8×10.8 inches)
- **Backend:** matplotlib Agg (no display needed)

### Colour Palette
| Name | Hex | Usage |
|------|-----|-------|
| NAVY | `#010E1F` | Base background |
| GOLD | `#F0C040` | Brand accent, CTA, key metrics |
| GREEN | `#00E096` | Positive values, LONG direction |
| RED | `#FF6B6B` | Negative values, SHORT direction, alerts |
| AMBER | `#FFA040` | Volatility, secondary accent |
| WHITE | `#FFFFFF` | Primary text, values |
| CREAM | `#F0EEE8` | Body text, secondary values |
| MUTED | `#B8CFEA` | Labels, subdued text |
| DIM | `#6A8EB8` | Fine print, footers only |

### Typography Hierarchy
| Role | Size | Weight | Color |
|------|------|--------|-------|
| Display hero | 88–110pt | black | GREEN/RED or WHITE |
| Large value | 36–56pt | bold/black | varies |
| Section title | 20–24pt | bold | WHITE or GOLD |
| Body text | 15–20pt | regular | CREAM |
| Labels | 13–15pt | bold | MUTED |
| Footer | 12–14pt | regular | MUTED |

### Design Rules (as of Jun 2026)
- No gold top bar
- No "VERA LEVEL FX" text on images
- No FancyBboxPatch boxes — all text is plain, separated by thin `_hline` dividers
- No Telegram ID on images — use `@veralevel.fx`
- DIR and P&L columns on daily card: WHITE (not colored)
- No embedded QR code — QR stamped via `overlay_qr()` in run.py instead

---

## 8. Buffer System

Drop pre-made `.png` files into the buffer folders to bypass live generation:

```
instagram/buffer/
├── daily/          → used on Wed/Fri
├── weekly/         → used on Monday
├── monthly/        → used on 1st of month
├── trust/          → used when post_type=trust (manual only)
└── edu/
    ├── risk/       → used on Tue/Thu when edu slot is risk
    ├── pairs/      → used on Tue/Thu when edu slot is pairs
    └── setup/      → used on Tue/Thu when edu slot is setup
```

Files are consumed (moved to `instagram/posts/`) on use. Only `.png` files are picked up; `.gitkeep` files are ignored.

---

## 9. Running Locally

### Prerequisites
```
Python 3.11+
pip install -r instagram/requirements.txt
```

### Generate a preview
```python
python -c "
import json, sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from instagram.generate import make_weekly_card
with open('data/vera-snapshot.json') as f:
    data = json.load(f)
fig = make_weekly_card(data)
fig.savefig('preview.png', dpi=100, bbox_inches='tight', facecolor='#010E1F')
plt.close('all')
"
```

Replace `make_weekly_card` with any generator function.

### Fetch fresh data manually
```
MYFX_EMAIL=you@email.com MYFX_PASSWORD=xxx python fetch_snapshot.py
```

### Run tests
```
pytest instagram/tests/
```

### Trigger a manual post
On GitHub → Actions → "Instagram Auto-Post" → Run workflow → choose post_type.

---

## 10. Maintenance

### Meta Access Token refresh (every 60 days)
1. Go to [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)
2. Generate a new long-lived token with `instagram_basic`, `instagram_content_publish`, `pages_read_engagement` permissions
3. Update `META_ACCESS_TOKEN` secret in GitHub repo settings

### Adding new educational content
1. Add to `RISK_RULES`, `PAIRS`, or `SETUPS` list in `instagram/edu_content.py`
2. Add a new slot to `ROTATION_SEQUENCE` (extends from 12 slots)
3. Commit and push — takes effect on next Tuesday/Thursday post

### Updating background images
Drop new JPEG/PNG files into `instagram/assets/` with the correct filename.  
No code changes needed — `composer.py` loads by path. Falls back to dark navy if missing.

### Resetting the edu counter
Edit `data/edu-counter.json` to `{"index": 0}` and commit.

---

## 11. Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| matplotlib | 3.8.4 | Image generation (Agg backend) |
| numpy | 1.26.4 | Array manipulation for image composition |
| Pillow | 10.3.0 | Image loading, cropping, QR stamp |
| requests | 2.31.0 | Myfxbook API + Meta Graph API |
