# AI Reel Format Fix — Corner Badge Removal + Instagram Compliance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the data card corner badge that overlays and disturbs the equity curve reel, then fix three format issues found by Fable 5's Instagram Reel spec audit.

**Architecture:** Two independent fixes. (1) `pipeline.py` — delete the `composite_data_card()` call and its import; the assembled reel at `out_path` is already complete, the thumbnail stays for the Instagram cover. (2) Three format hardening changes across `_client_gemini.py` and `composer.py` — add missing `yuv420p` pixel format to `_ken_burns_mp4`, clamp fps to 23–60, add aspect-ratio guard.

**Tech Stack:** Python 3.11, MoviePy, matplotlib, PIL/Pillow, ffmpeg (libx264), GitHub Actions.

---

## File Map

| File | Change |
|------|--------|
| `instagram/higgsfield/pipeline.py` | Remove `composite_data_card` import + call (lines 17, 195–199) |
| `instagram/higgsfield/_client_gemini.py` | Add `ffmpeg_params=['-pix_fmt', 'yuv420p']` to `_ken_burns_mp4` (line 206) |
| `instagram/higgsfield/composer.py` | Clamp `fps` to 23–60 in `composite_data_card`; add 9:16 aspect guard |

---

## Task 1: Remove the corner badge overlay from pipeline.py

**Files:**
- Modify: `instagram/higgsfield/pipeline.py`

The problem: `composite_data_card()` downloads the assembled reel, stamps a 32%-width trust card badge in the bottom-right corner, and overwrites `out_path`. This creates the visible overlay in the screenshot. The reel already has all data embedded in the three Ken Burns scenes — no overlay is needed. The thumbnail (`_make_data_card`) is still needed as the Instagram cover image.

- [ ] **Step 1: Remove the `composite_data_card` import**

In `instagram/higgsfield/pipeline.py`, change line 17 from:

```python
from higgsfield.composer  import composite_data_card
```

to — delete it entirely. The remaining composer imports on adjacent lines stay. After the edit the import block looks like:

```python
from higgsfield.avatar    import generate_reel
from higgsfield.cinematic import generate_broker_reel
from higgsfield.client    import predict_virality, dub_to_tamil as _dub
from higgsfield.scripts   import build_script, ReelScript
from higgsfield.hashtags  import get_hashtags, get_hashtags_tamil
```

- [ ] **Step 2: Remove the composite_data_card call**

In `instagram/higgsfield/pipeline.py`, find the data card section (around line 192). Replace:

```python
    # ── Data card composite ───────────────────────────────────────────────────
    _make_data_card(reel_type, snapshot, thumb_path)
    composite_data_card(
        video_url=hook_url,
        data_card_path=thumb_path,
        out_path=out_path,
    )
```

with:

```python
    # ── Thumbnail for Instagram cover image ───────────────────────────────────
    _make_data_card(reel_type, snapshot, thumb_path)
```

- [ ] **Step 3: Verify the commit block still references `out_path` correctly**

After the edit, the section should read:

```python
    # ── Thumbnail for Instagram cover image ───────────────────────────────────
    _make_data_card(reel_type, snapshot, thumb_path)

    # ── Commit EN reel to get public URL ─────────────────────────────────────
    en_video_url, thumb_gh_url = commit_and_push(out_path, thumb_path)
    print(f'  [pipeline] committed: {en_video_url}')
```

`out_path` was written by `_generate_with_virality_gate()` in the step above and is unchanged. This is correct.

- [ ] **Step 4: Commit**

```bash
git add instagram/higgsfield/pipeline.py
git commit -m "fix(pipeline): remove data card corner badge overlay from AI reel"
```

---

## Task 2: Fix yuv420p in _client_gemini.py (Fable 5 FAIL)

**Files:**
- Modify: `instagram/higgsfield/_client_gemini.py` (line 206)

The problem: `_ken_burns_mp4()` writes without `ffmpeg_params=['-pix_fmt', 'yuv420p']`. When MoviePy receives RGB24 frames from numpy arrays, libx264 defaults to yuv444p — a pixel format Instagram rejects or mangles on upload.

- [ ] **Step 1: Find the write_videofile call in `_ken_burns_mp4`**

Open `instagram/higgsfield/_client_gemini.py`. Locate the function `_ken_burns_mp4` (around line 183). Find this line inside it (around line 206):

```python
    clip.write_videofile(tmp.name, codec='libx264', audio=False, logger=None)
```

- [ ] **Step 2: Add the yuv420p flag**

Replace that line with:

```python
    clip.write_videofile(tmp.name, codec='libx264', audio=False, logger=None,
                         ffmpeg_params=['-pix_fmt', 'yuv420p'])
```

- [ ] **Step 3: Verify all other write_videofile calls already have yuv420p**

Run this check — expect zero output (no missing ones):

