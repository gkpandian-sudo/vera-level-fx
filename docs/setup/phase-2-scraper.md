---
phase: 2
title: "Myfxbook Scraper Setup"
estimated_time: "45 minutes"
prerequisites: ["Phase 0 complete", "Phase 1 complete"]
outputs:
  - myfxbook-mcp/ folder with all source files
  - .env configured with real credentials
  - node src/runner.js runs successfully and produces real data
  - vera-snapshot.json committed to my-fx-instagram GitHub repo
  - Windows Task Scheduler running daily at 08:00
---

# Phase 2 — Myfxbook Scraper Setup

The scraper is a Node.js program that runs on your Windows laptop every morning. It logs into Myfxbook, collects your live account data, and pushes it as `vera-snapshot.json` to your GitHub repo — where GitHub Actions picks it up to generate Instagram posts.

> 🔒 SECURITY: This folder stays on your laptop only. It is never pushed to a public GitHub repo. Your Myfxbook credentials live in a `.env` file that is excluded from version control.

---

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

Replace `yourusername` with your actual GitHub username.

Your folder structure will be:

```
myfxbook-mcp/
├── src/
│   ├── runner.js      ← entry point (you will create this)
│   ├── scraper.js     ← Puppeteer browser scraper
│   ├── fetcher.js     ← Myfxbook REST API client
│   └── telegram.js    ← Telegram notification sender
├── public/            ← local copy of snapshot (not pushed)
├── .env               ← your credentials (never committed)
├── .gitignore         ← excludes .env and node_modules
└── package.json       ← dependencies
```

---

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

Then install dependencies:

```powershell
npm install
```

This creates a `node_modules/` folder and a `package-lock.json`. The install takes 1–2 minutes the first time.

> 💡 TIP: `node-fetch` version **2** (not 3) is used because it supports `require()`. Version 3 is ESM-only and requires extra project configuration.

---

## 2.3 Create .gitignore

**`.gitignore`**
```
node_modules/
.env
*.log
public/
```

---

## 2.4 Create .env

Create `.env` in the `myfxbook-mcp/` root folder. Fill in your values from the Phase 0 reference table.

**`.env`**
```env
# ── Myfxbook credentials ──────────────────────────────────────────
MYFXBOOK_EMAIL=your@email.com
MYFXBOOK_PASSWORD=your_myfxbook_password

# ── Your Myfxbook account ID (from the URL when viewing your system)
MYFXBOOK_ACCOUNT_ID=YOUR_ACCOUNT_ID

# ── Telegram (from Phase 0 section 0.7) ──────────────────────────
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

> 🔒 SECURITY: `.env` is listed in `.gitignore` and must **NEVER** be committed. It contains your Myfxbook login credentials. If you accidentally commit it, change your Myfxbook password immediately.

---

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

---

## 2.6 Create src/fetcher.js

This file calls the Myfxbook REST API to retrieve open trades, trade history, and daily gain data.

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
  // 1. Login — returns a session token
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
  console.log('  ✓ Myfxbook fetch complete');

  return { openTrades, history, dailyGain };
}

module.exports = { fetchVeraData };
```

---

## 2.7 Create src/scraper.js

The REST API does not return all stats (win rate, profit factor, pips, total trades). The scraper uses a real Chrome browser with stealth mode to log in to Myfxbook and extract these from the page.

**`src/scraper.js`**
```js
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const EMAIL = process.env.MYFXBOOK_EMAIL;
const PASS  = process.env.MYFXBOOK_PASSWORD;
const ACCT  = process.env.MYFXBOOK_ACCOUNT_ID;

// CUSTOMISE: update if Chrome is installed at a different path on your machine
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

    // CUSTOMISE: replace the URL below with your actual Myfxbook system page URL
    // Find it by logging into Myfxbook manually and copying the URL of your system
    await page.goto(
      `https://www.myfxbook.com/members/yourusername/yoursystemname/${ACCT}`,
      { waitUntil: 'networkidle2', timeout: 30000 }
    );

    // Extract account stats from the DOM
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

> ⚠️ WARNING: The `page.goto()` URL must match your actual Myfxbook system page. Log in to Myfxbook manually, navigate to your system, and copy the URL from your browser address bar. Replace the placeholder in the code above.

> ⚠️ WARNING: The DOM selectors (`[id*="totalBalance"]` etc.) target Myfxbook's HTML. If Myfxbook updates their site layout, these selectors may stop working. If stats come back as empty strings, open the Myfxbook page in Chrome DevTools (F12), inspect the balance element, and find its `id` attribute.

---

## 2.8 Create src/runner.js

The main orchestrator — runs the fetcher and scraper, merges results, writes the snapshot file, and sends you a Telegram notification.

