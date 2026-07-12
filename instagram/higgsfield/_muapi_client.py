# instagram/higgsfield/_muapi_client.py
"""Muapi.ai Creative Agent client — Image-to-Video for Instagram Reels.

Calls https://api.muapi.ai directly (no local proxy needed for CI/CD).

Flow per card:
  1. Create session
  2. Upload PNG to Muapi CDN via signed S3 URL
  3. Register asset in session
  4. Chat: "Animate asset_1 as a 9:16 video…"
  5. Poll job until completed / failed
  6. Download generated MP4 to out_path

Requires env var: MUAPI_API_KEY
"""
import os
import time
import tempfile
from pathlib import Path

import requests

_BASE = 'https://api.muapi.ai/api/v1'
_POLL_INTERVAL = 12   # seconds between status checks
_POLL_TIMEOUT  = 600  # 10 minutes max per clip


def _api_key() -> str:
    key = os.environ.get('MUAPI_API_KEY', '')
    if not key:
        raise RuntimeError('MUAPI_API_KEY env var not set')
    return key


def _headers() -> dict:
    return {'x-api-key': _api_key(), 'Content-Type': 'application/json'}


def _upload_png(png_path: Path) -> str:
    """Upload PNG to Muapi CDN. Returns public CDN URL."""
    key = _api_key()

    # Get pre-signed S3 upload URL
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

    # POST to S3 (pre-signed form upload — file field must be last)
    with open(png_path, 'rb') as fh:
        form_fields = {k: (None, str(v)) for k, v in fields.items()}
        form_fields['file'] = (png_path.name, fh, 'image/png')
        s3_resp = requests.post(upload_url, files=form_fields, timeout=60)
    s3_resp.raise_for_status()

    return cdn_url


def _create_session() -> str:
    resp = requests.post(
        f'{_BASE}/creative-agent/sessions',
        headers=_headers(),
        json={},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()['id']


def _register_asset(session_id: str, cdn_url: str) -> str:
    """Register image asset in session. Returns the assigned asset_label (e.g. 'asset_1')."""
    resp = requests.post(
        f'{_BASE}/creative-agent/sessions/{session_id}/assets',
        headers=_headers(),
        json={'url': cdn_url, 'kind': 'image', 'asset_label': 'card_image'},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()['asset_label']


def _start_animation(session_id: str, asset_label: str, prompt: str) -> str:
    """Send chat message to animate the asset. Returns job_id."""
    full_prompt = (
        f'Animate {asset_label} as a smooth 9:16 portrait video, 8 seconds. '
        f'{prompt}'
    )
    resp = requests.post(
        f'{_BASE}/creative-agent/sessions/{session_id}/chat',
        headers=_headers(),
        json={'message': full_prompt},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()['job_id']


def _poll_job(job_id: str) -> dict:
    """Poll until job reaches a terminal state. Returns final status dict."""
    deadline = time.time() + _POLL_TIMEOUT
    while time.time() < deadline:
        resp = requests.get(
            f'{_BASE}/creative-agent/jobs/{job_id}/status',
            headers=_headers(),
            timeout=30,
        )
        if resp.status_code == 404:
            raise RuntimeError(f'Job {job_id} not found — may have been rejected (check account balance)')
        resp.raise_for_status()
        status = resp.json()
        state = status.get('state', '')
        if state == 'completed':
            return status
        if state == 'failed':
            raise RuntimeError(f'Muapi job {job_id} failed: {status.get("error", "unknown")}')
        print(f'    [muapi] job {job_id[:8]}… state={state}')
        time.sleep(_POLL_INTERVAL)
    raise TimeoutError(f'Muapi job {job_id} timed out after {_POLL_TIMEOUT}s')


def _get_video_url(session_id: str) -> str:
    """Retrieve the most recently generated video asset URL from the session."""
    resp = requests.get(
        f'{_BASE}/creative-agent/sessions/{session_id}/assets',
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    assets = resp.json()
    videos = [a for a in assets if a.get('kind') == 'video']
    if not videos:
        raise RuntimeError(f'No video asset found in session {session_id}')
    return videos[-1]['url']


def _download_video(url: str, out_path: Path) -> None:
    resp = requests.get(url, timeout=120, stream=True)
    resp.raise_for_status()
    with open(out_path, 'wb') as fh:
        for chunk in resp.iter_content(chunk_size=65536):
            fh.write(chunk)


def animate_card(png_path: Path, out_path: Path, motion_prompt: str) -> Path:
    """Run full Muapi I2V pipeline for one card PNG. Returns out_path (local MP4).

    Args:
        png_path:      Local 1080×1920 PNG card to animate.
        out_path:      Where to write the resulting MP4.
        motion_prompt: Short description of the motion style (e.g. "green glow, particle rise").
    """
    print(f'  [muapi] uploading {png_path.name}…')
    cdn_url    = _upload_png(png_path)

    session_id = _create_session()
    print(f'  [muapi] session {session_id[:8]}')

    asset_label = _register_asset(session_id, cdn_url)
    job_id      = _start_animation(session_id, asset_label, motion_prompt)
    print(f'  [muapi] job {job_id[:8]} queued')

    _poll_job(job_id)

    video_url = _get_video_url(session_id)
    print(f'  [muapi] downloading result…')
    _download_video(video_url, out_path)
    print(f'  [muapi] saved: {out_path}')

    return out_path
