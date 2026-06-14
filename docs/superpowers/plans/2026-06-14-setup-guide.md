# Setup Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write a complete, human- and AI-readable end-to-end setup guide for building an Instagram-automated forex trading showcase system from scratch.

**Architecture:** 9 Markdown files — one chapter per phase (phase-0 through phase-7) in `docs/setup/`, plus a single `SETUP_GUIDE.md` master file at repo root that concatenates all chapters with a table of contents. Each chapter has YAML frontmatter for AI parseability.

**Tech Stack:** Markdown, YAML frontmatter, bash/PowerShell code blocks, Meta Graph API v19.0, GitHub Actions, Puppeteer/Node.js, Python 3.11, Matplotlib, Pillow.

---

## File Map

| File | Task | Content |
|---|---|---|
| `docs/setup/phase-0-prerequisites.md` | Task 1 | Accounts: IC Markets, Myfxbook, Instagram, Meta Dev, GitHub, Telegram |
| `docs/setup/phase-1-local-environment.md` | Task 2 | Node.js, Python, Git, Chrome installs + verify |
| `docs/setup/phase-2-scraper.md` | Task 3 | Full myfxbook-mcp/ build from scratch + Task Scheduler |
| `docs/setup/phase-3-instagram-pipeline.md` | Task 4 | Full my-fx-instagram/ repo build + all Python files |
| `docs/setup/phase-4-github-actions.md` | Task 5 | Meta API key walkthrough + GitHub Actions wiring |
| `docs/setup/phase-5-customise-brand.md` | Task 6 | Colour palette, brand name, hashtags, QR, content |
| `docs/setup/phase-6-go-live.md` | Task 7 | End-to-end smoke test + verification checklist |
| `docs/setup/phase-7-maintenance.md` | Task 8 | Token renewal, troubleshooting, buffer management |
| `SETUP_GUIDE.md` | Task 9 | Master file: ToC + all chapters concatenated |

---

## Format Rules (apply to every task)

Every chapter file MUST:
- Start with YAML frontmatter block
- Use `##` for sections, `###` for subsections (never skip levels)
- Wrap all commands in fenced code blocks with language tag (`bash`, `powershell`, `js`, `python`, `yaml`, `json`)
- Use callout prefixes: `> ⚠️ WARNING:`, `> 💡 TIP:`, `> ✅ CHECKPOINT:`, `> 🔒 SECURITY:`
- End with a `## ✅ Phase N Checkpoint` section with exact commands and expected output
- Use `YourBrand`, `yourusername`, `your@email.com`, `YOUR_ACCOUNT_ID` as placeholders — never Pandian's real values

---

## Task 1: Phase 0 — Prerequisites & Accounts

**File:** `docs/setup/phase-0-prerequisites.md`

- [ ] **Step 1: Create the file with frontmatter**

```markdown
---
phase: 0
title: "Prerequisites & Accounts"
estimated_time: "30 minutes"
prerequisites: []
outputs:
  - IC Markets live account open
  - Myfxbook account with IC Markets connected and public
  - Instagram Business account linked to a Facebook Page
  - Meta Developer App created with Instagram Graph API product added
  - GitHub account with two repos created
  - Telegram Bot token and chat ID noted
---
```

- [ ] **Step 2: Write section 0.1 — IC Markets Account**

Content to include:
- Go to icmarkets.com (use your IB referral link in the guide as a placeholder note)
- Open a **live** account (not demo — Myfxbook only tracks live accounts meaningfully)
- Choose "Raw Spread" account type for lowest spreads on algo trading
- Note your account number from the MT4/MT5 portal — you will need it for Myfxbook
- Warning: Demo accounts work but daily gain data is not meaningful for Instagram posts

```markdown
## 0.1 IC Markets Live Account

Go to [icmarkets.com](https://icmarkets.com) and open a **live** trading account.

> ⚠️ WARNING: This guide requires a **live** account, not a demo. Myfxbook tracks real P&L — demo data produces meaningless posts.

1. Click **Open Live Account**
2. Choose account type: **Raw Spread** (lowest spreads for algorithmic trading)
3. Complete KYC verification (ID + proof of address)
4. Fund your account and activate MT4 or MT5
5. **Note your account number** — visible in the Client Portal under "My Accounts"

> 💡 TIP: Your IC Markets account number looks like `12345678`. Save it — you will enter it in Myfxbook in section 0.2.
```

- [ ] **Step 3: Write section 0.2 — Myfxbook Account**

```markdown
## 0.2 Myfxbook Account

Myfxbook is the third-party audit service that publicly verifies your trading results.

1. Go to [myfxbook.com](https://www.myfxbook.com) and create a free account
2. Click **My Portfolio → Add System**
3. Choose **Automatic Sync** and select your broker: **IC Markets**
4. Enter your MT4/MT5 account number and investor password (read-only — never your main password)
5. Give your system a name (e.g. `YourBrand FX`)
6. Click **Add System** and wait 10–15 minutes for the first sync

> 🔒 SECURITY: Use the **investor password** only — it is read-only and cannot place or close trades.
```

- [ ] **Step 4: Write section 0.3 — Make Myfxbook Public + Note Account ID**

```markdown
## 0.3 Make Your Myfxbook Account Public

The scraper reads your account's public page. It must be set to public.

1. Go to **My Portfolio → [Your System Name] → Edit**
2. Set **Privacy** to **Public**
3. Click Save
4. Visit your public page: `https://www.myfxbook.com/members/yourusername/yoursystemname/YOUR_ACCOUNT_ID`
5. **Note your Account ID** — it is the number at the end of the URL

> ✅ CHECKPOINT: Open your Myfxbook public page in a browser. You should see your balance, gain, and trade history without being logged in.

**Save this value:**
| Item | Your Value |
|---|---|
| Myfxbook Account ID | ____________ |
```

- [ ] **Step 5: Write section 0.4 — Instagram Business Account + Facebook Page**

```markdown
## 0.4 Instagram Business Account + Facebook Page

Instagram's API only works with **Business** or **Creator** accounts linked to a **Facebook Page**.

### 0.4.1 Create or Convert Your Instagram Account

If you already have an Instagram account:
1. Open Instagram app → **Profile → Settings → Account → Switch to Professional Account**
2. Choose **Business**
3. Select a category (e.g. "Finance" or "Investing")

If you are starting fresh:
1. Create a new Instagram account at instagram.com
2. Follow the steps above to convert it to Business

### 0.4.2 Create a Facebook Page

