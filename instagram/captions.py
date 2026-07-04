import os
from datetime import datetime

# --- CTAs ---
_TELEGRAM = os.environ.get('BRAND_TELEGRAM', 't.me/pandiangk')
_WEBSITE  = os.environ.get('BRAND_WEBSITE', 'vera-level-forex.vercel.app')
_IB_URL   = os.environ.get('BRAND_IB_URL', 'icmarkets.com/?camp=91936')

_CTA_TELEGRAM = f"\n📲 Live trade alerts → {_TELEGRAM}"
_CTA_IB       = f"\n🏦 Open IC Markets (raw ECN, ASIC regulated) → {_IB_URL}"
_CTA_VERIFY   = f"\n🔍 Verify my full track record → Myfxbook #12044019"
_CTA_ALL      = f"\n📲 {_TELEGRAM}  |  🌐 {_WEBSITE}  |  🏦 {_IB_URL}"

# --- Hashtags (3-tier, no guru-signal tags) ---
_TAGS_BRAND  = "#veralevelFX #icmarkets #myfxbook"
_TAGS_NICHE  = "#xauusd #gold #eurusd #forexsingapore #sgtrader #forextrading"
_TAGS_BROAD  = "#forex #forextrader #priceaction #tradingstrategy #algotrading"
_TAGS_EDU    = "#forexeducation #riskmanagement #tradingpsychology #learnforex"

TAGS         = f"{_TAGS_BRAND} {_TAGS_NICHE} {_TAGS_BROAD}"
TAGS_EDU     = f"{_TAGS_BRAND} {_TAGS_NICHE} {_TAGS_EDU}"

# Tamil summary lines (appended when lang='tamil')
_TAMIL = {
    'daily':   "📊 இன்றைய live positions — எல்லாம் IC Markets real account, Myfxbook-ல் verify பண்ணலாம்.",
    'weekly':  "📈 இந்த வார P&L — live account, எல்லாம் Myfxbook-ல் verify பண்ணலாம்.",
    'monthly': "📅 இந்த மாத P&L முழு breakdown — Myfxbook-ல் நேரடியா பாருங்க.",
    'trust':   "✅ Real track record — Myfxbook-ல் search பண்ணுங்க 'Vera Level'.",
    'edu':     "📚 இந்த rule follow பண்ணா உங்க capital safe-ஆ இருக்கும்.",
}


def _tamil_line(key: str, lang: str) -> str:
    if lang == 'tamil':
        return f"\n\n{_TAMIL.get(key, '')}"
    return ''


def weekly(account: dict, lang: str = 'en', recovery_day: int = 0) -> str:
    bal    = account.get('balance') or 0
    gain   = account.get('gain') or 0
    wr     = account.get('winRate') or 0
    pf     = account.get('profitFactor') or 0
    pips   = int(account.get('pips') or 0)
    trades = int(account.get('trades') or 0)
    date   = datetime.now().strftime('%d %b %Y')
    sign   = '+' if gain >= 0 else ''

    recovery_line = (
        f"Recovery Day {recovery_day}. The rebuild is live and fully visible.\n\n"
        if recovery_day > 0 and gain < 0 else ''
    )

    return f"""📊 Weekly Performance — {date}

{recovery_line}{sign}{gain:.1f}% total gain. {trades:,} trades. {wr:.0f}% win rate.
Every single one verified on Myfxbook. Nothing hidden.

This is a live IC Markets account — not a demo, not a backtest.
ASIC regulated. Same oversight as Australian financial institutions.

💰 Balance: ${bal:,.0f}
🎯 Win Rate: {wr:.0f}% across {trades:,} trades
⚡ Profit Factor: {pf:.2f}
💹 Total Pips: +{pips:,}
{_CTA_VERIFY}{_tamil_line('weekly', lang)}

{TAGS}"""


def monthly(account: dict, monthly_pnl: dict, lang: str = 'en') -> str:
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

No emotional decisions. No manual overrides. No hiding losses.
{_CTA_IB}{_tamil_line('monthly', lang)}

{TAGS}"""


def edu(edu_type: str, content: dict, lang: str = 'en') -> str:
    cta = _CTA_TELEGRAM

    if edu_type == 'risk':
        return (
            f"⚠️ Risk Rule #{content['rule_num']} — {content['title']}\n\n"
            f"{content['body']}\n\n"
            f"Example: ${content['example_account']:,} account → "
            f"max ${content['example_risk']:,} at risk per trade.\n"
            f"At {content['example_rr']} — that is how professionals protect capital.\n\n"
            f"Save this post. Refer to it before your next trade.\n"
            f"I use this rule on every position in my live IC Markets account."
            f"{cta}{_tamil_line('edu', lang)}\n\n{TAGS_EDU}"
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
            f"you are giving away your edge before the trade starts."
            f"{cta}{_tamil_line('edu', lang)}\n\n{TAGS_EDU}"
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
        f"This is the exact logic behind every position in my verified IC Markets account."
        f"{cta}{_tamil_line('edu', lang)}\n\n{TAGS_EDU}"
    )


def daily_status(account: dict, open_trades: list, lang: str = 'en', recovery_day: int = 0) -> str:
    balance   = account.get('balance') or 0
    equity    = account.get('equity') or balance
    daily_pct = account.get('daily') or 0
    win_rate  = account.get('winRate') or 0
    pf        = account.get('profitFactor') or 0
    pips      = int(account.get('pips') or 0)
    trades    = int(account.get('trades') or 0)
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

    recovery_line = (
        f"Recovery Day {recovery_day}.\n\n"
        if recovery_day > 0 else ''
    )

    return f"""{direction_emoji} Live Position Update — {date}

{recovery_line}Real trades. Real P&L. Nothing hidden.

💰 Balance: ${balance:,.0f}
⚖️ Equity: ${equity:,.0f}
📊 Daily: {daily_sign}{daily_pct:.2f}%

Open positions right now:
{positions_block}

Running record: {win_rate:.0f}% win rate · PF {pf:.2f} · +{pips:,} pips · {trades:,} trades
Every trade visible on Myfxbook — zero manipulation.
{_CTA_TELEGRAM}{_tamil_line('daily', lang)}

{TAGS}"""


def trust(account: dict, lang: str = 'en') -> str:
    wr     = account.get('winRate') or 0
    pf     = account.get('profitFactor') or 0
    gain   = account.get('gain') or 0
    trades = int(account.get('trades') or 0)
    pips   = int(account.get('pips') or 0)
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
{_CTA_VERIFY}{_tamil_line('trust', lang)}

{TAGS}"""


def transparency(account: dict, lang: str = 'en') -> str:
    """One-time recovery/drawdown transparency post."""
    bal  = account.get('balance', 0)
    gain = account.get('gain', 0)
    dd   = account.get('drawdown', 0)

    return f"""📉 Down {gain:.1f}%. Here's the full story.

Most accounts hide drawdowns. I don't.

This live IC Markets account has gone through the hardest stretch I have had as a trader. \
The numbers are ugly. They are also all there on Myfxbook for anyone to verify.

What happened: position sizing errors compounded during a volatile XAUUSD run. \
Max 1% rule was followed — but entry frequency was too high. \
Capital eroded faster than wins recovered.

What changed: reduced trade frequency, tightened session filters, \
no trading outside London/NY overlap.

Why I am showing you this: any account showing only winning months is lying to you. \
This is what real trading looks like. The recovery starts now.

💰 Current balance: ${bal:,.0f}
📉 Max drawdown: {dd:.1f}%
🔍 Full history: Myfxbook #12044019
{_CTA_TELEGRAM}{_tamil_line('trust', lang)}

{TAGS}"""
