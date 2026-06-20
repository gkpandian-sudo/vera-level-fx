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
