import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import datetime
import numpy as np
import pandas as pd


# ── Symbol mapping ────────────────────────────────────────────────────────────

def test_symbol_map_known():
    from reels.chart import yf_ticker
    assert yf_ticker('XAUUSD') == 'XAUUSD=X'
    assert yf_ticker('EURUSD') == 'EURUSD=X'
    assert yf_ticker('AUDCAD') == 'AUDCAD=X'


def test_symbol_map_unknown_passthrough():
    from reels.chart import yf_ticker
    assert yf_ticker('WEIRD') == 'WEIRD'


# ── auto_interval ─────────────────────────────────────────────────────────────

def test_auto_interval_short_trade_recent():
    from reels.chart import auto_interval
    now = datetime.datetime.utcnow()
    open_dt  = now - datetime.timedelta(hours=3)
    close_dt = now - datetime.timedelta(hours=1)
    assert auto_interval(open_dt, close_dt) == '5m'


def test_auto_interval_intraday_recent():
    from reels.chart import auto_interval
    now = datetime.datetime.utcnow()
    open_dt  = now - datetime.timedelta(hours=12)
    close_dt = now - datetime.timedelta(hours=4)
    assert auto_interval(open_dt, close_dt) == '15m'


def test_auto_interval_multiday_recent():
    from reels.chart import auto_interval
    now = datetime.datetime.utcnow()
    open_dt  = now - datetime.timedelta(hours=50)   # 36h trade → '1h'
    close_dt = now - datetime.timedelta(hours=14)
    assert auto_interval(open_dt, close_dt) == '1h'


def test_auto_interval_old_trade_forces_1h():
    from reels.chart import auto_interval
    now = datetime.datetime.utcnow()
    open_dt  = now - datetime.timedelta(days=58)
    close_dt = now - datetime.timedelta(days=57)
    assert auto_interval(open_dt, close_dt) == '1h'


# ── synthetic_ohlc ────────────────────────────────────────────────────────────

def test_synthetic_ohlc_shape():
    from reels.chart import synthetic_ohlc
    df = synthetic_ohlc([], n_candles=40)
    assert len(df) == 40
    assert set(['Open', 'High', 'Low', 'Close']).issubset(df.columns)


def test_synthetic_ohlc_anchored_to_open_price():
    from reels.chart import synthetic_ohlc
    trades = [{'openPrice': 2000.0, 'closePrice': 2050.0}]
    df = synthetic_ohlc(trades, n_candles=20)
    assert abs(df['Open'].iloc[0] - 2000.0) < 30.0


def test_synthetic_ohlc_high_gte_low():
    from reels.chart import synthetic_ohlc
    df = synthetic_ohlc([{'openPrice': 1.1000, 'closePrice': 1.1050}], n_candles=30)
    assert (df['High'] >= df['Low']).all()


def test_synthetic_ohlc_high_gte_open_and_close():
    from reels.chart import synthetic_ohlc
    df = synthetic_ohlc([{'openPrice': 3000.0, 'closePrice': 2980.0}], n_candles=20)
    assert (df['High'] >= df['Open']).all()
    assert (df['High'] >= df['Close']).all()


def test_synthetic_ohlc_low_lte_open_and_close():
    from reels.chart import synthetic_ohlc
    df = synthetic_ohlc([{'openPrice': 3000.0, 'closePrice': 2980.0}], n_candles=20)
    assert (df['Low'] <= df['Open']).all()
    assert (df['Low'] <= df['Close']).all()


# ── get_ohlc ──────────────────────────────────────────────────────────────────

def test_get_ohlc_empty_history_returns_df():
    from reels.chart import get_ohlc
    df = get_ohlc([])
    assert not df.empty
    assert 'Open' in df.columns


def test_get_ohlc_returns_dataframe_type():
    from reels.chart import get_ohlc
    df = get_ohlc([])
    assert isinstance(df, pd.DataFrame)


# ── fetch_ohlc ────────────────────────────────────────────────────────────────

from unittest.mock import patch, MagicMock


def _make_mock_df(n=20):
    return pd.DataFrame({
        'Open':   [2000.0 + i for i in range(n)],
        'High':   [2001.5 + i for i in range(n)],
        'Low':    [1999.0 + i for i in range(n)],
        'Close':  [2000.8 + i for i in range(n)],
        'Volume': [1000] * n,
    }, index=pd.date_range('2026-07-20', periods=n, freq='5min'))


def test_fetch_ohlc_success_returns_four_column_df():
    from reels.chart import fetch_ohlc
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = _make_mock_df(20)
    with patch('yfinance.Ticker', return_value=mock_ticker):
        result = fetch_ohlc(
            'XAUUSD',
            datetime.datetime(2026, 7, 20, 0, 0),
            datetime.datetime(2026, 7, 20, 2, 0),
            '5m',
        )
    assert not result.empty
    assert set(['Open', 'High', 'Low', 'Close']).issubset(result.columns)
    assert 'Volume' not in result.columns


def test_fetch_ohlc_network_error_returns_empty_df():
    from reels.chart import fetch_ohlc
    with patch('yfinance.Ticker', side_effect=Exception('network error')):
        result = fetch_ohlc(
            'XAUUSD',
            datetime.datetime(2026, 7, 20, 0, 0),
            datetime.datetime(2026, 7, 20, 2, 0),
            '5m',
        )
    assert result.empty


def test_fetch_ohlc_insufficient_candles_returns_empty():
    from reels.chart import fetch_ohlc
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = _make_mock_df(5)   # < 10 rows → reject
    with patch('yfinance.Ticker', return_value=mock_ticker):
        result = fetch_ohlc(
            'XAUUSD',
            datetime.datetime(2026, 7, 20, 0, 0),
            datetime.datetime(2026, 7, 20, 2, 0),
            '5m',
        )
    assert result.empty


def test_fetch_ohlc_empty_response_returns_empty():
    from reels.chart import fetch_ohlc
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = pd.DataFrame()
    with patch('yfinance.Ticker', return_value=mock_ticker):
        result = fetch_ohlc(
            'XAUUSD',
            datetime.datetime(2026, 7, 20, 0, 0),
            datetime.datetime(2026, 7, 20, 2, 0),
            '5m',
        )
    assert result.empty
