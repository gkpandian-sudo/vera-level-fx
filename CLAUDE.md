# Vera Level FX — Claude Code Context

## Project Overview

Automated Instagram content engine for @veralevel.fx — Pandian's Singapore-based FX trading account.
Fetches live Myfxbook data, generates trading performance cards, and posts to Instagram via Meta Graph API.

## Architecture

```
vera-level-fx/
├── data/vera-snapshot.json     ← Live Myfxbook snapshot (updated daily by fetch-snapshot.yml)
├── data/edu-counter.json       ← Rotating educational content index (0 to 13, 14 slots)
├── fetch_snapshot.py           ← Pulls live account data from Myfxbook API
├── instagram/
│   ├── run.py                  ← Static image post entry point (insta-post.yml)
│   ├── run_reel.py             ← Reel video entry point (insta-reel.yml)
│   ├── captions.py             ← All Instagram caption functions
│   ├── generate.py             ← Weekly/monthly/trust/transparency card renderers
│   ├── generate_status.py      ← Daily live-positions card
│   ├── generate_edu.py         ← Educational content card renderers
│   ├── edu_content.py          ← Educational content library (14-slot, 7-week rotation)
│   ├── post.py                 ← Meta Graph API publish functions
│   ├── composer.py             ← Background/overlay image utilities
│   ├── reels/                  ← Reel video generation (scenes, render, audio, effects)
│   └── buffer/                 ← Pre-made images for offline fallback
└── .github/workflows/
    ├── fetch-snapshot.yml      ← Cron: daily 05:30 SGT fetch
    ├── insta-post.yml          ← Cron: daily 06:00 SGT static post
    ├── insta-reel.yml          ← Cron: 07:00 SGT rotation + 20:00 SGT daily reel
    ├── ai-reel.yml             ← Cron: daily 03:30 SGT AI-animated reel (Path E motion graphics)
    └── token-renewal-reminder.yml ← Cron: 1st of month 09:00 SGT Telegram reminder
```

## Brand: Vera Level FX

