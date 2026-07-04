# Vera Level FX — System Update
**Date:** 2026-07-05

---

## Overview

This document captures the current state of the Vera Level FX automation system as of 5 July 2026, including recent feature additions, workflow architecture, file structure, and live validation status.

---

## What Was Built (2026-07-04 Session)

### Instagram Reels Pipeline

A full end-to-end Instagram Reels automation pipeline was designed, implemented, tested, and validated live in a single session.

**Motivation:** Static image posts were already running on autopilot. Reels offer 3–5× organic reach on the Instagram algorithm. The goal was to match the existing post quality — real Myfxbook data, IC Markets IB link, no guru framing — and package it as a short animated video (~10–30s) that publishes automatically alongside image posts.

---

## System Architecture

```
vera-level-fx/
├── data/
│   └── vera-snapshot.json          # Live Myfxbook data (auto-updated by fetch workflow)
│
├── instagram/
│   ├── requirements.txt            # matplotlib, numpy, requests, Pillow, moviepy
│   ├── run.py                      # Image post entry point
│   ├── run_reel.py                 # Reel entry point (NEW)
│   ├── post.py                     # Meta Graph API — publish() + publish_reel() (NEW)
│   ├── captions.py                 # All caption templates (shared by image + reel)
│   ├── generate.py                 # Matplotlib image composers
│   ├── generate_status.py          # Daily status card
│   ├── generate_edu.py             # Edu card composers
│   ├── composer.py                 # Shared matplotlib utilities
│   ├── edu_content.py              # 12-item rotating edu library
│   │
│   ├── reels/                      # NEW — Reels package
│   │   ├── __init__.py
│   │   ├── animator.py             # PIL frame-generation primitives
│   │   ├── audio.py                # CC0 track mapping + AudioFileClip builder
│   │   ├── render.py               # MoviePy concatenation + ffmpeg MP4 export
│   │   └── scenes.py               # 7 scene composers (one per post type)
│   │
│   ├── assets/
│   │   └── audio/                  # NEW — 6 CC0 MP3 tracks
│   │       ├── calm.mp3
│   │       ├── momentum.mp3
│   │       ├── pulse.mp3
│   │       ├── reflect.mp3
│   │       ├── rise.mp3
│   │       └── tension.mp3
│   │
│   └── tests/
│       ├── test_reels.py           # NEW — 18 tests, all passing
│       ├── test_composer.py
│       ├── test_edu.py
│       └── test_redesign.py
│
├── .github/workflows/
│   ├── fetch-snapshot.yml          # Mon–Fri 05:30 SGT — pull Myfxbook data
│   ├── insta-post.yml              # Mon–Fri 06:00 SGT — image post
│   └── insta-reel.yml              # Mon/Wed/Fri 07:00 SGT — Reel (NEW)
│
└── fetch_snapshot.py               # Myfxbook scraper
```

---

## GitHub Actions Workflows

| Workflow | Schedule (SGT) | Trigger | Purpose |
|---|---|---|---|
| Fetch Vera Snapshot | Mon–Fri 05:30 | Cron + manual | Pull live Myfxbook data → commit to `data/vera-snapshot.json` |
| Instagram Auto-Post | Mon–Fri 06:00 | Cron + manual | Generate static image card → publish to Instagram |
| Instagram Reel Auto-Post | Mon/Wed/Fri 07:00 | Cron + manual | Render animated Reel MP4 → publish to Instagram Reels |

**Dispatch inputs (all workflows):** `post_type` (weekly | monthly | daily | trust | edu | transparency | recovery-plan), `post_lang` (en | tamil)

**Required secrets:** `IG_USER_ID`, `META_ACCESS_TOKEN`, `GITHUB_TOKEN`, `GITHUB_REPOSITORY`, `RECOVERY_START`, `BRAND_IB_URL`, `MYFX_EMAIL`, `MYFX_PASSWORD`

---

## Reels Package — Technical Detail

### animator.py

Core PIL/NumPy frame-generation layer. All functions return `np.ndarray (H=1920, W=1080, C=3) uint8`.

| Function | Purpose |
|---|---|
| `ease_out(t, dur)` | Cubic ease-out: `1 - (1-x)³`, guard for `dur=0` |
| `bg_frame(t)` | Returns PIL RGB Image — navy radial gradient + gold particles |
| `draw_alpha_text(img, pos, text, font, color, alpha)` | Alpha composite text onto PIL Image; `alpha` is float 0.0–1.0 |
| `load_font(size)` | Tries project fonts → Ubuntu system fonts → DejaVuSans → PIL bitmap |
| `countup_frame(...)` | Animated number count-up |
| `cascade_text_frame(...)` | Staggered line reveal |
| `fade_in_frame(...)` | Simple opacity fade-in |
| `typewriter_frame(...)` | Character-by-character typewriter |
| `logo_fade_frame(...)` | Brand name fade |
| `cta_fade_frame(...)` | CTA two-line fade |

**Design notes:**
- Background gradient cached in `_BG_CACHE` (computed once per process)
- Gold particles seeded with `np.random.default_rng(seed)` — reproducible per frame
- No ImageMagick dependency — all text via PIL/ImageDraw

### audio.py

| Track | Post types |
|---|---|
| `pulse.mp3` | daily |
| `momentum.mp3` | weekly, trust |
| `reflect.mp3` | monthly |
| `tension.mp3` | transparency |
| `rise.mp3` | recovery-plan |
| `calm.mp3` | edu |

