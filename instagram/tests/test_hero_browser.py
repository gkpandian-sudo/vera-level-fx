"""TDD tests for instagram/reels/hero_browser.py — Playwright frame-capture bridge."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # repo root
sys.path.insert(0, str(Path(__file__).parent.parent))         # instagram/

import pytest

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------
SAMPLE_DATA = {
    'account': {
        'balance': 24813, 'todayDaily': 2.14, 'daily': 2.14,
        'winRate': 68.5, 'profitFactor': 1.82,
        'pips': 3420, 'trades': 847,
        'gain': 12.4, 'drawdown': 8.3,
    },
    'openTrades': [
        {'symbol': 'XAUUSD', 'action': 'buy', 'profit': 42.50},
        {'symbol': 'EURUSD', 'action': 'sell', 'profit': -12.30},
    ],
    'dailyGain': [
        ['01/01/2026', '0.5', '200'],
        ['01/15/2026', '1.2', '480'],
        ['02/01/2026', '0.8', '320'],
        ['02/15/2026', '2.1', '840'],
        ['03/01/2026', '-0.4', '-160'],
        ['03/15/2026', '3.0', '1200'],
    ],
    'weekly_gain': 2.34,
}


# ---------------------------------------------------------------------------
# test_coerce_data_types
# ---------------------------------------------------------------------------
def test_coerce_data_types():
    from reels.hero_browser import _coerce_data

    result = _coerce_data('trust', SAMPLE_DATA)

    assert isinstance(result['balance'], float), "balance must be float"
    assert isinstance(result['balance_fmt'], str), "balance_fmt must be str"
    assert isinstance(result['today_daily'], float), "today_daily must be float"
    assert isinstance(result['today_daily_sign'], str), "today_daily_sign must be str"
    assert isinstance(result['win_rate'], float), "win_rate must be float"
    assert isinstance(result['profit_factor'], float), "profit_factor must be float"
    assert isinstance(result['pips'], int), "pips must be int"
    assert isinstance(result['trades'], int), "trades must be int"
    assert isinstance(result['gain'], float), "gain must be float"
    assert isinstance(result['gain_sign'], str), "gain_sign must be str"
    assert isinstance(result['drawdown'], float), "drawdown must be float"
    assert isinstance(result['weekly_gain'], float), "weekly_gain must be float"
    assert isinstance(result['weekly_gain_sign'], str), "weekly_gain_sign must be str"
    assert isinstance(result['open_pairs'], list), "open_pairs must be list"
    assert isinstance(result['open_pairs_str'], str), "open_pairs_str must be str"
    assert isinstance(result['sparkline_points'], list), "sparkline_points must be list"
    assert isinstance(result['monthly_items'], list), "monthly_items must be list"
    assert isinstance(result['month_name'], str), "month_name must be str"
    assert isinstance(result['this_month'], float), "this_month must be float"
    assert isinstance(result['this_month_sign'], str), "this_month_sign must be str"

    # Spot-check values
    assert result['balance'] == 24813.0
    assert result['balance_fmt'] == '$24,813'
    assert result['win_rate'] == 68.5
    assert result['pips'] == 3420
    assert result['trades'] == 847
    assert result['open_pairs'] == ['XAUUSD', 'EURUSD']
    assert result['open_pairs_str'] == 'XAUUSD · EURUSD'
    assert result['today_daily_sign'] == '+'  # 2.14 >= 0


# ---------------------------------------------------------------------------
# test_coerce_data_weekly_gain_fallback
# ---------------------------------------------------------------------------
def test_coerce_data_weekly_gain_fallback():
    from reels.hero_browser import _coerce_data

    data_no_weekly = {
        'account': {
            'balance': 10000, 'gain': 5.5, 'drawdown': 3.0,
            'winRate': 60.0, 'profitFactor': 1.5,
            'pips': 100, 'trades': 50,
            'todayDaily': -0.5, 'daily': -0.5,
        },
        'openTrades': [],
        'dailyGain': [],
    }
    # No 'weekly_gain' key — should fall back to gain
    result = _coerce_data('weekly', data_no_weekly)
    assert result['weekly_gain'] == 5.5
    assert result['weekly_gain_sign'] == '+'  # 5.5 >= 0

    # Negative today_daily sign
    assert result['today_daily'] == -0.5
    assert result['today_daily_sign'] == ''  # negative, no sign prefix


# ---------------------------------------------------------------------------
# test_coerce_data_monthly_items
# ---------------------------------------------------------------------------
def test_coerce_data_monthly_items():
    from reels.hero_browser import _coerce_data

    result = _coerce_data('monthly', SAMPLE_DATA)
    items = result['monthly_items']

    assert isinstance(items, list), "monthly_items must be a list"
    assert len(items) <= 6, "monthly_items must have at most 6 items"
    assert len(items) > 0, "monthly_items must not be empty for valid dailyGain"

    for item in items:
        assert isinstance(item, list), "each monthly_item must be a list pair"
        assert len(item) == 2, "each monthly_item must be [str, float]"
        month_str, val = item
        assert isinstance(month_str, str), f"month label must be str, got {type(month_str)}"
        assert isinstance(val, float), f"monthly value must be float, got {type(val)}"

    # this_month should match last item
    assert result['this_month'] == items[-1][1]


# ---------------------------------------------------------------------------
# test_coerce_data_trust_fallback
# ---------------------------------------------------------------------------
def test_coerce_data_trust_fallback():
    from reels.hero_browser import _coerce_data

    data_minimal = {
        'account': {
            'balance': 5000, 'winRate': 0, 'profitFactor': 0,
            'pips': 0, 'trades': 0, 'gain': 0, 'drawdown': 0,
            'todayDaily': 0, 'daily': 0,
        },
        'openTrades': [],
        'dailyGain': [],  # empty → flat-line sparkline
    }

    result = _coerce_data('trust', data_minimal)

    # Flat-line sparkline when < 2 values
    sp = result['sparkline_points']
    assert sp == [[0.0, 0.5], [1.0, 0.5]], (
        f"Expected flat-line sparkline [[0.0, 0.5], [1.0, 0.5]], got {sp}"
    )

    # open_pairs_str fallback
    assert result['open_pairs_str'] == 'No open positions'
    assert result['open_pairs'] == []

    # this_month fallback when no dailyGain
    assert result['this_month'] == 0.0


# ---------------------------------------------------------------------------
# test_build_hero_html_creates_file
# ---------------------------------------------------------------------------
def test_build_hero_html_creates_file():
    """Skips if vendor files or template are missing; verifies no markers remain."""
    vendor_dir = Path(__file__).parent.parent / 'reels' / 'templates' / 'vendor'
    anime_js = vendor_dir / 'anime.min.js'
    roboto_black = vendor_dir / 'Roboto-Black.woff2'

    if not vendor_dir.exists() or not anime_js.exists() or not roboto_black.exists():
        pytest.skip("Vendor assets not present — skipping HTML build test")

    template_path = Path(__file__).parent.parent / 'reels' / 'templates' / 'hero_trust.html'
    if not template_path.exists():
        pytest.skip("hero_trust.html template not yet created (Task 3-6 will add it)")

    from reels.hero_browser import build_hero_html

    out_path = build_hero_html('trust', SAMPLE_DATA, duration=6.0)

    assert out_path.exists(), f"Expected output HTML at {out_path}"
    content = out_path.read_text(encoding='utf-8')

    for marker in ('__ANIME_JS__', '__FONTS_CSS__', '__DATA_JSON__', '__DURATION_MS__'):
        assert marker not in content, f"Marker {marker!r} was not substituted in output HTML"
