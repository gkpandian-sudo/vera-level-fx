# Build Your Own Instagram Forex Automation System
## A Complete Setup Guide

> **For AI assistants reading this guide:** This document is structured for both human and machine parsing.
> Each phase is self-contained with YAML frontmatter (in the chapter files), code blocks with language tags,
> and explicit checkpoint sections. You can execute any single phase by reading the corresponding
> `docs/setup/phase-N-*.md` file. Prerequisites are listed in each chapter's frontmatter.
> Callout prefixes: `> ⚠️ WARNING:` (breaks system if missed), `> 💡 TIP:` (optional),
> `> ✅ CHECKPOINT:` (verify before continuing), `> 🔒 SECURITY:` (credential handling).

**What this guide builds:** A fully automated system that posts live forex trading results to Instagram
5 days a week — weekly performance cards, daily live position updates, monthly P&L charts, and
rotating educational content. Every post includes your IC Markets referral QR code.

**Time to complete:** ~3.5 hours total (broken into phases you can spread across multiple sessions)

**Who this is for:** Intermediate users — comfortable with computers and terminals, not a developer.

**Starting point:** Zero code, zero accounts.

**End state:** Fully automated Instagram posting pipeline running unattended, 5 days per week.

---

## Table of Contents

| Phase | Title | Time | Chapter |
|---|---|---|---|
| 0 | Prerequisites & Accounts | 30 min | [docs/setup/phase-0-prerequisites.md](docs/setup/phase-0-prerequisites.md) |
| 1 | Local Environment | 20 min | [docs/setup/phase-1-local-environment.md](docs/setup/phase-1-local-environment.md) |
| 2 | Myfxbook Scraper | 45 min | [docs/setup/phase-2-scraper.md](docs/setup/phase-2-scraper.md) |
| 3 | Instagram Pipeline | 60 min | [docs/setup/phase-3-instagram-pipeline.md](docs/setup/phase-3-instagram-pipeline.md) |
| 4 | GitHub Actions & API Keys | 20 min | [docs/setup/phase-4-github-actions.md](docs/setup/phase-4-github-actions.md) |
| 5 | Customise Your Brand | 45 min | [docs/setup/phase-5-customise-brand.md](docs/setup/phase-5-customise-brand.md) |
| 6 | Go Live & Verify | 15 min | [docs/setup/phase-6-go-live.md](docs/setup/phase-6-go-live.md) |
| 7 | Maintenance & Troubleshooting | Reference | [docs/setup/phase-7-maintenance.md](docs/setup/phase-7-maintenance.md) |

**Total estimated time: ~3.5 hours**

---

## System Architecture

```
[Your Windows Laptop]
  └── myfxbook-mcp/               ← private, stays on your machine only
      └── src/runner.js           ← runs at 08:00 daily (Windows Task Scheduler)
          ├── fetcher.js          ← calls Myfxbook REST API (trades, daily gain)
          ├── scraper.js          ← Puppeteer + stealth Chrome (win rate, pips, etc.)
          └── telegram.js         ← sends you a daily summary notification
              │
              └── pushes vera-snapshot.json ──→ [GitHub: my-fx-instagram/data/]

[GitHub Actions] ← triggered at 09:00 daily by cron schedule
  └── my-fx-instagram/
      ├── instagram/run.py          ← reads snapshot, decides post type by weekday
      ├── instagram/generate*.py    ← renders 1080×1080 PNG with Matplotlib
      ├── instagram/captions.py     ← builds caption text with your CTA links
      ├── instagram/run.py          ← stamps QR code, commits PNG to repo, calls Meta API
      └── instagram/post.py         ← Meta Graph API: create container → poll → publish

[Meta Graph API v19.0]
  └── Instagram @yourusername       ← post appears on your feed
```

### Post Schedule

