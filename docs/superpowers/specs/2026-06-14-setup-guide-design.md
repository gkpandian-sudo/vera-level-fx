# Setup Guide Design — Vera Level FX (Build Your Own Version)

## Goal

Produce a comprehensive, human- and AI-readable end-to-end guide for an intermediate user who wants to build their own Instagram-automated forex trading showcase system — using their own IC Markets account, Myfxbook tracking, Instagram Business page, and branding.

## Target Reader

- **Technical level:** Intermediate — comfortable with terminals and computers, not a developer
- **Starting point:** Zero code, zero accounts
- **End state:** Fully automated Instagram posting pipeline running unattended, 5 days/week

## Output Files

| File | Purpose |
|---|---|
| `SETUP_GUIDE.md` | Single master file — full guide, human + AI readable |
| `docs/setup/phase-0-prerequisites.md` | Chapter 0 |
| `docs/setup/phase-1-local-environment.md` | Chapter 1 |
| `docs/setup/phase-2-scraper.md` | Chapter 2 |
| `docs/setup/phase-3-instagram-pipeline.md` | Chapter 3 |
| `docs/setup/phase-4-github-actions.md` | Chapter 4 |
| `docs/setup/phase-5-customise-brand.md` | Chapter 5 |
| `docs/setup/phase-6-go-live.md` | Chapter 6 |
| `docs/setup/phase-7-maintenance.md` | Chapter 7 |

## Format Standards

Every file follows these rules so AI tools can parse and execute them:

1. **YAML frontmatter** on every chapter file:
   ```yaml
   ---
   phase: 2
   title: "Myfxbook Scraper Setup"
   estimated_time: "45 minutes"
   prerequisites: ["Phase 0 complete", "Phase 1 complete"]
   outputs: ["myfxbook-mcp/ folder", "vera-snapshot.json updating daily"]
   ---
   ```

2. **Section headers** use `##` for major sections, `###` for subsections — never skip levels

3. **All commands** in fenced code blocks with language tag:
   ```bash
   node src/runner.js
   ```

4. **All file contents** shown in full with filename as code block header:
   ````markdown
   **`src/telegram.js`**
   ```js
   // full file content here
   ```
   ````

5. **Callout boxes** using blockquote + emoji prefix:
   - `> ⚠️ WARNING:` — something that will break the system if missed
   - `> 💡 TIP:` — optional but helpful
   - `> ✅ CHECKPOINT:` — verify this before moving on
   - `> 🔒 SECURITY:` — credential/secret handling

6. **Checkpoint at end of every phase** — exact command to run and exact expected output

## Phase Specifications

### Phase 0 — Prerequisites & Accounts (~30 min)

**Sections:**
- 0.1 IC Markets Account (live account required, not demo)
- 0.2 Myfxbook Account + Connect IC Markets account
- 0.3 Make Myfxbook account public + note the Account ID from URL
- 0.4 Instagram Business Account + Facebook Page linkage
- 0.5 Meta Developer App — create app, add Instagram Graph API product
- 0.6 GitHub Account + create two repos: `myfxbook-mcp` (private) and `my-fx-instagram` (public)
- 0.7 Telegram Bot — create via @BotFather, note token + get chat ID

**Checkpoint:** All 7 items ticked, account IDs noted in a reference table

---

### Phase 1 — Local Environment (~20 min)

**Sections:**
- 1.1 Node.js 20+ (nodejs.org)
- 1.2 Python 3.11+ (python.org — check "Add to PATH" on Windows installer)
- 1.3 Git (git-scm.com)
- 1.4 Google Chrome — must be the real browser (not Chromium/Edge) for Puppeteer stealth
- 1.5 Verify all installs

**Checkpoint:**
```
node --version    → v20.x.x or higher
python --version  → Python 3.11.x or higher
git --version     → git version 2.x.x
```

---

### Phase 2 — Myfxbook Scraper (~45 min)

Reader builds `myfxbook-mcp/` locally. This folder is **never pushed to public GitHub** — it stays on their Windows laptop only.

**Sections:**
- 2.1 Folder structure to create
- 2.2 `package.json` — exact content with all dependencies (puppeteer-extra, puppeteer-extra-plugin-stealth, dotenv, node-fetch)
- 2.3 `npm install`
- 2.4 `.env` file — template with every variable explained
- 2.5 `src/runner.js` — full file with inline comments on what to customise (account IDs)
- 2.6 `src/scraper.js` — full file, note: uses real Chrome path on Windows
- 2.7 `src/fetcher.js` — full file with Myfxbook REST API calls
- 2.8 `src/telegram.js` — full file
- 2.9 Local test: run manually, verify output
- 2.10 Push `vera-snapshot.json` to `my-fx-instagram` GitHub repo (the data bridge)
- 2.11 Windows Task Scheduler — step-by-step with screenshots described

**Checkpoint:** `node src/runner.js` produces a snapshot with real balance, open trades, and sends Telegram message

