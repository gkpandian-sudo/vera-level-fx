# Vera Level FX — Pending Todo List

> Audit: 2026-07-20 | Status: awaiting human review

---

## Phase 1: CRITICAL — Token Renewal (Human Action Required)

- [ ] **Task 1:** Renew META_ACCESS_TOKEN in GitHub secrets
  - Visit: developers.facebook.com/tools/explorer
  - Generate new long-lived token (60 days)
  - Update secret: `META_ACCESS_TOKEN` in github.com/gkpandian-sudo/vera-level-fx → Settings → Secrets
  - Test: `gh workflow run insta-post.yml --field post_type=trust`
  - Deadline: **before 2026-08-12** (sooner = better, already past safe window)

---

## Phase 2: Infrastructure — Missing Secrets (Human input needed for values)

- [ ] **Task 2a:** Add `BRAND_TELEGRAM` → value: `t.me/pandiangk`
- [ ] **Task 2b:** Add `BRAND_WEBSITE` → value: `vera-level-forex.vercel.app`
- [ ] **Task 2c:** Add `BRAND_AUTHOR` → value: `Pandian`
- [ ] **Task 2d:** Add `BRAND_DOMAIN` → value: confirm with Pandian
- [ ] **Task 2e:** Add `BRAND_SIGNAL_CTA` → value: confirm with Pandian (what is this?)
- [ ] **Task 3:** Fix token-renewal-reminder.yml workflow
  - Option A: Add TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID secrets
  - Option B: Rewrite to use GitHub notification instead
  - Acceptance: workflow runs clean on next 1st of month

---

## Phase 3: Git Hygiene (Claude can do these once approved)

- [ ] **Task 4:** Update `.gitignore` — add entries for:
  - `instagram/Open-Poe-AI/`
  - `instagram/Vibe-Workflow/`
  - `instagram/posts/preview-*.png`
  - `instagram/previews/`
  - `instagram/reels/*.jpg`
  - `previews/`
- [ ] **Task 5:** Commit brand/campaign assets:
  - `docs/Vera_Level_FX_System_Documentation.docx`
  - `instagram/CampaingDynamicLinkQRCode.jpg`

---

## Checkpoint

- [ ] META_ACCESS_TOKEN renewed and test post succeeds
- [ ] All BRAND_* secrets set — captions show correct CTAs
- [ ] token-renewal-reminder.yml runs clean
- [ ] `git status` shows no untracked files (or only gitignored ones)
- [ ] `git status` after gitignore update: Open-Poe-AI and Vibe-Workflow no longer listed
