"""Smoke tests: each generator runs without error and produces valid output."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image

DUMMY_ACCOUNT = {
    'balance': 3460.38, 'gain': 9.11, 'monthly': 1.2,
    'winRate': 76, 'profitFactor': 1.32, 'drawdown': 51.0,
    'pips': 31819, 'trades': 739, 'equity': 3420.0, 'daily': 0.12,
}
DUMMY_OPEN_TRADES = [
    {'symbol': 'EURUSD', 'action': 'buy', 'profit': 128, 'pips': 12.3, 'openPrice': 1.0823},
    {'symbol': 'XAUUSD', 'action': 'buy', 'profit': 42,  'pips': 4.2,  'openPrice': 2315.50},
    {'symbol': 'AUDCAD', 'action': 'sell','profit': -9,  'pips': -8.1, 'openPrice': 0.9122},
]
DUMMY_DATA = {'account': DUMMY_ACCOUNT, 'openTrades': DUMMY_OPEN_TRADES, 'dailyGain': []}


def _fig_to_pil(fig) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, facecolor='#010E1F')
    buf.seek(0)
    plt.close('all')
    return Image.open(buf)


def test_weekly_card_size():
    from instagram.generate import make_weekly_card
    fig = make_weekly_card(DUMMY_DATA)
    img = _fig_to_pil(fig)
    w, h = img.size
    assert w == h, f"Expected square image, got {img.size}"
    assert w >= 900, f"Expected at least 900px wide, got {w}"


def test_weekly_card_has_content():
    from instagram.generate import make_weekly_card
    fig = make_weekly_card(DUMMY_DATA)
    img = _fig_to_pil(fig)
    arr = np.array(img)
    assert arr.mean() > 5, "Image appears to be entirely black"


def test_daily_card_size():
    from instagram.generate_status import make_daily_card
    fig = make_daily_card(DUMMY_DATA)
    img = _fig_to_pil(fig)
    w, h = img.size
    assert w == h, f"Expected square image, got {img.size}"
    assert w >= 900, f"Expected at least 900px, got {w}"


def test_daily_card_with_no_trades():
    from instagram.generate_status import make_daily_card
    data = {'account': DUMMY_ACCOUNT, 'openTrades': [], 'dailyGain': []}
    fig = make_daily_card(data)
    img = _fig_to_pil(fig)
    w, h = img.size
    assert w == h, "Expected square image"


def test_pairs_card_eurusd():
    from instagram.generate_edu import make_pairs_post
    content = {
        'pair': 'EURUSD', 'full_name': 'Euro / US Dollar',
        'best_session': 'London+NY 1300-1700 SGT',
        'avg_spread': '0.0-0.2 pips (IC Raw)',
        'volatility': 'Medium - 60-90 pips/day',
        'my_edge': 'Cleanest structure',
        'quote': 'The most liquid instrument on earth.',
    }
    fig = make_pairs_post(content)
    img = _fig_to_pil(fig)
    w, h = img.size
    assert w == h, f"Expected square image, got {img.size}"
    assert w >= 900, f"Expected at least 900px, got {w}"


def test_pairs_card_xauusd():
    from instagram.generate_edu import make_pairs_post
    content = {
        'pair': 'XAUUSD', 'full_name': 'Gold / US Dollar',
        'best_session': 'London+NY overlap',
        'avg_spread': '0.1-0.3 pips (IC Raw)',
        'volatility': 'High - 150-300 pips/day',
        'my_edge': 'Institutional order flow',
        'quote': 'Gold is not random. Learn to read it.',
    }
    fig = make_pairs_post(content)
    img = _fig_to_pil(fig)
    w, h = img.size
    assert w == h, "Expected square image"


def test_setup_card():
    from instagram.generate_edu import make_setup_post
    content = {
        'pair': 'EURUSD', 'direction': 'LONG',
        'setup_type': 'Liquidity Sweep + Reentry',
        'timeframe': 'H4 to M15', 'rr': '1:2.5',
        'steps': [
            ('H4 Bias Confirmed', 'Price above key EMA. Institutional trend bullish.'),
            ('Liquidity Sweep', 'Price dips below H1 swing low, sweeps retail stops.'),
            ('Structure Break', 'M15 breaks the last lower high, confirms reversal.'),
            ('Entry + Risk', 'Long on M15 BOS candle close. SL below sweep. RR 1:2.5.'),
        ],
    }
    fig = make_setup_post(content)
    img = _fig_to_pil(fig)
    w, h = img.size
    assert w == h, f"Expected square image, got {img.size}"
    assert w >= 900, f"Expected at least 900px, got {w}"


def test_trust_card_size():
    from instagram.generate import make_winrate_card
    fig = make_winrate_card(DUMMY_DATA)
    img = _fig_to_pil(fig)
    w, h = img.size
    assert w == h, f"Expected square image, got {img.size}"
    assert w >= 900, f"Expected at least 900px, got {w}"


def test_monthly_chart_size():
    from instagram.generate import make_monthly_chart
    data = {'account': DUMMY_ACCOUNT, 'openTrades': [], 'dailyGain': [
        ['2026-01-15', 2.1, 80], ['2026-02-15', -0.5, -20],
        ['2026-03-15', 3.2, 120], ['2026-04-15', 1.8, 70],
        ['2026-05-15', -1.1, -40], ['2026-06-15', 4.0, 160],
    ]}
    fig = make_monthly_chart(data)
    img = _fig_to_pil(fig)
    w, h = img.size
    assert w == h, f"Expected square image, got {img.size}"
    assert w >= 900


def test_weekly_card_renders_negative_pips_without_error():
    from instagram.generate import make_weekly_card
    data = {**DUMMY_DATA, 'account': {**DUMMY_ACCOUNT, 'pips': -500}}
    fig = make_weekly_card(data)
    img = _fig_to_pil(fig)
    assert img.size[0] == img.size[1]


def test_daily_card_renders_negative_pips_without_error():
    from instagram.generate_status import make_daily_card
    data = {**DUMMY_DATA, 'account': {**DUMMY_ACCOUNT, 'pips': -200}}
    fig = make_daily_card(data)
    img = _fig_to_pil(fig)
    assert img.size[0] == img.size[1]