`build_audio_clip()` lazy-imports MoviePy, applies 0.15 volume, 0.5s fade-in, 1.0s fade-out. `source.close()` is intentionally absent — MoviePy 1.0.3 lazy-evaluates audio frames and requires the ffmpeg reader to stay open until `write_videofile()` completes.

### render.py

`render(clips, audio_path, out_path, fps=30)` — concatenates clips via `concatenate_videoclips(method='compose')`, attaches audio, writes MP4 with `libx264` / `aac`, `preset=fast`, `threads=4`.

No system ffmpeg required — `moviepy==1.0.3` bundles `imageio_ffmpeg`.

### scenes.py

7 scene composers, each returning a list of 4 `VideoClip` objects:

| Post type | Duration | Audio | CTA |
|---|---|---|---|
| daily | ~10s | pulse.mp3 | Myfxbook #12044019 |
| weekly | ~12s | momentum.mp3 | Myfxbook #12044019 |
| trust | ~12s | momentum.mp3 | Myfxbook #12044019 |
| monthly | ~28s | reflect.mp3 | IC Markets IB link |
| transparency | ~25s | tension.mp3 | Myfxbook #12044019 |
| recovery-plan | ~29.4s | rise.mp3 | IC Markets IB link |
| edu | ~22s | calm.mp3 | IC Markets IB link |

Constants: `_VERIFY_CTA = 'Myfxbook #12044019'`, `_IB_CTA = 'icmarkets.com/?camp=91936'`

### post.py — publish_reel()

```python
publish_reel(video_url: str, caption: str) -> str
```

- Creates container with `media_type='REELS'`
- Polls status every 10s for up to 5 minutes (30 × 10s)
- `for…else` raises `TimeoutError` on exhaustion
- Returns published post ID

### run_reel.py

Entry point mirroring `run.py`. Reads `POST_TYPE` (default `weekly`), `POST_LANG` (default `en`), `RECOVERY_START`. Dispatches to all 7 scene builders. Waits 60s for CDN before `publish_reel()`. Raises `ValueError` on unknown `POST_TYPE`. Raises `RuntimeError` on git push failure. Shares `read_counter` / `write_and_commit_counter` with `run.py` for edu rotation.

---

## Live Validation Log (2026-07-04)

| Time (UTC) | Event | Result |
|---|---|---|
| 23:21 | Instagram Reel Auto-Post — `trust` (first live test) | ✅ Published in 2m25s |
| 23:36 | Fetch Vera Snapshot — manual trigger | ✅ Completed in ~10s |
| 23:36 | Instagram Reel Auto-Post — `daily` (with fresh data) | ✅ Published in 2m28s |

Both Reels confirmed posted to @veralevel.fx. Full pipeline end-to-end: data fetch → render → CDN push → Meta Reels API → Instagram.

---

## Known Issues / Bugs Fixed

| Bug | Fix |
|---|---|
| `ease_out` ZeroDivisionError when `dur=0` | Guard: `if dur <= 0: return 1.0` |
| `source.close()` silently breaking audio | Removed — MoviePy lazy eval requires reader alive |
| Private animator helpers (`_ease_out` etc.) inaccessible from scenes.py | Renamed to public API (no underscores) |
| Loop variable `t` shadowing time parameter in daily scene | Renamed `for t in open_trades` → `for trade in open_trades` |
| Weekly hero `+-96.8%` format string | Captured format string before closure |
| `bg_frame()` wrongly wrapped in `Image.fromarray()` | Returns PIL Image directly — no wrapping needed |
| `draw` object stale after `draw_alpha_text` reassigns `img` | `draw = ImageDraw.Draw(img)` refreshed after each call |
| Edu body text character-split (mid-word cuts) | Replaced manual slice with `textwrap.wrap(body, width=42)` |
| Dead `size` param in `render()` | Removed — MoviePy derives dimensions from clips |
| Silent git push failure in `run_reel.py` | Raises `RuntimeError` on non-zero returncode |
| Unknown `POST_TYPE` silently falling through to trust | Explicit `elif` + `else: raise ValueError(...)` |
| POST_TYPE/POST_LANG null on scheduled workflow runs | Added `|| 'weekly'` and `|| 'en'` YAML fallbacks |
| Artifact upload skipped on failure | `if: always()` on upload-artifact step |

---

## Account Snapshot (as of 2026-07-02 fetch)

| Metric | Value |
|---|---|
| Balance | $972.64 |
| Total Gain | -96.82% |
| Fetched At | 2026-07-02 22:33 UTC |

Note: snapshot was stale as of 2026-07-04 session — `Fetch Vera Snapshot` workflow was manually triggered to refresh before the daily Reel.

---

## Dependencies

```
matplotlib==3.8.4
numpy==1.26.4
requests==2.31.0
Pillow==10.3.0
moviepy==1.0.3
```

Python version on CI: 3.11 (ubuntu-latest)

---

## Next Steps / Pending

- Monitor scheduled Reel runs (Mon/Wed/Fri 07:00 SGT) to confirm cron fires correctly
- Confirm Myfxbook snapshot data refreshes populate `winRate` and `trades` fields (currently `null` in last fetch — may be a scraper field mapping issue)
- Consider adding weekly Reel to the Friday slot instead of trust post once recovery P&L improves
