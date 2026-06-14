---
phase: 1
title: "Local Environment Setup"
estimated_time: "20 minutes"
prerequisites: ["Phase 0 complete"]
outputs:
  - Node.js 20+ installed and on PATH
  - Python 3.11+ installed with pip on PATH
  - Git installed and configured with your identity
  - Google Chrome installed
---

# Phase 1 — Local Environment Setup

Install the four tools the system needs on your Windows machine. Everything here is a standard installer — no terminal tricks required.

---

## 1.1 Node.js 20+

Node.js runs the Myfxbook scraper. You need version 20 or higher.

1. Go to [nodejs.org](https://nodejs.org)
2. Download the **LTS** version (labelled "Recommended For Most Users")
3. Run the installer — accept all defaults
4. Click through the installer — no options need changing

✅ Verify:

```powershell
node --version
```

Expected output: `v20.x.x` or higher

```powershell
npm --version
```

Expected output: `10.x.x` or higher

> 💡 TIP: If you already have Node.js but it is older than version 20, download and install the latest LTS — the installer will replace the old version automatically.

---

## 1.2 Python 3.11+

Python runs the Instagram image generation pipeline — the card renderer, caption builder, and publisher.

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python **3.11.x** or **3.12.x**
3. Run the installer

> ⚠️ WARNING: On the **first screen** of the installer, tick **"Add Python to PATH"** before clicking "Install Now". If you skip this, `python` and `pip` commands will not work in PowerShell and you will need to reinstall.

✅ Verify:

```powershell
python --version
```

Expected: `Python 3.11.x` or `Python 3.12.x`

```powershell
pip --version
```

Expected: `pip 23.x.x from C:\Users\...\Python3xx\...`

> 💡 TIP: If `python` returns `Python 2.7.x`, try `python3 --version` instead. Python 2 ships with some older Windows setups — you need Python 3.

---

## 1.3 Git

Git tracks your code and is used by the scraper to push the daily snapshot to GitHub.

1. Go to [git-scm.com/download/win](https://git-scm.com/download/win)
2. Download **Git for Windows** (64-bit)
3. Run the installer
4. On the **"Adjusting your PATH environment"** step, choose **"Git from the command line and also from 3rd-party software"**
5. All other defaults are fine — click through

✅ Verify:

```powershell
git --version
```

Expected: `git version 2.x.x.windows.x`

### Configure Your Identity

Git requires a name and email to create commits. Run these two commands, replacing the values:

```powershell
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

> 💡 TIP: These don't have to be your real name — just something identifiable. They appear in commit messages.

---

## 1.4 Google Chrome

The Myfxbook scraper uses Puppeteer with **real Google Chrome** (not Chromium). This is critical — Cloudflare detects and blocks Chromium-based headless browsers, but passes real Chrome.

1. Go to [google.com/chrome](https://www.google.com/chrome/)
2. Download and install Google Chrome
3. After installing, note the path (for reference later):
   - Default Windows path: `C:\Program Files\Google\Chrome\Application\chrome.exe`

> ⚠️ WARNING: Do NOT use Microsoft Edge or the Chromium browser. Myfxbook's Cloudflare protection detects these and returns a "403 Forbidden" page. Only Google Chrome passes the check.

> 💡 TIP: If Chrome is already installed, you're done — just confirm the path above exists.

---

## 1.5 Verify All Installs

Run all four version checks at once to confirm everything is on PATH:

```powershell
node --version; npm --version; python --version; git --version
```

Expected output (exact versions may differ):

```
v20.11.0
10.2.4
Python 3.11.7
git version 2.43.0.windows.1
```

If any command returns an error, go back to that section and reinstall, making sure to accept all defaults.

---

## ✅ Phase 1 Checkpoint

All four commands produce version numbers without errors:

```powershell
node --version    # v20.x.x or higher
python --version  # Python 3.11.x or higher
git --version     # git version 2.x.x
```

Google Chrome is installed and the executable exists at:
```
C:\Program Files\Google\Chrome\Application\chrome.exe
```

**Time spent so far:** ~50 minutes total. Next: build the Myfxbook scraper.