---

### Phase 3 — Instagram Pipeline (~60 min)

Reader builds `my-fx-instagram/` (their public GitHub repo). Every file shown in full with `# CUSTOMISE:` comments on lines they must change.

**Sections:**
- 3.1 Clone their empty GitHub repo locally
- 3.2 Folder structure
- 3.3 `instagram/requirements.txt`
- 3.4 `instagram/generate_status.py` — daily card (customise: brand name, colours)
- 3.5 `instagram/generate.py` — weekly/monthly/trust cards (customise: brand name, colours)
- 3.6 `instagram/generate_edu.py` — edu post renderers (customise: colours only)
- 3.7 `instagram/edu_content.py` — **fully replace** with their own content (guided template)
- 3.8 `instagram/captions.py` — replace CTA block with their links
- 3.9 `instagram/post.py` — Meta Graph API publisher (no changes needed)
- 3.10 `instagram/run.py` — pipeline entry point (no changes needed)
- 3.11 `instagram/assets/` — their own background image + QR code
- 3.12 `data/vera-snapshot.json` — placeholder to bootstrap before live data
- 3.13 `data/edu-counter.json` — `{"index": 0}`
- 3.14 `instagram/buffer/` — folder structure + `.gitkeep` files

**Checkpoint:** `python instagram/run.py` with `POST_TYPE=weekly` generates a PNG locally without errors

---

### Phase 4 — GitHub Actions Automation (~20 min)

**Sections:**
- 4.1 `.github/workflows/insta-post.yml` — exact file content
- 4.2 Getting `IG_USER_ID` — step-by-step via Meta Graph API Explorer (`/me/accounts` → find Instagram Business account)
- 4.3 Getting long-lived `META_ACCESS_TOKEN` — generate short-lived token → exchange for 60-day token
- 4.4 Adding secrets to GitHub repo (Settings → Secrets → Actions)
- 4.5 Cron schedule explanation — SGT/UTC conversion table, how to change posting times
- 4.6 `workflow_dispatch` manual trigger — how to run from GitHub Actions UI

**Checkpoint:** Manually trigger the workflow from GitHub → workflow runs green → image appears in `instagram/posts/`

---

### Phase 5 — Customise Your Brand (~30–60 min)

**Sections:**
- 5.1 Colour palette — one reference table of every constant to change across all generator files
- 5.2 Your name / brand name — grep-style: every string to replace
- 5.3 Hashtags — `TAGS` constant in `captions.py`
- 5.4 CTA block — `_CTA` constant: your Telegram, website, IC Markets referral link
- 5.5 QR code — generate free at qr-code-generator.com (target: your IB referral URL), save as `instagram/assets/qr-icmarkets.jpg` at 200×200px minimum
- 5.6 Daily card background — how to photograph/find a suitable notebook image, PIL crop requirements
- 5.7 Educational content — fill in the 12-slot template with your own:
  - 5 risk management rules (your methodology)
  - 4 pair spotlights (the pairs you trade)
  - 4 trade setup breakdowns (your actual entry method)

---

### Phase 6 — Go Live & Verify (~15 min)

Step-by-step end-to-end smoke test.

1. Run scraper → check `vera-snapshot.json` has real data
2. Commit + push snapshot to GitHub
3. Trigger `workflow_dispatch` → select `daily` post type
4. Watch Actions log live — expected log lines shown
5. Check Instagram feed on phone
6. Scan QR code on published image → confirm referral URL opens
7. Check caption contains all three CTA links

**Checkpoint table:**

| Check | Expected |
|---|---|
| Actions run | ✅ green, ~55 seconds |
| `[qr] stamped referral QR` in log | ✅ present |
| `published: <id>` in log | ✅ present |
| Post on Instagram | ✅ visible within 30 seconds |
| Caption links | ✅ all three tappable on mobile |

---

### Phase 7 — Maintenance & Troubleshooting (reference)

**Sections:**
- 7.1 Monthly: renew META_ACCESS_TOKEN (step-by-step, before 60-day expiry)
- 7.2 Cloudflare blocking the scraper — symptoms, fixes (disable VPN, check IP)
- 7.3 Common error codes:
  - Meta API 190 → token expired
  - Meta API 400 → image URL not yet on CDN (increase sleep)
  - Git push rejected → pull --rebase first
  - edu-counter wrong → manual fix procedure
- 7.4 Content buffer — how to add pre-made images to queue
- 7.5 Refreshing educational content after 6-week cycle
- 7.6 Quarterly: check IB referral link + QR code still valid

## Constraints

- **No Pandian-specific content** — guide uses placeholder names (`YourBrand`, `yourusername`, `your@email.com`)
- **No private repo links** — all code shown inline in the guide
- **Windows-first** — all commands are PowerShell/Windows; Mac equivalents noted where they differ
- **Security first** — `.env` and credential handling called out in every phase
- **Every code file shown in full** — no "add the following function" without showing the complete file context