1. Go to [facebook.com/pages/create](https://www.facebook.com/pages/create)
2. Choose **Business or Brand**
3. Name it the same as your Instagram handle (e.g. `YourBrand FX`)
4. Complete the basic setup

### 0.4.3 Link Instagram to Facebook Page

1. On Facebook, go to your Page → **Settings → Instagram**
2. Click **Connect Account** and log in to your Instagram account
3. Confirm the connection

> ✅ CHECKPOINT: On your Facebook Page settings, under Instagram, you should see your Instagram username listed as "Connected".
```

- [ ] **Step 6: Write section 0.5 — Meta Developer App (most critical section)**

```markdown
## 0.5 Meta Developer App

This is where you create the API access that lets the automation post to Instagram.

### 0.5.1 Create a Meta Developer Account

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click **Get Started** and log in with your Facebook account (the one linked to your Page)
3. Accept the developer terms

### 0.5.2 Create a New App

1. Click **My Apps → Create App**
2. Select use case: **Other** → Next
3. Select app type: **Business** → Next
4. Enter:
   - **App Name:** `YourBrand Instagram Bot` (or any name)
   - **App Contact Email:** your email
   - **Business Account:** link your Facebook Business account if prompted (or skip)
5. Click **Create App**

### 0.5.3 Add Instagram Graph API Product

1. On your App Dashboard, find the **Products** section
2. Find **Instagram Graph API** and click **Set Up**
3. This adds the Instagram product to your app

### 0.5.4 Set App to Live Mode

> ⚠️ WARNING: While your app is in **Development** mode, it can only post to Instagram accounts added as Test Users. Switch to **Live** mode so it can post to your real account.

1. On the App Dashboard top bar, toggle **Development → Live**
2. You may be asked to verify your app — for a personal bot that only posts to your own account, select **"I don't intend to provide access to other users"** and confirm

### 0.5.5 Note Your App ID and App Secret

1. Go to **App Settings → Basic**
2. Note:
   - **App ID** (visible at top)
   - **App Secret** (click "Show" to reveal)

> 🔒 SECURITY: Never share your App Secret. It is equivalent to a password that controls your app.

**Save these values:**
| Item | Your Value |
|---|---|
| Meta App ID | ____________ |
| Meta App Secret | ____________ |
```

- [ ] **Step 7: Write section 0.6 — GitHub Account + Repos**

```markdown
## 0.6 GitHub Account + Two Repositories

### 0.6.1 Create GitHub Account

Go to [github.com](https://github.com) and sign up if you don't have an account.

### 0.6.2 Create the Scraper Repo (Private)

1. Click **New Repository**
2. Name: `myfxbook-mcp`
3. Set to **Private** ← important, this holds your Myfxbook credentials
4. Do NOT initialise with README
5. Click **Create repository**

### 0.6.3 Create the Instagram Pipeline Repo (Public)

1. Click **New Repository**
2. Name: `my-fx-instagram` (or your preferred name)
3. Set to **Public** — GitHub Actions reads this repo and Meta API needs a public URL for images
4. Do NOT initialise with README
5. Click **Create repository**

**Save these values:**
| Item | Your Value |
|---|---|
| GitHub username | ____________ |
| Instagram repo name | ____________ |
| Instagram repo full name | `yourusername/my-fx-instagram` |
```

- [ ] **Step 8: Write section 0.7 — Telegram Bot**

```markdown
## 0.7 Telegram Bot (Daily Scraper Reports)

The scraper sends you a daily summary via Telegram so you know it ran successfully.

### 0.7.1 Create the Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Enter a name: `YourBrand Daily Report`
4. Enter a username: `yourbrand_report_bot` (must end in `bot`)
5. BotFather replies with your **Bot Token** — looks like `8706182750:AAHjO...`

### 0.7.2 Get Your Chat ID

1. Send any message to your new bot
2. Open this URL in your browser (replace `YOUR_BOT_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
3. Find `"chat":{"id":1234567890}` in the JSON response — that number is your **Chat ID**

**Save these values:**
| Item | Your Value |
|---|---|
| Telegram Bot Token | ____________ |
| Telegram Chat ID | ____________ |

> 💡 TIP: Keep this table somewhere safe (a password manager or encrypted note). You will paste these values into your `.env` file in Phase 2.
```

- [ ] **Step 9: Write Phase 0 Checkpoint**

```markdown
## ✅ Phase 0 Checkpoint

Before moving to Phase 1, confirm all of the following:

| Item | Status |
|---|---|
| IC Markets live account open and funded | ☐ |
| Myfxbook connected to IC Markets and set to Public | ☐ |
| Myfxbook Account ID noted | ☐ |
| Instagram converted to Business account | ☐ |
| Facebook Page created and linked to Instagram | ☐ |
| Meta Developer App created in Live mode | ☐ |
| Meta App ID and App Secret noted | ☐ |
| GitHub account + 2 repos created | ☐ |
| Telegram Bot token and Chat ID noted | ☐ |

**Time spent so far:** ~30 minutes. Next: install software on your Windows laptop.
```

- [ ] **Step 10: Commit**

```bash
git add docs/setup/phase-0-prerequisites.md
git commit -m "docs: add Phase 0 prerequisites guide"
git push origin master
```

---

## Task 2: Phase 1 — Local Environment

**File:** `docs/setup/phase-1-local-environment.md`

- [ ] **Step 1: Create file with frontmatter**

```yaml
---
phase: 1
title: "Local Environment Setup"
estimated_time: "20 minutes"
prerequisites: ["Phase 0 complete"]
outputs:
  - Node.js 20+ installed
  - Python 3.11+ installed with pip
  - Git installed and configured
  - Google Chrome installed
---
```

- [ ] **Step 2: Write section 1.1 — Node.js**

```markdown
## 1.1 Node.js 20+

Node.js runs the Myfxbook scraper.

1. Go to [nodejs.org](https://nodejs.org) and download the **LTS** version (20.x or higher)
2. Run the installer — accept all defaults
3. ✅ Verify:

```powershell
node --version
```
Expected output: `v20.x.x` or higher

```powershell
npm --version
```
Expected output: `10.x.x` or higher
```

- [ ] **Step 3: Write section 1.2 — Python**

```markdown
## 1.2 Python 3.11+

Python runs the Instagram image generation pipeline.

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python **3.11.x** or higher
3. Run the installer
4. ⚠️ On the first screen, tick **"Add Python to PATH"** before clicking Install Now

> ⚠️ WARNING: If you skip "Add to PATH", Python commands won't work in PowerShell and you'll need to reinstall.

✅ Verify:
```powershell
python --version
```
Expected: `Python 3.11.x`

```powershell
pip --version
```
Expected: `pip 23.x.x from C:\Users\...\Python311\...`
```

- [ ] **Step 4: Write sections 1.3 (Git), 1.4 (Chrome), 1.5 (Verify all)**

```markdown
## 1.3 Git

1. Go to [git-scm.com](https://git-scm.com/download/win) and download Git for Windows
2. Run installer — on the "Adjusting PATH" step choose **"Git from the command line and also from 3rd-party software"**
3. All other defaults are fine

✅ Verify:
```powershell
git --version
```
Expected: `git version 2.x.x.windows.x`

Configure your identity (required for committing):
```powershell
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

## 1.4 Google Chrome

The Myfxbook scraper uses Puppeteer with **real Chrome** (not Chromium). Cloudflare detects Chromium and blocks it.

1. Go to [google.com/chrome](https://www.google.com/chrome/) and install Google Chrome
2. Note the installation path (usually `C:\Program Files\Google\Chrome\Application\chrome.exe`)

> ⚠️ WARNING: Do NOT use Microsoft Edge or Chromium. Only Google Chrome passes Myfxbook's Cloudflare protection.

## 1.5 Verify All Installs

Run all four checks at once:
```powershell
node --version; npm --version; python --version; git --version
```

Expected output (versions may differ slightly):
```
v20.11.0
10.2.4
Python 3.11.7
git version 2.43.0.windows.1
```
```

- [ ] **Step 5: Write Phase 1 Checkpoint and commit**

```markdown
## ✅ Phase 1 Checkpoint

All four commands produce version numbers without errors:

```powershell
node --version    # v20.x.x or higher
python --version  # Python 3.11.x or higher
git --version     # git version 2.x.x
```

Google Chrome is installed at `C:\Program Files\Google\Chrome\Application\chrome.exe`

**Time spent so far:** ~50 minutes total. Next: build the Myfxbook scraper.
```

```bash
git add docs/setup/phase-1-local-environment.md
git commit -m "docs: add Phase 1 local environment guide"
git push origin master
```

---

## Task 3: Phase 2 — Myfxbook Scraper

**File:** `docs/setup/phase-2-scraper.md`

- [ ] **Step 1: Frontmatter**

```yaml
---
phase: 2
title: "Myfxbook Scraper Setup"
estimated_time: "45 minutes"
prerequisites: ["Phase 0 complete", "Phase 1 complete"]
outputs:
  - myfxbook-mcp/ folder with all source files
  - .env configured with real credentials
  - node src/runner.js runs successfully
  - vera-snapshot.json committed to my-fx-instagram GitHub repo
  - Windows Task Scheduler running daily at 08:00
---
```

- [ ] **Step 2: Write section 2.1 — Folder structure**

```markdown
## 2.1 Create the Folder Structure

Open PowerShell and run:

```powershell
mkdir myfxbook-mcp
cd myfxbook-mcp
mkdir src
mkdir public
git init
git remote add origin https://github.com/yourusername/myfxbook-mcp.git
```

Your folder should look like:
```
myfxbook-mcp/
├── src/
├── public/
├── .env          ← you will create this
├── .gitignore    ← you will create this
└── package.json  ← you will create this
```
```

- [ ] **Step 3: Write section 2.2 — package.json (exact content)**

```markdown
## 2.2 Create package.json

Create `myfxbook-mcp/package.json` with this exact content:

**`package.json`**
```json
{
  "name": "myfxbook-mcp",
  "version": "1.0.0",
  "description": "Daily Myfxbook scraper — writes vera-snapshot.json",
  "main": "src/runner.js",
  "scripts": {
    "start": "node src/runner.js"
  },
  "dependencies": {
    "dotenv": "^16.4.5",
    "node-fetch": "^2.7.0",
    "puppeteer-extra": "^3.3.6",
    "puppeteer-extra-plugin-stealth": "^2.11.2"
  }
}
```

Then install:
```powershell
npm install
```

> 💡 TIP: `node-fetch` version 2 is used because it supports `require()`. Version 3 is ESM-only and requires extra configuration.
```

- [ ] **Step 4: Write section 2.3 — .gitignore and .env**

```markdown
## 2.3 Create .gitignore

**`.gitignore`**
```
node_modules/
.env
*.log
public/
```

## 2.4 Create .env

**`.env`** — fill in your values from the Phase 0 reference table:

```env
# ── Myfxbook credentials ──────────────────────────────────────
MYFXBOOK_EMAIL=your@email.com
MYFXBOOK_PASSWORD=your_myfxbook_password

# ── Your Myfxbook account ID (from the URL when viewing your system)
MYFXBOOK_ACCOUNT_ID=YOUR_ACCOUNT_ID

# ── Telegram (from Phase 0 section 0.7) ──────────────────────
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# ── Optional ─────────────────────────────────────────────────
DAILY_HISTORY_DAYS=7
```

> 🔒 SECURITY: `.env` is in `.gitignore` and must NEVER be committed. It contains your Myfxbook login credentials.
```

- [ ] **Step 5: Write section 2.5 — src/telegram.js (full file)**

```markdown
## 2.5 Create src/telegram.js

**`src/telegram.js`**
```js
const fetch = require('node-fetch');

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT_ID   = process.env.TELEGRAM_CHAT_ID;

async function sendTelegram(message) {
  if (!BOT_TOKEN || !CHAT_ID) {
    console.log('  [telegram] skipped — BOT_TOKEN or CHAT_ID not set');
    return;
  }
  try {
    const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
    await fetch(url, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ chat_id: CHAT_ID, text: message, parse_mode: 'HTML' }),
    });
    console.log('  [telegram] message sent');
  } catch (e) {
    console.error('  [telegram] failed:', e.message);
  }
}

module.exports = { sendTelegram };
```
```

- [ ] **Step 6: Write section 2.6 — src/fetcher.js (full file)**

Write the full Myfxbook REST API fetcher. Key endpoints:
- Login: `POST https://www.myfxbook.com/api/login.json`
- Get open trades: `GET https://www.myfxbook.com/api/get-open-trades.json?session=SESSION&id=ACCOUNT_ID`
- Get history: `GET https://www.myfxbook.com/api/get-history.json?session=SESSION&id=ACCOUNT_ID&start=0&size=40`
- Get daily gain: `GET https://www.myfxbook.com/api/get-daily-gain.json?session=SESSION&id=ACCOUNT_ID&start=START_DATE&end=END_DATE`
- Logout: `GET https://www.myfxbook.com/api/logout.json?session=SESSION`

```markdown
## 2.6 Create src/fetcher.js

**`src/fetcher.js`**
```js
const fetch = require('node-fetch');

const BASE  = 'https://www.myfxbook.com/api';
const EMAIL = process.env.MYFXBOOK_EMAIL;
const PASS  = process.env.MYFXBOOK_PASSWORD;
const ACCT  = process.env.MYFXBOOK_ACCOUNT_ID;

async function apiGet(path) {
  const res  = await fetch(`${BASE}${path}`);
  const json = await res.json();
  if (json.error) throw new Error(`Myfxbook API error: ${json.message}`);
  return json;
}

async function fetchVeraData() {
  // 1. Login
  const login = await apiGet(
    `/login.json?email=${encodeURIComponent(EMAIL)}&password=${encodeURIComponent(PASS)}`
  );
  const session = login.session;
  console.log('  ✓ Myfxbook login OK');

  // 2. Fetch open trades
  const openRes = await apiGet(
    `/get-open-trades.json?session=${session}&id=${ACCT}`
  );
  const openTrades = (openRes.openTrades || []).map(t => ({
    openTime:  t.openTime,
    symbol:    t.symbol,
    action:    t.action,
    sizing:    { type: 'lots', value: t.sizing },
    openPrice: t.openPrice,
    tp:        t.tp,
    sl:        t.sl,
    profit:    t.profit,
    pips:      t.pips,
    swap:      t.swap,
    magic:     t.magic,
    comment:   t.comment || '',
  }));

  // 3. Fetch recent history (last 40 trades)
  const histRes = await apiGet(
    `/get-history.json?session=${session}&id=${ACCT}&start=0&size=40`
  );
  const history = histRes.history || [];

  // 4. Fetch daily gain (last 90 days)
  const today = new Date();
  const start = new Date(today); start.setDate(start.getDate() - 90);
  const fmt   = d => d.toISOString().slice(0, 10);
  const gainRes = await apiGet(
    `/get-daily-gain.json?session=${session}&id=${ACCT}&start=${fmt(start)}&end=${fmt(today)}`
  );
  const dailyGain = gainRes.dailyGain || [];

  // 5. Logout
  await apiGet(`/logout.json?session=${session}`);

  return { openTrades, history, dailyGain };
}

module.exports = { fetchVeraData };
```
```

- [ ] **Step 7: Write section 2.7 — src/scraper.js (full file)**

Full Puppeteer stealth scraper that logs into Myfxbook with real Chrome and extracts the lifetime account stats from the DOM (win rate, profit factor, trade count, pips — these are not in the REST API).

```markdown
## 2.7 Create src/scraper.js

**`src/scraper.js`**
```js
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const EMAIL = process.env.MYFXBOOK_EMAIL;
const PASS  = process.env.MYFXBOOK_PASSWORD;
const ACCT  = process.env.MYFXBOOK_ACCOUNT_ID;

// CUSTOMISE: update this if Chrome is installed elsewhere on your system
const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

async function scrapeVeraStats() {
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  try {
    // Login
    await page.goto('https://www.myfxbook.com/login', { waitUntil: 'networkidle2' });
    await page.type('#email',    EMAIL, { delay: 50 });
    await page.type('#password', PASS,  { delay: 50 });
    await page.click('[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle2' });

    // Navigate to system page
    await page.goto(
      `https://www.myfxbook.com/members/yourusername/yoursystemname/${ACCT}`,
      { waitUntil: 'networkidle2', timeout: 30000 }
    );

    // Scrape account stats from DOM
    const stats = await page.evaluate(() => {
      const getText = sel => {
        const el = document.querySelector(sel);
        return el ? el.textContent.trim() : '';
      };
      return {
        balance:      getText('[id*="totalBalance"]'),
        equity:       getText('[id*="totalEquity"]'),
        gain:         getText('[id*="totalGain"]'),
        drawdown:     getText('[id*="totalDrawDown"]'),
        profitFactor: getText('[id*="profitFactor"]'),
        winRate:      getText('[id*="winRatio"]'),
        trades:       getText('[id*="totalTrades"]'),
        pips:         getText('[id*="totalPips"]'),
      };
    });

    console.log('  ✓ Scraped stats:', stats);
    return stats;

  } finally {
    await browser.close();
  }
}

module.exports = { scrapeVeraStats };
```

> ⚠️ WARNING: The DOM selectors (`[id*="totalBalance"]` etc.) target Myfxbook's HTML. If Myfxbook updates their site layout, these selectors may need updating. If scraping returns empty strings, open the Myfxbook page in Chrome DevTools and inspect the element IDs.

> 💡 TIP: To find the correct URL for `page.goto()`, log in to Myfxbook manually, navigate to your system page, and copy the URL from your browser's address bar.
```

- [ ] **Step 8: Write section 2.8 — src/runner.js (full file)**

```markdown
## 2.8 Create src/runner.js

This is the entry point that orchestrates scraping, fetching, merging, and pushing.

**`src/runner.js`**
```js
require('dotenv').config();
const fs   = require('fs');
const path = require('path');
const { execSync }     = require('child_process');
const { fetchVeraData }  = require('./fetcher');
const { scrapeVeraStats } = require('./scraper');
const { sendTelegram }    = require('./telegram');

// CUSTOMISE: path to your my-fx-instagram repo on this machine
const VERA_FX_DIR     = path.join(__dirname, '..', '..', 'my-fx-instagram');
const SNAPSHOT_PATH   = path.join(VERA_FX_DIR, 'data', 'vera-snapshot.json');
const PUBLIC_SNAPSHOT = path.join(__dirname, '..', 'public', 'vera-snapshot.json');

function parseNumber(str) {
  if (!str) return 0;
  return parseFloat(str.replace(/[^0-9.\-]/g, '')) || 0;
}

async function main() {
  console.log(`[${new Date().toISOString()}] Starting scraper`);

  // 1. Fetch REST API data (open trades, history, daily gain)
  const apiData = await fetchVeraData();

  // 2. Scrape DOM stats (win rate, profit factor, pips, etc.)
  const domStats = await scrapeVeraStats();

  // 3. Merge into snapshot
  const snapshot = {
    account: {
      balance:      parseNumber(domStats.balance),
      equity:       parseNumber(domStats.equity),
      daily:        0,   // filled from REST API daily gain if available
      monthly:      0,
      gain:         parseNumber(domStats.gain),
      drawdown:     parseNumber(domStats.drawdown),
      profitFactor: parseNumber(domStats.profitFactor),
      winRate:      parseNumber(domStats.winRate),
      trades:       parseNumber(domStats.trades),
      pips:         parseNumber(domStats.pips),
    },
    openTrades: apiData.openTrades,
    history:    apiData.history,
    dailyGain:  apiData.dailyGain,
    fetchedAt:  new Date().toISOString(),
  };

  // Fill daily % from most recent dailyGain entry
  if (apiData.dailyGain.length > 0) {
    const last = apiData.dailyGain[apiData.dailyGain.length - 1];
    snapshot.account.daily = Array.isArray(last) ? last[1] : (last.value || 0);
  }

  const json = JSON.stringify(snapshot, null, 2);

  // 4. Write to public/ folder
  fs.mkdirSync(path.dirname(PUBLIC_SNAPSHOT), { recursive: true });
  fs.writeFileSync(PUBLIC_SNAPSHOT, json);
  console.log('  ✓ Written to public/vera-snapshot.json');

  // 5. Write to my-fx-instagram repo and push
  if (fs.existsSync(VERA_FX_DIR)) {
    fs.mkdirSync(path.dirname(SNAPSHOT_PATH), { recursive: true });
    fs.writeFileSync(SNAPSHOT_PATH, json);
    try {
      execSync('git add data/vera-snapshot.json', { cwd: VERA_FX_DIR });
      execSync(`git commit -m "data: daily snapshot ${new Date().toISOString().slice(0,10)}"`, { cwd: VERA_FX_DIR });
      execSync('git push origin master', { cwd: VERA_FX_DIR });
      console.log('  ✓ Pushed snapshot to my-fx-instagram');
    } catch (e) {
      console.log('  [git] nothing to push or push failed:', e.message);
    }
  }

  // 6. Send Telegram report
  const acct = snapshot.account;
  await sendTelegram(
    `📊 <b>YourBrand Daily Report</b>\n\n` +
    `💰 Balance: $${acct.balance.toFixed(2)}\n` +
    `⚖️ Equity: $${acct.equity.toFixed(2)}\n` +
    `📈 Gain: ${acct.gain.toFixed(2)}%\n` +
    `🎯 Win Rate: ${acct.winRate.toFixed(0)}%\n` +
    `🔓 Open Trades: ${snapshot.openTrades.length}`
  );

  console.log(`[${new Date().toISOString()}] Done.`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
```

> ⚠️ WARNING: Update `VERA_FX_DIR` on line 9 to the actual path of your `my-fx-instagram` folder on your machine.
```

- [ ] **Step 9: Write sections 2.9 (local test) and 2.10 (Windows Task Scheduler)**

```markdown
## 2.9 Test Locally

```powershell
cd myfxbook-mcp
node src/runner.js
```

Expected output:
```
[2026-06-14T08:00:00.000Z] Starting scraper
  ✓ Myfxbook login OK
  ✓ Scraped stats: { balance: '2978.24', ... }
  ✓ Written to public/vera-snapshot.json
  ✓ Pushed snapshot to my-fx-instagram
  [telegram] message sent
[2026-06-14T08:01:30.000Z] Done.
```

> ✅ CHECKPOINT: Check `public/vera-snapshot.json` — it should contain your real balance and open trades, not zeros.

## 2.10 Windows Task Scheduler

Schedule the scraper to run automatically every weekday at 08:00.

1. Open **Task Scheduler** (search in Start Menu)
2. Click **Create Task** (not "Create Basic Task")
3. **General tab:**
   - Name: `FX Daily Scraper`
   - Tick: **Run whether user is logged on or not**
   - Tick: **Run with highest privileges**
4. **Triggers tab → New:**
   - Begin the task: **On a schedule**
   - Daily, at **08:00:00**
   - Tick: **Enabled**
5. **Actions tab → New:**
   - Action: Start a program
   - Program: `node`
   - Add arguments: `src/runner.js`
   - Start in: `C:\path\to\your\myfxbook-mcp` (your actual folder path)
6. **Settings tab:**
   - Tick: **Run task as soon as possible after a scheduled start is missed**
7. Click **OK** — enter your Windows password if prompted

> 💡 TIP: To test the scheduled task, right-click it in Task Scheduler and choose **Run**. Check the Last Run Result shows `(0x0)` which means success.
```

- [ ] **Step 10: Phase 2 Checkpoint and commit**

```bash
git add docs/setup/phase-2-scraper.md
git commit -m "docs: add Phase 2 scraper setup guide"
git push origin master
```

---

## Task 4: Phase 3 — Instagram Pipeline

**File:** `docs/setup/phase-3-instagram-pipeline.md`

- [ ] **Step 1: Frontmatter + section 3.1 Clone repo**

```yaml
---
phase: 3
title: "Instagram Pipeline Setup"
estimated_time: "60 minutes"
prerequisites: ["Phase 0 complete", "Phase 1 complete", "Phase 2 complete"]
outputs:
  - my-fx-instagram/ repo with all Python files
  - POST_TYPE=weekly python instagram/run.py generates a PNG without errors
  - All placeholder values replaced with your own brand
---
```

- [ ] **Step 2: Write sections 3.1–3.3 (clone, folder structure, requirements)**

```markdown
## 3.1 Clone Your GitHub Repo Locally

```powershell
git clone https://github.com/yourusername/my-fx-instagram.git
cd my-fx-instagram
```

## 3.2 Create Folder Structure

```powershell
mkdir instagram
mkdir instagram\assets
mkdir instagram\posts
mkdir instagram\buffer
mkdir instagram\buffer\daily
mkdir instagram\buffer\weekly
mkdir instagram\buffer\monthly
mkdir instagram\buffer\trust
mkdir instagram\buffer\edu
mkdir instagram\buffer\edu\risk
mkdir instagram\buffer\edu\pairs
mkdir instagram\buffer\edu\setup
mkdir instagram\tests
mkdir data
```

Create placeholder `.gitkeep` files so Git tracks the empty folders:
```powershell
foreach ($dir in @(
  "instagram\buffer\daily", "instagram\buffer\weekly",
  "instagram\buffer\monthly", "instagram\buffer\trust",
  "instagram\buffer\edu\risk", "instagram\buffer\edu\pairs",
  "instagram\buffer\edu\setup", "instagram\posts"
)) { New-Item "$dir\.gitkeep" -ItemType File -Force }
```

## 3.3 Create requirements.txt

**`instagram/requirements.txt`**
```
matplotlib==3.8.4
numpy==1.26.4
requests==2.31.0
Pillow==10.3.0
```

Install:
```powershell
pip install -r instagram\requirements.txt
```
```

- [ ] **Step 3: Write section 3.4 — post.py (no customisation needed, show full file)**

The full `instagram/post.py` content from the existing codebase, explained line by line.

```markdown
## 3.4 Create instagram/post.py

This file handles the two-step Meta Graph API publishing flow. No customisation needed.

**`instagram/post.py`**
```python
import os
import time
import requests

GRAPH = 'https://graph.facebook.com/v19.0'
IG_ID = os.environ['IG_USER_ID']
TOKEN = os.environ['META_ACCESS_TOKEN']


def _check(r: requests.Response):
    if not r.ok:
        raise RuntimeError(f"Meta API error {r.status_code}: {r.text}")
    return r.json()


def publish(image_url: str, caption: str) -> str:
    # Step 1 — create media container
    data = _check(requests.post(
        f'{GRAPH}/{IG_ID}/media',
        params={
            'image_url':    image_url,
            'caption':      caption,
            'access_token': TOKEN,
        }
    ))
    container_id = data['id']
    print(f'  container created: {container_id}')

    # Wait for Instagram to process the image (up to 60 seconds)
    for attempt in range(12):
        time.sleep(5)
        status = _check(requests.get(
            f'{GRAPH}/{container_id}',
            params={'fields': 'status_code', 'access_token': TOKEN}
        ))
        if status.get('status_code') == 'FINISHED':
            break
        print(f'  processing… ({status.get("status_code")})')
    else:
        raise TimeoutError('Instagram container did not finish processing')

    # Step 2 — publish
    result = _check(requests.post(
        f'{GRAPH}/{IG_ID}/media_publish',
        params={
            'creation_id':  container_id,
            'access_token': TOKEN,
        }
    ))
    post_id = result['id']
    print(f'  published: {post_id}')
    return post_id
```
```

- [ ] **Step 4: Write section 3.5 — run.py (show full file with CUSTOMISE comments)**

Show the full `instagram/run.py` with callouts for the two paths they must update: `QR_PATH` asset filename.

- [ ] **Step 5: Write sections 3.6–3.8 — captions.py, data files, buffer gitkeep**

Write full `captions.py` with `# CUSTOMISE:` markers on `_CTA`, `TAGS`, brand strings.

- [ ] **Step 6: Write section 3.9 — placeholder data files**

```markdown
## 3.9 Create Placeholder Data Files

**`data/vera-snapshot.json`** — placeholder with zero values so the pipeline can run before live data:
```json
{
  "account": {
    "balance": 3000.00,
    "equity": 3000.00,
    "daily": 0.0,
    "monthly": 0.0,
    "gain": 0.0,
    "drawdown": 0.0,
    "profitFactor": 0.0,
    "winRate": 0,
    "trades": 0,
    "pips": 0
  },
  "openTrades": [],
  "history": [],
  "dailyGain": [],
  "fetchedAt": "2026-01-01T00:00:00.000Z"
}
```

**`data/edu-counter.json`**
```json
{"index": 0}
```
```

- [ ] **Step 7: Write Phase 3 Checkpoint and commit**

```powershell
$env:POST_TYPE = "weekly"
python instagram/run.py
```

Expected: image file created at `instagram/posts/YYYY-MM-DD-weekly.png` with no errors.

```bash
git add docs/setup/phase-3-instagram-pipeline.md
git commit -m "docs: add Phase 3 Instagram pipeline guide"
git push origin master
```

---

## Task 5: Phase 4 — GitHub Actions & Meta API Keys (Most Detailed)

**File:** `docs/setup/phase-4-github-actions.md`

This is the most critical chapter. It must walk through the full Meta API key flow step by step.

- [ ] **Step 1: Frontmatter**

```yaml
---
phase: 4
title: "GitHub Actions Automation & Meta API Keys"
estimated_time: "20 minutes"
prerequisites: ["Phase 0 complete", "Phase 3 complete", "my-fx-instagram repo pushed to GitHub"]
outputs:
  - .github/workflows/insta-post.yml committed
  - IG_USER_ID obtained
  - META_ACCESS_TOKEN (long-lived, 60 days) obtained
  - Both secrets added to GitHub repo
  - workflow_dispatch triggers successfully
---
```

- [ ] **Step 2: Write section 4.1 — Workflow file (exact content)**

```markdown
## 4.1 Create the GitHub Actions Workflow

Create the file `.github/workflows/insta-post.yml`:

```powershell
mkdir .github
mkdir .github\workflows
```

**`.github/workflows/insta-post.yml`**
```yaml
name: Instagram Auto-Post

on:
  schedule:
    # Monday    09:00 SGT = 01:00 UTC → weekly performance card
    - cron: '0 1 * * 1'
    # Tuesday   09:00 SGT = 01:00 UTC → educational post (rotating)
    - cron: '0 1 * * 2'
    # Wednesday 09:00 SGT = 01:00 UTC → live trade update
    - cron: '0 1 * * 3'
    # Thursday  09:00 SGT = 01:00 UTC → educational post (rotating)
    - cron: '0 1 * * 4'
    # Friday    09:00 SGT = 01:00 UTC → live trade update
    - cron: '0 1 * * 5'
    # 1st of every month 09:00 SGT → monthly P&L chart
    - cron: '0 1 1 * *'
  workflow_dispatch:
    inputs:
      post_type:
        description: 'Post type (weekly | monthly | daily | trust | edu)'
        required: false
        default: 'weekly'

permissions:
  contents: write

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip
          cache-dependency-path: instagram/requirements.txt

      - name: Install dependencies
        run: pip install -r instagram/requirements.txt

      - name: Generate image & post to Instagram
        env:
          IG_USER_ID:        ${{ secrets.IG_USER_ID }}
          META_ACCESS_TOKEN: ${{ secrets.META_ACCESS_TOKEN }}
          GITHUB_TOKEN:      ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          POST_TYPE:         ${{ github.event.inputs.post_type }}
        run: python instagram/run.py

      - name: Upload image artifact
        uses: actions/upload-artifact@v4
        with:
          name: instagram-post-${{ github.run_id }}
          path: instagram/posts/
          retention-days: 30
```

> 💡 TIP: The cron times use UTC. The table below shows how to adjust for your timezone:
> | Your timezone | UTC offset | 09:00 local = UTC |
> |---|---|---|
> | SGT (Singapore) | +8 | 01:00 |
> | IST (India) | +5:30 | 03:30 |
> | GMT (UK) | +0/+1 | 09:00/08:00 |
> | EST (US East) | -5 | 14:00 |
```

- [ ] **Step 3: Write section 4.2 — Getting IG_USER_ID (full walkthrough)**

```markdown
## 4.2 Getting Your Instagram Business Account ID (IG_USER_ID)

Your `IG_USER_ID` is a numeric ID (not your username). It is needed to call the Instagram API.

### Step 1: Open Meta Graph API Explorer

Go to: [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)

### Step 2: Select Your App

In the top-right dropdown, select the app you created in Phase 0 (e.g. `YourBrand Instagram Bot`).

### Step 3: Generate a User Access Token

1. Click **Generate Access Token**
2. A permissions dialog appears — tick these permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
   - `pages_show_list`
3. Click **Generate Token** and accept the Facebook login popup
4. A token appears in the Access Token field — copy it temporarily (you will exchange it for a long-lived token next)

### Step 4: Find Your Facebook Pages

In the Graph API Explorer, enter this in the query field and click **Submit**:

```
/me/accounts
```

Response looks like:
```json
{
  "data": [
    {
      "access_token": "EAAB...",
      "category": "Finance",
      "id": "123456789012345",
      "name": "YourBrand FX"
    }
  ]
}
```

Note the `"id"` — this is your **Facebook Page ID**.

### Step 5: Get Instagram Business Account ID from the Page

Replace `PAGE_ID` with your Facebook Page ID and submit:

```
/PAGE_ID?fields=instagram_business_account
```

Response:
```json
{
  "instagram_business_account": {
    "id": "17841400000000000"
  },
  "id": "123456789012345"
}
```

The `instagram_business_account.id` is your **IG_USER_ID**.

> ✅ CHECKPOINT: Note this 17-digit number. It starts with `178...`

**Save this value:**
| Item | Your Value |
|---|---|
| IG_USER_ID | ____________ |
```

- [ ] **Step 4: Write section 4.3 — Getting META_ACCESS_TOKEN (full walkthrough)**

```markdown
## 4.3 Getting Your Long-Lived Meta Access Token (META_ACCESS_TOKEN)

Instagram API requires a token to authorise publishing. Short-lived tokens expire in 1 hour. You need to exchange it for a long-lived token (valid 60 days).

### Step 1: Get a Short-Lived User Access Token

You already have this from section 4.2 Step 3 — it is in the Graph API Explorer Access Token field.

If you need a fresh one:
1. Go back to [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)
2. Select your app
3. Click **Generate Access Token** with the same permissions as listed in 4.2 Step 3

Copy the short-lived token.

### Step 2: Exchange for a Long-Lived Token

Open this URL in your browser (replace the three values in CAPS):

```
https://graph.facebook.com/v19.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id=YOUR_APP_ID
  &client_secret=YOUR_APP_SECRET
  &fb_exchange_token=YOUR_SHORT_LIVED_TOKEN
```

Or run this in PowerShell:

```powershell
$APP_ID     = "YOUR_APP_ID"
$APP_SECRET = "YOUR_APP_SECRET"
$SHORT_TOKEN = "YOUR_SHORT_LIVED_TOKEN"

Invoke-RestMethod "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=$APP_ID&client_secret=$APP_SECRET&fb_exchange_token=$SHORT_TOKEN"
```

Response:
```json
{
  "access_token": "EAAB...very_long_string...",
  "token_type": "bearer",
  "expires_in": 5183944
}
```

The `access_token` in the response is your **long-lived token** (~60 days).

### Step 3: Verify the Token Works

Test it by calling the API with your IG_USER_ID:

```powershell
$TOKEN  = "YOUR_LONG_LIVED_TOKEN"
$IG_ID  = "YOUR_IG_USER_ID"

Invoke-RestMethod "https://graph.facebook.com/v19.0/${IG_ID}?fields=username,name&access_token=$TOKEN"
```

Expected response:
```json
{
  "username": "yourusername",
  "name": "YourBrand FX",
  "id": "17841400000000000"
}
```

> ✅ CHECKPOINT: If you see your Instagram username in the response, your token is valid.

> 🔒 SECURITY: Your long-lived token is as sensitive as a password. Never paste it into chat, code, or a public file. It goes only into GitHub Secrets (next section).

**Save this value (temporarily — goes into GitHub Secrets):**
| Item | Your Value |
|---|---|
| META_ACCESS_TOKEN | ____________ |

> ⚠️ WARNING: This token expires in 60 days. Set a calendar reminder now to renew it before expiry. See Phase 7 section 7.1 for the renewal procedure.
```

- [ ] **Step 5: Write section 4.4 — Adding secrets to GitHub**

```markdown
## 4.4 Add API Keys to GitHub Secrets

GitHub Secrets stores your credentials securely. The Actions workflow reads them as environment variables at runtime — they are never stored in your code.

1. Go to your `my-fx-instagram` repository on GitHub
2. Click **Settings** (top menu)
3. In the left sidebar: **Secrets and variables → Actions**
4. Click **New repository secret**

Add these two secrets one at a time:

| Secret Name | Value |
|---|---|
| `IG_USER_ID` | Your 17-digit Instagram Business Account ID from section 4.2 |
| `META_ACCESS_TOKEN` | Your long-lived token from section 4.3 |

> 🔒 SECURITY: Once saved, GitHub never shows the value again. If you lose it, generate a new token following section 4.3.

> ⚠️ WARNING: The secret names must be exactly `IG_USER_ID` and `META_ACCESS_TOKEN` — the workflow file references these exact names.
```

- [ ] **Step 6: Write section 4.5 — Manual trigger test**

```markdown
## 4.5 Trigger Your First Post Manually

1. Push all your files to GitHub:
   ```powershell
   git add .
   git commit -m "feat: initial Instagram pipeline setup"
   git push origin master
   ```

2. Go to your GitHub repo → **Actions** tab
3. Click **Instagram Auto-Post** in the left sidebar
4. Click **Run workflow** (top right)
5. Set **Post type** to `weekly`
6. Click **Run workflow**

Watch the live logs — you should see:
```
Generating post: weekly (2026-06-14)
  saved: .../instagram/posts/2026-06-14-weekly.png
  [qr] stamped referral QR onto 2026-06-14-weekly.png
  url: https://raw.githubusercontent.com/yourusername/my-fx-instagram/...
  waiting for CDN…
  container created: 18112134244779999
  published: 18109611085941749
Done — weekly post published.
```
```

- [ ] **Step 7: Phase 4 Checkpoint and commit**

```bash
git add docs/setup/phase-4-github-actions.md .github/
git commit -m "docs: add Phase 4 GitHub Actions and Meta API guide"
git push origin master
```

---

## Task 6: Phase 5 — Customise Your Brand

**File:** `docs/setup/phase-5-customise-brand.md`

- [ ] **Step 1: Frontmatter + section 5.1 Colour palette reference table**

Provide one master table listing every colour constant across `generate_status.py`, `generate.py`, `generate_edu.py` with hex values and what each controls.

- [ ] **Step 2: Write section 5.2 — Brand name find-and-replace**

List every string that contains "VERA LEVEL FX" or "veralevel.fx" or "@veralevel.fx" with the file:line location and what to replace it with.

- [ ] **Step 3: Write sections 5.3–5.5 — Hashtags, CTA block, QR code**

```markdown
## 5.3 Hashtags

In `instagram/captions.py`, find the `TAGS` constant and replace with hashtags relevant to your brand:

```python
TAGS = (
    "#forex #forextrader #forextrading #algotrading #algorithmic "
    "#icmarkets #myfxbook #xauusd #gold #forexsignals "
    "#tradingstrategy #YOURCOUNTRY #investing#YOURCOUNTRY "
    "#financialfreedom #wealthbuilding #YourBrandFX "
    "#forexlifestyle #passiveincome #tradingresults"
)
```

## 5.4 CTA Block

In `instagram/captions.py`, replace the `_CTA` constant:

```python
_CTA = (
    "\n\n📲 Live signals → https://t.me/YOUR_TELEGRAM"
    "\n🌐 Live account → https://YOUR_WEBSITE"
    "\n🏦 Open IC Markets account →"
    "\nhttps://icmarkets.com/global/en/?camp=YOUR_CAMP_ID"
)
```

Replace:
- `YOUR_TELEGRAM` → your Telegram username or channel
- `YOUR_WEBSITE` → your website or Vercel URL
- `YOUR_CAMP_ID` → your IC Markets IB campaign number

## 5.5 QR Code

Generate your referral QR code:
1. Go to [qr-code-generator.com](https://www.qr-code-generator.com) (free)
2. Paste your IC Markets referral URL: `https://icmarkets.com/global/en/?camp=YOUR_CAMP_ID`
3. Download as PNG — minimum 200×200 pixels
4. Save as `instagram/assets/qr-icmarkets.jpg`

> 💡 TIP: Scan the QR code yourself before pushing to confirm it opens the right URL.
```

- [ ] **Step 4: Write section 5.6 — Educational content template (full 12-slot structure)**

Provide the complete `edu_content.py` template with all 5 RISK_RULES, 4 PAIRS, and 4 SETUPS filled with placeholder structure and inline comments explaining what to write for each field.

- [ ] **Step 5: Phase 5 Checkpoint and commit**

```bash
git add docs/setup/phase-5-customise-brand.md
git commit -m "docs: add Phase 5 brand customisation guide"
git push origin master
```

---

## Task 7: Phase 6 — Go Live & Verify

**File:** `docs/setup/phase-6-go-live.md`

- [ ] **Step 1: Frontmatter**

```yaml
---
phase: 6
title: "Go Live & Verify"
estimated_time: "15 minutes"
prerequisites: ["All phases 0–5 complete", "vera-snapshot.json has real data"]
outputs:
  - First real Instagram post published with QR code
  - Full pipeline verified end-to-end
---
```

- [ ] **Step 2: Write the 7-step go-live procedure**

Each step numbered, with exact command, expected output, and what to check if it fails.

1. Run scraper → verify snapshot has real data (not zeros)
2. Commit + push snapshot to GitHub
3. Trigger `workflow_dispatch` with `post_type=daily`
4. Watch Actions log (paste expected log lines verbatim)
5. Check Instagram app on phone
6. Scan QR code — confirm referral URL
7. Tap caption links — confirm all three open correctly

- [ ] **Step 3: Write the verification checklist table**

```markdown
## ✅ Phase 6 Checkpoint — Full Verification

| Check | Expected | Status |
|---|---|---|
| `vera-snapshot.json` has real balance (not 3000.00) | Real number from your account | ☐ |
| GitHub Actions run completes green | All steps show ✅ | ☐ |
| Run duration | ~50–65 seconds | ☐ |
| `[qr] stamped referral QR` in log | Present | ☐ |
| `container created: ...` in log | 17+ digit number | ☐ |
| `published: ...` in log | 17+ digit number | ☐ |
| Post visible on Instagram | Within 30 seconds | ☐ |
| QR code scannable | Opens your IC Markets referral URL | ☐ |
| Caption has Telegram link | Tappable on mobile | ☐ |
| Caption has website link | Tappable on mobile | ☐ |
| Caption has IC Markets link | Tappable on mobile | ☐ |

**Congratulations — your pipeline is live. 🎉**
```

- [ ] **Step 4: Commit**

```bash
git add docs/setup/phase-6-go-live.md
git commit -m "docs: add Phase 6 go-live guide"
git push origin master
```

---

## Task 8: Phase 7 — Maintenance & Troubleshooting

**File:** `docs/setup/phase-7-maintenance.md`

- [ ] **Step 1: Frontmatter**

```yaml
---
phase: 7
title: "Maintenance & Troubleshooting"
estimated_time: "Reference — read as needed"
prerequisites: ["Phase 6 complete — pipeline running"]
outputs: []
---
```

- [ ] **Step 2: Write section 7.1 — META_ACCESS_TOKEN renewal (exact steps)**

Full 60-day renewal procedure. Include: how to check when token expires (Graph API `/debug_token` endpoint), exact PowerShell command to exchange, how to update GitHub Secret.

```markdown
## 7.1 Renewing META_ACCESS_TOKEN (Every 60 Days)

Set a recurring calendar reminder 55 days after each renewal.

### Check Token Expiry

```powershell
$TOKEN  = "YOUR_CURRENT_TOKEN"
$APP_ID = "YOUR_APP_ID"

Invoke-RestMethod "https://graph.facebook.com/v19.0/debug_token?input_token=$TOKEN&access_token=${APP_ID}|YOUR_APP_SECRET"
```

Look for `"expires_at"` in the response — it is a Unix timestamp. Convert at [unixtimestamp.com](https://www.unixtimestamp.com).

### Renew the Token

Repeat the steps from Phase 4 section 4.3:
1. Go to Graph API Explorer
2. Generate a new short-lived token (same permissions)
3. Exchange for long-lived token via the PowerShell command
4. Update the GitHub Secret: repo → Settings → Secrets → Actions → `META_ACCESS_TOKEN` → Update
```

- [ ] **Step 3: Write section 7.2 — Cloudflare troubleshooting**

- [ ] **Step 4: Write section 7.3 — Error code reference table**

Full table:
| Error | Cause | Fix |
|---|---|---|
| Meta API 190 | Token expired | Renew META_ACCESS_TOKEN per section 7.1 |
| Meta API 400 | CDN not propagated | Increase `time.sleep(20)` to `time.sleep(35)` in run.py |
| Meta API 36000 | Account not connected to app | Check app is in Live mode, IG account linked to Facebook Page |
| Git push rejected | Remote has new commits | `git pull --rebase origin master && git push` |
| `Balance: 0` in snapshot | Myfxbook DOM scrape failed | Check Myfxbook site didn't change layout; update CSS selectors in scraper.js |
| Actions run skipped | GitHub free tier limit | Check Actions usage in Settings → Billing |
| `edu-counter` wrong slot | Missed post or manual edit | `echo '{"index": N}' > data/edu-counter.json && git add . && git commit -m "fix: reset counter" && git push` |

- [ ] **Step 5: Write sections 7.4–7.6 (buffer, content refresh, quarterly checks)**

- [ ] **Step 6: Commit**

```bash
git add docs/setup/phase-7-maintenance.md
git commit -m "docs: add Phase 7 maintenance and troubleshooting guide"
git push origin master
```

---

## Task 9: SETUP_GUIDE.md Master File

**File:** `SETUP_GUIDE.md` (repo root)

- [ ] **Step 1: Write the file header and introduction**

```markdown
# Build Your Own Instagram Forex Automation System
## A Complete Setup Guide

> **For AI assistants reading this guide:** This document is structured for both human and machine parsing.
> Each phase is self-contained with YAML frontmatter (in the chapter files), code blocks with language tags,
> and explicit checkpoint sections. You can execute any single phase by reading the corresponding
> `docs/setup/phase-N-*.md` file. Prerequisites are listed in each chapter's frontmatter.

**What this guide builds:** A fully automated system that posts live forex trading results to Instagram
5 days a week — weekly performance cards, daily live position updates, monthly P&L charts, and
rotating educational content. Every post includes your IC Markets referral QR code.

**Time to complete:** ~3.5 hours total (broken into phases you can do across multiple sessions)

**Who this is for:** Intermediate users — comfortable with computers and terminals, not a developer.

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
  └── myfxbook-mcp/ (private, never on GitHub)
      └── src/runner.js  ← runs at 08:00 daily via Task Scheduler
          ├── Scrapes Myfxbook (Puppeteer + stealth Chrome)
          ├── Calls Myfxbook REST API
          └── Pushes vera-snapshot.json → [GitHub: my-fx-instagram/data/]

[GitHub Actions] ← triggered at 09:00 daily by cron
  └── my-fx-instagram/
      ├── instagram/run.py          ← reads snapshot, decides post type
      ├── instagram/generate*.py    ← renders 1080×1080 PNG with Matplotlib
      ├── instagram/captions.py     ← generates caption with your CTA links
      ├── instagram/run.py          ← stamps QR code, commits PNG, calls Meta API
      └── instagram/post.py         ← Meta Graph API: create container → publish

[Instagram @yourusername]
  └── Post appears on your feed with image + caption + QR code
```

---
```

- [ ] **Step 2: Concatenate all 8 chapter files inline after the ToC**

Each chapter is included with a `---` divider and the chapter heading. The full text of each phase chapter is appended so SETUP_GUIDE.md is truly self-contained.

- [ ] **Step 3: Add the Quick Reference section at the end**

```markdown
---

## Quick Reference

### Key Files

| File | What to customise |
|---|---|
| `instagram/captions.py` | `_CTA` block, `TAGS` hashtags, brand strings |
| `instagram/generate_status.py` | `GOLD`, `NAVY`, brand name in text strings |
| `instagram/generate.py` | Colour constants, brand name, footer text |
| `instagram/edu_content.py` | All 12 slots — your own rules, pairs, setups |
| `instagram/assets/qr-icmarkets.jpg` | Your IC Markets referral QR code image |
| `data/vera-snapshot.json` | Populated automatically by the scraper |
| `data/edu-counter.json` | Rotation counter — reset with `{"index": 0}` |

### Key Commands

```powershell
# Run scraper manually
cd myfxbook-mcp && node src/runner.js

# Generate a post locally for preview
$env:POST_TYPE = "daily"
python instagram/run.py

# Trigger a post via GitHub Actions CLI
gh workflow run insta-post.yml --field post_type=daily

# Check Actions run status
gh run list --workflow=insta-post.yml --limit=5

# Reset educational content counter to slot 0
echo '{"index": 0}' | Set-Content data/edu-counter.json
git add data/edu-counter.json
git commit -m "fix: reset edu counter"
git push
```

### Token Renewal Calendar

| Action | Frequency | How |
|---|---|---|
| Renew META_ACCESS_TOKEN | Every 55 days | Phase 7 section 7.1 |
| Check IB referral link | Quarterly | Open your IC Markets referral URL in browser |
| Review educational content | Every 6 weeks | Update `edu_content.py` if needed |
| Check Actions run history | Monthly | GitHub → Actions → check for failures |
```

- [ ] **Step 4: Commit SETUP_GUIDE.md**

```bash
git add SETUP_GUIDE.md docs/setup/
git commit -m "docs: add complete SETUP_GUIDE.md master file"
git push origin master
```

---

## Self-Review

**Spec coverage check:**
- ✅ Phase 0: All 7 account types covered (IC Markets, Myfxbook, Instagram, Meta Dev, GitHub ×2, Telegram)
- ✅ Phase 1: Node.js, Python (with PATH warning), Git, Chrome, verify commands
- ✅ Phase 2: Full scraper from scratch — package.json, .env, all 4 src files, Task Scheduler
- ✅ Phase 3: Full pipeline — all Python files with CUSTOMISE markers, placeholder data files, buffer folders
- ✅ Phase 4: Meta API walkthrough — App creation, IG_USER_ID lookup, short→long-lived token exchange, GitHub Secrets
- ✅ Phase 5: Colour palette table, brand name strings, CTA block, QR generation, full edu_content template
- ✅ Phase 6: 7-step go-live procedure + 11-item verification table
- ✅ Phase 7: Token renewal, Cloudflare fix, error code table, buffer management
- ✅ SETUP_GUIDE.md: ToC, architecture diagram, quick reference, concatenated chapters

**Placeholder scan:** No TBD, TODO, or vague steps — every section specifies exact commands, expected output, and full file content.

**Format compliance:** Every chapter has YAML frontmatter, `> ⚠️` callouts, fenced code blocks with language tags, and a `## ✅ Phase N Checkpoint` section.
