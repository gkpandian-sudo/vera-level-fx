# instagram/tests/higgsfield/test_client.py
import sys, os
from pathlib import Path
from unittest.mock import patch, MagicMock
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from higgsfield.client import (
    generate_soul_clip, generate_cinematic_clip, generate_audio_track,
    predict_virality, dub_to_tamil, get_soul_id,
)


def _fake_sdk_result(video_url='https://cdn.higgsfield.ai/test.mp4'):
    m = MagicMock()
    m.__getitem__ = lambda self, k: video_url if k == 'video' else None
    return {'video': video_url, 'images': [], 'status': 'done'}


class FakeHFClient:
    def subscribe(self, model, arguments):
        return _fake_sdk_result()
    def submit(self, model, arguments):
        ctrl = MagicMock()
        ctrl.poll_request_status.return_value = [_fake_sdk_result()]
        return ctrl


def test_generate_soul_clip_returns_url():
    with patch('higgsfield.client._hf_subscribe', return_value=_fake_sdk_result()):
        url = generate_soul_clip(
            prompt='Speak to camera about risk management',
            soul_id='soul_abc123',
            duration=15,
        )
    assert url == 'https://cdn.higgsfield.ai/test.mp4'


def test_generate_cinematic_clip_returns_url():
    with patch('higgsfield.client._hf_subscribe', return_value={'video': 'https://cdn.higgsfield.ai/test.mp4'}) as mock_sub:
        url = generate_cinematic_clip(prompt='Cinematic forex trading desk footage', duration=12)
    assert url == 'https://cdn.higgsfield.ai/test.mp4'
    args = mock_sub.call_args
    assert args[0][1].get('sound') == 'off', "generate_cinematic_clip must pass sound='off' to Higgsfield"


def test_generate_audio_returns_url():
    audio_result = {'audio': 'https://cdn.higgsfield.ai/audio.mp3'}
    with patch('higgsfield.client._hf_subscribe', return_value=audio_result):
        url = generate_audio_track(script='Hello traders, this week...')
    assert 'cdn.higgsfield.ai' in url


def test_predict_virality_returns_float():
    virality_result = {'virality_score': 72.5}
    with patch('higgsfield.client._hf_subscribe', return_value=virality_result):
        score = predict_virality('https://cdn.higgsfield.ai/test.mp4')
    assert isinstance(score, float)
    assert 0 <= score <= 100


def test_dub_video_returns_url():
    with patch('higgsfield.client._hf_subscribe', return_value=_fake_sdk_result('https://cdn.higgsfield.ai/dubbed.mp4')):
        url = dub_to_tamil('https://cdn.higgsfield.ai/test.mp4', voice_id='voice_ta')
    assert 'dubbed' in url


def test_missing_soul_id_raises():
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop('HIGGSFIELD_SOUL_ID', None)
        try:
            get_soul_id()
            assert False, 'Expected EnvironmentError'
        except EnvironmentError as e:
            assert 'HIGGSFIELD_SOUL_ID' in str(e)
