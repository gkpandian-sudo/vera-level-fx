from datetime import datetime

TAGS = (
    "#forex #forextrader #forextrading #algotrading #algorithmic "
    "#icmarkets #myfxbook #xauusd #gold #forexsignals "
    "#tradingstrategy #singapore #investingsingapore "
    "#financialfreedom #wealthbuilding #veralevelFX "
    "#forexlifestyle #passiveincome #tradingresults"
)

_CTA = (
    "\n\n📲 Live signals → t.me/pandiangk"
    "\n🌐 Live account → https://vera-level-forex.vercel.app"
    "\n🏦 Open IC Markets account →"
    "\nhttps://icmarkets.com/global/en/?camp=91936"
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
{_CTA}

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
{_CTA}

{TAGS}"""


def edu(edu_type: str, content: dict) -> str:
    base_tags = (
        "#forex #forextrader #forexsingapore #icmarkets #xauusd "
        "#veralevelFX #tradingstrategy #singaporetrader #pandian "
        "#forexeducation #fxtrading #priceaction"
    )
    cta = _CTA

    if edu_type == 'risk':
        return (
            f"⚠️ Risk Management Rule #{content['rule_num']} — {content['title']}\n\n"
            f"{content['body']}\n\n"
            f"💰 Example: ${content['example_account']:,} account → "
            f"${content['example_risk']:,} max risk per trade\n"
            f"🎯 At {content['example_rr']} — that's the professional way."
            f"{cta}\n\n{base_tags}"
        )

    if edu_type == 'pairs':
        return (
            f"🌍 Pair Spotlight — {content['pair']} ({content['full_name']})\n\n"
            f"Best session: {content['best_session']}\n"
            f"Avg spread: {content['avg_spread']}\n"
            f"Volatility: {content['volatility']}\n"
            f"My edge: {content['my_edge']}\n\n"
            f'"{content["quote"]}"\n\n'
            f"— Pandian, Vera Level FX"
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
        f"Risk:Reward: {content['rr']}\n\n"
        f"{steps_text}\n\n"
        f"This is exactly how I structure every trade — no guessing, no emotion."
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

    return f"""{direction_emoji} Live Trade Update — {date}

💰 Balance: ${balance:,.2f}
⚖️ Equity: ${equity:,.2f}
📊 Daily: {daily_sign}{daily_pct:.2f}%

🔓 Open Positions:
{positions_block}

📈 Running stats: {win_rate:.0f}% win rate · PF {pf:.2f} · +{pips:,} pips · {trades:,} trades

Fully automated system on IC Markets.
Every position tracked live on Myfxbook — zero manipulation.
{_CTA}

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
{_CTA}

{TAGS}"""
