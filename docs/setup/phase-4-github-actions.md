---
phase: 4
title: "GitHub Actions Automation & Meta API Keys"
estimated_time: "20 minutes"
prerequisites: ["Phase 0 complete", "Phase 3 complete", "my-fx-instagram repo pushed to GitHub"]
outputs:
  - .github/workflows/insta-post.yml committed to repo
  - IG_USER_ID obtained (17-digit Instagram Business Account ID)
  - META_ACCESS_TOKEN obtained (long-lived, valid ~60 days)
  - Both secrets added to GitHub repo Settings → Secrets
  - workflow_dispatch manual trigger runs successfully
---

# Phase 4 — GitHub Actions Automation & Meta API Keys

This phase automates the Instagram posting by creating a GitHub Actions workflow that runs on a schedule. It also walks through the full Meta API setup — getting your Instagram Business Account ID and a long-lived access token.

---

## 4.1 Create the GitHub Actions Workflow

Create the folder structure:

```powershell
mkdir .github
mkdir .github\workflows
```

Create the workflow file:

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

### Cron Schedule — Timezone Reference

The cron times above are set for Singapore time (SGT = UTC+8). Adjust for your timezone:

| Your timezone | UTC offset | 09:00 local = UTC |
|---|---|---|
| SGT (Singapore) | +8 | `0 1 * * N` |
| IST (India) | +5:30 | `30 3 * * N` |
| GMT (UK, winter) | +0 | `0 9 * * N` |
| BST (UK, summer) | +1 | `0 8 * * N` |
| EST (US East, winter) | -5 | `0 14 * * N` |
| AEST (Australia, Sydney) | +10 | `0 23 * * N` (previous day UTC) |

> 💡 TIP: cron day-of-week uses numbers: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday.

---

## 4.2 Getting Your Instagram Business Account ID (IG_USER_ID)

Your `IG_USER_ID` is a 17-digit numeric ID (not your Instagram username). The Meta API requires this to publish to your account.

### Step 1: Open Meta Graph API Explorer

Go to: [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)

### Step 2: Select Your App

In the top-right **Meta App** dropdown, select the app you created in Phase 0 (e.g. `YourBrand Instagram Bot`).

### Step 3: Generate a User Access Token

1. Click **Generate Access Token**
2. A permissions dialog appears — tick all of these:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
   - `pages_show_list`
3. Click **Generate Token** and accept the Facebook login popup
4. A token appears in the **Access Token** field

> 💡 TIP: Copy this token somewhere temporary — you will use it in the next two steps, and also to exchange for a long-lived token in section 4.3.

### Step 4: Find Your Facebook Page ID

In the Graph API Explorer query field, enter:

```
/me/accounts
```

Click **Submit**. The response looks like:

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

Note the `"id"` field — this is your **Facebook Page ID**.

### Step 5: Get Your Instagram Business Account ID

In the Graph API Explorer, replace `PAGE_ID` with your Facebook Page ID and submit:

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

The `instagram_business_account.id` value is your **IG_USER_ID**.

> ✅ CHECKPOINT: This number should be 17 digits and start with `178`. Note it down.

**Save this value:**

| Item | Your Value |
|---|---|
| IG_USER_ID | ____________ |

> ⚠️ WARNING: If `instagram_business_account` is missing from the response, your Instagram account is not connected to this Facebook Page. Go back to Phase 0 section 0.4.3 and re-link the accounts, then retry this step.

---

## 4.3 Getting Your Long-Lived Meta Access Token (META_ACCESS_TOKEN)

Instagram requires a valid access token to authorise publishing. Short-lived tokens from the Graph API Explorer expire in **1 hour**. You need to exchange it for a **long-lived token** (valid ~60 days).

### Step 1: Get the Short-Lived Token

You already have this from section 4.2 Step 3 — the token in the Graph API Explorer Access Token field.

If you need a fresh one: go back to the Graph API Explorer, select your app, and click **Generate Access Token** again with the same permissions.

Copy the token value.

### Step 2: Exchange for a Long-Lived Token

Run this in PowerShell, replacing the three values:

