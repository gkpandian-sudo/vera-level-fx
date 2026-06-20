import os
from datetime import datetime

TAGS = (
    "#forex #forextrader #forextrading #algotrading #algorithmic "
    "#icmarkets #myfxbook #xauusd #gold #forexsignals "
    "#tradingstrategy #singapore #investingsingapore "
    "#financialfreedom #wealthbuilding #veralevelFX "
    "#indiaforex #forexindia #indiantrader #goldtrading "
    "#forexlifestyle #passiveincome #tradingresults"
)

_TELEGRAM = os.environ.get('BRAND_TELEGRAM', 't.me/pandiangk')
_WEBSITE  = os.environ.get('BRAND_WEBSITE', 'vera-level-forex.vercel.app')
_IB_URL   = os.environ.get('BRAND_IB_URL', 'icmarkets.com/?camp=91936')

_CTA = (
    f"\n\n📲 Live trade alerts → {_TELEGRAM}"
    f"\n🏦 Open IC Markets account → {_IB_URL}"
    f"\n🌐 Live results → {_WEBSITE}"
)


def weekly(account: dict) -> str:
    bal    = account.get('balance', 0)
    gain   = account.get('gain', 0)
    wr     = account.get('winRate', 0)
    pf     = account.get('profitFactor', 0)
    pips   = int(account.get('pips', 0))
    trades = int(account.get('trades', 0))
    date   = datetime.now().strftime('%d %b %Y')
    sign   = '+' if gain >= 0 else ''

    return f"""📊 Weekly Performance — {date}

{sign}{gain:.1f}% total gain. {trades:,} trades. {wr:.0f}% win rate.
Every single one verified on Myfxbook. Nothing hidden.

This is a live IC Markets account — not a demo, not a backtest.
ASIC regulated. Same oversight as Australian financial institutions.

If you want to trade forex with a broker that actually gives you the edge:
🏦 {_IB_URL}

💰 Balance: ${bal:,.0f}
🎯 Win Rate: {wr:.0f}% across {trades:,} trades
⚡ Profit Factor: {pf:.2f}
💹 Total Pips: +{pips:,}

IC Markets is open for traders in India. Raw ECN spreads.
Same account I trade every day.
{_CTA}

{TAGS}"""


def monthly(account: dict, monthly_pnl: dict) -> str:
    last_months = list(monthly_pnl.items())[-6:]
    lines = '\n'.join(
        f"{'🟢' if v >= 0 else '🔴'} {k}: {v:+.1f}%"
        for k, v in last_months
    )
    gain = account.get('gain', 0)
    sign = '+' if gain >= 0 else ''

    return f"""📅 Monthly P&L — {datetime.now().strftime('%B %Y')}

Full breakdown above. Every trade visible on Myfxbook.

{lines}

{sign}{gain:.1f}% total since inception.

This is what consistent algorithmic trading looks like.
No emotional decisions. No manual overrides. No hiding losses.

IC Markets is open for Indian traders — raw ECN, ASIC regulated:
🏦 {_IB_URL}
{_CTA}

{TAGS}"""


