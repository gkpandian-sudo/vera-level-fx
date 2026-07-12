# instagram/tests/higgsfield/test_pipeline.py
import sys, json, os
from pathlib import Path
from unittest.mock import patch, MagicMock, call
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

SNAPSHOT = {
    'account': {
        'balance': 1500.0, 'equity': 1480.0, 'gain': -1.2, 'daily': 0.5,
        'winRate': 55.0, 'profitFactor': 1.05, 'pips': 1200, 'trades': 150,
        'drawdown': 25.0,
    },
    'openTrades': [],
    'dailyGain': [],
}

def _env(reel_type='trust', lang='en'):
    return {
        'REEL_TYPE': reel_type, 'POST_LANG': lang,
        'IG_USER_ID': 'fake_ig', 'META_ACCESS_TOKEN': 'fake_token',
        'HIGGSFIELD_API_KEY': 'fake_hf_key', 'HIGGSFIELD_API_SECRET': 'fake_hf_secret',
        'GITHUB_REPOSITORY': 'user/repo', 'GITHUB_TOKEN': 'fake_gh',
        'BRAND_IB_URL': 'https://icmarkets.com/?camp=91936',
    }

FAKE_VIDEO_URL = 'https://cdn.higgsfield.ai/test.mp4'
FAKE_GH_URL   = 'https://raw.githubusercontent.com/user/repo/master/instagram/reels/test.mp4'
FAKE_THUMB_URL = 'https://raw.githubusercontent.com/user/repo/master/instagram/reels/test-thumb.jpg'

def test_run_trust_en_calls_generate_reel_and_publish():
    from higgsfield import pipeline
    with patch.dict(os.environ, _env('trust', 'en')), \
         patch('higgsfield.pipeline.generate_reel',         return_value=(FAKE_VIDEO_URL, Path('/tmp/out.mp4'))), \
         patch('higgsfield.pipeline.predict_virality',      return_value=75.0), \
         patch('higgsfield.pipeline.composite_data_card',   return_value=Path('/tmp/out.mp4')), \
         patch('higgsfield.pipeline._make_data_card'), \
         patch('higgsfield.pipeline.commit_and_push',       return_value=[FAKE_GH_URL, FAKE_THUMB_URL]), \
         patch('higgsfield.pipeline.publish_reel') as mock_pub, \
         patch('time.sleep'):
        pipeline.run(reel_type='trust', lang='en', snapshot=SNAPSHOT)
    mock_pub.assert_called_once()

def test_run_edu_increments_counter():
    from higgsfield import pipeline
    with patch.dict(os.environ, _env('edu', 'en')), \
         patch('higgsfield.pipeline.generate_reel',         return_value=(FAKE_VIDEO_URL, Path('/tmp/out.mp4'))), \
         patch('higgsfield.pipeline.predict_virality',      return_value=75.0), \
         patch('higgsfield.pipeline.composite_data_card',   return_value=Path('/tmp/out.mp4')), \
         patch('higgsfield.pipeline._make_data_card'), \
         patch('higgsfield.pipeline.commit_and_push',       return_value=[FAKE_GH_URL, FAKE_THUMB_URL]), \
         patch('higgsfield.pipeline.publish_reel'), \
         patch('higgsfield.pipeline.read_counter',          return_value=0), \
         patch('higgsfield.pipeline.write_counter') as mock_write, \
         patch('higgsfield.pipeline.get_edu_content',       return_value=('risk', {'title': 'T', 'body': 'B', 'rule_num': '01', 'example_account': 1000, 'example_risk': 10, 'example_rr': '1:2'})), \
         patch('higgsfield.pipeline.ROTATION_LEN',          new=14), \
         patch('time.sleep'):
        pipeline.run(reel_type='edu', lang='en', snapshot=SNAPSHOT)
    mock_write.assert_called_once_with(1)

def test_virality_gate_regenerates_when_score_below_threshold():
    from higgsfield import pipeline
    # First two calls score below threshold, third passes
    with patch.dict(os.environ, _env('trust', 'en')), \
         patch('higgsfield.pipeline.generate_reel',         return_value=(FAKE_VIDEO_URL, Path('/tmp/out.mp4'))) as mock_gen, \
         patch('higgsfield.pipeline.predict_virality',      side_effect=[40.0, 40.0, 70.0]), \
         patch('higgsfield.pipeline.composite_data_card',   return_value=Path('/tmp/out.mp4')), \
         patch('higgsfield.pipeline._make_data_card'), \
         patch('higgsfield.pipeline.commit_and_push',       return_value=[FAKE_GH_URL, FAKE_THUMB_URL]), \
         patch('higgsfield.pipeline.publish_reel'), \
         patch('time.sleep'):
        pipeline.run(reel_type='trust', lang='en', snapshot=SNAPSHOT)
    # generate_reel called 3 times (1 original + 2 retries)
    assert mock_gen.call_count == 3

def test_run_tamil_reel_calls_dub():
    from higgsfield import pipeline
    with patch.dict(os.environ, _env('edu', 'tamil')), \
         patch('higgsfield.pipeline.generate_reel',         return_value=(FAKE_VIDEO_URL, Path('/tmp/out.mp4'))), \
         patch('higgsfield.pipeline.predict_virality',      return_value=75.0), \
         patch('higgsfield.pipeline.composite_data_card',   return_value=Path('/tmp/out.mp4')), \
         patch('higgsfield.pipeline._make_data_card'), \
         patch('higgsfield.pipeline.commit_and_push',       return_value=[FAKE_GH_URL, FAKE_THUMB_URL]), \
         patch('higgsfield.pipeline.publish_reel') as mock_pub, \
         patch('higgsfield.pipeline.dub_to_tamil_video',    return_value='https://cdn.higgsfield.ai/dubbed.mp4') as mock_dub, \
         patch('higgsfield.pipeline.read_counter',          return_value=0), \
         patch('higgsfield.pipeline.write_counter'), \
         patch('higgsfield.pipeline.get_edu_content',       return_value=('risk', {'title': 'T', 'body': 'B', 'rule_num': '01', 'example_account': 1000, 'example_risk': 10, 'example_rr': '1:2'})), \
         patch('higgsfield.pipeline.ROTATION_LEN',          new=14), \
         patch('time.sleep'):
        pipeline.run(reel_type='edu', lang='tamil', snapshot=SNAPSHOT)
    mock_dub.assert_called_once()
    # publish_reel should be called with the dubbed URL
    call_args = mock_pub.call_args
    assert 'dubbed' in call_args[0][0]
