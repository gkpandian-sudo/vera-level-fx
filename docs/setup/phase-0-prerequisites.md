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

# Phase 0 — Prerequisites & Accounts

Before writing a single line of code, you need to set up the external accounts and services this system depends on. This phase is all clicks — no terminal required.

---

## 0.1 IC Markets Live Account

Go to [icmarkets.com](https://icmarkets.com) and open a **live** trading account.

> ⚠️ WARNING: This guide requires a **live** account, not a demo. Myfxbook tracks real P&L — demo data produces meaningless posts.

1. Click **Open Live Account**
2. Choose account type: **Raw Spread** (lowest spreads for algorithmic trading)
3. Complete KYC verification (ID + proof of address — takes 1–2 business days)
4. Fund your account and activate MT4 or MT5
5. **Note your account number** — visible in the Client Portal under "My Accounts"

> 💡 TIP: Your IC Markets account number looks like `12345678`. Save it — you will enter it in Myfxbook in section 0.2.

> 💡 TIP: If you have an IB (Introducing Broker) referral link, use it when signing up — it usually entitles you to rebates on commissions.

---

## 0.2 Myfxbook Account

Myfxbook is the third-party audit service that publicly verifies your trading results. It gives your Instagram posts credibility — every stat is live-verified, not self-reported.

1. Go to [myfxbook.com](https://www.myfxbook.com) and create a free account
2. Click **My Portfolio → Add System**
3. Choose **Automatic Sync** and select your broker: **IC Markets**
4. Enter your MT4/MT5 **account number** and **investor password** (read-only — never your main password)
5. Give your system a name (e.g. `YourBrand FX`)
6. Click **Add System** and wait 10–15 minutes for the first sync

> 🔒 SECURITY: Use the **investor password** only — it is read-only and cannot place or close trades. Your main trading password should never leave your MT4 terminal.

---

## 0.3 Make Your Myfxbook Account Public

The scraper reads your account's public page. It must be set to public.

1. Go to **My Portfolio → [Your System Name] → Edit**
2. Set **Privacy** to **Public**
3. Click **Save**
4. Visit your public page:
   ```
   https://www.myfxbook.com/members/yourusername/yoursystemname/YOUR_ACCOUNT_ID
   ```
5. **Note your Account ID** — it is the number at the end of the URL

> ✅ CHECKPOINT: Open your Myfxbook public page in a browser while logged out (incognito mode). You should see your balance, gain, and trade history without being logged in.

**Save this value:**

| Item | Your Value |
|---|---|
| Myfxbook Account ID | ____________ |
| Myfxbook public page URL | ____________ |

---

## 0.4 Instagram Business Account + Facebook Page

Instagram's Graph API only works with **Business** or **Creator** accounts that are linked to a **Facebook Page**. Both are required.

### 0.4.1 Create or Convert Your Instagram Account

If you already have an Instagram account:
1. Open Instagram app → **Profile → Settings (⚙️) → Account → Switch to Professional Account**
2. Choose **Business**
3. Select a category (e.g. "Finance" or "Investing")

If you are starting fresh:
1. Create a new Instagram account at [instagram.com](https://www.instagram.com)
2. Follow the steps above to convert it to Business

### 0.4.2 Create a Facebook Page

1. Go to [facebook.com/pages/create](https://www.facebook.com/pages/create)
2. Choose **Business or Brand**
3. Name it the same as your Instagram handle (e.g. `YourBrand FX`)
4. Complete the basic setup (profile photo, description)

### 0.4.3 Link Instagram to Facebook Page

1. On Facebook, go to your Page → **Settings → Instagram**
2. Click **Connect Account** and log in to your Instagram account
3. Confirm the connection

> ✅ CHECKPOINT: On your Facebook Page settings, under Instagram, you should see your Instagram username listed as "Connected".

**Save this value:**

| Item | Your Value |
|---|---|
| Instagram username | @____________ |
| Facebook Page name | ____________ |

---

## 0.5 Meta Developer App

This is where you create the API credentials that allow the automation to post to Instagram. This is the most important account to set up correctly.

### 0.5.1 Create a Meta Developer Account

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click **Get Started** and log in with your **Facebook account** (the one linked to your Page)
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

1. On your App Dashboard, scroll down to the **Products** section
2. Find **Instagram Graph API** and click **Set Up**
3. This adds the Instagram product to your app — no further configuration needed here

### 0.5.4 Switch App to Live Mode

> ⚠️ WARNING: While your app is in **Development** mode, it can only post to Instagram accounts that have been added as Test Users. You must switch to **Live** mode so it can post to your real account.

1. On the App Dashboard top bar, toggle **Development → Live**
2. If asked to verify your app: select **"I don't intend to provide access to other users"** and confirm
3. The toggle should now show **Live** in green

> 💡 TIP: If Meta asks you to complete "App Review" — you do not need to. App Review is for apps that access other people's accounts. For a bot that only posts to your own Instagram, Live mode with basic permissions is sufficient.

### 0.5.5 Note Your App ID and App Secret

1. Go to **App Settings → Basic**
2. Copy:
   - **App ID** (visible at top of the page)
   - **App Secret** → click **Show** to reveal it

> 🔒 SECURITY: Never share your App Secret. It is equivalent to a master password for your app. Do not commit it to GitHub — it will go in GitHub Secrets in Phase 4.

**Save these values:**

| Item | Your Value |
|---|---|
| Meta App ID | ____________ |
| Meta App Secret | ____________ |

---

## 0.6 GitHub Account + Two Repositories

You need two GitHub repos:
- A **private** repo for the scraper (contains your Myfxbook credentials)
- A **public** repo for the Instagram pipeline (GitHub Actions needs public access to images)

### 0.6.1 Create GitHub Account

Go to [github.com](https://github.com) and sign up if you don't have an account.

### 0.6.2 Create the Scraper Repo (Private)

1. Click **New Repository** (the `+` button top right)
2. **Repository name:** `myfxbook-mcp`
3. Set visibility to **Private** ← important: this repo will contain your Myfxbook login credentials in `.env`
4. Do NOT tick "Initialize this repository with a README"
5. Click **Create repository**

### 0.6.3 Create the Instagram Pipeline Repo (Public)

1. Click **New Repository**
2. **Repository name:** `my-fx-instagram` (or your preferred name)
3. Set visibility to **Public** — GitHub Actions runs here, and the Meta API fetches images by raw URL which requires public access
4. Do NOT tick "Initialize this repository with a README"
5. Click **Create repository**

**Save these values:**

| Item | Your Value |
|---|---|
| GitHub username | ____________ |
| Instagram repo name | `my-fx-instagram` |
| Instagram repo full name | `yourusername/my-fx-instagram` |

---

## 0.7 Telegram Bot (Daily Scraper Reports)

The scraper sends you a daily summary via Telegram so you know it ran successfully without you having to check manually.

### 0.7.1 Create the Bot

1. Open Telegram and search for **@BotFather**
2. Send the message: `/newbot`
3. Enter a display name: `YourBrand Daily Report`
4. Enter a username: `yourbrand_report_bot` (must end in `bot`, must be unique)
5. BotFather replies with your **Bot Token** — it looks like `8706182750:AAHjO_QVmXcR...`

### 0.7.2 Get Your Chat ID

1. Send any message to your new bot (e.g. "hello")
2. Open this URL in your browser, replacing `YOUR_BOT_TOKEN` with your actual token:

```
https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
```

3. Find the JSON field `"chat":{"id":1234567890}` — that number is your **Chat ID**

> 💡 TIP: If the response shows `"result":[]` (empty), send another message to your bot and refresh the URL.

**Save these values:**

| Item | Your Value |
|---|---|
| Telegram Bot Token | ____________ |
| Telegram Chat ID | ____________ |

> 💡 TIP: Keep this reference table in a password manager or encrypted note. You will paste these values into your `.env` file in Phase 2.

---

## ✅ Phase 0 Checkpoint

Before moving to Phase 1, confirm all of the following:

| Item | Status |
|---|---|
| IC Markets live account open and funded | ☐ |
| Myfxbook connected to IC Markets and set to Public | ☐ |
| Myfxbook Account ID noted | ☐ |
| Instagram converted to Business account | ☐ |
| Facebook Page created and linked to Instagram | ☐ |
| Meta Developer App created and switched to Live mode | ☐ |
| Meta App ID and App Secret noted | ☐ |
| GitHub account with 2 repos created (1 private, 1 public) | ☐ |
| Telegram Bot token and Chat ID noted | ☐ |

**Time spent so far:** ~30 minutes. Next: install software on your Windows laptop.