| Day | Post Type | Content |
|---|---|---|
| Monday | `weekly` | Weekly performance card — balance, gain, win rate, pips |
| Tuesday | `edu` | Educational post (rotating 6-week library) |
| Wednesday | `daily` | Live trade update — open positions, daily P&L |
| Thursday | `edu` | Educational post (rotating 6-week library) |
| Friday | `daily` | Live trade update — open positions, daily P&L |
| 1st of month | `monthly` | Monthly P&L breakdown chart |

---

## Prerequisites Summary

Before starting Phase 1, you need:
1. **IC Markets** — live trading account (not demo)
2. **Myfxbook** — connected to IC Markets, set to Public, Account ID noted
3. **Instagram Business** — converted to Business type, linked to a Facebook Page
4. **Meta Developer App** — created, Instagram Graph API added, switched to Live mode
5. **GitHub** — two repos: `myfxbook-mcp` (private) and `my-fx-instagram` (public)
6. **Telegram Bot** — Bot Token and Chat ID noted

See [Phase 0](docs/setup/phase-0-prerequisites.md) for step-by-step setup of all six.

---

## Quick Reference

### Key Files to Customise

| File | What to change |
|---|---|
| `instagram/captions.py` | `_CTA` block (your links), `TAGS` (your hashtags), brand name in trust caption |
| `instagram/edu_content.py` | All 12 slots — your own rules, pair analyses, trade setups |
| `instagram/assets/qr-icmarkets.jpg` | Your IC Markets IB referral QR code image |
| `instagram/assets/bg-daily-notepad.jpg` | Your background photo for the daily card |
| `instagram/generate.py` | Colour constants (`GOLD`, `NAVY`), brand name in footer text |
| `instagram/generate_edu.py` | Colour constants, brand name and handle in footer text |
| `instagram/generate_status.py` | Colour constants, security strip list |

### Files That Need NO Changes

| File | Why leave it alone |
|---|---|
| `instagram/post.py` | Pure Meta API plumbing — no brand content |
| `instagram/run.py` | Pipeline logic — only change QR filename if different |
| `instagram/generate_status.py` | Only change colours and `_STRIP` list |
| `.github/workflows/insta-post.yml` | Only change cron times for your timezone |

### Key Commands

```powershell
# Run scraper manually (from myfxbook-mcp folder)
node src/runner.js

# Generate a post locally for preview (from my-fx-instagram folder)
$env:POST_TYPE = "daily"
python instagram/run.py

# Generate each post type locally
$env:POST_TYPE = "weekly"    ; python instagram/run.py
$env:POST_TYPE = "monthly"   ; python instagram/run.py
$env:POST_TYPE = "trust"     ; python instagram/run.py
$env:POST_TYPE = "edu"       ; python instagram/run.py

# Trigger a post via GitHub CLI
gh workflow run insta-post.yml --field post_type=daily

# Check recent Actions run status
gh run list --workflow=insta-post.yml --limit=5

# Reset educational content counter to start
'{"index": 0}' | Set-Content data\edu-counter.json
git add data\edu-counter.json && git commit -m "fix: reset edu counter" && git push

# Pull and push after Actions commits
git pull --rebase origin master && git push
```

### Token Renewal Calendar

| Task | Frequency | How |
|---|---|---|
| Renew `META_ACCESS_TOKEN` | Every 55 days | Phase 7 section 7.1 |
| Verify IC Markets referral link | Quarterly | Open referral URL in browser |
| Scan QR code to confirm | Quarterly | Point phone at QR code on a post |
| Review educational content | Every 6 weeks | Update `edu_content.py` |
| Check Actions run history | Monthly | GitHub → Actions → check for failures |

---

## Common Issues at a Glance

| Symptom | Most likely cause | See |
|---|---|---|
| `Meta API error 190` | Access token expired | Phase 7 § 7.1 |
| `Balance: 0` in snapshot | Myfxbook DOM scrape failed | Phase 7 § 7.3 |
| No Telegram message | Wrong Bot Token or Chat ID | Phase 0 § 0.7 |
| `[qr] skipped:` in log | QR file not found | Phase 5 § 5.5 |
| Git push rejected | Actions committed ahead of you | Run `git pull --rebase origin master && git push` |
| `ModuleNotFoundError: No module named 'generate'` | Wrong working directory | Run from `my-fx-instagram/` root |
| Workflow never fires at scheduled time | Cron is UTC — check timezone table | Phase 4 § 4.1 |

