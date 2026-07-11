# instagram/higgsfield/_avatar_hf.py
"""Higgsfield avatar reel generation — paid fallback."""
import os
import tempfile
from pathlib import Path

from higgsfield.client import (
    get_soul_id, generate_soul_clip, generate_cinematic_clip,
    generate_audio_track, dub_to_tamil as _dub,
)
from higgsfield.scripts import ReelScript
from higgsfield.composer import download_video, stitch_videos, add_audio_to_video


def _soul_prompts(script: ReelScript) -> list[tuple[str, int]]:
    return [
        (f"Professional South Asian male trader, dark studio, direct eye contact. "
         f"Speaks confidently: '{script.hook}'", 5),
        (f"Same trader, same studio, calm and authoritative. "
         f"Continues: '{script.content[:200]}'", 15),
        (f"Same trader, same studio, holds phone toward camera showing Myfxbook. "
         f"Says: '{script.proof}' then '{script.cta}'", 15),
    ]


def _cinematic_prompts(_script: ReelScript) -> list[tuple[str, int]]:
    return [
        ("Cinematic forex trading desk, Singapore city skyline at dawn, gold candlestick "
         "charts, dark navy background, dramatic lighting", 12),
        ("Extreme close-up of XAUUSD live chart on multiple screens, green profit line "
         "rising, professional trading terminal, dark studio", 12),
        ("IC Markets platform interface, Myfxbook verified badge on screen, "
         "Singapore financial district backdrop, cinematic grade", 12),
    ]


def _generate_soul_clips(script: ReelScript, soul_id: str) -> list[str]:
    urls = []
    for i, (prompt, dur) in enumerate(_soul_prompts(script)):
        print(f'  [avatar] Soul clip {i + 1}/3 ({dur}s)...')
        urls.append(generate_soul_clip(prompt=prompt, soul_id=soul_id, duration=dur))
    return urls


def _generate_cinematic_clips(script: ReelScript) -> list[str]:
    urls = []
    for i, (prompt, dur) in enumerate(_cinematic_prompts(script)):
        print(f'  [avatar] cinematic clip {i + 1}/3 ({dur}s)...')
        urls.append(generate_cinematic_clip(prompt=prompt, duration=dur))
    return urls


def _assemble(clip_urls: list[str], script: ReelScript, out_path: Path, voice_id: str) -> Path:
    with tempfile.TemporaryDirectory() as tmp:
        clip_paths = []
        for i, url in enumerate(clip_urls):
            dest = Path(tmp) / f'clip_{i}.mp4'
            download_video(url, dest)
            clip_paths.append(dest)
        silent_path = Path(tmp) / 'silent.mp4'
        stitch_videos(clip_paths, silent_path)
        print('  [avatar] generating voiceover...')
        audio_url = generate_audio_track(script=script.full_text, voice_id=voice_id)
        add_audio_to_video(silent_path, audio_url, out_path)
    print(f'  [avatar] assembled: {out_path}')
    return out_path


def generate_reel(script: ReelScript, out_path: Path, voice_id: str = '') -> tuple[str, Path]:
    soul_id = os.environ.get('HIGGSFIELD_SOUL_ID', '')
    if soul_id:
        print('  [avatar] Path B — Soul talking head')
        clip_urls = _generate_soul_clips(script, soul_id)
    else:
        print('  [avatar] Path A — cinematic B-roll')
        clip_urls = _generate_cinematic_clips(script)
    if not clip_urls:
        raise RuntimeError('[avatar] no clips were generated — check Higgsfield API response')
    hook_url = clip_urls[0]
    _assemble(clip_urls, script, out_path, voice_id)
    return hook_url, out_path


def dub_to_tamil(en_video_url: str, voice_id: str = '') -> str:
    print('  [avatar] dubbing to Tamil...')
    return _dub(en_video_url, voice_id=voice_id)
