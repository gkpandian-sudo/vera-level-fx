import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from captions import (weekly, monthly, daily_status, trust, edu,
                      transparency, recovery_plan, broker, trades,
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
    assert first_line.startswith('Live Position Update')

def test_daily_hook_flat_when_no_trades():
    cap = daily_status(SAMPLE_ACCOUNT, [])
    first_line = cap.strip().split('\n')[0]
    assert first_line.startswith('Live Position Update')

def test_trust_hook_not_label():
    cap = trust(SAMPLE_ACCOUNT)
    first_line = cap.strip().split('\n')[0]
    assert 'Live Track Record ·' not in first_line

def test_daily_has_no_telegram():
    cap = daily_status(SAMPLE_ACCOUNT, [])
    assert 't.me/' not in cap and 'telegram' not in cap.lower()

def test_no_telegram_in_any_caption():
    from edu_content import RISK_RULES
    caps = [
        daily_status(SAMPLE_ACCOUNT, [], recovery_day=45),
        weekly(SAMPLE_ACCOUNT, recovery_day=45),
        monthly(SAMPLE_ACCOUNT, {'Jun 26': -3.2, 'Jul 26': 1.1}),
        trust(SAMPLE_ACCOUNT, recovery_day=45),
        transparency(SAMPLE_ACCOUNT, recovery_day=45),
        recovery_plan(recovery_day=45, balance=1500.0, pf=0.9),
        broker(),
        edu('risk', RISK_RULES[0]),
    ]
    for cap in caps:
        assert 't.me/' not in cap and 'telegram' not in cap.lower()

def test_daily_has_comment_broker_cta():
    cap = daily_status(SAMPLE_ACCOUNT, [])
    assert 'Comment BROKER' in cap

def test_daily_recovery_day_in_caption():
    cap = daily_status(SAMPLE_ACCOUNT, [], recovery_day=11, recovery_total=180)
    assert 'Recovery Day 11' in cap

def test_trust_hook_has_contradiction():
    cap = trust(SAMPLE_ACCOUNT)
    # Both win rate and total return must appear early in the caption
    assert '55%' in cap[:300] and '-62.0%' in cap[:300]

def test_monthly_has_which_month_hook():
    pnl = {'Jun 26': -3.2, 'Jul 26': 1.1}
    cap = monthly(SAMPLE_ACCOUNT, pnl)
    assert 'Which month hurt most' in cap

def test_weekly_has_link_in_bio():
    cap = weekly(SAMPLE_ACCOUNT)
    assert 'link in bio' in cap.lower() or 'bio' in cap.lower()

def test_trust_has_link_in_bio():
    cap = trust(SAMPLE_ACCOUNT)
    assert 'link in bio' in cap.lower() or 'bio' in cap.lower()

def test_daily_ib_cta_has_attribution_warning():
    cap = daily_status(SAMPLE_ACCOUNT, [])
    assert 'IB #91936' in cap  # risk disclaimer carries IB attribution

def test_edu_risk_cta_is_save_not_open_broker():
    from edu_content import RISK_RULES
    caption = edu('risk', RISK_RULES[0])
    assert 'Open IC Markets' not in caption
    assert 'Save this' in caption or 'RULES' in caption

def test_edu_pairs_cta_is_save_not_open_broker():
    from edu_content import PAIRS
    caption = edu('pairs', PAIRS[0])
    assert 'Open IC Markets' not in caption
    assert 'Save this' in caption or 'RULES' in caption

def test_edu_rule05_no_hardcoded_pf():
    from edu_content import RISK_RULES
    rule05 = next(r for r in RISK_RULES if r['rule_num'] == '05')
    assert 'PF 0.75' not in rule05['body']
    assert 'PF 0.75' not in rule05.get('example_rr', '')
    assert 'Myfxbook' in rule05['body']

def test_ib_signup_has_4_steps():
    from captions import ib_signup
    cap = ib_signup()
    assert '1' in cap and '2' in cap and '3' in cap and '4' in cap

def test_ib_signup_has_attribution_warning():
    from captions import ib_signup
    cap = ib_signup()
    assert 'my link' in cap.lower() or "referral" in cap.lower()
    assert 'credited' in cap.lower() or 'bio' in cap.lower()

def test_ib_signup_has_risk_disclaimer():
    from captions import ib_signup
    cap = ib_signup()
    assert 'IB #91936' in cap

def test_milestone_has_verify_link():
    from captions import milestone
    cap = milestone(SAMPLE_ACCOUNT, 'PF crossed 1.0')
    assert 'Myfxbook' in cap

def test_milestone_has_label_in_caption():
    from captions import milestone
    cap = milestone(SAMPLE_ACCOUNT, 'First green month post-rebuild')
    assert 'First green month' in cap

def test_milestone_no_projection():
    from captions import milestone
    cap = milestone(SAMPLE_ACCOUNT, 'Balance hit $2,000')
    assert 'projected' not in cap.lower()
    assert 'guaranteed' not in cap.lower()

def test_monthly_pnl_time_weighted_not_cumulative_sum():
    """monthly_pnl_from_daily must produce time-weighted deltas, not cumulative sums."""
    from captions import monthly_pnl_from_daily
    # Jan end cumulative = 10%, Feb end cumulative = 15%
    # Correct: Jan=10%, Feb=((115)/(110)-1)*100 ≈ 4.545%
    # Wrong (old chart): Jan=10, Feb=15 (raw cumulative values)
    data = [
        ['01/31/2026', 10.0, 50],
        ['02/28/2026', 15.0, 30],
    ]
    result = monthly_pnl_from_daily(data)
    assert abs(result['Jan 26'] - 10.0) < 0.01
    assert abs(result['Feb 26'] - 4.545) < 0.01
    assert result['Feb 26'] < result['Jan 26']   # 4.5% not 15%


from datetime import date

def test_weekly_gain_positive_week():
    """Cumulative moves from -62 (Sun) to -61 (Tue) → small positive week."""
    from captions import weekly_gain_from_daily
    today = date(2026, 7, 7)   # Tuesday
    daily_gain = [
        ['07/05/2026', -62.0, -10],   # Sunday — last row before Monday
        ['07/07/2026', -61.0,  30],   # Tuesday (today)
    ]
    gain = weekly_gain_from_daily(daily_gain, today=today)
    assert gain is not None
    # ((100 + -61) / (100 + -62) - 1) * 100 = (39/38 - 1)*100 ≈ 2.63%
    assert abs(gain - 2.631) < 0.01

def test_weekly_gain_negative_week():
    from captions import weekly_gain_from_daily
    today = date(2026, 7, 9)
    daily_gain = [
        ['07/05/2026', -60.0, 10],
        ['07/09/2026', -62.0, -30],
    ]
    gain = weekly_gain_from_daily(daily_gain, today=today)
    assert gain is not None
    assert gain < 0

def test_weekly_gain_returns_none_when_no_data():
    from captions import weekly_gain_from_daily
    assert weekly_gain_from_daily([], today=date(2026, 7, 9)) is None

def test_weekly_gain_returns_none_when_only_this_week_data():
    """No pre-Monday baseline means we can't compute a delta."""
    from captions import weekly_gain_from_daily
    today = date(2026, 7, 9)   # Thursday
    daily_gain = [['07/07/2026', -61.0, 30]]  # only Monday — no Sunday baseline
    result = weekly_gain_from_daily(daily_gain, today=today)
    assert result is None


def test_weekly_recovery_line_has_of_180():
    cap = weekly(SAMPLE_ACCOUNT, recovery_day=45, recovery_total=180)
    assert 'Recovery Day 45' in cap

def test_daily_recovery_line_has_of_180():
    cap = daily_status(SAMPLE_ACCOUNT, [], recovery_day=45, recovery_total=180)
    assert 'Recovery Day 45' in cap

def test_recovery_plan_has_of_180():
    cap = recovery_plan(recovery_day=45, recovery_total=180)
    assert '45/180' in cap

def test_no_recovery_line_when_day_zero():
    cap = weekly(SAMPLE_ACCOUNT, recovery_day=0, recovery_total=180)
    assert '0/180' not in cap
    assert 'Day 0' not in cap


def test_weekly_hook_does_not_say_this_week_for_total_gain():
    """Total gain must never be labeled 'this week'."""
    cap = weekly(SAMPLE_ACCOUNT)
    first_line = cap.strip().split('\n')[0]
    # With no weekly_gain and no recovery: hook should NOT say 'this week' for total gain
    # SAMPLE_ACCOUNT has gain=-62.0 which is total gain — it's not a weekly figure
    assert 'this week' not in first_line.lower()


def test_weekly_hook_recovery_leads_with_day_counter():
    cap = weekly(SAMPLE_ACCOUNT, recovery_day=45, recovery_total=180)
    first_line = cap.strip().split('\n')[0]
    assert first_line.startswith('Weekly P&L')


def test_weekly_hook_uses_weekly_gain_when_provided():
    cap = weekly(SAMPLE_ACCOUNT, weekly_gain=1.4)
    assert '1.4%' in cap
    assert 'this week' in cap.lower()


def test_weekly_hook_recovery_with_weekly_gain():
    cap = weekly(SAMPLE_ACCOUNT, recovery_day=45, recovery_total=180, weekly_gain=-0.6)
    assert 'Recovery Day 45' in cap
    assert '-0.6%' in cap


def test_tags_has_campaign_hashtag_during_recovery():
    cap = weekly(SAMPLE_ACCOUNT, recovery_day=45)
    assert '#180dayrebuild' in cap

def test_tags_no_campaign_when_no_recovery():
    cap = weekly(SAMPLE_ACCOUNT, recovery_day=0)
    assert '#180dayrebuild' not in cap

def test_total_hashtag_count_weekly_no_recovery():
    cap = weekly(SAMPLE_ACCOUNT, recovery_day=0)
    tags_line = [l for l in cap.split('\n') if '#veralevelFX' in l][0]
    count = tags_line.count('#')
    assert 14 <= count <= 20, f"Expected 14–20 hashtags, got {count}: {tags_line}"

def test_edu_has_separate_edu_tags():
    from edu_content import RISK_RULES
    cap = edu('risk', RISK_RULES[0])
    assert '#forexeducation' in cap or '#learnforex' in cap


def test_trust_has_audit_steps():
    cap = trust(SAMPLE_ACCOUNT)
    # Must include numbered audit instructions
    assert ('1.' in cap or '1️⃣' in cap) and ('2.' in cap or '2️⃣' in cap)

def test_trust_explains_win_rate_with_rr():
    """Win rate without RR context is a scam metric — caption must pair them."""
    cap = trust(SAMPLE_ACCOUNT)
    assert '1:' in cap or 'RR' in cap or 'risk' in cap.lower()

def test_weekly_has_prediction_cta():
    cap = weekly(SAMPLE_ACCOUNT)
    assert 'Comment G' in cap or 'Green or red' in cap.lower() or 'G or R' in cap

def test_monthly_has_save_cta():
    pnl = {'Jun 26': -3.2, 'Jul 26': 1.1}
    cap = monthly(SAMPLE_ACCOUNT, pnl)
    assert 'Save' in cap or 'save' in cap


def test_recovery_plan_has_failure_condition():
    cap = recovery_plan(recovery_day=45, recovery_total=180,
                        recovery_start_str='2026-05-25', balance=1500.0, pf=0.9)
    assert 'Day 180' in cap or 'final result' in cap.lower()

def test_recovery_plan_has_milestone_checklist():
    # PF < 1.0 → both PF milestones unchecked
    cap = recovery_plan(recovery_day=45, recovery_total=180, pf=0.85, balance=1400.0)
    assert '☐' in cap

def test_recovery_plan_pf_milestone_checked_when_above_1():
    # PF >= 1.0 → first PF milestone checked
    cap = recovery_plan(recovery_day=45, recovery_total=180, pf=1.1, balance=1500.0)
    assert '☑' in cap

def test_recovery_plan_end_date_computed_from_start():
    cap = recovery_plan(recovery_day=1, recovery_total=180,
                        recovery_start_str='2026-05-25', balance=1200.0)
    # 2026-05-25 + 179 days = 2026-11-20
    assert 'Nov 2026' in cap or '20 Nov' in cap


# ── New tests: hashtag expansion ─────────────────────────────────────
_BROAD_TAGS = ['#forex', '#forextrading', '#forextrader',
               '#priceaction', '#tradingstrategy', '#algotrading']

def test_tags_includes_broad_discovery():
    from captions import TAGS
    for tag in _BROAD_TAGS:
        assert tag in TAGS, f'{tag} missing from TAGS'

def test_tags_edu_includes_broad_discovery():
    from captions import TAGS_EDU
    for tag in _BROAD_TAGS:
        assert tag in TAGS_EDU, f'{tag} missing from TAGS_EDU'

def test_broker_caption_includes_broad_tags():
    cap = broker()
    for tag in _BROAD_TAGS:
        assert tag in cap, f'{tag} missing from broker caption'

# ── New tests: hook formats ───────────────────────────────────────────
def test_daily_hook_punchy_line():
    cap = daily_status(SAMPLE_ACCOUNT, [])
    assert 'Real trades. Real P&L. Nothing hidden.' in cap

def test_daily_hook_recovery_day_line():
    cap = daily_status(SAMPLE_ACCOUNT, [], recovery_day=7)
    assert 'Recovery Day 7.' in cap

def test_monthly_hook_title_format():
    pnl = {'Jun 26': -3.2, 'Jul 26': 1.1}
    cap = monthly(SAMPLE_ACCOUNT, pnl)
    assert cap.strip().split('\n')[0].startswith('Monthly P&L')

def test_trust_hook_title_format():
    cap = trust(SAMPLE_ACCOUNT)
    assert cap.strip().split('\n')[0].startswith('Track Record')

# ── New tests: CTA trimming ───────────────────────────────────────────
def test_no_old_ib_bio_cta_in_daily():
    cap = daily_status(SAMPLE_ACCOUNT, [])
    assert 'Opening an account anyway?' not in cap

def test_no_old_follow_cta_in_daily():
    cap = daily_status(SAMPLE_ACCOUNT, [])
    assert '➕ Follow @veralevel.fx' not in cap

def test_compact_cta_in_all_p_and_l_posts():
    pnl = {'Jun 26': -3.2, 'Jul 26': 1.1}
    posts = [
        ('daily',        daily_status(SAMPLE_ACCOUNT, [])),
        ('weekly',       weekly(SAMPLE_ACCOUNT)),
        ('monthly',      monthly(SAMPLE_ACCOUNT, pnl)),
        ('trust',        trust(SAMPLE_ACCOUNT)),
        ('transparency', transparency(SAMPLE_ACCOUNT)),
        ('recovery',     recovery_plan(balance=1500.0, pf=0.9)),
    ]
    for name, cap in posts:
        assert 'Comment BROKER → IC Markets setup straight to your DMs' in cap, \
               f'_CTA_COMPACT missing from {name}'

def test_myfxbook_verify_cta_in_all_p_and_l_posts():
    pnl = {'Jun 26': -3.2, 'Jul 26': 1.1}
    posts = [
        ('daily',        daily_status(SAMPLE_ACCOUNT, [])),
        ('weekly',       weekly(SAMPLE_ACCOUNT)),
        ('monthly',      monthly(SAMPLE_ACCOUNT, pnl)),
        ('trust',        trust(SAMPLE_ACCOUNT)),
        ('transparency', transparency(SAMPLE_ACCOUNT)),
        ('recovery',     recovery_plan(balance=1500.0, pf=0.9)),
    ]
    for name, cap in posts:
        assert 'Myfxbook #12044019' in cap, f'_CTA_VERIFY missing from {name}'

def test_risk_disclaimer_in_all_p_and_l_posts():
    pnl = {'Jun 26': -3.2, 'Jul 26': 1.1}
    posts = [
        ('daily',        daily_status(SAMPLE_ACCOUNT, [])),
        ('weekly',       weekly(SAMPLE_ACCOUNT)),
        ('monthly',      monthly(SAMPLE_ACCOUNT, pnl)),
        ('trust',        trust(SAMPLE_ACCOUNT)),
        ('transparency', transparency(SAMPLE_ACCOUNT)),
    ]
    for name, cap in posts:
        assert 'Trading FX on margin' in cap, f'risk disclaimer missing from {name}'

def test_edu_soft_cta_updated_wording():
    from edu_content import RISK_RULES
    cap = edu('risk', RISK_RULES[0])
    assert "I'll DM you" not in cap
    assert 'Comment RULES for the full library' in cap


# ── trades caption ─────────────────────────────────────────────────────────────

SAMPLE_TRADES = [
    {'symbol': 'XAUUSD', 'action': 'Buy',  'pips': 15,  'profit': 16.50, 'commission': -0.80},
    {'symbol': 'XAUUSD', 'action': 'Buy',  'pips': 2,   'profit':  1.80, 'commission': -0.76},
    {'symbol': 'XAUUSD', 'action': 'Sell', 'pips': -8,  'profit': -7.20, 'commission': -0.80},
    {'symbol': 'EURUSD', 'action': 'Buy',  'pips': 22,  'profit': 22.00, 'commission': -3.50},
    {'symbol': 'XAUUSD', 'action': 'Buy',  'pips': 19,  'profit': 20.50, 'commission': -0.80},
]

def test_trades_caption_contains_last_5_heading():
    cap = trades(SAMPLE_ACCOUNT, SAMPLE_TRADES)
    assert 'Last 5 Closed Trades' in cap

def test_trades_caption_shows_symbol_and_direction():
    cap = trades(SAMPLE_ACCOUNT, SAMPLE_TRADES)
    assert 'XAUUSD' in cap
    assert 'BUY' in cap

def test_trades_caption_shows_net_line():
    cap = trades(SAMPLE_ACCOUNT, SAMPLE_TRADES)
    assert 'Net:' in cap

def test_trades_caption_shows_win_loss_count():
    cap = trades(SAMPLE_ACCOUNT, SAMPLE_TRADES)
    assert 'W' in cap and 'L' in cap

def test_trades_caption_has_risk_disclaimer():
    cap = trades(SAMPLE_ACCOUNT, SAMPLE_TRADES)
    assert 'Trading FX on margin' in cap

def test_trades_caption_has_myfxbook_verify():
    cap = trades(SAMPLE_ACCOUNT, SAMPLE_TRADES)
    assert 'Myfxbook' in cap

def test_trades_caption_empty_history_is_graceful():
    cap = trades(SAMPLE_ACCOUNT, [])
    assert 'Last 5 Closed Trades' in cap
    assert 'No closed trades' in cap

def test_trades_caption_ib_link_uses_camp_param():
    cap = trades(SAMPLE_ACCOUNT, SAMPLE_TRADES)
    assert 'camp=91936' in cap
