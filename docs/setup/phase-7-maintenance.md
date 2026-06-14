---
phase: 7
title: "Maintenance & Troubleshooting"
estimated_time: "Reference — read as needed"
prerequisites: ["Phase 6 complete — pipeline is running"]
outputs: []
---

# Phase 7 — Maintenance & Troubleshooting

This is a reference chapter. Bookmark it — you will come back here when something breaks or needs routine maintenance.

---

## 7.1 Renewing META_ACCESS_TOKEN (Every ~60 Days)

The long-lived token expires in approximately 60 days. If it expires, every GitHub Actions run will fail with `Meta API error 190`.

> ⚠️ WARNING: Set a calendar reminder for **55 days** after each renewal — renew before expiry, not after.

### Check When Your Token Expires

Run this in PowerShell (replace values):

```powershell
$TOKEN      = "YOUR_CURRENT_TOKEN"
$APP_ID     = "YOUR_APP_ID"
$APP_SECRET = "YOUR_APP_SECRET"

Invoke-RestMethod "https://graph.facebook.com/v19.0/debug_token?input_token=$TOKEN&access_token=${APP_ID}|${APP_SECRET}"
```

Look for `"expires_at"` in the response — it is a Unix timestamp. Paste it at [unixtimestamp.com](https://www.unixtimestamp.com) to read the human-readable expiry date.

### Renew the Token

1. Go to [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)
2. Select your app
3. Click **Generate Access Token** with these permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
   - `pages_show_list`
4. Copy the short-lived token
5. Exchange for long-lived (Phase 4 section 4.3 PowerShell command):

```powershell
$APP_ID      = "YOUR_APP_ID"
$APP_SECRET  = "YOUR_APP_SECRET"
$SHORT_TOKEN = "PASTE_NEW_SHORT_TOKEN"

Invoke-RestMethod "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=$APP_ID&client_secret=$APP_SECRET&fb_exchange_token=$SHORT_TOKEN"
```

6. Copy the new `access_token` from the response
7. Update the GitHub Secret:
   - Go to repo → **Settings → Secrets and variables → Actions**
   - Click **META_ACCESS_TOKEN** → **Update secret**
   - Paste the new token → **Save changes**

> 💡 TIP: The token renewal takes about 3 minutes. You can do it from any device with a browser.

---

## 7.2 Cloudflare Blocking the Scraper

Myfxbook uses Cloudflare to block bots. If the scraper returns empty stats or a `403 Forbidden` page, Cloudflare has flagged your IP.

### Symptoms

- Telegram report shows all zeros
- `scraper.js` logs: `✓ Scraped stats: { balance: '', equity: '', ... }`
- Puppeteer page loads a Cloudflare challenge screen

### Fixes

**Option 1: Disable VPN (most common cause)**

If your laptop is connected to a VPN, disconnect it before the scraper runs. Cloudflare blocks most VPN/datacenter IP ranges. Residential ISP addresses almost always pass.

**Option 2: Check your IP is not on a blocklist**

Go to [whatismyip.com](https://whatismyip.com) and note your IP. Paste it at [ipqualityscore.com](https://www.ipqualityscore.com/ip-lookup) — if it shows as "VPN" or "proxy", Cloudflare will block it.

**Option 3: Run Chrome in non-headless mode temporarily**

Change `headless: true` to `headless: false` in `scraper.js` to see what the browser actually sees. If you see a Cloudflare challenge, complete it manually once — Cloudflare may whitelist your session.

**Option 4: Add a user agent string**

In `scraper.js`, add after `page.setViewport()`:

```js
await page.setUserAgent(
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
);
```

---

## 7.3 Error Code Reference

### Meta API Errors

| Error | Message | Cause | Fix |
|---|---|---|---|
| `190` | Invalid OAuth access token | Token expired or revoked | Renew `META_ACCESS_TOKEN` per section 7.1 |
| `400` | Image URL unreachable | CDN hasn't propagated yet | Increase `time.sleep(20)` to `time.sleep(35)` in `run.py` |
| `36000` | App not authorised | IG account not linked to Facebook Page | Re-link accounts (Phase 0 section 0.4.3), ensure app is in Live mode |
| `200` | Permission error | Missing `instagram_content_publish` permission | Regenerate token with all required permissions (Phase 4 section 4.2 Step 3) |

### Git Errors

| Error | Cause | Fix |
|---|---|---|
| `rejected — fetch first` | GitHub has commits you don't have locally (Actions added one) | `git pull --rebase origin master && git push` |
| `nothing to commit` | Snapshot content unchanged from yesterday | Normal — push is skipped automatically |

### Python Errors

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'generate'` | Running from wrong directory | Run from repo root: `cd my-fx-instagram && python instagram/run.py` |
| `FileNotFoundError: vera-snapshot.json` | Snapshot not on GitHub yet | Run scraper first, or push placeholder data manually |
| `KeyError: 'IG_USER_ID'` | Environment variable not set | GitHub Secret missing or wrong name — check Settings → Secrets |

### Scraper Errors

| Error | Cause | Fix |
|---|---|---|
| `Balance: 0` in snapshot | Myfxbook DOM scrape failed | Check `page.goto()` URL in `scraper.js` — must match your actual system URL |
| `error: spawn node ENOENT` | Node.js not on PATH in Task Scheduler | Use full path to node.exe in Task Scheduler Actions tab: `C:\Program Files\nodejs\node.exe` |
| Telegram: no message received | Bot token or chat ID wrong | Test token with `getUpdates` URL from Phase 0 section 0.7.2 |

---

## 7.4 Educational Content Counter

The `data/edu-counter.json` file tracks which slot in the 12-post rotation is next. The counter increments automatically after each educational post.

### If the Counter Gets Out of Sync

To reset to a specific slot:

```powershell
# Reset to start of rotation (slot 0)
'{"index": 0}' | Set-Content data\edu-counter.json
git add data\edu-counter.json
git commit -m "fix: reset edu counter to 0"
git push
```

To set to a specific slot (e.g. slot 4):

```powershell
'{"index": 4}' | Set-Content data\edu-counter.json
git add data\edu-counter.json
git commit -m "fix: set edu counter to 4"
git push
```

The 12-slot rotation sequence:
```
0  → risk rule 1        6  → risk rule 3
1  → pair: EURUSD       7  → pair: GBPJPY
2  → setup: EURUSD      8  → setup: GBPJPY
3  → risk rule 2        9  → risk rule 4
4  → pair: XAUUSD       10 → pair: USDJPY
5  → setup: XAUUSD      11 → setup: USDJPY
```

---

## 7.5 Content Buffer

If you want to pre-make images (e.g. a custom graphic for a special occasion) and have the system use those instead of the auto-generated ones, place them in the buffer folders.

Buffer folder structure:
```
instagram/buffer/
├── daily/          ← pre-made daily cards
├── weekly/         ← pre-made weekly cards
├── monthly/        ← pre-made monthly charts
├── trust/          ← pre-made trust/track record cards
└── edu/
    ├── risk/       ← pre-made risk management cards
    ├── pairs/      ← pre-made pair spotlight cards
    └── setup/      ← pre-made setup breakdown cards
```

Rules:
- Filename must end in `.png`
- The system always picks the **oldest** file alphabetically (so name files `001-...`, `002-...` to control order)
- Used files are moved to `instagram/posts/` automatically — they won't be used twice
- The system falls back to auto-generating if the buffer folder is empty

---

## 7.6 Refreshing Educational Content

After 12 educational posts (6 weeks), the rotation repeats. If you want to refresh the content rather than repeat the same posts, update `instagram/edu_content.py` before the cycle completes.

Options:
1. **Update in place** — replace old content in `edu_content.py` before the cycle repeats. The rotation index doesn't change — slot 0 now shows your new content.
2. **Pre-make a new batch** — create 12 new PNG images and place them in the buffer folders. The buffer is used first, then auto-generated content for any empty slots.

---

## 7.7 Quarterly Checklist

Run through this every 3 months to keep the system healthy:

| Task | Why |
|---|---|
| Verify IC Markets referral link still works | IB programs occasionally change URLs |
| Scan your QR code | Confirm it still points to the correct URL |
| Check Myfxbook public page is still public | Privacy settings can reset after account updates |
| Review `TAGS` hashtag set | Trending hashtags change — refresh for reach |
| Check Actions usage in GitHub Settings → Billing | Free tier has 2,000 minutes/month — you use ~1 minute per post |
| Review educational content | Update content that has become outdated |

---

## 7.8 If You Need to Pause Posting

To temporarily disable the automated schedule without deleting anything:

1. Go to GitHub repo → **Actions** tab
2. Click **Instagram Auto-Post** in the left sidebar
3. Click the `...` menu → **Disable workflow**

To re-enable: same steps, choose **Enable workflow**.

The Windows Task Scheduler scraper continues running — it just pushes data to GitHub with no one consuming it. That is fine.

> 💡 TIP: GitHub automatically disables workflows that have not run in 60 days to conserve resources. If you pause for more than 2 months, you will need to manually re-enable the workflow.
