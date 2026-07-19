# Vera Level FX — Pending Tasks Plan

**Audit date:** 2026-07-20 (Monday SGT)
**Branch:** master

---

## Summary

Three categories of pending work found: **critical security** (token expiry), **broken infrastructure** (missing secrets + failing workflow), and **git hygiene** (untracked files, .gitignore gaps).

---

## Findings

### 1. META_ACCESS_TOKEN — PAST RENEWAL THRESHOLD ⚠️

- Last set: **2026-06-13** — that is 37 days ago
- Expires after 60 days: **~2026-08-12**
- CLAUDE.md policy: renew every 45 days (threshold was **2026-07-28**)
- We are already past safe renewal date
- **Action required by human:** visit Meta for Developers → Graph API Explorer → generate new long-lived token → update GitHub secret

### 2. token-renewal-reminder.yml — Consistently Failing

- Failing on every push since at least 2026-07-18
- gh reports: "This run likely failed because of a workflow file issue"
- Root cause: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` secrets are **not set** in the repo
- When GitHub validates the YAML against available secrets and finds referenced secrets missing it logs the run as failed
- **Action required:** either add the Telegram bot secrets OR rework the workflow to not require them

### 3. Missing GitHub Secrets Used in Active Workflows

The following secrets are referenced in workflow env blocks but absent from repo secrets:

| Secret | Workflow | Impact |
|--------|----------|--------|
| `BRAND_TELEGRAM` | insta-post.yml, ai-reel.yml | Caption CTA missing or blank |
| `BRAND_WEBSITE` | insta-post.yml | Caption CTA blank |
| `BRAND_AUTHOR` | insta-post.yml | Author name blank in captions |
| `BRAND_SIGNAL_CTA` | insta-post.yml | Signal CTA blank |
| `BRAND_DOMAIN` | insta-post.yml | Domain blank in captions |
| `TELEGRAM_BOT_TOKEN` | token-renewal-reminder.yml | Reminder can never send |
| `TELEGRAM_CHAT_ID` | token-renewal-reminder.yml | Reminder can never send |

Already set (✓): `IG_USER_ID`, `META_ACCESS_TOKEN`, `MYFX_EMAIL`, `MYFX_PASSWORD`, `RECOVERY_START`, `BRAND_IB_URL`, `GEMINI_API_KEY`

### 4. Untracked Files — Git Hygiene

| Path | Type | Action |
|------|------|--------|
| `instagram/Open-Poe-AI/` | Foreign OSS project (no .git) | Add to .gitignore |
| `instagram/Vibe-Workflow/` | Nested git repo (has .git) | Add to .gitignore (nested git won't track) |
| `docs/Vera_Level_FX_System_Documentation.docx` | Brand doc | Commit |
| `instagram/CampaingDynamicLinkQRCode.jpg` | Campaign asset | Commit |
| `instagram/posts/preview-*.png` | Local preview outputs | Add to .gitignore |
| `instagram/previews/*.png` | Local preview outputs | Already a previews dir in .gitignore? No — add |
| `instagram/reels/2026-07-11-hf-*.jpg` | Reel thumbnail artifacts | Add to .gitignore |
| `previews/` (root) | Motion MP4 test files | Add to .gitignore |

---

## Architecture / Dependency Notes

```
META_ACCESS_TOKEN (secret)
    └── insta-post.yml + insta-reel.yml + ai-reel.yml (all posting workflows)
            └── Every auto-post to @veralevel.fx

BRAND_* secrets
    └── insta-post.yml → run.py → captions.py
            └── Caption CTAs (Telegram link, IB link, author, website)

TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID
    └── token-renewal-reminder.yml (monthly alert workflow)
            └── Sends Telegram message warning about token expiry

.gitignore
    └── Untracked files (Open-Poe-AI, Vibe-Workflow, previews, thumbnails)
            └── Repo cleanliness, prevents accidental large commits
```

---

## Task List

### Phase 1: Critical — Token (Human Action Required)

**Task 1: Renew META_ACCESS_TOKEN**
- Requires: browser, Meta developer portal
- Acceptance: new token set in GitHub repo secrets, test post succeeds
- Verification: `gh workflow run insta-post.yml --field post_type=trust`

---

### Phase 2: Infrastructure Fixes (Can Automate Most)

**Task 2: Add missing BRAND_* secrets**
- `BRAND_TELEGRAM=t.me/pandiangk`
- `BRAND_WEBSITE=vera-level-forex.vercel.app`
- `BRAND_AUTHOR=Pandian`
- `BRAND_DOMAIN=veralevelforex.com` (or the actual domain — needs confirmation)
- `BRAND_SIGNAL_CTA` — what is this? Needs confirmation from user

**Task 3: Fix token-renewal-reminder.yml**
- Option A: Add TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID secrets (requires Telegram bot)
- Option B: Remove telegram dependency, use email/GitHub notification instead
- Option C: Accept it fails silently (not recommended for token expiry alerts)

---

### Phase 3: Git Hygiene (Automatable)

**Task 4: Update .gitignore**
- Add: `instagram/Open-Poe-AI/`
- Add: `instagram/Vibe-Workflow/`
- Add: `instagram/posts/preview-*.png`
- Add: `instagram/previews/`
- Add: `instagram/reels/*.jpg` (thumbnails)
- Add: `previews/` (root motion MP4s)

**Task 5: Commit campaign assets**
- `docs/Vera_Level_FX_System_Documentation.docx`
- `instagram/CampaingDynamicLinkQRCode.jpg`

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| META_ACCESS_TOKEN expires Aug 12 | All posting stops | Renew immediately (Task 1) |
| BRAND_* secrets missing | Captions show blank CTAs | Add known values now (Task 2) |
| Nested Vibe-Workflow repo | git submodule confusion | gitignore, don't commit (Task 4) |
| Open-Poe-AI in wrong location | Unintentional large commit | gitignore immediately (Task 4) |

---

## Open Questions for Human

1. **BRAND_SIGNAL_CTA** — what is the value? (e.g., a Signal group link or CTA phrase?)
2. **BRAND_DOMAIN** — `vera-level-forex.vercel.app` or a custom domain?
3. **Telegram bot for reminders** — do you have TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID? Or prefer to remove that workflow dependency?
4. **Open-Poe-AI & Vibe-Workflow** — are these intentionally in the `instagram/` folder for reference? Or can they be moved to a different location outside the repo?
5. **META_ACCESS_TOKEN renewal** — ready to do this now?
