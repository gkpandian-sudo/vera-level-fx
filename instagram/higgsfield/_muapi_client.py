# instagram/higgsfield/_muapi_client.py
"""Muapi.ai direct model API client — Image-to-Video for Instagram Reels.

Uses the direct REST endpoint (not Creative Agent) for simplicity and cost:
  - Default model: grok-imagine-image-to-video  ($0.15 / 6s clip)
  - Fallback model: hunyuan-image-to-video      ($0.15 / 5s clip)

Cost for a 3-clip reel: ~$0.45.  Activate by funding the Muapi account.

Env vars:
  MUAPI_API_KEY       — required
  MUAPI_MODEL         — optional override (default: grok-imagine-image-to-video)
"""
import os
import time
import tempfile
from pathlib import Path

import requests

_BASE = 'https://api.muapi.ai/api/v1'
_POLL_INTERVAL = 10   # seconds between status checks
_POLL_TIMEOUT  = 600  # 10 minutes max per clip

# Supported direct-endpoint models and their request schemas
_MODELS = {
    'grok-imagine-image-to-video': {
        'field': 'images_list',
        'list': True,
        'extra': {'duration': 6, 'aspect_ratio': '9:16'},
    },
    'hunyuan-image-to-video': {
        'field': 'image_url',
        'list': False,
        'extra': {'duration': 5},
    },
    'minimax-hailuo-02-standard-i2v': {
        'field': 'image_url',
        'list': False,
        'extra': {'resolution': '768'},
    },
}
_DEFAULT_MODEL = 'grok-imagine-image-to-video'


def _api_key() -> str:
    key = os.environ.get('MUAPI_API_KEY', '')
    if not key:
        raise RuntimeError('MUAPI_API_KEY env var not set')
    return key


def _headers() -> dict:
    return {'x-api-key': _api_key(), 'Content-Type': 'application/json'}


def _upload_image(png_path: Path) -> str:
    """Upload PNG to Muapi CDN. Returns public CDN URL."""
    key = _api_key()
    resp = requests.get(
        f'{_BASE}/get_upload_url',
        params={'filename': png_path.name, 'content_type': 'image/png'},
        headers={'x-api-key': key},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    upload_url = data['url']
    fields     = data['fields']
    cdn_url    = data['cdn_url']

    with open(png_path, 'rb') as fh:
        form_fields = {k: (None, str(v)) for k, v in fields.items()}
        form_fields['file'] = (png_path.name, fh, 'image/png')
        s3_resp = requests.post(upload_url, files=form_fields, timeout=60)
    s3_resp.raise_for_status()
    return cdn_url


def _submit_job(cdn_url: str, prompt: str) -> str:
    """Submit I2V job to the configured model. Returns job_id."""
    model_name = os.environ.get('MUAPI_MODEL', _DEFAULT_MODEL)
    schema     = _MODELS.get(model_name, _MODELS[_DEFAULT_MODEL])

    payload = {'prompt': prompt}
    payload.update(schema['extra'])
    if schema['list']:
        payload[schema['field']] = [cdn_url]
    else:
        payload[schema['field']] = cdn_url

    resp = requests.post(
        f'{_BASE}/{model_name}',
        headers=_headers(),
        json=payload,
        timeout=30,
    )
    if resp.status_code == 402 or 'INSUFFICIENT_CREDITS' in resp.text:
        raise RuntimeError(
            f'Muapi account has $0 balance — top up at https://muapi.ai/topup '
            f'(cost per clip: ~$0.15, per reel: ~$0.45)'
        )
    resp.raise_for_status()
    data = resp.json()
    return data.get('job_id') or data.get('id') or data['task_id']


def _poll_job(job_id: str) -> dict:
    """Poll until job completes. Returns final status dict."""
    deadline = time.time() + _POLL_TIMEOUT
    while time.time() < deadline:
        resp = requests.get(
            f'{_BASE}/jobs/{job_id}',
            headers=_headers(),
            timeout=30,
        )
        resp.raise_for_status()
        data   = resp.json()
        status = data.get('status', '')
        if status in ('completed', 'success', 'done'):
            return data
        if status in ('failed', 'error', 'cancelled'):
            raise RuntimeError(f'Muapi job {job_id} {status}: {data.get("error", "unknown")}')
        print(f'    [muapi] job {job_id[:8]}… status={status}')
        time.sleep(_POLL_INTERVAL)
    raise TimeoutError(f'Muapi job {job_id} timed out after {_POLL_TIMEOUT}s')


def _extract_video_url(data: dict) -> str:
    """Extract video URL from completed job data."""
    # Try common response shapes
    for key in ('video_url', 'output', 'result', 'url'):
        val = data.get(key)
        if isinstance(val, str) and val.startswith('http'):
            return val
        if isinstance(val, dict):
            for inner in ('video_url', 'url', 'video'):
                v = val.get(inner)
                if isinstance(v, str) and v.startswith('http'):
                    return v
    raise RuntimeError(f'Cannot find video URL in job response: {list(data.keys())}')


def _download_video(url: str, out_path: Path) -> None:
    resp = requests.get(url, timeout=120, stream=True)
    resp.raise_for_status()
    with open(out_path, 'wb') as fh:
        for chunk in resp.iter_content(chunk_size=65536):
            fh.write(chunk)


def animate_card(png_path: Path, out_path: Path, motion_prompt: str) -> Path:
    """Animate a card PNG via Muapi direct I2V API. Returns out_path (local MP4).

    Args:
        png_path:      Local 1080×1920 PNG card to animate.
        out_path:      Where to write the resulting MP4.
        motion_prompt: Short motion description appended to the base prompt.
    """
    full_prompt = (
        'cinematic slow camera push-in, professional financial trading data card, '
        'dark navy background, subtle emerald green glow, 9:16 portrait. '
        + motion_prompt
    )

    print(f'  [muapi] uploading {png_path.name}…')
    cdn_url = _upload_image(png_path)

    print(f'  [muapi] submitting I2V job…')
    job_id = _submit_job(cdn_url, full_prompt)
    print(f'  [muapi] job {job_id[:8]} queued')

    result    = _poll_job(job_id)
    video_url = _extract_video_url(result)

    print(f'  [muapi] downloading result…')
    _download_video(video_url, out_path)
    print(f'  [muapi] saved: {out_path}')
    return out_path
