# instagram/tests/test_edu.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from edu_content import (
    ROTATION_SEQUENCE, RISK_RULES, PAIRS, SETUPS,
    get_edu_content,
)


def test_rotation_sequence_length():
    assert len(ROTATION_SEQUENCE) == 12


def test_get_edu_content_risk():
    post_type, content = get_edu_content(0)
    assert post_type == "risk"
    assert content["rule_num"] == "01"
    assert "title" in content
    assert "body" in content


def test_get_edu_content_pairs():
    post_type, content = get_edu_content(1)
    assert post_type == "pairs"
    assert content["pair"] == "EURUSD"
    assert "quote" in content


def test_get_edu_content_setup():
    post_type, content = get_edu_content(2)
    assert post_type == "setup"
    assert content["pair"] == "GBPJPY"
    assert len(content["steps"]) == 3


def test_rotation_wraps_at_12():
    type_a, content_a = get_edu_content(0)
    type_b, content_b = get_edu_content(12)
    assert type_a == type_b
    assert content_a == content_b


def test_all_rotation_slots_valid():
    for i in range(12):
        post_type, content = get_edu_content(i)
        assert post_type in ("risk", "pairs", "setup")
        assert isinstance(content, dict)
        assert len(content) > 0


def test_risk_rules_have_required_fields():
    for rule in RISK_RULES:
        for field in ("rule_num", "title", "body", "tag"):
            assert field in rule, f"Missing field '{field}' in rule {rule}"


def test_pairs_have_required_fields():
    for pair in PAIRS:
        for field in ("pair", "full_name", "best_session", "avg_spread", "volatility", "my_edge", "quote"):
            assert field in pair, f"Missing field '{field}' in pair {pair}"


def test_setups_have_required_fields():
    for setup in SETUPS:
        for field in ("pair", "direction", "setup_type", "rr", "steps"):
            assert field in setup, f"Missing field '{field}' in setup {setup}"
        assert len(setup["steps"]) == 3
