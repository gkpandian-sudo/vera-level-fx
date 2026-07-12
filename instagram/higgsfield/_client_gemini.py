# instagram/higgsfield/client.py
"""Zero-cost drop-in for Higgsfield API. No paid API calls anywhere.

Cinematic B-roll  → PIL branded navy card + moviepy Ken Burns (no API)
Voiceover (EN)    → edge-tts en-SG-WayneNeural (Microsoft, no key, no cost)
Voiceover (Tamil) → edge-tts ta-IN-ValluvarNeural (same)
Tamil dub         → gemini-2.5-flash translate (free tier) + edge-tts + git commit
Virality gate     → gemini-2.5-flash text rubric (free tier, scores script not video)
Soul avatar       → NotImplementedError (no free CPU-viable option)

gemini-2.5-flash text model is on Google's free tier (rate-limited, never billed).
Imagen 3 and Gemini TTS are paid models and have been intentionally removed.

Public API is identical to the original Higgsfield client: same function names,
same signatures. Only the implementations change.
"""
import asyncio
import hashlib
import io
import json
import os
import subprocess
import tempfile
import time
import wave
from pathlib import Path

import numpy as np
import requests
from google import genai
from google.genai import types
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent

# Reel output dimensions (Instagram portrait)
_W, _H = 1080, 1920

# ── Module-level caches and state ─────────────────────────────────────────────
_IMAGE_CACHE: dict[str, bytes] = {}   # md5(prompt+ratio) → PNG/JPEG bytes
_CLIP_CACHE:  dict[str, str]   = {}   # md5(prompt+ratio)+duration → local mp4 path
_CURRENT_SCRIPT: str = ''             # stashed by avatar/cinematic for dub_to_tamil


# ── SDK bootstrap ─────────────────────────────────────────────────────────────
def _gemini() -> genai.Client:
    key = os.environ.get('GEMINI_API_KEY', '')
    if not key:
        raise EnvironmentError('GEMINI_API_KEY not set')
    return genai.Client(api_key=key)


def _retry(fn, attempts: int = 3, delays: tuple = (10, 30, 60)):
    """Call fn with exponential-backoff retries on any exception."""
    last: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:
            last = exc
            if i < attempts - 1:
                delay = delays[i] if i < len(delays) else delays[-1]
                print(f'  [client] retry {i + 1}/{attempts - 1} in {delay}s ({exc})')
                time.sleep(delay)
    raise last  # type: ignore[misc]


# ── Script stash (needed by dub_to_tamil) ────────────────────────────────────
def register_script_text(script: str) -> None:
    """Called by avatar.py / cinematic.py so dub_to_tamil can access the EN script."""
    global _CURRENT_SCRIPT
    _CURRENT_SCRIPT = script


# ── Image generation → Ken Burns MP4 ─────────────────────────────────────────
def _branded_card_bytes() -> bytes:
    """Branded navy card — guaranteed-free fallback when all AI image APIs fail."""
    from PIL import ImageDraw
    img  = Image.new('RGB', (_W, _H), color=(1, 14, 31))   # NAVY #010E1F
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0),    (_W, 10)], fill=(5, 150, 105))   # EMERALD top bar
    draw.rectangle([(0, _H-10), (_W, _H)], fill=(5, 150, 105))  # EMERALD bottom bar
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=95)
    return buf.getvalue()


def _generate_image_bytes(prompt: str) -> bytes:
    """Return branded PIL card — zero API cost, zero billing risk.

    Imagen 3 and Gemini Flash image models are either paid or unavailable.
    Branded card is the only reliable free path.
    """
    print('  [client] using branded card (zero-cost)')
    return _branded_card_bytes()


def _ken_burns_mp4(image_bytes: bytes, duration: float = 12.0, fps: int = 24) -> str:
    """Animate image as a slow-zoom Ken Burns clip. Returns local MP4 path."""
    from moviepy.editor import VideoClip

    ZOOM_END = 1.15
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    iw, ih = img.size
    scale = max(_W * ZOOM_END / iw, _H * ZOOM_END / ih)
    padded = img.resize((int(iw * scale), int(ih * scale)), Image.LANCZOS)
    arr = np.array(padded)
    bh, bw = arr.shape[:2]

    def make_frame(t: float) -> np.ndarray:
        z = 1.0 + (ZOOM_END - 1.0) * (t / duration)
        cw, ch = int(_W / z), int(_H / z)
        x0, y0 = (bw - cw) // 2, (bh - ch) // 2
        return np.array(
            Image.fromarray(arr[y0:y0 + ch, x0:x0 + cw]).resize((_W, _H), Image.LANCZOS)
        )

    clip = VideoClip(make_frame, duration=duration).set_fps(fps)
    tmp = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    tmp.close()
    clip.write_videofile(tmp.name, codec='libx264', audio=False, logger=None)
    clip.close()
    return tmp.name