---

## Full Guide

The following sections contain the complete content of each phase chapter. The individual chapter files in `docs/setup/` are the canonical versions — this master file concatenates them for easy reading and AI processing.

---

# Phase 0 — Prerequisites & Accounts

*See also: [docs/setup/phase-0-prerequisites.md](docs/setup/phase-0-prerequisites.md)*

**Estimated time:** 30 minutes | **Prerequisites:** None

Before writing a single line of code, you need to set up the external accounts and services this system depends on.

## 0.1 IC Markets Live Account

Go to [icmarkets.com](https://icmarkets.com) and open a **live** trading account.

> ⚠️ WARNING: This guide requires a **live** account, not a demo. Myfxbook tracks real P&L — demo data produces meaningless posts.

1. Click **Open Live Account** → choose **Raw Spread** account type
2. Complete KYC verification
3. Fund your account and activate MT4 or MT5
4. **Note your account number** from the Client Portal under "My Accounts"

## 0.2 Myfxbook Account

1. Go to [myfxbook.com](https://www.myfxbook.com) → create free account
2. Click **My Portfolio → Add System → Automatic Sync → IC Markets**
3. Enter your MT4/MT5 account number and **investor password** (read-only)
4. Wait 10–15 minutes for first sync

> 🔒 SECURITY: Use the **investor password** only — it cannot place or close trades.

## 0.3 Make Myfxbook Public + Note Account ID

1. **My Portfolio → [Your System] → Edit → Privacy: Public → Save**
2. Visit your public page URL and note the Account ID (number at end of URL)

**Save:** `Myfxbook Account ID = ____________`

## 0.4 Instagram Business Account + Facebook Page

1. Convert Instagram to Business: **Profile → Settings → Account → Switch to Professional Account → Business**
2. Create Facebook Page: [facebook.com/pages/create](https://www.facebook.com/pages/create) → Business or Brand
3. Link: Facebook Page → **Settings → Instagram → Connect Account**

## 0.5 Meta Developer App

1. Go to [developers.facebook.com](https://developers.facebook.com) → **My Apps → Create App**
2. Use case: **Other** → App type: **Business**
3. Add product: **Instagram Graph API → Set Up**
4. Toggle **Development → Live** (top bar)
5. Go to **App Settings → Basic** → note **App ID** and **App Secret**

> 🔒 SECURITY: Never share your App Secret. It is equivalent to a master password for your app.

**Save:** `App ID = ____________` | `App Secret = ____________`

## 0.6 GitHub Account + Two Repos

1. Create repo `myfxbook-mcp` → **Private**
2. Create repo `my-fx-instagram` → **Public**

**Save:** `GitHub username = ____________`

## 0.7 Telegram Bot

1. In Telegram, message **@BotFather** → `/newbot` → follow prompts
2. Note the Bot Token
3. Send a message to your bot, then visit `https://api.telegram.org/botYOUR_TOKEN/getUpdates` → note Chat ID

**Save:** `Bot Token = ____________` | `Chat ID = ____________`

> ✅ CHECKPOINT: All 7 items above completed and values saved before moving to Phase 1.

---

# Phase 1 — Local Environment Setup

*See also: [docs/setup/phase-1-local-environment.md](docs/setup/phase-1-local-environment.md)*

**Estimated time:** 20 minutes | **Prerequisites:** Phase 0

Install four tools on your Windows machine.

## 1.1 Node.js 20+

Download LTS from [nodejs.org](https://nodejs.org) → run installer → accept all defaults.

## 1.2 Python 3.11+

Download from [python.org/downloads](https://www.python.org/downloads/) → **tick "Add Python to PATH"** → Install Now.

> ⚠️ WARNING: "Add to PATH" must be ticked on the first installer screen. Without it, `python` won't work in PowerShell.

## 1.3 Git

Download from [git-scm.com/download/win](https://git-scm.com/download/win) → on "Adjusting PATH" step choose **"Git from the command line and also from 3rd-party software"**.

```powershell
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## 1.4 Google Chrome

Install from [google.com/chrome](https://www.google.com/chrome/).

> ⚠️ WARNING: The scraper requires real Google Chrome — not Edge or Chromium. Cloudflare blocks Chromium.

## ✅ Phase 1 Checkpoint

```powershell
node --version; npm --version; python --version; git --version
```

All four commands return version numbers. Chrome is at `C:\Program Files\Google\Chrome\Application\chrome.exe`.

---

# Phase 2 — Myfxbook Scraper Setup

*See also: [docs/setup/phase-2-scraper.md](docs/setup/phase-2-scraper.md)*

**Estimated time:** 45 minutes | **Prerequisites:** Phase 0, Phase 1

> 🔒 SECURITY: The `myfxbook-mcp/` folder stays on your laptop only — never push it to a public GitHub repo.

## 2.1 Create Folder Structure

```powershell
mkdir myfxbook-mcp; cd myfxbook-mcp; mkdir src; mkdir public
git init
git remote add origin https://github.com/yourusername/myfxbook-mcp.git
```

## 2.2 package.json

**`package.json`**
```json
{
  "name": "myfxbook-mcp",
  "version": "1.0.0",
  "main": "src/runner.js",
  "scripts": { "start": "node src/runner.js" },
  "dependencies": {
    "dotenv": "^16.4.5",
    "node-fetch": "^2.7.0",
    "puppeteer-extra": "^3.3.6",
    "puppeteer-extra-plugin-stealth": "^2.11.2"
  }
}
```

```powershell
npm install
```

## 2.3 .gitignore

```
node_modules/
.env
*.log
public/
```

## 2.4 .env

```env
MYFXBOOK_EMAIL=your@email.com
MYFXBOOK_PASSWORD=your_myfxbook_password
MYFXBOOK_ACCOUNT_ID=YOUR_ACCOUNT_ID
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

> 🔒 SECURITY: `.env` must NEVER be committed. It is in `.gitignore`.

For the complete source files (`src/telegram.js`, `src/fetcher.js`, `src/scraper.js`, `src/runner.js`) — see the full chapter at [docs/setup/phase-2-scraper.md](docs/setup/phase-2-scraper.md).

> ⚠️ WARNING: In `src/scraper.js`, update the `page.goto()` URL to match your actual Myfxbook system page URL. In `src/runner.js`, update `VERA_FX_DIR` to the path of your `my-fx-instagram` folder.

## 2.10 Windows Task Scheduler

Schedule `node src/runner.js` to run daily at 08:00:
- Task Scheduler → Create Task
- General: "Run whether user is logged on or not" + "Run with highest privileges"
- Trigger: Daily at 08:00
- Action: Program = `node`, Arguments = `src/runner.js`, Start in = `C:\path\to\myfxbook-mcp`

## ✅ Phase 2 Checkpoint

```powershell
cd myfxbook-mcp
node src/runner.js
```

Expected: `✓ Myfxbook login OK` · `✓ Scraped stats: { balance: 'XXXX', ... }` · Telegram message received · `vera-snapshot.json` committed to GitHub.

---

# Phase 3 — Instagram Pipeline Setup

*See also: [docs/setup/phase-3-instagram-pipeline.md](docs/setup/phase-3-instagram-pipeline.md)*

**Estimated time:** 60 minutes | **Prerequisites:** Phase 0, Phase 1, Phase 2

```powershell
git clone https://github.com/yourusername/my-fx-instagram.git
cd my-fx-instagram
```

Create folders, install dependencies, then create the following files. Full file content is in [docs/setup/phase-3-instagram-pipeline.md](docs/setup/phase-3-instagram-pipeline.md).

| File | Customise? | What it does |
|---|---|---|
| `instagram/requirements.txt` | No | Python dependencies |
| `instagram/post.py` | **No** | Meta API publisher |
| `instagram/captions.py` | **Yes** — `_CTA`, `TAGS`, brand name | Caption text generator |
| `instagram/edu_content.py` | **Yes** — all content | 12-slot educational library |
| `instagram/run.py` | Minimal — QR filename only | Pipeline orchestrator |
| `instagram/generate.py` | **Yes** — colours, brand name | Weekly/monthly/trust card renderer |
| `instagram/generate_status.py` | **Yes** — colours, brand name | Daily card renderer |
| `instagram/generate_edu.py` | **Yes** — colours, brand name | Edu post renderer |
| `data/vera-snapshot.json` | Replace with real data | Account data bridge |
| `data/edu-counter.json` | No | Rotation counter: `{"index": 0}` |

## ✅ Phase 3 Checkpoint

```powershell
$env:POST_TYPE = "weekly"
python instagram/run.py
```

Expected: PNG file created at `instagram/posts/YYYY-MM-DD-weekly.png` with no errors.

---

# Phase 4 — GitHub Actions Automation & Meta API Keys

*See also: [docs/setup/phase-4-github-actions.md](docs/setup/phase-4-github-actions.md)*

**Estimated time:** 20 minutes | **Prerequisites:** Phase 3 pushed to GitHub

## 4.1 Workflow File

Create `.github/workflows/insta-post.yml` — see the full file content in [docs/setup/phase-4-github-actions.md](docs/setup/phase-4-github-actions.md) section 4.1.

The workflow runs on a cron schedule (Mon–Fri 09:00 SGT = 01:00 UTC) and via manual `workflow_dispatch`.

## 4.2 Getting IG_USER_ID

1. Go to [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer) → select your app
2. Click **Generate Access Token** with permissions: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`, `pages_show_list`
3. Submit `/me/accounts` → note Facebook Page `"id"`
4. Submit `/PAGE_ID?fields=instagram_business_account` → note `instagram_business_account.id`

This 17-digit number is your `IG_USER_ID`.

## 4.3 Getting META_ACCESS_TOKEN (Long-Lived)

Exchange your short-lived token (1 hour) for a long-lived token (~60 days):

```powershell
$APP_ID      = "YOUR_APP_ID"
$APP_SECRET  = "YOUR_APP_SECRET"
$SHORT_TOKEN = "PASTE_SHORT_LIVED_TOKEN"

Invoke-RestMethod "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=$APP_ID&client_secret=$APP_SECRET&fb_exchange_token=$SHORT_TOKEN"
```

The `access_token` in the response is your `META_ACCESS_TOKEN`.

> ⚠️ WARNING: This token expires in ~60 days. Set a calendar reminder 55 days from now to renew it (Phase 7 section 7.1).

## 4.4 Add Secrets to GitHub

Repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Value |
|---|---|
| `IG_USER_ID` | 17-digit Instagram Business Account ID |
| `META_ACCESS_TOKEN` | Long-lived token from section 4.3 |

## ✅ Phase 4 Checkpoint

Trigger `workflow_dispatch` with `post_type=weekly` → workflow runs green → `published: XXXXXXXXXX` in log → post appears on Instagram.

---

# Phase 5 — Customise Your Brand

*See also: [docs/setup/phase-5-customise-brand.md](docs/setup/phase-5-customise-brand.md)*

**Estimated time:** 30–60 minutes | **Prerequisites:** Phase 3 files created

## Colour Palette

All three generator files share these constants. Change them once in each file:

```python
NAVY   = '#010E1F'   # main background      → change to your brand background
GOLD   = '#F0C040'   # accent / headings     → change to your brand accent colour
WHITE  = '#FFFFFF'   # primary text          → usually keep white
GREEN  = '#00E096'   # profit numbers        → keep green or change to brand colour
RED    = '#FF6B6B'   # loss numbers          → keep red for clarity
```

## CTA Block (captions.py)

```python
_CTA = (
    "\n\n📲 Live signals → https://t.me/YOUR_TELEGRAM_USERNAME"
    "\n🌐 Live account → https://YOUR_WEBSITE_URL"
    "\n🏦 Open IC Markets account →"
    "\nhttps://icmarkets.com/global/en/?camp=YOUR_CAMP_ID"
)
```

## QR Code

1. Get your IC Markets IB referral URL (from your IB portal)
2. Generate QR at [qr-code-generator.com](https://www.qr-code-generator.com)
3. Download as PNG (400×400px minimum)
4. Save as `instagram/assets/qr-icmarkets.jpg`

## Educational Content

Fill in `instagram/edu_content.py`:
- 5 `RISK_RULES` — your risk management methodology
- 4 `PAIRS` — the instruments you trade (spread, session, your edge)
- 4 `SETUPS` — your actual entry setups, step by step

See [docs/setup/phase-5-customise-brand.md](docs/setup/phase-5-customise-brand.md) section 5.6 for the full template and field descriptions.

## ✅ Phase 5 Checkpoint

```powershell
$env:POST_TYPE = "daily"  ; python instagram/run.py
$env:POST_TYPE = "weekly" ; python instagram/run.py
$env:POST_TYPE = "edu"    ; python instagram/run.py
```

Each generates a PNG with your brand colours, name, and CTA links visible.

---

# Phase 6 — Go Live & Verify

*See also: [docs/setup/phase-6-go-live.md](docs/setup/phase-6-go-live.md)*

**Estimated time:** 15 minutes | **Prerequisites:** All phases 0–5 complete

1. Run scraper → confirm `vera-snapshot.json` has real balance (not `3000.00`)
2. Commit + push snapshot to GitHub
3. Trigger `workflow_dispatch` with `post_type=daily`
4. Watch Actions log — confirm `[qr] stamped`, `container created`, `published`
5. Check Instagram feed on phone — post visible within 30 seconds
6. Scan QR code → confirm referral URL
7. Check caption → all 3 CTA lines present

## ✅ Phase 6 Checkpoint

| Check | Expected |
|---|---|
| Actions run completes | ✅ green tick |
| `[qr] stamped referral QR` in log | ✅ present |
| `published: ...` in log | ✅ 17+ digit post ID |
| Post on Instagram | ✅ visible, live data |
| QR code scannable | ✅ opens IC Markets referral URL |

**Pipeline is live.** 🎉

---

# Phase 7 — Maintenance & Troubleshooting

*See also: [docs/setup/phase-7-maintenance.md](docs/setup/phase-7-maintenance.md)*

**Reference — read as needed.**

## Token Renewal (Every ~60 Days)

1. Graph API Explorer → Generate Access Token (same permissions as Phase 4)
2. Exchange for long-lived token (Phase 4 section 4.3 PowerShell command)
3. Repo → **Settings → Secrets → META_ACCESS_TOKEN → Update secret**

## Error Reference

| Error | Fix |
|---|---|
| `Meta API error 190` | Renew `META_ACCESS_TOKEN` (see above) |
| `Meta API error 400` | Increase `time.sleep(20)` to `35` in `run.py` |
| `Balance: 0` in snapshot | Fix `page.goto()` URL in `scraper.js` |
| Git push rejected | `git pull --rebase origin master && git push` |
| Cloudflare blocking scraper | Disconnect VPN; scraper needs residential IP |

## Counter Reset

```powershell
'{"index": 0}' | Set-Content data\edu-counter.json
git add data\edu-counter.json && git commit -m "fix: reset edu counter" && git push
```

For the full error code table, buffer management guide, and quarterly checklist — see [docs/setup/phase-7-maintenance.md](docs/setup/phase-7-maintenance.md).
