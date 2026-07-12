# instagram/higgsfield/_cinematic_gemini.py
"""Gemini broker reel: Imagen 3 + Ken Burns B-roll + Gemini/edge-tts voiceover."""
import tempfile
from pathlib import Path

from higgsfield.client import generate_cinematic_clip, generate_audio_track, register_script_text
from higgsfield.composer import download_video, stitch_videos, add_audio_to_video
from higgsfield.scripts import ReelScript

_BROKER_PROMPTS: list[tuple[str, int]] = [
    ("Financial trading floor, Singapore skyline at golden hour, multiple monitors "
     "with live forex charts, dark professional studio", 12),
    ("IC Markets trading terminal close-up, XAUUSD chart with green profit line, "
     "professional dark studio, no people", 12),
    ("Myfxbook verified badge on screen, trade history visible, Singapore financial "
     "district background, navy and gold palette", 12),
]


def generate_broker_reel(
    script: ReelScript,
    out_path: Path,
    voice_id: str = '',
) -> tuple[str, Path]:
    """Generate broker B-roll reel with Ken Burns clips. Returns (str(out_path), out_path).

    Returns out_path as hook_url so composite_data_card() overlays the full reel,
    not just the first 12s hook clip.
    """
    register_script_text(script.full_text)

    clip_paths = []
    for i, (prompt, dur) in enumerate(_BROKER_PROMPTS):
        print(f'  [cinematic] broker clip {i + 1}/3 ({dur}s)…')
        clip_paths.append(generate_cinematic_clip(prompt=prompt, duration=dur, scene_index=i))

    if not clip_paths:
        raise RuntimeError('[cinematic] no clips were generated')

    with tempfile.TemporaryDirectory() as tmp:
        local_clips = []
        for i, path in enumerate(clip_paths):
            dest = Path(tmp) / f'clip_{i}.mp4'
            download_video(path, dest)
            local_clips.append(dest)

        silent_path = Path(tmp) / 'silent.mp4'
        stitch_videos(local_clips, silent_path)

        print('  [cinematic] generating voiceover…')
        audio_path = generate_audio_track(script=script.full_text, voice_id=voice_id)
        add_audio_to_video(silent_path, audio_path, out_path)

    print(f'  [cinematic] assembled: {out_path}')
    return str(out_path), out_path
