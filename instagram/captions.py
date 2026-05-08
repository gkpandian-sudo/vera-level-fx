from datetime import datetime

TAGS = (
    "#forex #forextrader #forextrading #algotrading #algorithmic "
    "#icmarkets #myfxbook #xauusd #gold #forexsignals "
    "#tradingstrategy #singapore #investingsingapore "
    "#financialfreedom #wealthbuilding #veralevelFX "
    "#forexlifestyle #passiveincome #tradingresults"
)


def weekly(account: dict) -> str:
    bal   = account.get('balance', 0)
    gain  = account.get('gain', 0)
    mo    = account.get('monthly', 0)
    wr    = account.get('winRate', 0)
    pf    = account.get('profitFactor', 0)
    pips  = int(account.get('pips', 0))
    date  = datetime.now().strftime('%d %b %Y')

    return f"""📊 Weekly Performance Update — {date}

💰 Balance: ${bal:,.2f}
📈 Total Gain: +{gain:.2f}% since inception
📅 Monthly Avg: +{mo:.2f}%
🎯 Win Rate: {wr:.0f}%
⚡ Profit Factor: {pf:.2f}
💹 Total Pips: +{pips:,}

Fully automated algorithmic trading on IC Markets.
Every trade live-verified on Myfxbook — zero manipulation.

🔗 Live stats: veralevel-fx.github.io
📩 DM to connect

{TAGS}"""


def monthly(account: dict, monthly_pnl: dict) -> str:
    last_months = list(monthly_pnl.items())[-6:]
    lines = '  '.join(
        f"{'🟢' if v >= 0 else '🔴'} {k}: {v:+.1f}%"
        for k, v in last_months
    )
    gain = account.get('gain', 0)

    return f"""📅 Monthly P&L Breakdown — {datetime.now().strftime('%B %Y')}

{lines}

📈 Total Gain to date: +{gain:.2f}%

Systematic execution. No emotions. No manual overrides.
IC Markets raw spreads — ASIC regulated.

🔗 Full chart: veralevel-fx.github.io

{TAGS}"""


def trust(account: dict) -> str:
    wr    = account.get('winRate', 0)
    pf    = account.get('profitFactor', 0)
    gain  = account.get('gain', 0)
    trades = int(account.get('trades', 0))
    pips  = int(account.get('pips', 0))

    return f"""✅ Live Track Record — Vera Level FX

🎯 Win Rate: {wr:.0f}% across {trades:,} trades
⚡ Profit Factor: {pf:.2f}
📈 Total Gain: +{gain:.2f}%
💹 Pips: +{pips:,}

This is a LIVE account on IC Markets.
Not a demo. Not backtested. Publicly audited on Myfxbook.

Every entry. Every exit. Every result — visible to anyone.

🔗 Verify yourself: veralevel-fx.github.io
📩 DM for details

{TAGS}"""
