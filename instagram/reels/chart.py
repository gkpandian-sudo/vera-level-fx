# instagram/reels/chart.py
from __future__ import annotations
import logging
from collections import Counter
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Colours (duplicated intentionally — no cross-dependency on animator.py) ───
EMERALD = (5,   150, 105)
RED     = (239, 68,  68)
MUTED   = (107, 114, 128)
AMBER   = (245, 158, 11)
WHITE   = (255, 255, 255)

# ── Symbol mapping ─────────────────────────────────────────────────────────────
SYMBOL_MAP: dict[str, str] = {
    'XAUUSD': 'XAUUSD=X',
    'EURUSD': 'EURUSD=X',
    'AUDCAD': 'AUDCAD=X',
    'USDJPY': 'USDJPY=X',
    'GBPUSD': 'GBPUSD=X',
    'USDCAD': 'USDCAD=X',
    'AUDUSD': 'AUDUSD=X',
}


def yf_ticker(myfxbook_symbol: str) -> str:
    """Map Myfxbook symbol to yfinance ticker. Passes through unknown symbols."""
    return SYMBOL_MAP.get(myfxbook_symbol, myfxbook_symbol)


def auto_interval(open_dt: datetime, close_dt: datetime) -> str:
    """Pick the yfinance candle interval that best fits trade age and duration."""
    age_days   = (datetime.utcnow() - close_dt).days
    duration_h = (close_dt - open_dt).total_seconds() / 3600

    if age_days > 55:    return '1h'   # 5m/15m unavailable beyond ~60 days in yf
    if duration_h < 4:   return '5m'
    if duration_h < 24:  return '15m'
    return '1h'


def _ease_out(t: float, dur: float) -> float:
    if dur <= 0:
        return 1.0
    x = min(t / dur, 1.0)
    return 1 - (1 - x) ** 3


def _parse_time(s: str) -> datetime:
    for fmt in ('%m/%d/%Y %H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return datetime.utcnow()


def _load_font(size: int = 14) -> ImageFont.FreeTypeFont:
    font_dir = Path(__file__).parent.parent / 'assets' / 'fonts'
    for path in [
        str(font_dir / 'Roboto-Regular.ttf'),
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/dejavu/DejaVuSans.ttf',
    ]:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            pass
    return ImageFont.load_default()


def synthetic_ohlc(trades: list, n_candles: int = 80) -> pd.DataFrame:
    """
    Numpy random walk anchored to trades[0].openPrice → trades[-1].closePrice.
    Wicks sized at 30–80% of body. Deterministic seed 42.
    """
    if not trades:
        start_price, end_price = 1000.0, 1000.0
    else:
        start_price = float(trades[0].get('openPrice',  1000.0))
        end_price   = float(trades[-1].get('closePrice', start_price))

    rng = np.random.default_rng(42)
    drift  = np.linspace(0, end_price - start_price, n_candles)
    noise  = rng.normal(0, max(abs(end_price - start_price) * 0.015, 0.001), n_candles)
    closes = start_price + drift + noise.cumsum()

    opens      = np.roll(closes, 1)
    opens[0]   = closes[0]
    body_sizes = np.abs(closes - opens)

    rng2     = np.random.default_rng(7)
    wick_pct = rng2.uniform(0.3, 0.8, n_candles)
    highs    = np.maximum(opens, closes) + body_sizes * wick_pct
    lows     = np.minimum(opens, closes) - body_sizes * wick_pct

    now = datetime.utcnow()
    idx = pd.date_range(end=now, periods=n_candles, freq='5min')
    return pd.DataFrame({'Open': opens, 'High': highs, 'Low': lows, 'Close': closes}, index=idx)


def get_ohlc(trades: list) -> pd.DataFrame:
    """
    Fetch real OHLC for the dominant symbol; fall back to synthetic.
    Always returns a non-empty DataFrame with Open/High/Low/Close columns.
    """
    if not trades:
        return synthetic_ohlc([])

    symbol = Counter(tr.get('symbol', '') for tr in trades).most_common(1)[0][0]

    open_dts  = [_parse_time(tr.get('openTime',  '')) for tr in trades]
    close_dts = [_parse_time(tr.get('closeTime', '')) for tr in trades]
    min_open  = min(open_dts)
    max_close = max(close_dts)
    interval  = auto_interval(min_open, max_close)

    start_dt = min_open  - timedelta(minutes=5)
    end_dt   = max_close + timedelta(hours=2)

    df = fetch_ohlc(symbol, start_dt, end_dt, interval)
    return df if not df.empty else synthetic_ohlc(trades)


def fetch_ohlc(symbol: str, start_dt: datetime, end_dt: datetime, interval: str) -> pd.DataFrame:
    """Stub — implemented in Task 2."""
    return pd.DataFrame()


def draw_chart_frame(img: Image.Image, ohlc_df: pd.DataFrame, trades: list,
                     t: float, duration: float, rect: tuple) -> Image.Image:
    """Stub — implemented in Task 3."""
    return img