def edu(edu_type: str, content: dict) -> str:
    base_tags = (
        "#forex #forextrader #forexeducation #icmarkets #xauusd "
        "#veralevelFX #tradingstrategy #priceaction #forexindia "
        "#indiantrader #goldtrading #algotrading"
    )
    cta = _CTA

    if edu_type == 'risk':
        return (
            f"⚠️ Risk Rule #{content['rule_num']} — {content['title']}\n\n"
            f"{content['body']}\n\n"
            f"Example: ${content['example_account']:,} account → "
            f"max ${content['example_risk']:,} at risk per trade.\n"
            f"At {content['example_rr']} — that is how professionals protect capital.\n\n"
            f"Save this post. Refer to it before your next trade.\n"
            f"I use this rule on every position in my live IC Markets account."
            f"{cta}\n\n{base_tags}"
        )

    if edu_type == 'pairs':
        return (
            f"📊 Pair Spotlight — {content['pair']} ({content['full_name']})\n\n"
            f"Best session: {content['best_session']}\n"
            f"Avg spread on IC Markets Raw: {content['avg_spread']}\n"
            f"Daily volatility: {content['volatility']}\n"
            f"Why I trade it: {content['my_edge']}\n\n"
            f'"{content["quote"]}"\n\n'
            f"If you are trading {content['pair']} with high spreads, "
            f"you are giving away your edge before the trade starts.\n"
            f"IC Markets Raw gives you the tightest spreads available.\n"
            f"Available for Indian traders: {_IB_URL}"
            f"{cta}\n\n{base_tags}"
        )

    # setup
    steps_text = '\n'.join(
        f"{i+1}. {title} — {desc}"
        for i, (title, desc) in enumerate(content['steps'])
    )
    return (
        f"📈 Setup Breakdown — {content['pair']} {content['direction']} "
        f"({content['setup_type']})\n\n"
        f"Timeframe: {content['timeframe']}\n"
        f"Risk:Reward: {content['rr']}\n"
        f"Max risk: 1% of account\n\n"
        f"{steps_text}\n\n"
        f"Save this post — use it as a checklist before your next {content['pair']} trade.\n\n"
        f"This is the exact logic behind every position in my verified IC Markets account.\n"
        f"Get notified when this setup triggers:"
        f"{cta}\n\n{base_tags}"
    )


def daily_status(account: dict, open_trades: list) -> str:
    balance   = account.get('balance', 0)
    equity    = account.get('equity', balance)
    daily_pct = account.get('daily', 0)
    win_rate  = account.get('winRate', 0)
    pf        = account.get('profitFactor', 0)
    pips      = int(account.get('pips', 0))
    trades    = int(account.get('trades', 0))
    date      = datetime.now().strftime('%d %b %Y')

    direction_emoji = '📈' if daily_pct >= 0 else '📉'
    daily_sign      = '+' if daily_pct >= 0 else ''

    open_lines = []
    for t in open_trades[:5]:
        pair   = t.get('symbol', '')
        action = t.get('action', '').upper()
        profit = t.get('profit', 0)
        icon   = '🟢' if profit >= 0 else '🔴'
        open_lines.append(f"  {icon} {pair} {action}  ${profit:+.2f}")
    positions_block = '\n'.join(open_lines) if open_lines else '  No open positions'

    return f"""{direction_emoji} Live Position Update — {date}

Real trades. Real P&L. Nothing hidden.

💰 Balance: ${balance:,.0f}
⚖️ Equity: ${equity:,.0f}
📊 Daily: {daily_sign}{daily_pct:.2f}%

Open positions right now:
{positions_block}

Running record: {win_rate:.0f}% win rate · PF {pf:.2f} · +{pips:,} pips · {trades:,} trades
Every trade visible on Myfxbook — zero manipulation.

This is a live IC Markets account. Not a signal seller. Not a demo.
ASIC regulated. Available for Indian traders.

Get live alerts when I open or close a position:
{_CTA}

{TAGS}"""


def trust(account: dict) -> str:
    wr     = account.get('winRate', 0)
    pf     = account.get('profitFactor', 0)
    gain   = account.get('gain', 0)
    trades = int(account.get('trades', 0))
    pips   = int(account.get('pips', 0))
    sign   = '+' if gain >= 0 else ''

    return f"""✅ Live Track Record — Vera Level FX

{wr:.0f}% win rate across {trades:,} trades.
Every single one is on Myfxbook. Go check.

I am not a signal seller. I am not showing you screenshots.
I am showing you a live, ASIC-regulated IC Markets account
that anyone can verify in 30 seconds.

🎯 Win Rate: {wr:.0f}%
⚡ Profit Factor: {pf:.2f}
📈 Total Gain: {sign}{gain:.1f}%
💹 Pips: +{pips:,}

Verify yourself: search "Vera Level" on Myfxbook.com

IC Markets is open for Indian traders. Raw ECN spreads. ASIC regulated.
This is the broker I actually trade.

🏦 {_IB_URL}
{_CTA}

{TAGS}"""
