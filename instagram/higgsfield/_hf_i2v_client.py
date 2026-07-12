# instagram/higgsfield/_hf_i2v_client.py
"""Free HuggingFace Space I2V via gradio_client — Path D.

Calls a ZeroGPU I2V Space (default: Lightricks/ltx-video-distilled).
Raises RuntimeError on any failure; caller falls back to Ken Burns (Path A).

Env vars:
  HF_I2V_SPACE        — Space id to use (must be set to activate Path D)
  HUGGING_FACE_TOKEN  — HF token (improves ZeroGPU queue priority; optional)
"""
import os
import shutil
from pathlib import Path

_DEFAULT_SPACE = 'Lightricks/ltx-video-distilled'
_TIMEOUT = 1200   # 20 min — leaves headroom in 45-min GitHub Actions job

_BASE_PROMPT = (
    'cinematic slow camera push-in, professional financial data visualization, '
    'dark navy background, subtle emerald green glow, trading terminal aesthetic, '
    '9:16 portrait, smooth motion, no text overlay'
)

# Try these Gradio endpoint names in order; different spaces use different names
_ENDPOINT_TRIES = ('/infer', '/predict', '/generate', '/run/predict')


def animate_card(png_path: Path, out_path: Path, motion_prompt: str) -> Path:
    """Animate a card PNG via HuggingFace I2V Space. Returns out_path.

    Raises RuntimeError if the Space is unavailable, times out, or all
    endpoint names fail — caller is responsible for Ken Burns fallback.
    """
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        raise RuntimeError('gradio-client not installed — add gradio-client>=1.3 to requirements.txt')

    space = os.environ.get('HF_I2V_SPACE', _DEFAULT_SPACE)
    token = os.environ.get('HUGGING_FACE_TOKEN') or None

    print(f'  [hf_i2v] connecting to {space}…')
    try:
        client = Client(space, hf_token=token)
    except Exception as e:
        raise RuntimeError(f'[hf_i2v] cannot connect to {space}: {e}')

    full_prompt = f'{_BASE_PROMPT}. {motion_prompt}'
    img_handle  = handle_file(str(png_path))

    # Try known endpoint names; use submit/result for timeout control
    last_err = None
    for api_name in _ENDPOINT_TRIES:
        try:
            print(f'  [hf_i2v] trying {api_name}…')
            job    = client.submit(img_handle, full_prompt, api_name=api_name)
            result = job.result(timeout=_TIMEOUT)
            break
        except Exception as e:
            last_err = e
            continue
    else:
        raise RuntimeError(f'[hf_i2v] all endpoints failed — last error: {last_err}')

    # Result may be a path string, a Path, or a list/tuple (take first .mp4)
    if isinstance(result, (list, tuple)):
        mp4 = next((r for r in result if str(r).endswith('.mp4')), result[0])
    else:
        mp4 = result

    src = Path(str(mp4))
    if not src.exists():
        raise RuntimeError(f'[hf_i2v] output file not found: {src}')

    shutil.copy2(src, out_path)
    print(f'  [hf_i2v] saved: {out_path}')
    return out_path