```bash
grep -n "write_videofile" instagram/higgsfield/_client_gemini.py instagram/higgsfield/_scenes.py instagram/higgsfield/composer.py | grep -v "yuv420p"
```

Expected: only the line you just fixed shows, or empty output after the fix.

- [ ] **Step 4: Commit**

```bash
git add instagram/higgsfield/_client_gemini.py
git commit -m "fix(client): add yuv420p to _ken_burns_mp4 write_videofile"
```

---

## Task 3: Harden fps clamping and aspect ratio guard in composer.py (Fable 5 RISK)

**Files:**
- Modify: `instagram/higgsfield/composer.py` (lines 93–130)

The problem: `composite_data_card()` and `stitch_videos()` pass through whatever fps the source video has without clamping. If a source is outside 23–60 fps, Instagram will reject the reel. The aspect ratio is also unvalidated — a non-9:16 source would silently produce a non-compliant output.

Note: since Task 1 removes the `composite_data_card()` call from `pipeline.py`, the aspect guard is defense-in-depth (the function still exists for future use).

- [ ] **Step 1: Add the fps clamp and aspect guard to `composite_data_card`**

In `instagram/higgsfield/composer.py`, find the `composite_data_card` function. After `video = VideoFileClip(str(raw_path))` and the `W, H = video.w, video.h` line, add the guard. The section currently looks like:

```python
        video = VideoFileClip(str(raw_path))
        try:
            W, H  = video.w, video.h
            is_portrait = H > W
```

Replace it with:

```python
        video = VideoFileClip(str(raw_path))
        try:
            W, H  = video.w, video.h
            if abs(W / H - 9 / 16) > 0.02:
                raise ValueError(f'Video is not 9:16 ({W}×{H}) — Instagram Reels require portrait 1080×1920')
            is_portrait = H > W
```

- [ ] **Step 2: Add fps clamping to the final write_videofile call in `composite_data_card`**

In the same function, find the `final.write_videofile(...)` call (around line 122). Change:

```python
            final.write_videofile(
                str(out_path),
                codec='libx264',
                audio_codec='aac',
                fps=video.fps,
                logger=None,
                ffmpeg_params=['-pix_fmt', 'yuv420p'],
            )
```

to:

```python
            safe_fps = max(23, min(int(video.fps or 24), 60))
            final.write_videofile(
                str(out_path),
                codec='libx264',
                audio_codec='aac',
                fps=safe_fps,
                logger=None,
                ffmpeg_params=['-pix_fmt', 'yuv420p'],
            )
```

- [ ] **Step 3: Commit**

```bash
git add instagram/higgsfield/composer.py
git commit -m "fix(composer): clamp fps to 23-60 and add 9:16 aspect guard"
```

---

## Task 4: Verify end-to-end — trigger a reel and inspect the output

**Files:** None — this is a verification step only.

- [ ] **Step 1: Trigger a trust reel manually**

```bash
gh workflow run ai-reel.yml --field reel_type=trust --field post_lang=en
```

- [ ] **Step 2: Watch the run**

```bash
gh run watch $(gh run list --workflow=ai-reel.yml -L 1 --json databaseId -q '.[0].databaseId') --exit-status
```

Expected: all steps ✓, run completes in under 10 minutes.

- [ ] **Step 3: Check the committed MP4 has no badge**

After the run, pull the latest commit and inspect:

```bash
git pull origin master
ls -lh instagram/reels/
```

Download the artifact from the Actions run or find the MP4 in `instagram/reels/`. Open it and confirm:
- No data card badge in the bottom-right corner
- Equity curve fills the full 1080×1920 portrait frame
- Voiceover plays cleanly over all three scenes

- [ ] **Step 4: Confirm yuv420p in the final MP4**

```bash
ffprobe -v error -show_streams -select_streams v:0 instagram/reels/$(ls -t instagram/reels/*.mp4 | head -1 | xargs basename) 2>&1 | grep pix_fmt
```

Expected output: `pix_fmt=yuv420p`

- [ ] **Step 5: Push all three commits if not already pushed**

```bash
git push origin master
```

---

## Summary of changes

| Issue | Severity | Fix | File |
|-------|----------|-----|------|
| Corner badge overlay ruins visual flow | High | Remove `composite_data_card()` call + import | `pipeline.py` |
| yuv420p missing in Ken Burns clip writer | High (Fable 5 FAIL) | Add `ffmpeg_params=['-pix_fmt', 'yuv420p']` | `_client_gemini.py:206` |
| fps not clamped — could be <23 or >60 | Medium (Fable 5 RISK) | `safe_fps = max(23, min(int(video.fps or 24), 60))` | `composer.py` |
| Aspect ratio not validated | Low (Fable 5 RISK) | Assert 9:16 before processing | `composer.py` |
