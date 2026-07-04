# Instagram Reels Automation — Design Spec
**Date:** 2026-07-04  
**Status:** Approved  
**Stack:** Python + MoviePy + matplotlib + ffmpeg  

---

## Goal

Extend the existing Vera Level FX Instagram automation pipeline to generate and publish fully automated, animated Reels (MP4 video) to @veralevel.fx — covering all existing post types, vertical 9:16 format, with background music baked in. No manual involvement required.

---

## Architecture

New module `instagram/reels/` added alongside existing code. The static post pipeline (`run.py`, `generate.py`, etc.) is untouched.

```
vera-level-fx/
├── instagram/
│   ├── reels/
│   │   ├── __init__.py
│   │   ├── animator.py       # animation primitives
│   │   ├── scenes.py         # per-post-type scene composers
│   │   ├── audio.py          # music selection + mixing
│   │   └── render.py         # MoviePy composition → MP4
│   ├── assets/
│   │   └── audio/
│   │       ├── pulse.mp3         # daily
│   │       ├── momentum.mp3      # weekly, trust
│   │       ├── reflect.mp3       # monthly
│   │       ├── tension.mp3       # transparency
│   │       ├── rise.mp3          # recovery-plan
│   │       └── calm.mp3          # edu
│   ├── run_reel.py           # entry point (mirrors run.py)
│   └── post.py               # extended with publish_reel()
└── .github/workflows/
    └── insta-reel.yml        # new workflow
```

**Data flow:**
```
vera-snapshot.json → run_reel.py → scenes.py → animator.py clips
→ render.py (MoviePy + ffmpeg) → MP4 → GitHub raw URL
→ Meta Reels API → @veralevel.fx
```

---

## Canvas & Format

| Property | Value |
|---|---|
| Resolution | 1080 × 1920 px (9:16 vertical) |
| Frame rate | 30 FPS |
| Codec | H.264 (libx264) |
| Audio codec | AAC |
| Colour space | sRGB |
| Estimated file size | 10–40 MB per Reel |

---

## Brand Palette (unchanged)

```python
NAVY   = '#010E1F'   # background
GOLD   = '#F0C040'   # brand accent
WHITE  = '#FFFFFF'
CREAM  = '#F0EEE8'
MUTED  = '#B8CFEA'
GREEN  = '#00E096'   # positive / win
RED    = '#FF6B6B'   # negative / loss
AMBER  = '#FFA040'   # warning / neutral
```

---

## Scene Structure

Every Reel is composed of 4 sequential scenes:

```
INTRO (1.5s) → HERO (3–6s) → DATA (3–8s) → CTA (2s)
```

| Scene | Content | Animation |
|---|---|---|
| **Intro** | Logo + brand name + gold sweep bar | Logo slides in from top, gold bar sweeps L→R, brand name fades |
| **Hero** | Primary metric (the number that matters most) | Ease-out countup, bold centered, large font |
| **Data** | Supporting stats / text / chart | Cascade up with 0.15s stagger between elements |
| **CTA** | IC Markets or Myfxbook URL | Fade in, gold text |

**Background:** Radial gradient (deep navy core → near-black edges) + 8 slow-drifting gold particles at 8% opacity for depth.

---

## Post Type Specs

### daily (10s)
- **Hero:** Balance (`$973`) counts up + daily P&L % slams in (green/red)
- **Data:** Open positions reveal line by line (symbol · action · P&L)
- **CTA:** Myfxbook verification

### weekly (12s)
- **Hero:** Total gain % counts up (red when negative, green when positive)
- **Data:** Win rate · Profit factor · Pips · Trades cascade in
- **CTA:** Myfxbook verification

### monthly (28s)
- **Hero:** "Monthly P&L" title fades in, current month name
- **Data:** Each monthly bar draws left→right in sequence (green/red), value label appears after bar completes
- **CTA:** IC Markets IB link

### transparency (25s)
- **Hero:** `-96.8%` smashes in full-screen red, holds 2s
- **Data:** Scene 1 — "WHAT HAPPENED" text cascades. Scene 2 — "WHAT CHANGED" cascades
- **CTA:** Myfxbook verification

### recovery-plan (28s)
- **Hero:** "Recovery Plan" + `$1,000/month · 50% target` fades in
- **Data:** Table rows appear one by one (month → end balance counts up per row)
- **CTA:** `$31,172` projected slams in gold, IC Markets IB link

### trust (12s)
- **Hero:** `71%` win rate counts up from 0 in massive font
- **Data:** Trades · Pips · Profit factor cascade
- **CTA:** Myfxbook verification

### edu (22s)
- **Hero:** Rule title types onto screen character by character
- **Data:** Body text fades in paragraph by paragraph, example animates (number → calculation → result)
- **CTA:** IC Markets IB link

---

## Animation Primitives (`animator.py`)

All functions return MoviePy `VideoClip` or `ImageClip` compositable objects.

