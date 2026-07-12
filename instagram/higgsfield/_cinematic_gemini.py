# instagram/higgsfield/_cinematic_gemini.py
"""Gemini broker reel: Imagen 3 + Ken Burns B-roll + Gemini/edge-tts voiceover."""
import tempfile
from pathlib import Path

from higgsfield.client import generate_audio_track, register_script_text
from higgsfield.composer import download_video, stitch_videos, add_audio_to_video
from higgsfield.scripts import ReelScript
from higgsfield._scenes import make_performance_clip, make_equity_clip, make_trust_clip


def generate_broker_reel(
    script: ReelScript,
    out_path: Path,
    voice_id: str = '',
) -> tuple[str, Path]:
    """Generate broker B-roll reel with animated data clips. Returns (str(out_path), out_path)."""
    register_script_text(script.full_text)

    clip_paths = [
        make_performance_clip(duration=12),
        make_equity_clip(duration=12),
        make_trust_clip(duration=12),
    ]

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
