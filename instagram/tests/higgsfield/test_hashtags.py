# instagram/tests/higgsfield/test_hashtags.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from higgsfield.hashtags import get_hashtags, get_hashtags_tamil

def test_get_hashtags_returns_11_tags():
    tags = get_hashtags(reel_index=0)
    assert len(tags) == 11

def test_get_hashtags_all_start_with_hash():
    tags = get_hashtags(reel_index=0)
    assert all(t.startswith('#') for t in tags)

def test_get_hashtags_rotates_between_calls():
    tags_0 = get_hashtags(reel_index=0)
    tags_1 = get_hashtags(reel_index=1)
    # At least one tag should differ — rotation prevents identical blocks
    assert tags_0 != tags_1

def test_get_hashtags_deterministic():
    # Same index always gives same tags
    assert get_hashtags(reel_index=5) == get_hashtags(reel_index=5)

def test_get_hashtags_tamil_contains_tamil_tags():
    tags = get_hashtags_tamil(reel_index=0)
    assert len(tags) == 11
    joined = ' '.join(tags)
    assert '#tamiltrader' in joined or '#tamilforex' in joined or '#sgtrader' in joined

def test_get_hashtags_no_duplicates():
    tags = get_hashtags(reel_index=3)
    assert len(tags) == len(set(tags))