```powershell
$APP_ID      = "YOUR_APP_ID"        # from Phase 0 section 0.5.5
$APP_SECRET  = "YOUR_APP_SECRET"    # from Phase 0 section 0.5.5
$SHORT_TOKEN = "PASTE_SHORT_LIVED_TOKEN_HERE"

Invoke-RestMethod "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=$APP_ID&client_secret=$APP_SECRET&fb_exchange_token=$SHORT_TOKEN"
```

Or open this URL in your browser directly (replace values):

```
https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN
```

Successful response:

```json
{
  "access_token": "EAAB...very_long_string...",
  "token_type": "bearer",
  "expires_in": 5183944
}
```

The `access_token` in the response is your **long-lived token** (expires in ~60 days).

### Step 3: Verify the Token Works

Test that the token can read your Instagram account:

```powershell
$TOKEN = "YOUR_LONG_LIVED_TOKEN"
$IG_ID = "YOUR_IG_USER_ID"

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

> ✅ CHECKPOINT: If you see your Instagram username in the response, the token is valid and has permission to publish.

> 🔒 SECURITY: Your long-lived token is as sensitive as a password. **Never** paste it into chat, source code, or a public file. It goes only into GitHub Secrets (next section).

> ⚠️ WARNING: This token expires in **60 days**. Set a calendar reminder for **55 days from today** to renew it before it expires. See Phase 7 section 7.1 for the renewal procedure.

**Save this value (temporarily — it goes straight into GitHub Secrets):**

| Item | Your Value |
|---|---|
| META_ACCESS_TOKEN | _(do not write down — paste directly into GitHub Secrets)_ |

---

## 4.4 Add API Keys to GitHub Secrets

GitHub Secrets stores credentials securely. The Actions workflow reads them as environment variables at runtime — they are never visible in logs or stored in your code.

1. Go to your `my-fx-instagram` repository on GitHub
2. Click **Settings** (tab at the top)
3. In the left sidebar: **Secrets and variables → Actions**
4. Click **New repository secret**

Add these two secrets, one at a time:

| Secret Name | Value |
|---|---|
| `IG_USER_ID` | Your 17-digit Instagram Business Account ID from section 4.2 |
| `META_ACCESS_TOKEN` | Your long-lived token from section 4.3 |

For each secret:
1. Enter the **Name** exactly as shown (case-sensitive)
2. Paste the **Value**
3. Click **Add secret**

> 🔒 SECURITY: Once saved, GitHub never shows the secret value again. If you lose it or it expires, generate a new token (section 4.3) and update the secret by clicking **Update** on the existing secret.

> ⚠️ WARNING: The secret names must be exactly `IG_USER_ID` and `META_ACCESS_TOKEN` — the workflow YAML file references these exact names. A typo means the workflow runs with empty values and fails.

---

## 4.5 Push and Trigger Your First Post

Push everything to GitHub:

```powershell
git add .
git commit -m "feat: initial Instagram pipeline setup"
git push origin master
```

Now trigger a manual test post:

1. Go to your GitHub repo
2. Click the **Actions** tab
3. In the left sidebar, click **Instagram Auto-Post**
4. Click **Run workflow** (top right, grey button)
5. Set **Post type** to `weekly`
6. Click the green **Run workflow** button

### Expected Log Output

Click on the running workflow to see live logs. You should see:

```
Generating post: weekly (2026-06-14)
  saved: /home/runner/work/.../instagram/posts/2026-06-14-weekly.png
  [qr] stamped referral QR onto 2026-06-14-weekly.png
  url:   https://raw.githubusercontent.com/yourusername/my-fx-instagram/master/instagram/posts/...
  waiting for CDN…
  container created: 18112134244779999
  processing… (IN_PROGRESS)
  published: 18109611085941749
Done — weekly post published.
```

---

## ✅ Phase 4 Checkpoint

| Check | Expected |
|---|---|
| `.github/workflows/insta-post.yml` committed to GitHub | ✅ visible in repo |
| `IG_USER_ID` secret added | ✅ shows in Settings → Secrets (value hidden) |
| `META_ACCESS_TOKEN` secret added | ✅ shows in Settings → Secrets (value hidden) |
| Manual `workflow_dispatch` run completes | ✅ green tick in Actions tab |
| `published: ...` line in workflow log | ✅ 17+ digit post ID |
| Post appears on your Instagram feed | ✅ visible within 30 seconds |

**Time spent so far:** ~2 hours 55 minutes total. Next: customise the branding to match your own identity.
