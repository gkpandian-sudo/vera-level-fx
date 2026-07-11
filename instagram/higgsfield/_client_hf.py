# instagram/higgsfield/_client_hf.py
"""Higgsfield SDK client — paid fallback when GEMINI_API_KEY is not set."""
import os

def _init_sdk():
    import higgsfield_client as _sdk
    key    = os.environ.get('HIGGSFIELD_API_KEY', '')
    secret = os.environ.get('HIGGSFIELD_API_SECRET', '')
    if key and secret:
        os.environ.setdefault('HF_KEY', f'{key}:{secret}')
    return _sdk

def _hf_subscribe(model: str, arguments: dict) -> dict:
    sdk = _init_sdk()
    return sdk.subscribe(model, arguments=arguments)

_MODEL_SOUL  = 'soul_cinema_studio'

def get_soul_id() -> str:
    soul_id = os.environ.get('HIGGSFIELD_SOUL_ID', '')
    if not soul_id:
        raise EnvironmentError('HIGGSFIELD_SOUL_ID not set. Run Soul training first.')
    return soul_id

def generate_soul_clip(*, prompt: str, soul_id: str, duration: int = 15, aspect_ratio: str = '9:16') -> str:
    result = _hf_subscribe(_MODEL_SOUL, {'prompt': prompt, 'soul_id': soul_id, 'duration': duration, 'aspect_ratio': aspect_ratio})
    return result['video']

_MODEL_CINEMA = 'cinematic_studio_video_v2'

def generate_cinematic_clip(*, prompt: str, duration: int = 12, aspect_ratio: str = '9:16', genre: str = 'drama') -> str:
    result = _hf_subscribe(_MODEL_CINEMA, {'prompt': prompt, 'duration': duration, 'aspect_ratio': aspect_ratio, 'genre': genre, 'sound': 'off'})
    return result['video']

def generate_audio_track(*, script: str, voice_id: str = '') -> str:
    args = {'prompt': script}
    if voice_id:
        args['voice_id'] = voice_id
    result = _hf_subscribe('generate_audio', args)
    url = result.get('audio') or result.get('video', '')
    if not url:
        raise ValueError(f'generate_audio_track: unexpected response: {result!r}')
    return url

def predict_virality(video_url: str) -> float:
    result = _hf_subscribe('virality_predictor', {'video_url': video_url})
    raw = result.get('virality_score', result.get('score'))
    if raw is None:
        raise ValueError(f'predict_virality: unexpected response: {result!r}')
    return float(raw)

def dub_to_tamil(video_url: str, *, voice_id: str = '') -> str:
    args = {'video_url': video_url, 'target_language': 'tamil'}
    if voice_id:
        args['voice_id'] = voice_id
    result = _hf_subscribe('dubbing', args)
    return result.get('video') or result.get('video_url', '')
