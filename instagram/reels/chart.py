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

    if age_days > 55:     return '1h'   # 5m/15m unavailable beyond ~60 days in yf
    if duration_h <= 4:   return '5m'
    if duration_h <= 24:  return '15m'
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
    """
    Fetch OHLC via yfinance. Returns DataFrame[Open, High, Low, Close] on success,
    empty DataFrame on any failure or if fewer than 10 candles returned.
    """
    try:
        import yfinance as yf
        ticker = yf.Ticker(yf_ticker(symbol))
        df = ticker.history(
            start=start_dt.strftime('%Y-%m-%d'),
            end=(end_dt + timedelta(days=1)).strftime('%Y-%m-%d'),
            interval=interval,
            auto_adjust=True,
        )
        if df.empty or len(df) < 10:
            return pd.DataFrame()

        # Normalise index to timezone-naive UTC
        df.index = pd.to_datetime(df.index)
        if hasattr(df.index, 'tz') and df.index.tz is not None:
            df.index = df.index.tz_convert('UTC').tz_localize(None)

        # Trim to requested window
        df = df[
            (df.index >= pd.Timestamp(start_dt)) &
            (df.index <= pd.Timestamp(end_dt))
        ]
        if len(df) < 10:
            return pd.DataFrame()

        return df[['Open', 'High', 'Low', 'Close']]
    except Exception as exc:
        logger.debug('fetch_ohlc failed for %s: %s', symbol, exc)
        return pd.DataFrame()


def _draw_up_arrow(draw: ImageDraw.Draw, cx: int, tip_y: int, size: int = 14) -> None:
    """Filled upward triangle — EMERALD entry marker."""
    half = size // 2
    draw.polygon([(cx, tip_y), (cx - half, tip_y + size), (cx + half, tip_y + size)],
                 fill=EMERALD)


def _draw_x_marker(draw: ImageDraw.Draw, cx: int, cy: int, size: int = 10) -> None:
    """Amber × cross — exit marker."""
    h = size // 2
    draw.line([(cx - h, cy - h), (cx + h, cy + h)], fill=AMBER, width=2)
    draw.line([(cx + h, cy - h), (cx - h, cy + h)], fill=AMBER, width=2)


def draw_chart_frame(
    img: Image.Image,
    ohlc_df: pd.DataFrame,
    trades: list,
    t: float,
    duration: float,
    rect: tuple,
) -> Image.Image:
    """
    Draw an animated candlestick chart onto img at time t.

    Candles reveal left→right over 0..duration using ease_out.
    Entry arrows (EMERALD ▲) and exit markers (AMBER ×) appear when
    the animation reaches each trade's bar.
    Returns the modified PIL Image (never raises).
    """
    if ohlc_df.empty:
        return img

    x0, y0, x1, y1 = rect
    chart_w = x1 - x0
    chart_h = y1 - y0

    n_total   = len(ohlc_df)
    progress  = _ease_out(t, duration)
    n_visible = int(n_total * progress)

    if n_visible == 0:
        return img

    visible_df = ohlc_df.iloc[:n_visible]
    p_min = float(visible_df['Low'].min())
    p_max = float(visible_df['High'].max())
    p_range = p_max - p_min
    if p_range == 0.0:
        p_range = max(p_min * 0.01, 0.001)
    pad     = p_range * 0.05
    p_min  -= pad
    p_max  += pad
    p_range = p_max - p_min

    def price_to_y(price: float) -> int:
        return int(y1 - (price - p_min) / p_range * chart_h)

    spacing  = chart_w / n_total
    candle_w = max(2, int(spacing * 0.7))

    draw = ImageDraw.Draw(img)
    font = _load_font(18)

    # Y-axis grid — 4 dashed horizontal lines with price labels
    grid_color = (60, 80, 100)
    for i in range(1, 5):
        gy    = int(y0 + chart_h * i / 5)
        gp    = p_max - p_range * i / 5
        label = f'{gp:.0f}' if gp >= 100 else f'{gp:.4f}'
        for gx in range(x0, x1, 14):
            draw.line([(gx, gy), (min(gx + 7, x1), gy)], fill=grid_color, width=1)
        draw.text((x0 + 4, gy - 20), label, fill=grid_color, font=font)

    # Candle bodies and wicks
    for i in range(n_visible):
        row  = ohlc_df.iloc[i]
        cx   = int(x0 + i * spacing + spacing / 2)
        op_y = price_to_y(float(row['Open']))
        cl_y = price_to_y(float(row['Close']))
        hi_y = price_to_y(float(row['High']))
        lo_y = price_to_y(float(row['Low']))

        is_bull    = float(row['Close']) >= float(row['Open'])
        body_color = EMERALD if is_bull else RED
        wick_color = (80, 100, 120)

        draw.line([(cx, hi_y), (cx, lo_y)], fill=wick_color, width=1)

        body_top = min(op_y, cl_y)
        body_bot = max(op_y, cl_y)
        if body_bot - body_top < 1:
            body_bot = body_top + 1
        draw.rectangle(
            [cx - candle_w // 2, body_top, cx + candle_w // 2, body_bot],
            fill=body_color,
        )

    # Entry/exit arrows for each trade
    timestamps = ohlc_df.index.tolist()

    for tr in trades:
        entry_dt = _parse_time(tr.get('openTime',  ''))
        exit_dt  = _parse_time(tr.get('closeTime', ''))

        entry_ts = pd.Timestamp(entry_dt)
        exit_ts  = pd.Timestamp(exit_dt)

        dists_entry = [abs((ts - entry_ts).total_seconds()) for ts in timestamps]
        dists_exit  = [abs((ts - exit_ts).total_seconds())  for ts in timestamps]
        entry_idx   = int(np.argmin(dists_entry))
        exit_idx    = int(np.argmin(dists_exit))

        if entry_idx < n_visible:
            ex = int(x0 + entry_idx * spacing + spacing / 2)
            ey = price_to_y(float(ohlc_df.iloc[entry_idx]['Low'])) + 16
            _draw_up_arrow(draw, ex, ey)

        if exit_idx < n_visible:
            ex2 = int(x0 + exit_idx * spacing + spacing / 2)
            ey2 = price_to_y(float(ohlc_df.iloc[exit_idx]['High'])) - 22
            _draw_x_marker(draw, ex2, ey2)

    return img
