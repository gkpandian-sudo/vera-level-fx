#!/usr/bin/env python3
"""
Fetch fresh Myfxbook data → data/vera-snapshot.json

Usage:
  python fetch_snapshot.py EMAIL PASSWORD
  or set env vars:  MYFX_EMAIL  MYFX_PASSWORD
"""
import json, os, sys, requests
from datetime import date, datetime
from pathlib import Path

EMAIL    = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('MYFX_EMAIL', '')
PASSWORD = sys.argv[2] if len(sys.argv) > 2 else os.environ.get('MYFX_PASSWORD', '')

MYFX_ID  = 12027369           # Myfxbook account ID (from existing snapshot)
START    = '2026-01-01'       # fetch daily gain from this date
OUT      = Path(__file__).parent / 'data' / 'vera-snapshot.json'
BASE     = 'https://www.myfxbook.com/api'


def api(path, params):
    r = requests.get(f'{BASE}/{path}', params=params, timeout=30)
    r.raise_for_status()
    d = r.json()
    if d.get('error'):
        raise RuntimeError(f"Myfxbook API: {d.get('message', path)}")
    return d


def main():
    if not EMAIL or not PASSWORD:
        sys.exit("Usage: python fetch_snapshot.py EMAIL PASSWORD\n"
                 "  or set MYFX_EMAIL and MYFX_PASSWORD environment variables")

    print("Logging in to Myfxbook …")
    login   = api('login.json', {'email': EMAIL, 'password': PASSWORD})
    session = login['session']
    print(f"  session: {session[:10]}…")

    # ── Account info ──────────────────────────────────────────────
    print("Fetching account info …")
    accts = api('get-my-accounts.json', {'session': session}).get('accounts', [])
    acct  = next((a for a in accts if a['id'] == MYFX_ID), accts[0] if accts else {})
    if not acct:
        sys.exit("No account found — check MYFX_ID")
    print(f"  account: {acct.get('name')} (id={acct.get('id')}) gain={acct.get('gain')}%")

    # ── Daily gain curve ─────────────────────────────────────────
    end = date.today().strftime('%Y-%m-%d')
    print(f"Fetching daily gain ({START} → {end}) …")
    raw_daily = api('get-data-daily.json', {
        'session': session, 'id': MYFX_ID,
        'start': START, 'end': end,
    }).get('dataDaily', [])
    # Myfxbook returns {date, value, profit} per day; value = cumulative % gain
    if raw_daily and isinstance(raw_daily[0], dict):
        daily_gain = [[d['date'], d['value']] for d in raw_daily]
    else:
        # Already [[date, value], ...] format
        daily_gain = raw_daily
    print(f"  {len(daily_gain)} daily data points")

    # ── Open trades ───────────────────────────────────────────────
    print("Fetching open trades …")
    open_trades = api('get-open-trades.json', {
        'session': session, 'id': MYFX_ID
    }).get('openTrades', [])
    print(f"  {len(open_trades)} open positions")

    # ── Full trade history ────────────────────────────────────────
    print("Fetching full trade history …")
    history = api('get-history.json', {
        'session': session, 'id': MYFX_ID
    }).get('history', [])
    print(f"  {len(history)} history entries")

    # ── Logout ────────────────────────────────────────────────────
    try:
        api('logout.json', {'session': session})
        print("Logged out")
    except Exception:
        pass

    # ── Save snapshot ─────────────────────────────────────────────
    snapshot = {
        'fetchedAt':  datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'account':    acct,
        'openTrades': open_trades,
        'history':    history,
        'dailyGain':  daily_gain,
    }
    OUT.write_text(json.dumps(snapshot, indent=2))
    print(f"\nSaved → {OUT}")
    print(f"  Gain       : {acct.get('gain')}%")
    print(f"  History    : {len(history)} trades")
    print(f"  Daily pts  : {len(daily_gain)}")
    print(f"  Open trades: {len(open_trades)}")
