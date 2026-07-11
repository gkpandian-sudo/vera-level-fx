# instagram/tests/higgsfield/test_scripts.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from higgsfield.scripts import build_script, ReelScript

SAMPLE_ACCOUNT = {
    'balance': 1500.0, 'equity': 1480.0, 'gain': -12.0, 'daily': 0.5,
    'winRate': 55.0, 'profitFactor': 1.05, 'pips': 1200, 'trades': 150,
}
SAMPLE_EDU = {
    'rule_num': '01', 'title': 'Lot Sizing By Balance',
    'body': 'Fixed lots is how accounts die slowly.',
    'example_account': 1000, 'example_risk': 10,
    'example_rr': '1% max risk', 'example_target': 25, 'tag': 'SIZING',
}
SAMPLE_PAIRS_EDU = {
    'pair': 'EURUSD', 'best_session': 'London+NY',
    'avg_spread': '0.1 pips', 'my_edge': 'structure and momentum',
}
SAMPLE_SETUP_EDU = {
    'pair': 'EURUSD', 'direction': 'LONG', 'rr': '1:2.5',
    'steps': [('Sweep low', 'wait for liquidity grab'), ('Break of structure', 'confirm direction'), ('50% retracement', 'enter at FVG')],
}

def test_build_script_edu_returns_reel_script():
    s = build_script('edu', account=SAMPLE_ACCOUNT,
                     edu_type='risk', edu_content=SAMPLE_EDU)
    assert isinstance(s, ReelScript)

def test_build_script_edu_hook_is_nonempty():
    s = build_script('edu', account=SAMPLE_ACCOUNT,
                     edu_type='risk', edu_content=SAMPLE_EDU)
    assert len(s.hook) > 10

def test_build_script_edu_proof_contains_myfxbook():
    s = build_script('edu', account=SAMPLE_ACCOUNT,
                     edu_type='risk', edu_content=SAMPLE_EDU)
    assert '12044019' in s.proof

def test_build_script_edu_cta_contains_save_and_bio():
    s = build_script('edu', account=SAMPLE_ACCOUNT,
                     edu_type='risk', edu_content=SAMPLE_EDU)
    assert 'save' in s.cta.lower() and 'bio' in s.cta.lower()

def test_build_script_trust_hook_is_challenge():
    s = build_script('trust', account=SAMPLE_ACCOUNT)
    assert 'screenshot' in s.hook.lower() or 'fake' in s.hook.lower() or 'audit' in s.hook.lower()

def test_build_script_weekly_hook_contains_gain():
    neg = build_script('weekly', account=SAMPLE_ACCOUNT, weekly_gain=-1.2)
    assert '-1.2' in neg.hook
    pos = build_script('weekly', account=SAMPLE_ACCOUNT, weekly_gain=2.3)
    assert '+2.3' in pos.hook

def test_build_script_broker_hook_mentions_broker():
    s = build_script('broker', account=SAMPLE_ACCOUNT)
    assert 'broker' in s.hook.lower() or 'ic markets' in s.hook.lower() or 'months' in s.hook.lower()

def test_build_script_reel_type_stored():
    s = build_script('trust', account=SAMPLE_ACCOUNT)
    assert s.reel_type == 'trust'

def test_build_script_language_en_by_default():
    s = build_script('edu', account=SAMPLE_ACCOUNT,
                     edu_type='risk', edu_content=SAMPLE_EDU)
    assert s.language == 'en'

def test_build_script_all_segments_nonempty():
    for reel_type in ('trust', 'weekly', 'broker'):
        s = build_script(reel_type, account=SAMPLE_ACCOUNT, weekly_gain=1.5)
        assert s.hook and s.content and s.proof and s.cta, f"Empty segment in {reel_type}"

def test_build_script_edu_pairs_hook_mentions_pair():
    s = build_script('edu', account=SAMPLE_ACCOUNT,
                     edu_type='pairs', edu_content=SAMPLE_PAIRS_EDU)
    assert 'EURUSD' in s.hook

def test_build_script_edu_setup_hook_mentions_pair():
    s = build_script('edu', account=SAMPLE_ACCOUNT,
                     edu_type='setup', edu_content=SAMPLE_SETUP_EDU)
    assert 'EURUSD' in s.hook

def test_build_script_edu_setup_raises_if_steps_fewer_than_3():
    bad_content = {**SAMPLE_SETUP_EDU, 'steps': [('only one', 'step')]}
    try:
        build_script('edu', account=SAMPLE_ACCOUNT,
                     edu_type='setup', edu_content=bad_content)
        assert False, 'Expected ValueError'
    except ValueError as e:
        assert 'steps' in str(e).lower()

def test_build_script_weekly_zero_gain_uses_plus_sign():
    s = build_script('weekly', account=SAMPLE_ACCOUNT, weekly_gain=0.0)
    assert '+0.0' in s.hook