- **Instagram:** @veralevel.fx
- **Trader:** Pandian — Singapore-based, IC Markets live account (ASIC regulated)
- **Pairs traded:** XAUUSD, EURUSD, AUDCAD
- **Myfxbook account:** #12044019
- **IB link:** icmarkets.com/?camp=91936 (IB #91936) ← primary revenue
- **Telegram:** t.me/pandiangk ← secondary CTA
- **Voice:** Direct, transparent, no hype. "A trader who shows everything and hides nothing."

## Posting Schedule (SGT)

All times SGT. The UTC offset means the cron that fires 22:00–23:00 UTC belongs
to the *prior* UTC date — so Mon SGT static/reel use Sun UTC weekday logic, etc.

| SGT Day | 03:30 AI Reel (ai-reel.yml) | 05:30 Snapshot | 06:00 Static (insta-post.yml) | 07:00 Reel (insta-reel.yml) | 20:00 Reel |
|---------|----------------------------|----------------|-------------------------------|------------------------------|------------|
| **Mon** | trust | fetch | daily | weekly | daily |
| **Tue** | edu | fetch | weekly | edu | daily |
| **Wed** | edu | fetch | edu | trust | daily |
| **Thu** | trust | fetch | daily | edu | daily |
| **Fri** | weekly | fetch | daily | trust | daily |
| **Sat** | trust | fetch | daily | edu | daily |
| **Sun** | trust | fetch | daily | trust | daily |

Monthly specials (SGT date):

| SGT Date | Time | Workflow | Type |
|----------|------|----------|------|
| 1st | 09:00 | token-renewal-reminder | Telegram: renew META token |
| 2nd | 03:30 | ai-reel | broker |
| 2nd | 06:00 | insta-post | monthly |
| 2nd | 07:00 | insta-reel | broker |
| 3rd | 06:00 | insta-post | monthly |
| 3rd | 06:00 | insta-reel | monthly |

## Content Rotation — edu_content.py

14-slot rotation, 7-week cycle. Edu fires twice per week (reel on Tue SGT, static on Wed SGT).

| Slot | Type | Content |
|------|------|---------|
| 0 | risk | Lot Sizing By Balance |
| 1 | pairs | EURUSD |
| 2 | setup | EURUSD Liquidity Sweep Long |
| 3 | risk | Grid Spacing Discipline |
| 4 | pairs | XAUUSD |
| 5 | setup | XAUUSD Premium Zone Short |
| 6 | risk | Balance vs Equity Drawdown |
| 7 | pairs | AUDCAD |
| 8 | setup | AUDCAD Commodity Correlation Long |
| 9 | risk | Multi-Pair Diversification |
| 10 | pairs | USDJPY |
| 11 | setup | USDJPY Asian False Break |
| 12 | risk | Win Rate vs Profit Factor |
| 13 | setup | EURUSD Liquidity Sweep (repeat) |

## GitHub Secrets Required

| Secret | Purpose | Expiry |
|--------|---------|--------|
| `IG_USER_ID` | Instagram Business account numeric ID | Never |
| `META_ACCESS_TOKEN` | Long-lived Page Access Token | **60 days** ← renew every 45 days |
| `MYFX_EMAIL` | Myfxbook login | Never |
| `MYFX_PASSWORD` | Myfxbook login | Never |
| `RECOVERY_START` | YYYY-MM-DD date rebuild started | Until rebuild ends |
| `MUAPI_API_KEY` | Muapi.ai API key — enables Path C AI-animated card reels | Never |
| `HUGGING_FACE_TOKEN` | HF token — improves ZeroGPU queue priority for Path D (optional) | Never |
| `HF_I2V_SPACE` | Repository variable (not secret) — HF Space id for Path D, e.g. `Lightricks/ltx-video-distilled` | — |

## Reel Clip Path Priority (ai-reel.yml)

| Priority | Env var | Path | What it does |
|----------|---------|------|--------------|
| 1 | `MUAPI_API_KEY` | C | Muapi I2V AI-animated cards (~$0.45/reel) |
| 2 | `HIGGSFIELD_SOUL_ID` | B | Soul talking-head avatar |
| 3 | `HF_I2V_SPACE` | D | HuggingFace ZeroGPU I2V (free, unreliable) |
| 4 | `MOTION_GRAPHICS=1` | **E** | **Programmatic data animation (default — free, deterministic)** |
| 5 | _(none)_ | A | Ken Burns slow-zoom on static card |

Path E is hardcoded `MOTION_GRAPHICS: '1'` in `ai-reel.yml`. Performance card bars grow sequentially, equity curve draws itself with fill, trust arc sweeps from 0 to win rate. No external service, no cost.
| `BRAND_TELEGRAM` | t.me/pandiangk | Never |
| `BRAND_WEBSITE` | vera-level-forex.vercel.app | Never |
| `BRAND_IB_URL` | IC Markets IB URL | Never |
| `BRAND_AUTHOR` | Pandian | Never |

## ⚠️ CRITICAL: META_ACCESS_TOKEN Expires Every 60 Days

**This is the #1 failure mode for a long autonomous run.**

Long-lived tokens from Meta expire after 60 days. You MUST renew manually:
1. Go to Meta for Developers → Graph API Explorer
2. Generate new long-lived token
3. Update `META_ACCESS_TOKEN` in GitHub repo secrets
4. Do this EVERY 45 DAYS (before expiry)

**Token renewal calendar (from last known setup):**
- Renew by: check repo secrets page for current token creation date

## Commands

```bash
# Generate a preview image locally (any post type)
python instagram/run.py  # set POST_TYPE env var, needs vera-snapshot.json

# Trigger a manual post via GitHub Actions CLI
gh workflow run insta-post.yml --field post_type=weekly
gh workflow run insta-reel.yml --field post_type=trust

# Monitor workflow run
gh run watch $(gh run list --workflow=insta-post.yml -L 1 --json databaseId -q '.[0].databaseId') --exit-status

# Check GitHub Actions status
gh run list --workflow=insta-post.yml -L 5
gh run list --workflow=insta-reel.yml -L 5
```

## Code Conventions

- Image cards: 1080×1080px @ 100 DPI using matplotlib (Agg backend)
- Brand palette: NAVY `#010E1F`, EMERALD `#059669`, WHITE, RED `#EF4444`, MUTED `#B8CFEA`
- Caption functions: pure Python f-strings, no side effects, all data passed as dict
- Git commits from GitHub Actions use `[skip ci]` to prevent recursive triggers
- Risk disclaimer required on all posts citing live P&L (daily/weekly/monthly/trust/transparency)
- Post functions MUST NOT add new required parameters without updating run.py and run_reel.py

## Boundaries

- Never modify `data/vera-snapshot.json` manually — overwritten daily by fetch-snapshot.yml
- Never change caption function signatures — run.py and run_reel.py call them by position
- The edu counter (`data/edu-counter.json`) must always be `% len(ROTATION_SEQUENCE)` — never hardcode 12
- Never skip the risk disclaimer on posts with P&L data
- IB link must always use `?camp=91936` — this is the referral tracking parameter