def generate_cinematic_clip(
    *,
    prompt: str,
    duration: int = 12,
    aspect_ratio: str = '9:16',
    genre: str = 'drama',
) -> str:
    """Generate a Ken Burns animated clip from a Gemini image. Returns local MP4 path.

    Results are cached per prompt+duration so virality retries skip image API calls.
    """
    img_key  = hashlib.md5(f'{prompt}:{aspect_ratio}'.encode()).hexdigest()
    clip_key = f'{img_key}:{duration}'

    if clip_key in _CLIP_CACHE:
        return _CLIP_CACHE[clip_key]

    if img_key not in _IMAGE_CACHE:
        _IMAGE_CACHE[img_key] = _retry(lambda: _generate_image_bytes(prompt))

    path = _ken_burns_mp4(_IMAGE_CACHE[img_key], duration=float(duration))
    _CLIP_CACHE[clip_key] = path
    return path


# ── TTS (EN + Tamil) ──────────────────────────────────────────────────────────
def _is_tamil(text: str) -> bool:
    return any('஀' <= c <= '௿' for c in text)


async def _edge_tts_async(text: str, voice: str, out_path: str) -> None:
    import edge_tts
    await edge_tts.Communicate(text, voice).save(out_path)


def _tts_edge(text: str, voice: str) -> str:
    """Generate TTS via edge-tts. Returns local MP3 path."""
    tmp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    tmp.close()
    asyncio.run(_edge_tts_async(text, voice, tmp.name))
    return tmp.name


def _tts_gemini(text: str, voice_name: str = 'Charon') -> str:
    """Generate TTS via Gemini 2.5 Flash preview TTS. Returns local WAV path."""
    client = _gemini()
    resp = client.models.generate_content(
        model='gemini-2.5-flash-preview-tts',
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=['AUDIO'],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                )
            ),
        ),
    )
    raw = resp.candidates[0].content.parts[0].inline_data.data
    if isinstance(raw, str):
        import base64
        raw = base64.b64decode(raw)

    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmp.close()
    with wave.open(tmp.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(raw)
    return tmp.name


def generate_audio_track(*, script: str, voice_id: str = '') -> str:
    """Generate voiceover via edge-tts only — zero API cost, zero billing risk.

    Gemini TTS (gemini-2.5-flash-preview-tts) is a paid model and has been
    removed. edge-tts uses Microsoft neural voices with no API key or charges.

    EN:    en-SG-WayneNeural
    Tamil: ta-IN-ValluvarNeural
    """
    if _is_tamil(script):
        voice = voice_id if (voice_id and 'Neural' in voice_id) else 'ta-IN-ValluvarNeural'
    else:
        voice = voice_id if (voice_id and 'Neural' in voice_id) else 'en-SG-WayneNeural'
    return _retry(lambda: _tts_edge(script, voice))


# ── Virality prediction ───────────────────────────────────────────────────────
def predict_virality(video_url: str) -> float:
    """Score virality 0–100 via Gemini text rubric on the registered script.

    Scores the script text rather than the video — faster and avoids uploading
    a 36s MP4. Threshold calibration: log scores for ~2 weeks then adjust
    VIRALITY_THRESHOLD env var in the workflow.
    """
    if not _CURRENT_SCRIPT:
        return 70.0  # safe default if script not registered

    prompt = (
        'Rate this Instagram Reel script\'s virality potential 0–100.\n'
        'Scoring: hook curiosity gap in first sentence (0–30), '
        'retention through content section (0–25), '
        'social proof strength (0–25), CTA clarity (0–20).\n'
        'Context: Singapore FX trader, finance/trading niche, Instagram Reels algorithm.\n'
        'Return ONLY valid JSON: {"score": <integer>}\n\n'
        f'Script:\n{_CURRENT_SCRIPT[:800]}'
    )
    try:
        client = _gemini()
        resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type='application/json'),
        )
        return float(json.loads(resp.text)['score'])
    except Exception as e:
        print(f'  [client] virality scoring failed ({e}), defaulting 70')
        return 70.0


