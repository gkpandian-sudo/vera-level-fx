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
from urllib.parse import unquote

EMAIL    = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('MYFX_EMAIL', '')
PASSWORD = sys.argv[2] if len(sys.argv) > 2 else os.environ.get('MYFX_PASSWORD', '')

MYFX_ID  = 12044019           # Vera Level account ID
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

    print("Logging in to Myfxbook ...")
    login   = api('login.json', {'email': EMAIL, 'password': PASSWORD})
    session = unquote(login['session'])   # decode %2B → + etc. so params aren't double-encoded
    print(f"  session: {session[:10]}…")

    # ── Account info ──────────────────────────────────────────────
    print("Fetching account info ...")
    accts = api('get-my-accounts.json', {'session': session}).get('accounts', [])
    acct  = next((a for a in accts if a['id'] == MYFX_ID), accts[0] if accts else {})
    if not acct:
        sys.exit("No account found — check MYFX_ID")
    print(f"  account: {acct.get('name')} (id={acct.get('id')}) gain={acct.get('gain')}%")

    # ── Daily gain curve ─────────────────────────────────────────
    end = date.today().strftime('%Y-%m-%d')
    print(f"Fetching daily gain ({START} to {end}) ...")
    raw_daily = api('get-daily-gain.json', {
        'session': session, 'id': MYFX_ID,
        'start': START, 'end': end,
    }).get('dailyGain', [])
    # Each entry is [{date, value, profit}] — value = cumulative % gain, profit = daily $ profit
    daily_gain = []
    for entry in raw_daily:
        e = entry[0] if isinstance(entry, list) else entry
        if isinstance(e, dict):
            daily_gain.append([e['date'], e.get('value', 0), e.get('profit', 0)])
        else:
            daily_gain.append(e)
    print(f"  {len(daily_gain)} daily data points")

    # ── Open trades ───────────────────────────────────────────────
    print("Fetching open trades ...")
    open_trades = api('get-open-trades.json', {
        'session': session, 'id': MYFX_ID
    }).get('openTrades', [])
    print(f"  {len(open_trades)} open positions")

    # ── Full trade history ────────────────────────────────────────
    # Pass start/end to fetch full history (not just the default 40-entry cap)
    print("Fetching full trade history ...")
    history = api('get-history.json', {
        'session': session, 'id': MYFX_ID,
        'start': START, 'end': end,
    }).get('history', [])
    print(f"  {len(history)} history entries")

    # ── Logout ────────────────────────────────────────────────────
    try:
        api('logout.json', {'session': session})
        print("Logged out")
    except Exception:
        pass

    # ── Reconcile trades count and winRate ─────────────────────────
    # Myfxbook get-my-accounts returns trades=0 / winRate=0 intermittently.
    # We persist the highest confirmed values in data/known-trades.json so the
    # daily snapshot always reflects the growing trade count even when the API
    # blanks out. The file is committed by fetch-snapshot.yml alongside the snapshot.
    KNOWN_FILE   = Path(__file__).parent / 'data' / 'known-trades.json'
    known        = json.loads(KNOWN_FILE.read_text()) if KNOWN_FILE.exists() else {}
    KNOWN_TRADES = int(known.get('trades', 0))
    KNOWN_WR     = float(known.get('winRate', 0))

    api_trades = int(acct.get('trades') or 0)
    api_wr     = float(acct.get('winRate') or 0)

    if history:
        closed         = [t for t in history if t.get('profit') is not None]
        winners        = [t for t in closed if float(t.get('profit', 0)) > 0]
        history_trades = len(closed)
        history_wr     = round(100 * len(winners) / len(closed), 1) if closed else 0
    else:
        history_trades = 0
        history_wr     = 0

    best_trades = max(api_trades, history_trades, KNOWN_TRADES)
    best_wr     = api_wr if api_wr else (history_wr if history_wr else KNOWN_WR)
    acct['trades']  = best_trades
    acct['winRate'] = best_wr

    print(f"  Trades: API={api_trades}, history={history_trades}, known={KNOWN_TRADES} → stored={best_trades}")
    print(f"  WinRate: API={api_wr}%, history={history_wr}%, known={KNOWN_WR}% → stored={best_wr}%")

    # Persist if we learned a higher count (auto-bumps the floor for future runs)
    if best_trades > KNOWN_TRADES or best_wr > KNOWN_WR:
        KNOWN_FILE.write_text(json.dumps({
            'trades':   best_trades,
            'winRate':  best_wr,
            'updatedAt': date.today().strftime('%Y-%m-%d'),
        }, indent=2) + '\n')
        print(f"  known-trades.json updated: {best_trades} trades, {best_wr}% WR")

    # ── Save snapshot ─────────────────────────────────────────────
    snapshot = {
        'fetchedAt':  datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'account':    acct,
        'openTrades': open_trades,
        'history':    history,
        'dailyGain':  daily_gain,
    }
    OUT.write_text(json.dumps(snapshot, indent=2))
    print(f"\nSaved: {OUT}")
    print(f"  Gain       : {acct.get('gain')}%")
    print(f"  History    : {len(history)} trades")
    print(f"  Daily pts  : {len(daily_gain)}")
    print(f"  Open trades: {len(open_trades)}")


if __name__ == '__main__':
    main()