**`src/runner.js`**
```js
require('dotenv').config();
const fs   = require('fs');
const path = require('path');
const { execSync }        = require('child_process');
const { fetchVeraData }   = require('./fetcher');
const { scrapeVeraStats } = require('./scraper');
const { sendTelegram }    = require('./telegram');

// CUSTOMISE: update this to the actual path of your my-fx-instagram folder
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

  // 3. Merge into snapshot object
  const snapshot = {
    account: {
      balance:      parseNumber(domStats.balance),
      equity:       parseNumber(domStats.equity),
      daily:        0,
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

  // 4. Write local copy
  fs.mkdirSync(path.dirname(PUBLIC_SNAPSHOT), { recursive: true });
  fs.writeFileSync(PUBLIC_SNAPSHOT, json);
  console.log('  ✓ Written to public/vera-snapshot.json');

  // 5. Write to my-fx-instagram repo and push to GitHub
  if (fs.existsSync(VERA_FX_DIR)) {
    fs.mkdirSync(path.dirname(SNAPSHOT_PATH), { recursive: true });
    fs.writeFileSync(SNAPSHOT_PATH, json);
    try {
      execSync('git add data/vera-snapshot.json', { cwd: VERA_FX_DIR });
      execSync(
        `git commit -m "data: daily snapshot ${new Date().toISOString().slice(0,10)}"`,
        { cwd: VERA_FX_DIR }
      );
      execSync('git push origin master', { cwd: VERA_FX_DIR });
      console.log('  ✓ Pushed snapshot to my-fx-instagram');
    } catch (e) {
      console.log('  [git] nothing to push or push failed:', e.message);
    }
  } else {
    console.log('  [warning] my-fx-instagram folder not found at:', VERA_FX_DIR);
  }

  // 6. Send Telegram notification
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

> ⚠️ WARNING: Update `VERA_FX_DIR` on line 12 to the actual path of your `my-fx-instagram` folder on your machine. For example: `path.resolve('C:\\Users\\YourName\\projects\\my-fx-instagram')`.

---

## 2.9 Test Locally

Run the scraper:

```powershell
cd myfxbook-mcp
node src/runner.js
```

Expected output:

```
[2026-06-14T08:00:00.000Z] Starting scraper
  ✓ Myfxbook login OK
  ✓ Scraped stats: { balance: '2978.24', equity: '2971.50', ... }
  ✓ Written to public/vera-snapshot.json
  ✓ Pushed snapshot to my-fx-instagram
  [telegram] message sent
[2026-06-14T08:01:30.000Z] Done.
```

> ✅ CHECKPOINT: Open `public/vera-snapshot.json` and confirm it contains your real account balance and live open trades — not zeros. A `balance` of `0` means the DOM scrape failed (check the Myfxbook page URL in scraper.js).

---

## 2.10 Windows Task Scheduler

Schedule the scraper to run automatically every weekday at 08:00 — one hour before the GitHub Actions workflow posts to Instagram.

1. Press **Win + S** and search for **Task Scheduler** — open it
2. Click **Create Task** (not "Create Basic Task" — the full version has more options)

**General tab:**
- Name: `FX Daily Scraper`
- Tick: **Run whether user is logged on or not**
- Tick: **Run with highest privileges**

**Triggers tab → New:**
- Begin the task: **On a schedule**
- Settings: **Daily**, start at **08:00:00**
- Tick: **Enabled**

**Actions tab → New:**
- Action: **Start a program**
- Program/script: `node`
- Add arguments: `src/runner.js`
- Start in: `C:\path\to\your\myfxbook-mcp` (your actual full folder path)

**Settings tab:**
- Tick: **Run task as soon as possible after a scheduled start is missed**
- This ensures the scraper runs even if your laptop was off at 08:00

Click **OK** — enter your Windows password when prompted.

> 💡 TIP: To test the task, right-click it in Task Scheduler and choose **Run**. Wait 60–90 seconds, then check the **Last Run Result** column — `(0x0)` means success.

> 💡 TIP: Your laptop must be **on and not in sleep mode** at 08:00 for the task to fire. If you leave it in sleep, set the task to "Run as soon as possible after a scheduled start is missed" (already included above) — it will run when you wake the laptop.

---

## ✅ Phase 2 Checkpoint

```powershell
node src/runner.js
```

Expected results:
- Terminal shows `✓ Myfxbook login OK` and `✓ Scraped stats:` with real numbers
- `public/vera-snapshot.json` contains your real balance (not `0`)
- You received a Telegram message with your balance and open trade count
- GitHub repo `my-fx-instagram` has a new commit: `data: daily snapshot YYYY-MM-DD`

**Time spent so far:** ~1 hour 35 minutes total. Next: build the Instagram image pipeline.
