# instagram/higgsfield/avatar.py
"""Generate Instagram Reels via free stack (Gemini image + Ken Burns + edge-tts).

Path A (default): 3 × 12s Ken Burns clips from Gemini images + voiceover.
Path B (upgrade): 3 × 15s Soul talking-head (requires HIGGSFIELD_SOUL_ID — not available
                  on free CPU-only stack; raises NotImplementedError if activated).
"""
import os
import tempfile
from pathlib import Path

from higgsfield.client import (
    get_soul_id, generate_soul_clip,
    generate_audio_track, register_script_text,
)
from higgsfield.scripts import ReelScript
from higgsfield.composer import download_video, stitch_videos, add_audio_to_video
from higgsfield._scenes import make_performance_clip, make_equity_clip, make_trust_clip


# ── Prompt builders ──────────────────────────────────────────────────────────

def _soul_prompts(script: ReelScript) -> list[tuple[str, int]]:
    """3 Soul Cinema prompts [(prompt, duration_s)] summing to ~35s."""
    return [
        (f"Professional South Asian male trader, dark studio, direct eye contact. "
         f"Speaks confidently: '{script.hook}'", 5),
        (f"Same trader, same studio, calm and authoritative. "
         f"Continues: '{script.content[:200]}'", 15),
        (f"Same trader, same studio, holds phone toward camera showing Myfxbook. "
         f"Says: '{script.proof}' then '{script.cta}'", 15),
    ]


def _cinematic_prompts(_script: ReelScript) -> list[tuple[str, int]]:
    """3 cinematic B-roll prompts [(prompt, duration_s)] summing to ~36s."""
    return [
        ("Forex trading desk, Singapore city skyline at dawn, gold candlestick "
         "charts, dark navy background, dramatic lighting", 12),
        ("Extreme close-up of XAUUSD live chart on multiple screens, green profit line "
         "rising, professional trading terminal, dark studio", 12),
        ("IC Markets platform interface, Myfxbook verified badge on screen, "
         "Singapore financial district backdrop, cinematic grade", 12),
    ]


# ── Clip generators ──────────────────────────────────────────────────────────

def _generate_soul_clips(script: ReelScript, soul_id: str) -> list[str]:
    """Generate 3 Soul Cinema clips. Returns list of local/CDN paths."""
    paths = []
    for i, (prompt, dur) in enumerate(_soul_prompts(script)):
        print(f'  [avatar] Soul clip {i + 1}/3 ({dur}s)…')
        paths.append(generate_soul_clip(prompt=prompt, soul_id=soul_id, duration=dur))
    return paths


def _generate_cinematic_clips(script: ReelScript) -> list[str]:
    """Generate 3 animated portrait clips from live account data. Returns local MP4 paths."""
    return [
        make_performance_clip(duration=12),   # gain counter + monthly bars
        make_equity_clip(duration=12),        # equity curve drawing itself
        make_trust_clip(duration=12),         # win rate circle + metrics
    ]


# ── Assembly ─────────────────────────────────────────────────────────────────

def _assemble(clip_paths: list[str], script: ReelScript, out_path: Path, voice_id: str) -> Path:
    """Copy/download clips, stitch, add voiceover. Returns out_path."""
    with tempfile.TemporaryDirectory() as tmp:
        local_clips = []
        for i, path in enumerate(clip_paths):
            dest = Path(tmp) / f'clip_{i}.mp4'
            download_video(path, dest)       # handles both local paths and http URLs
            local_clips.append(dest)

        silent_path = Path(tmp) / 'silent.mp4'
        stitch_videos(local_clips, silent_path)

        print('  [avatar] generating voiceover…')
        audio_path = generate_audio_track(script=script.full_text, voice_id=voice_id)
        add_audio_to_video(silent_path, audio_path, out_path)

    print(f'  [avatar] assembled: {out_path}')
    return out_path


# ── Public API ───────────────────────────────────────────────────────────────

def generate_reel(
    script: ReelScript,
    out_path: Path,
    voice_id: str = '',
) -> tuple[str, Path]:
    """Generate full reel. Returns (hook_url, out_path).

    hook_url: local path of out_path — used by pipeline.py for both virality scoring
    (script-based, not video-based) and composite_data_card() overlay. Returning
    out_path fixes an original quirk where only the 12s hook clip got the data card;
    now the full assembled reel gets the overlay.

    Path B (Soul) when HIGGSFIELD_SOUL_ID is set; Path A (cinematic) otherwise.
    """
    # Stash script text so dub_to_tamil() can translate it later
    register_script_text(script.full_text)

    soul_id = os.environ.get('HIGGSFIELD_SOUL_ID', '')
    if soul_id:
        print('  [avatar] Path B — Soul talking head')
        clip_paths = _generate_soul_clips(script, soul_id)
    else:
        print('  [avatar] Path A — cinematic B-roll (Ken Burns)')
        clip_paths = _generate_cinematic_clips(script)

    if not clip_paths:
        raise RuntimeError('[avatar] no clips were generated')

    _assemble(clip_paths, script, out_path, voice_id)
    # Return str(out_path) as hook_url so composite_data_card overlays the full reel
    return str(out_path), out_path


def dub_to_tamil(en_video_url: str, voice_id: str = '') -> str:
    """Dub an EN video to Tamil. Returns Tamil video public URL."""
    from higgsfield.client import dub_to_tamil as _dub
    print('  [avatar] dubbing to Tamil…')
    return _dub(en_video_url, voice_id=voice_id)
