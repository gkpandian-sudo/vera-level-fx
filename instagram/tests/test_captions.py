import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from captions import (weekly, monthly, daily_status, trust, edu,
                      transparency, recovery_plan, broker,
                      monthly_pnl_from_daily)

SAMPLE_ACCOUNT = {
    'balance': 1500.0, 'equity': 1480.0, 'gain': -62.0, 'daily': 0.5,
    'winRate': 55.0, 'profitFactor': 1.05, 'pips': 1200, 'trades': 150,
    'drawdown': 65.0,
}

def test_recovery_plan_no_projection_table():
    cap = recovery_plan()
    assert '50%' not in cap
    assert '$31,171' not in cap
    assert 'Projected' not in cap

def test_recovery_plan_shows_balance_when_provided():
    cap = recovery_plan(balance=1500.0, pf=0.9)
    assert '$1,500' in cap

def test_recovery_plan_shows_pf_when_provided():
    cap = recovery_plan(balance=1500.0, pf=0.9)
    assert '0.9' in cap or '0.90' in cap

def test_recovery_plan_has_myfxbook_verify():
    cap = recovery_plan()
    assert 'Myfxbook' in cap

def test_broker_no_india_tags():
    cap = broker()
    assert '#forexindia' not in cap
    assert '#tradeindia' not in cap

def test_broker_no_hindi_any_lang():
    cap_en    = broker(lang='en')
    cap_hindi = broker(lang='hindi')
    assert 'करता' not in cap_en
    assert 'करता' not in cap_hindi

def test_broker_has_attribution_warning():
    cap = broker()
    assert 'credited' in cap.lower() or 'referral' in cap.lower()
    assert 'nothing extra' in cap.lower() or 'no cost' in cap.lower()

def test_weekly_hook_not_date_label():
    cap = weekly(SAMPLE_ACCOUNT)
    first_line = cap.strip().split('\n')[0]
    assert 'Weekly Performance' not in first_line
    assert 'Performance ·' not in first_line

def test_weekly_negative_says_loss_not_return():
    neg_acct = {**SAMPLE_ACCOUNT, 'gain': -5.2}
    cap = weekly(neg_acct)
    assert 'total loss' in cap
    assert 'total return' not in cap

def test_monthly_hook_not_date_label():
    pnl = {'Jun 26': -3.2, 'Jul 26': 1.1}
    cap = monthly(SAMPLE_ACCOUNT, pnl)
    first_line = cap.strip().split('\n')[0]
    assert 'Monthly P&L ·' not in first_line

def test_daily_hook_shows_live_position():
    trades = [{'symbol': 'XAUUSD', 'action': 'short', 'profit': -42.0}]
    cap = daily_status(SAMPLE_ACCOUNT, trades)
    first_line = cap.strip().split('\n')[0]
    assert 'Live Position Update' not in first_line
    assert 'XAUUSD' in first_line or 'LIVE' in first_line

def test_daily_hook_flat_when_no_trades():
    cap = daily_status(SAMPLE_ACCOUNT, [])
    first_line = cap.strip().split('\n')[0]
    assert 'Live Position Update' not in first_line

def test_trust_hook_not_label():
    cap = trust(SAMPLE_ACCOUNT)
    first_line = cap.strip().split('\n')[0]
    assert 'Live Track Record ·' not in first_line
