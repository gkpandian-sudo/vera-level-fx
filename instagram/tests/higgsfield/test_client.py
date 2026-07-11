# instagram/tests/higgsfield/test_client.py
import sys, os
from pathlib import Path
from unittest.mock import patch, MagicMock
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


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
        from higgsfield.client import generate_soul_clip
        url = generate_soul_clip(
            prompt='Speak to camera about risk management',
            soul_id='soul_abc123',
            duration=15,
        )
    assert url == 'https://cdn.higgsfield.ai/test.mp4'


def test_generate_cinematic_clip_returns_url():
    with patch('higgsfield.client._hf_subscribe', return_value=_fake_sdk_result()):
        from higgsfield.client import generate_cinematic_clip
        url = generate_cinematic_clip(
            prompt='Cinematic forex trading desk footage',
            duration=15,
        )
    assert url == 'https://cdn.higgsfield.ai/test.mp4'


def test_generate_audio_returns_url():
    audio_result = {'audio': 'https://cdn.higgsfield.ai/audio.mp3'}
    with patch('higgsfield.client._hf_subscribe', return_value=audio_result):
        from higgsfield.client import generate_audio_track
        url = generate_audio_track(script='Hello traders, this week...')
    assert 'cdn.higgsfield.ai' in url


def test_predict_virality_returns_float():
    virality_result = {'virality_score': 72.5}
    with patch('higgsfield.client._hf_subscribe', return_value=virality_result):
        from higgsfield.client import predict_virality
        score = predict_virality('https://cdn.higgsfield.ai/test.mp4')
    assert isinstance(score, float)
    assert 0 <= score <= 100


def test_dub_video_returns_url():
    with patch('higgsfield.client._hf_subscribe', return_value=_fake_sdk_result('https://cdn.higgsfield.ai/dubbed.mp4')):
        from higgsfield.client import dub_to_tamil
        url = dub_to_tamil('https://cdn.higgsfield.ai/test.mp4', voice_id='voice_ta')
    assert 'dubbed' in url


def test_missing_soul_id_raises():
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop('HIGGSFIELD_SOUL_ID', None)
        from higgsfield.client import get_soul_id
        try:
            get_soul_id()
            assert False, 'Expected EnvironmentError'
        except EnvironmentError as e:
            assert 'HIGGSFIELD_SOUL_ID' in str(e)
