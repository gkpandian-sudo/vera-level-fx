# instagram/higgsfield/cinematic.py
"""Generate cinematic B-roll for the broker reel (3 clips, voiceover, no avatar)."""
import tempfile
from pathlib import Path

from higgsfield.client import generate_cinematic_clip, generate_audio_track
from higgsfield.composer import download_video, stitch_videos, add_audio_to_video
from higgsfield.scripts import ReelScript

_BROKER_PROMPTS: list[tuple[str, int]] = [
    ("Cinematic financial trading floor, Singapore skyline at golden hour, multiple monitors "
     "with live forex charts, dark professional studio, slow pan", 12),
    ("Extreme close-up IC Markets trading terminal, XAUUSD chart with green profit line, "
     "professional dark studio, photorealistic 4K, no people", 12),
    ("Myfxbook verified badge on screen, trade history rows visible, Singapore financial "
     "district background, cinematic grade, navy and gold palette", 12),
]


def generate_broker_reel(
    script: ReelScript,
    out_path: Path,
    voice_id: str = '',
) -> tuple[str, Path]:
    """Generate broker B-roll reel. Returns (hook_clip_url, out_path).

    hook_clip_url: CDN URL of first clip, for virality scoring.
    out_path: local assembled MP4 (stitched + voiceover).
    """
    clip_urls = []
    for i, (prompt, dur) in enumerate(_BROKER_PROMPTS):
        print(f'  [cinematic] broker clip {i + 1}/3 ({dur}s)...')
        url = generate_cinematic_clip(prompt=prompt, duration=dur)
        clip_urls.append(url)

    if not clip_urls:
        raise RuntimeError('[cinematic] no clips were generated — check Higgsfield API response')

    hook_url = clip_urls[0]

    with tempfile.TemporaryDirectory() as tmp:
        clip_paths = []
        for i, url in enumerate(clip_urls):
            dest = Path(tmp) / f'clip_{i}.mp4'
            download_video(url, dest)
            clip_paths.append(dest)

        silent_path = Path(tmp) / 'silent.mp4'
        stitch_videos(clip_paths, silent_path)

        print('  [cinematic] generating voiceover...')
        audio_url = generate_audio_track(script=script.full_text, voice_id=voice_id)
        add_audio_to_video(silent_path, audio_url, out_path)

    print(f'  [cinematic] assembled: {out_path}')
    return hook_url, out_path
