# instagram/higgsfield/cinematic.py
"""Generate a cinematic B-roll video for the broker reel (no avatar, no voice)."""
import os
import tempfile
from pathlib import Path
from higgsfield.client import generate_cinematic_clip, generate_audio_track
from higgsfield.composer import download_video, stitch_videos, add_audio_to_video
from higgsfield.scripts import ReelScript

_BROKER_VISUAL_PROMPTS = [
    "Cinematic forex trading desk, Singapore city skyline at dawn, gold candlestick charts, dark navy background, dramatic lighting",
    "Extreme close-up of XAUUSD live chart on multiple screens, green profit line rising, professional trading terminal, dark studio",
    "IC Markets platform interface, Myfxbook verified badge on screen, Singapore financial district backdrop, cinematic grade"
]


def generate_broker_cinematic_url(
    script: ReelScript,
    client: None = None,
    timeout_s: int = 300,
) -> str:
    """Generate a cinematic B-roll for the broker reel. Returns video URL (raw GitHub URL)."""
    reels_dir = Path(__file__).resolve().parent.parent / 'reels'
    reels_dir.mkdir(parents=True, exist_ok=True)
    temp_path = reels_dir / 'temp_broker_stitched.mp4'

    clip_urls = []
    for i, prompt in enumerate(_BROKER_VISUAL_PROMPTS):
        print(f'  [cinematic] broker clip {i+1}/{len(_BROKER_VISUAL_PROMPTS)}...')
        url = generate_cinematic_clip(prompt=prompt, duration=15)
        clip_urls.append(url)

    # Stitch the clips
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
        print('  [cinematic] generating broker voiceover audio...')
        voice_id = os.environ.get('HIGGSFIELD_VOICE_EN_ID', '')
        audio_url = generate_audio_track(script=audio_script, voice_id=voice_id)

        add_audio_to_video(silent_path, audio_url, temp_path)
        print(f'  [cinematic] assembled broker reel: {temp_path}')

    # Commit temp_path and return its public URL
    from higgsfield.pipeline import commit_and_push
    urls = commit_and_push(temp_path)
    return urls[0]
