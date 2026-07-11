# instagram/higgsfield/avatar.py
"""Path B: Soul Cinema talking-head reel (3 clips × 15s → 45s).
   Path A: Cinematic B-roll fallback when HIGGSFIELD_SOUL_ID is absent."""
import os
import tempfile
from pathlib import Path
from higgsfield.client import (
    get_soul_id, generate_soul_clip, generate_cinematic_clip,
    generate_audio_track, dub_to_tamil,
)
from higgsfield.scripts import ReelScript
from higgsfield.composer import download_video, stitch_videos, add_audio_to_video

# Segment prompts for Soul Cinema — each ≤15s
def _soul_prompts(script: ReelScript) -> list[tuple[str, int]]:
    """Return [(prompt, duration_s)] for 3 clips summing to ~45s."""
    return [
        # Clip 1: Hook — punchy, lean forward, 5s
        (f"Professional South Asian male trader, dark studio, direct eye contact. "
         f"Speaks confidently: '{script.hook}'", 5),
        # Clip 2: Content part 1 — calm delivery, 15s
        (f"Same trader, same studio, calm and authoritative. "
         f"Continues: '{script.content[:200]}'", 15),
        # Clip 3: Proof + CTA — holds up phone, direct look, 15s
        (f"Same trader, same studio, holds phone toward camera showing Myfxbook. "
         f"Says: '{script.proof}' then '{script.cta}'", 15),
    ]

def _cinematic_prompts(script: ReelScript) -> list[tuple[str, int]]:
    """Path A: 3 cinematic B-roll clips summing to ~40s."""
    return [
        ("Cinematic forex trading desk, Singapore city skyline at dawn, gold candlestick charts, "
         "dark navy background, dramatic lighting", 12),
        ("Extreme close-up of XAUUSD live chart on multiple screens, green profit line rising, "
         "professional trading terminal, dark studio", 12),
        ("IC Markets platform interface, Myfxbook verified badge on screen, "
         "Singapore financial district backdrop, cinematic grade", 12),
    ]


def generate_avatar_reel_url(
    script: ReelScript,
    client: None = None,
    avatar_id: str = '',
    voice_id: str = '',
    timeout_s: int = 300,
) -> str:
    """Generate EN avatar reel (stitching 3 clips). Returns public URL (raw GitHub URL)."""
    try:
        soul_id = get_soul_id()
        use_soul = True
    except EnvironmentError:
        print('  [avatar] HIGGSFIELD_SOUL_ID absent — using Path A cinematic fallback')
        use_soul = False

    reels_dir = Path(__file__).resolve().parent.parent / 'reels'
    reels_dir.mkdir(parents=True, exist_ok=True)
    temp_path = reels_dir / 'temp_stitched.mp4'

    if use_soul:
        prompts = _soul_prompts(script)
        clip_urls = []
        for i, (prompt, dur) in enumerate(prompts):
            print(f'  [avatar] Soul clip {i+1}/{len(prompts)} ({dur}s)...')
            url = generate_soul_clip(prompt=prompt, soul_id=soul_id, duration=dur)
            clip_urls.append(url)
    else:
        prompts = _cinematic_prompts(script)
        clip_urls = []
        for i, (prompt, dur) in enumerate(prompts):
            print(f'  [avatar] cinematic clip {i+1}/{len(prompts)} ({dur}s)...')
            url = generate_cinematic_clip(prompt=prompt, duration=dur)
            clip_urls.append(url)

    # Assemble clips (stitch and add audio)
    _assemble(clip_urls, script, temp_path, voice_id)

    # Commit temp_path and return its public URL
    from higgsfield.pipeline import commit_and_push
    urls = commit_and_push(temp_path)
    return urls[0]


def _assemble(
    clip_urls: list[str],
    script: ReelScript,
    out_path: Path,
    voice_id: str,
) -> Path:
    """Download clips, stitch, add voiceover audio."""
    with tempfile.TemporaryDirectory() as tmp:
        clip_paths = []
        for i, url in enumerate(clip_urls):
            dest = Path(tmp) / f'clip_{i}.mp4'
            download_video(url, dest)
            clip_paths.append(dest)

        silent_path = Path(tmp) / 'silent.mp4'
        stitch_videos(clip_paths, silent_path)

        # Generate voiceover from full script text
        audio_script = f"{script.hook} {script.content} {script.proof} {script.cta}"
        print('  [avatar] generating voiceover audio...')
        audio_url = generate_audio_track(script=audio_script, voice_id=voice_id)

        add_audio_to_video(silent_path, audio_url, out_path)
        print(f'  [avatar] assembled: {out_path}')

    return out_path


def generate_tamil_dub_url(
    en_video_url: str,
    client: None = None,
    voice_id: str = '',
    timeout_s: int = 180,
) -> str:
    """Dub EN video URL to Tamil. Returns dubbed Higgsfield video URL."""
    voice_id = voice_id or os.environ.get('HIGGSFIELD_VOICE_TAMIL_ID', '')
    return dub_to_tamil(en_video_url, voice_id=voice_id)