# ── Tamil dubbing ─────────────────────────────────────────────────────────────
def _translate_to_tamil(en_text: str) -> str:
    """Translate EN FX trading script to colloquial spoken Tamil via Gemini."""
    client = _gemini()
    resp = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=(
            'Translate this FX trading Reel script to colloquial spoken Tamil.\n'
            'Rules:\n'
            '- Keep in English exactly: Myfxbook, IC Markets, 91936, '
            'XAUUSD, EURUSD, AUDCAD, IB, Instagram, Raw Spread\n'
            '- Keep all numbers as-is\n'
            '- Write natural spoken Tamil, not overly formal\n'
            '- Return ONLY the Tamil translation, no explanation\n\n'
            f'Script:\n{en_text}'
        ),
    )
    return resp.text.strip()


def _git_commit_file(local_path: Path) -> str:
    """Commit a single file and return its raw GitHub URL."""
    branch = 'master'
    repo   = os.environ.get('GITHUB_REPOSITORY', '')
    for cmd in [
        ['git', 'config', 'user.email', 'github-actions[bot]@users.noreply.github.com'],
        ['git', 'config', 'user.name',  'github-actions[bot]'],
        ['git', 'add', str(local_path)],
        ['git', 'commit', '-m', f'auto: tamil dub {local_path.name} [skip ci]'],
        ['git', 'pull',   '--rebase', 'origin', branch],
        ['git', 'push',   'origin', branch],
    ]:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0 and 'nothing to commit' not in r.stdout + r.stderr:
            raise RuntimeError(f'git {cmd[1]} failed: {r.stderr}')
    rel = local_path.relative_to(ROOT).as_posix()
    return f'https://raw.githubusercontent.com/{repo}/{branch}/{rel}'


def dub_to_tamil(video_url: str, *, voice_id: str = '') -> str:
    """Translate EN script → Tamil TTS → remix audio on EN video → commit → return URL.

    Receives the committed GitHub raw URL of the EN video. Returns a GitHub raw URL
    of the Tamil-dubbed version, ready for Meta Graph API publish.
    """
    from higgsfield.composer import add_audio_to_video

    if not _CURRENT_SCRIPT:
        raise RuntimeError(
            'register_script_text() must be called before dub_to_tamil(). '
            'avatar.generate_reel() and cinematic.generate_broker_reel() do this automatically.'
        )

    REEL_DIR = ROOT / 'instagram' / 'reels'
    REEL_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Translate
    tamil_text = _retry(lambda: _translate_to_tamil(_CURRENT_SCRIPT))
    print(f'  [client] Tamil: {tamil_text[:80]}…')

    # 2. Tamil TTS
    tamil_voice = voice_id if (voice_id and 'Neural' in voice_id) else 'ta-IN-ValluvarNeural'
    audio_path  = _retry(lambda: _tts_edge(tamil_text, tamil_voice))

    # 3. Download EN video
    video_name = video_url.split('/')[-1]
    tamil_name = video_name.replace('-en.mp4', '-tamil-dub.mp4')
    if '-tamil-dub' not in tamil_name:
        tamil_name = video_name.replace('.mp4', '-tamil-dub.mp4')
    tamil_path = REEL_DIR / tamil_name

    with tempfile.TemporaryDirectory() as tmp:
        en_path = Path(tmp) / 'en.mp4'
        with requests.get(video_url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(en_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
        # 4. Remix audio
        add_audio_to_video(en_path, audio_path, tamil_path)

    # 5. Commit and return public URL
    return _git_commit_file(tamil_path)


# ── Path B: Soul avatar ───────────────────────────────────────────────────────
def get_soul_id() -> str:
    soul_id = os.environ.get('HIGGSFIELD_SOUL_ID', '')
    if not soul_id:
        raise EnvironmentError('HIGGSFIELD_SOUL_ID not set — Soul avatar (Path B) not active.')
    return soul_id


def generate_soul_clip(
    *,
    prompt: str,
    soul_id: str,
    duration: int = 15,
    aspect_ratio: str = '9:16',
) -> str:
    """Path B talking-head avatar — not available on free CPU-only stack."""
    raise NotImplementedError(
        'Soul avatar requires GPU runtime and Higgsfield paid plan. '
        'Remove HIGGSFIELD_SOUL_ID secret to use cinematic B-roll (Path A).'
    )
