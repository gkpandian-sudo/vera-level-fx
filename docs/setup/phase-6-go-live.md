---
phase: 6
title: "Go Live & Verify"
estimated_time: "15 minutes"
prerequisites: ["All phases 0–5 complete", "vera-snapshot.json has real live data", "QR code image added"]
outputs:
  - First real Instagram post published with live data and QR code
  - Full pipeline verified end-to-end
---

# Phase 6 — Go Live & Verify

This is the end-to-end smoke test. Follow all 7 steps in order to confirm every component works together before the automation runs unattended.

---

## Step 1: Confirm Snapshot Has Real Data

Run the scraper on your laptop and check the output:

```powershell
cd myfxbook-mcp
node src/runner.js
```

Then open the snapshot file and confirm it contains real numbers:

```powershell
Get-Content ..\my-fx-instagram\data\vera-snapshot.json | Select-String "balance","winRate","trades"
```

Expected: real values (not zeros and not the placeholder `3000.00`)

Example of good data:
```json
"balance": 3147.82,
"winRate": 74,
"trades": 312
```

> ⚠️ WARNING: If balance is `0` or `3000.00`, the DOM scrape failed. Check `src/scraper.js` — the `page.goto()` URL must match your actual Myfxbook system page URL.

---

## Step 2: Confirm Snapshot Is on GitHub

Check that the scraper pushed the snapshot to your Instagram repo:

```powershell
cd my-fx-instagram
git log --oneline -3
```

Expected: the most recent commit should be `data: daily snapshot YYYY-MM-DD`

If the snapshot is not on GitHub yet, push it manually:

```powershell
git add data/vera-snapshot.json
git commit -m "data: initial live snapshot"
git push origin master
```

---

## Step 3: Trigger a Daily Post via GitHub Actions

1. Go to your `my-fx-instagram` repository on GitHub
2. Click the **Actions** tab
3. In the left sidebar, click **Instagram Auto-Post**
4. Click **Run workflow**
5. Set **Post type** to `daily`
6. Click the green **Run workflow** button

---

## Step 4: Watch the Live Log

Click on the running workflow to see the live log. Watch for these lines — each confirms a component is working:

```
Generating post: daily (YYYY-MM-DD)
  saved: .../instagram/posts/YYYY-MM-DD-daily.png
  [qr] stamped referral QR onto YYYY-MM-DD-daily.png     ← QR code stamped
  url:   https://raw.githubusercontent.com/...           ← image on CDN
  waiting for CDN…                                        ← 20-second pause
  container created: 18112134244779999                    ← Meta API step 1
  published: 18109611085941749                            ← Meta API step 2
Done — daily post published.
```

**What each line means:**
- `[qr] stamped` → QR code successfully overlaid on the image
- `container created` → Instagram received the image and created a media container
- `published` → Instagram published the post to your feed

> ⚠️ WARNING: If you see `[qr] skipped:` — the QR image file is missing or at the wrong path. Confirm `instagram/assets/qr-icmarkets.jpg` exists and is committed to GitHub.

> ⚠️ WARNING: If you see `Meta API error 190` — your `META_ACCESS_TOKEN` has expired. Follow Phase 7 section 7.1 to get a new long-lived token and update the GitHub Secret.

---

## Step 5: Verify the Post on Instagram

1. Open the Instagram app on your phone
2. Go to your profile
3. The new post should appear within **30 seconds** of the workflow completing

Check that:
- The image looks correct (live data, correct brand colours)
- The QR code is visible in the bottom-right corner of the image
- The caption is formatted correctly with your brand name

---

## Step 6: Scan the QR Code

Point your phone camera at the QR code in the posted image.

Confirm it opens your IC Markets referral URL:
```
https://icmarkets.com/global/en/?camp=YOUR_CAMP_ID
```

> ⚠️ WARNING: If the QR code opens a different URL or fails to scan, regenerate it in Phase 5 section 5.5 with the correct IC Markets URL.

---

## Step 7: Verify Caption Links

In the Instagram post, tap each link in the caption:

1. **Telegram link** — should open your Telegram channel or chat
2. **Website link** — should open your website or Vercel app
3. **IC Markets link** — should open your IC Markets referral page

> 💡 TIP: Instagram only makes links tappable in your **bio**, not in post captions. In captions, links appear as plain text and users must copy-paste them. This is an Instagram limitation — your followers know to copy-paste links from captions.

---

## ✅ Phase 6 Checkpoint — Full Verification

| Check | Expected | Status |
|---|---|---|
| `vera-snapshot.json` has real balance (not `3000.00`) | Real number from your live account | ☐ |
| Snapshot is committed to GitHub | Recent commit `data: daily snapshot ...` | ☐ |
| GitHub Actions run completes | Green tick in Actions tab | ☐ |
| Run duration | ~50–75 seconds | ☐ |
| `[qr] stamped referral QR` in log | Present (no "skipped") | ☐ |
| `container created: ...` in log | 17+ digit number | ☐ |
| `published: ...` in log | 17+ digit number | ☐ |
| Post visible on Instagram | Within 30 seconds of workflow completing | ☐ |
| Image shows live data (not placeholder) | Real balance and trade stats | ☐ |
| QR code is visible on image | Bottom-right corner | ☐ |
| QR code scans correctly | Opens IC Markets referral URL | ☐ |
| Caption displays all 3 CTA lines | Telegram · Website · IC Markets | ☐ |

**Congratulations — your pipeline is live.** 🎉

From tomorrow, the scraper runs at 08:00 via Windows Task Scheduler, and GitHub Actions posts at 09:00 automatically, 5 days a week.
