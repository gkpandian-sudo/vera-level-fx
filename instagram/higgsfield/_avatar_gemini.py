# instagram/higgsfield/avatar.py
"""Generate Instagram Reels via free stack (Gemini image + Ken Burns + edge-tts).

Path A (default): 3 × 12s Ken Burns clips from Gemini images + voiceover.
Path B (upgrade): 3 × 15s Soul talking-head (requires HIGGSFIELD_SOUL_ID — not available
                  on free CPU-only stack; raises NotImplementedError if activated).
"""
import os
import tempfile
from pathlib import Path
from datetime import date

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


_MUAPI_PROMPTS = [
    # Performance card — numbers glowing, dark financial atmosphere
    'professional financial trading card, green glowing numbers, gold candlestick particles '
    'drifting upward, dark navy background, cinematic light rays, subtle camera push-in',
    # Equity curve card — chart drawing itself with motion
    'equity curve line animating from left to right with green glow trail, financial chart '
    'background, dark professional trading terminal, subtle grid pulse',
    # Trust metrics card — UI elements illuminating one by one
    'financial metrics dashboard, glowing circular progress indicator, metric boxes lighting up '
    'sequentially, dark navy professional UI, soft emerald particle shimmer',
]


def _generate_muapi_clips(script: ReelScript) -> list[str]:
    """Generate 3 AI-animated portrait clips via Muapi I2V. Returns local MP4 paths.

    Requires MUAPI_API_KEY env var. Each card PNG is uploaded to Muapi and animated
    with cinematic motion. Falls back silently if upload fails — caller handles fallback.
    """
    from higgsfield._scenes import make_performance_png, make_equity_png, make_trust_png
    from higgsfield._muapi_client import animate_card

    png_fns = [make_performance_png, make_equity_png, make_trust_png]
    labels  = ['performance', 'equity', 'trust']
    clips   = []

    for make_png, label, prompt in zip(png_fns, labels, _MUAPI_PROMPTS):
        print(f'  [avatar] Muapi I2V: {label} card…')
        png_path = Path(make_png())
        try:
            mp4_tmp = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            mp4_tmp.close()
            out_mp4 = Path(mp4_tmp.name)
            animate_card(png_path, out_mp4, prompt)
            clips.append(str(out_mp4))
        finally:
            png_path.unlink(missing_ok=True)

    return clips


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

    hook_url: str(out_path) — passed to predict_virality() for the hook score,
    then discarded by pipeline.py. out_path is the assembled reel written by _assemble().

    Path B (Soul) when HIGGSFIELD_SOUL_ID is set; Path A (cinematic) otherwise.
    """
    # Stash script text so dub_to_tamil() can translate it later
    register_script_text(script.full_text)

    muapi_key = os.environ.get('MUAPI_API_KEY', '')
    soul_id   = os.environ.get('HIGGSFIELD_SOUL_ID', '')
    if muapi_key:
        print('  [avatar] Path C — Muapi AI-animated cards')
        clip_paths = _generate_muapi_clips(script)
    elif soul_id:
        print('  [avatar] Path B — Soul talking head')
        clip_paths = _generate_soul_clips(script, soul_id)
    else:
        print('  [avatar] Path A — cinematic B-roll (Ken Burns)')
        clip_paths = _generate_cinematic_clips(script)

    if not clip_paths:
        raise RuntimeError('[avatar] no clips were generated')

    _assemble(clip_paths, script, out_path, voice_id)
    # Return str(out_path) as hook_url so virality scorer can evaluate the full reel
    return str(out_path), out_path


def dub_to_tamil(en_video_url: str, voice_id: str = '') -> str:
    """Dub an EN video to Tamil. Returns Tamil video public URL."""
    from higgsfield.client import dub_to_tamil as _dub
    print('  [avatar] dubbing to Tamil…')
    return _dub(en_video_url, voice_id=voice_id)
