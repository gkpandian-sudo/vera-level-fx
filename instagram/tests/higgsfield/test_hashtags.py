# instagram/tests/higgsfield/test_hashtags.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from higgsfield.hashtags import get_hashtags, get_hashtags_tamil, _TIER_1_EN, _TIER_2, _TIER_3

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
    """#tamiltrader must appear in every Tamil result (pinned)."""
    for idx in range(20):
        tags = get_hashtags_tamil(idx)
        assert len(tags) == 11
        assert '#tamiltrader' in tags, f"#tamiltrader missing at idx={idx}: {tags}"

def test_get_hashtags_no_duplicates():
    tags = get_hashtags(reel_index=3)
    assert len(tags) == len(set(tags))

def test_get_hashtags_tier_mix():
    """Verify the 5+4+2 tier mix is respected across several indices."""
    t1_set = set(_TIER_1_EN)
    t2_set = set(_TIER_2)
    t3_set = set(_TIER_3)
    for idx in range(20):
        tags = get_hashtags(idx)
        t1_count = sum(1 for t in tags if t in t1_set)
        t2_count = sum(1 for t in tags if t in t2_set)
        t3_count = sum(1 for t in tags if t in t3_set)
        assert t1_count == 5, f"Expected 5 T1 tags at idx={idx}, got {t1_count}: {tags}"
        assert t2_count == 4, f"Expected 4 T2 tags at idx={idx}, got {t2_count}: {tags}"
        assert t3_count == 2, f"Expected 2 T3 tags at idx={idx}, got {t3_count}: {tags}"