```python
countup(start, end, duration, fmt, color, fontsize)
# Eased number animation: fast start, slow finish (ease-out cubic)

draw_line(points, duration, color, linewidth)
# Equity curve / chart line drawing itself left to right

cascade_text(lines, duration, stagger=0.15, color, fontsize)
# Lines slide up 20px + fade in, 0.15s stagger between each

fade_in(text, duration, color, fontsize)
# Simple opacity 0→1 over duration

typewriter(text, duration, color, fontsize)
# Characters appear one by one at even intervals

slide_bar(width, duration, color)
# Horizontal bar sweeps from x=0 to x=width

particle_drift(duration, n=8, opacity=0.08)
# Slow gold particles drifting upward, looped seamlessly

radial_bg(duration)
# Animated deep navy radial gradient background clip
```

---

## Audio (`audio.py`)

6 CC0 royalty-free tracks stored in `instagram/assets/audio/`. Each track is ≥30s and loop-able.

| Track file | Used for | Feel |
|---|---|---|
| `pulse.mp3` | daily | Upbeat, energetic |
| `momentum.mp3` | weekly, trust | Driving, confident |
| `reflect.mp3` | monthly | Measured, thoughtful |
| `tension.mp3` | transparency | Dark, atmospheric |
| `rise.mp3` | recovery-plan | Hopeful, building |
| `calm.mp3` | edu | Clean, focused |

**Mixing:**
- Volume: 0.15 (background, not intrusive)
- Fade in: 0.5s
- Fade out: 1.0s
- Trimmed to match video duration

---

## Render Pipeline (`render.py`)

```python
def render(clips, audio_path, out_path, fps=30, size=(1080, 1920)):
    video = CompositeVideoClip(clips, size=size)
    audio = (AudioFileClip(audio_path)
             .volumex(0.15)
             .audio_fadein(0.5)
             .audio_fadeout(1.0)
             .set_duration(video.duration))
    final = video.set_audio(audio)
    final.write_videofile(
        out_path, fps=fps,
        codec='libx264', audio_codec='aac',
        preset='fast', threads=4
    )
```

---

## Meta API — Reel Publishing (`post.py`)

New `publish_reel(video_url, caption)` function alongside existing `publish()`.

Key differences from image publishing:
- `media_type=REELS` in container creation request
- Poll timeout increased to **5 minutes** (30 × 10s intervals) — video encoding on Meta's end takes longer
- Same two-step pattern: create container → publish

```python
def publish_reel(video_url: str, caption: str) -> str:
    # Step 1 — create Reel media container
    data = _check(requests.post(f'{GRAPH}/{IG_ID}/media', params={
        'media_type':   'REELS',
        'video_url':    video_url,
        'caption':      caption,
        'access_token': TOKEN,
    }))
    container_id = data['id']

    # Poll up to 5 minutes
    for _ in range(30):
        time.sleep(10)
        status = _check(requests.get(f'{GRAPH}/{container_id}',
            params={'fields': 'status_code', 'access_token': TOKEN}))
        if status.get('status_code') == 'FINISHED':
            break

    # Step 2 — publish
    result = _check(requests.post(f'{GRAPH}/{IG_ID}/media_publish', params={
        'creation_id':  container_id,
        'access_token': TOKEN,
    }))
    return result['id']
```

---

## Entry Point (`run_reel.py`)

Mirrors `run.py` structure exactly:
- Reads `POST_TYPE`, `POST_LANG`, `RECOVERY_START` env vars
- Calls the matching `make_*_reel()` scene composer
- Renders via `render.py`
- Commits MP4 to `instagram/reels/` directory
- Returns raw GitHub URL
- Waits 60s for CDN (longer than images)
- Calls `publish_reel(url, caption)`

---

## GitHub Actions Workflow (`insta-reel.yml`)

```yaml
on:
  schedule:
    - cron: '0 23 * * 0,2,4'   # Mon/Wed/Fri 07:00 SGT
  workflow_dispatch:
    inputs:
      post_type:
        description: 'weekly|monthly|daily|trust|edu|transparency|recovery-plan'
        default: 'weekly'
      post_lang:
        description: 'en|tamil'
        default: 'en'
```

**Additional dependency install step:**
```yaml
- name: Install dependencies
  run: pip install -r instagram/requirements.txt
```

`moviepy==1.0.3` added to `instagram/requirements.txt`. ffmpeg pre-installed on `ubuntu-latest` runner — no extra install step needed.

---

## Audio Assets

4–6 CC0 tracks sourced from:
- **freemusicarchive.org** (CC0 or CC BY licences)
- **pixabay.com/music** (free for commercial use)
- **uppbeat.io** (free tier, attribution not required for CC0)

Tracks downloaded, normalised to -14 LUFS, trimmed to 35s, committed to `instagram/assets/audio/`. No runtime download — fully offline.

---

## File Storage

Generated MP4s committed to `instagram/reels/` with naming pattern:
`YYYY-MM-DD-{post_type}.mp4`

Same pattern as existing PNGs in `instagram/posts/`. GitHub raw URL used for Meta API — file sizes (10–40MB) are within GitHub's per-file limit (100MB).

---

## Schedule (combined static + Reels)

| Day | Static post (existing) | Reel (new) |
|---|---|---|
| Monday | weekly | weekly |
| Tuesday | edu | — |
| Wednesday | daily | daily |
| Thursday | edu | — |
| Friday | daily | trust |
| 1st of month | monthly | monthly |

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `moviepy` | 1.0.3 | Video composition + audio mixing |
| `ffmpeg` | system | Video encoding (pre-installed on runner) |
| All existing deps | unchanged | matplotlib, PIL, requests, numpy |
