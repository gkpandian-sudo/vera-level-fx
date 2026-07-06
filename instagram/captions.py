import os
from datetime import datetime

# --- CTAs ---
_TELEGRAM = os.environ.get('BRAND_TELEGRAM', 't.me/pandiangk')
_WEBSITE  = os.environ.get('BRAND_WEBSITE', 'vera-level-forex.vercel.app')
_IB_URL   = os.environ.get('BRAND_IB_URL', 'https://www.icmarkets.com/global/en/?camp=91936')

_CTA_TELEGRAM = f"\n📲 Live trade alerts → {_TELEGRAM}"
_CTA_IB       = f"\n🏦 Open IC Markets (Raw Spread, ASIC + CySEC regulated) → {_IB_URL}"
_CTA_IB_SOFT  = (f"\n🏦 I trade on IC Markets Raw Spread · ASIC + CySEC"
                 f"\n👉 Open your account: {_IB_URL}")
_CTA_VERIFY   = f"\n🔍 Verify my full track record → Myfxbook #12044019"
_CTA_ALL      = f"\n📲 {_TELEGRAM}  |  🌐 {_WEBSITE}  |  🏦 {_IB_URL}"

# Required on all posts citing live P&L (daily, weekly, trust, transparency, monthly, recovery-plan)
_RISK_DISCLAIMER = (
    "Trading FX on margin carries high risk. "
    "Past performance is not indicative of future results. IB #91936."
)

# --- Hashtags (3-tier, no guru-signal tags) ---
_TAGS_BRAND  = "#veralevelFX #icmarkets #myfxbook"
_TAGS_NICHE  = "#xauusd #gold #eurusd #forexsingapore #sgtrader #forextrading"
_TAGS_BROAD  = "#forex #forextrader #priceaction #tradingstrategy #algotrading"
_TAGS_EDU    = "#forexeducation #riskmanagement #tradingpsychology #learnforex"

TAGS         = f"{_TAGS_BRAND} {_TAGS_NICHE} {_TAGS_BROAD}"
TAGS_EDU     = f"{_TAGS_BRAND} {_TAGS_NICHE} {_TAGS_EDU}"

# Tamil summary lines (appended when lang='tamil')
# Translation note: "Recovery Day", "PF", and metric labels may need transliteration
# rather than direct translation — flag for native speaker review before going live.
_TAMIL = {
    'daily':   "📊 இன்றைய live positions. எல்லாம் IC Markets real account, Myfxbook-ல் verify பண்ணலாம்.",
    'weekly':  "📈 இந்த வார P&L. Live account, எல்லாம் Myfxbook-ல் verify பண்ணலாம்.",
    'monthly': "📅 இந்த மாத P&L முழு breakdown. Myfxbook-ல் நேரடியா பாருங்க.",
    'trust':   "✅ Real track record. Myfxbook-ல் search பண்ணுங்க 'Vera Level'.",
    'edu':     "📚 இந்த rule follow பண்ணா உங்க capital safe-ஆ இருக்கும்.",
}


def _tamil_line(key: str, lang: str) -> str:
    if lang == 'tamil':
        return f"\n\n{_TAMIL.get(key, '')}"
    return ''


def monthly_pnl_from_daily(daily_gain: list) -> dict:
    """Myfxbook dailyGain rows -> ordered {'%b %y': monthly gain %}.

    Each dailyGain row is [date, cumulative_total_gain_%, daily_profit_$].
    Dates come from Myfxbook as MM/DD/YYYY (ISO also accepted).
    Monthly gain is the time-weighted change in cumulative gain over the
    month: ((100 + end) / (100 + prev_month_end) - 1) * 100, so every
    figure traces directly to the Myfxbook cumulative gain series.
    """
    month_end: dict = {}
    for item in daily_gain:
        ds  = item[0] if isinstance(item, list) else item.get('date', '')
        val = item[1] if isinstance(item, list) else item.get('value', 0)
        d = None
        for fmt in ('%m/%d/%Y', '%Y-%m-%d'):
            try:
                d = datetime.strptime(str(ds)[:10], fmt)
                break
            except ValueError:
                continue
        if d is None:
            continue
        # rows are chronological; last row seen for a month is month-end
        month_end[d.strftime('%b %y')] = float(val)

    result: dict = {}
    prev = 0.0
    for month, cum in month_end.items():
        base = 100.0 + prev
        result[month] = ((100.0 + cum) / base - 1.0) * 100.0 if base > 0 else 0.0
        prev = cum
    return result


def weekly(account: dict, lang: str = 'en', recovery_day: int = 0) -> str:
    bal    = account.get('balance') or 0
    gain   = account.get('gain') or 0
    wr     = account.get('winRate') or 0
    pf     = account.get('profitFactor') or 0
    pips   = int(account.get('pips') or 0)
    trades = int(account.get('trades') or 0)
    now    = datetime.now().strftime('%d %b %Y')

    gain_label = 'total gain' if gain >= 0 else 'total loss'
    sign       = '+' if gain >= 0 else ''
    wr_str     = f'{wr:.0f}% win rate' if wr > 0 else 'win rate on Myfxbook'
    trades_part = f'. {trades:,} trades' if trades > 0 else ''
    wr_line     = (f'🎯 Win Rate: {wr:.0f}% across {trades:,} trades'
                   if wr > 0 else '🎯 Win Rate: Myfxbook #12044019')
    recovery_line = (
        f"Recovery Day {recovery_day}. Account is live, positions visible below.\n\n"
        if recovery_day > 0 else ''
    )
    hook = f"{sign}{gain:.1f}% this week — {trades:,} trades. Every one is public."

    return f"""{hook}

📊 {now}

{recovery_line}{sign}{gain:.1f}% {gain_label}{trades_part}. {wr_str}.
Every figure verified on Myfxbook. Account #12044019.

IC Markets Raw Spread. ASIC and CySEC regulated.
Max 1% risk per trade. Target 1:2.5+ RR.

💰 Balance: ${bal:,.0f}
{wr_line}
⚡ Profit Factor: {pf:.2f}
💹 Total Pips: +{pips:,}
{_CTA_IB_SOFT}{_CTA_VERIFY}{_tamil_line('weekly', lang)}

{_RISK_DISCLAIMER}

{TAGS}"""


def monthly(account: dict, monthly_pnl: dict, lang: str = 'en') -> str:
    last_months = list(monthly_pnl.items())[-6:]
    lines = '\n'.join(
        f"{'🟢' if v >= 0 else '🔴'} {k}: {v:+.1f}%"
        for k, v in last_months
    )
    gain      = account.get('gain', 0)
    sign      = '+' if gain >= 0 else ''
    month_now = datetime.now().strftime('%B %Y')

    return f"""Six months of real P&L. Red months included. Every one of them.

📅 {month_now}

{lines}

{sign}{gain:.1f}% total return since inception.

Pre-defined entry conditions. No news-event overrides.
All data from IC Markets live account, updated via authenticated API.
{_CTA_IB}{_CTA_VERIFY}{_tamil_line('monthly', lang)}

{_RISK_DISCLAIMER}

{TAGS}"""


def edu(edu_type: str, content: dict, lang: str = 'en') -> str:
    cta = _CTA_IB

    if edu_type == 'risk':
        return (
            f"⚠️ Risk Rule #{content['rule_num']} · {content['title']}\n\n"
            f"{content['body']}\n\n"
            f"Example: ${content['example_account']:,} account → "
            f"max ${content['example_risk']:,} at risk per trade.\n"
            f"At {content['example_rr']}. That is how professionals protect capital.\n\n"
            f"Save this post. Apply it before your next trade.\n"
            f"Every position in my live IC Markets account follows this rule."
            f"{cta}{_tamil_line('edu', lang)}\n\n{TAGS_EDU}"
        )

    if edu_type == 'pairs':
        return (
            f"📊 Pair Spotlight · {content['pair']} ({content['full_name']})\n\n"
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
        f"{i+1}. {title}: {desc}"
        for i, (title, desc) in enumerate(content['steps'])
    )
    return (
        f"📈 Setup Breakdown · {content['pair']} {content['direction']} "
        f"({content['setup_type']})\n\n"
        f"Timeframe: {content['timeframe']}\n"
        f"Risk:Reward: {content['rr']}\n"
        f"Max risk: 1% of account, sized by ATR\n\n"
        f"{steps_text}\n\n"
        f"Save this post. Use it as a checklist before your next {content['pair']} trade.\n\n"
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
    now       = datetime.now().strftime('%d %b %Y')

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

    wr_line = (f'{win_rate:.0f}% win rate · PF {pf:.2f} · +{pips:,} pips · {trades:,} trades'
               if win_rate > 0 else f'PF {pf:.2f} · +{pips:,} pips · Myfxbook #12044019')

    recovery_line = (
        f"Recovery Day {recovery_day}. Every position sized at max 1% account risk.\n\n"
        if recovery_day > 0 else ''
    )

    if open_trades:
        first  = open_trades[0]
        pair   = first.get('symbol', 'XAUUSD')
        action = first.get('action', '').upper()
        profit = float(first.get('profit') or 0)
        hook   = f"🔴 LIVE: {pair} {action}  ${profit:+.2f} floating right now."
    else:
        hook = f"🔵 Flat right now — no open positions. {direction_emoji} {daily_sign}{daily_pct:.2f}% today."

    return f"""{hook}

{recovery_line}Myfxbook #12044019. Open now to verify every row.

💰 Balance: ${balance:,.0f}
⚖️ Equity: ${equity:,.0f}
📊 Daily: {daily_sign}{daily_pct:.2f}%

Open positions right now:
{positions_block}

Running record: {wr_line}
{_CTA_IB_SOFT}{_CTA_VERIFY}{_tamil_line('daily', lang)}

{_RISK_DISCLAIMER}

{TAGS}"""


def trust(account: dict, lang: str = 'en') -> str:
    wr     = account.get('winRate') or 0
    pf     = account.get('profitFactor') or 0
    gain   = account.get('gain') or 0
    trades = int(account.get('trades') or 0)
    pips   = int(account.get('pips') or 0)
    sign   = '+' if gain >= 0 else ''

    wr_str    = f'{wr:.0f}% win rate across {trades:,} trades.' if wr > 0 else 'Full trade history on Myfxbook.'
    gain_note = ' (deep drawdown, fully disclosed)' if gain < -50 else ''
    wr_line   = f'🎯 Win Rate: {wr:.0f}%' if wr > 0 else '🎯 Win Rate: Myfxbook #12044019'

    return f"""No screenshots. No cherry-picked months. One live account, one public link. Go break it.

✅ Vera Level FX  ·  IC Markets  ·  Myfxbook #12044019

{wr_str}
Every trade on Myfxbook. Go check.

No screenshots. No cherry-picked months. One live account, one public link.
Account type: Raw Spread. Broker: IC Markets. Regulation: ASIC + CySEC.

{wr_line}
⚡ Profit Factor: {pf:.2f}
📈 Total Return: {sign}{gain:.1f}%{gain_note}
💹 Pips: +{pips:,}

Verify: search "Vera Level" on Myfxbook.com
{_CTA_IB_SOFT}{_CTA_VERIFY}{_tamil_line('trust', lang)}

{_RISK_DISCLAIMER}

{TAGS}"""


def transparency(account: dict, lang: str = 'en') -> str:
    bal  = account.get('balance') or 0
    gain = account.get('gain') or 0
    dd   = account.get('drawdown') or 0

    return f"""📉 Down {gain:.1f}%. The full account.

Most accounts hide drawdown months. This one does not.
Every number is on Myfxbook for anyone to verify.

WHAT HAPPENED
Position sizing errors compounded during volatile XAUUSD sessions.
Entry frequency exceeded system parameters.
Capital eroded faster than wins could recover.

WHAT CHANGED
Trade frequency reduced.
London and NY overlap sessions only.
Position sizing now ATR-based.
Hard daily drawdown limit enforced.

The rebuild is live on Myfxbook.

💰 Current balance: ${bal:,.0f}
📉 Max drawdown: {dd:.1f}%
🔍 Full history: Myfxbook #12044019
{_CTA_IB_SOFT}{_CTA_VERIFY}{_tamil_line('trust', lang)}

{_RISK_DISCLAIMER}

{TAGS}"""


def recovery_plan(lang: str = 'en', recovery_day: int = 0, recovery_start_str: str = '',
                  balance: float = 0.0, pf: float = 0.0) -> str:
    """Actuals-only rebuild report. No projections, no targets."""
    tamil = (
        "\n\n📈 Rebuild live இருக்கு. "
        "Every trade Myfxbook-ல் verify பண்ணலாம். #12044019"
    ) if lang == 'tamil' else ''

    if recovery_day > 0 and recovery_start_str:
        day_line = f"Day {recovery_day} since {recovery_start_str}.\n"
    elif recovery_day > 0:
        day_line = f"Recovery Day {recovery_day}.\n"
    else:
        day_line = ''

    bal_str = f"\n💰 Current balance: ${balance:,.0f}" if balance > 0 else ''
    if pf > 0:
        pf_note = ('  ← improving' if 0 < pf < 1.0
                   else '  ← target reached' if pf >= 1.2 else '')
        pf_str  = f"\n⚡ Profit Factor: {pf:.2f}  (target: 1.2+){pf_note}"
    else:
        pf_str = ''

    return f"""📈 Rebuild · Vera Level FX

{day_line}Every top-up and trade is live on Myfxbook. Nothing projected. Nothing hidden.

WHAT THE REBUILD LOOKS LIKE
Trade frequency: London/NY overlap sessions only.
Position sizing: ATR-based, max 1% per trade.
Monthly top-ups: documented on Myfxbook as they happen.
Milestones: reported when reached — not before.
{bal_str}{pf_str}
{_CTA_VERIFY}

{_RISK_DISCLAIMER}

{TAGS}{tamil}"""


def broker(lang: str = 'en') -> str:
    _TAGS_BROKER = (f"{_TAGS_BRAND} {_TAGS_NICHE} "
                    "#icmarkets #rawspread #forexbroker #asicregulated #forexsg #sgforex")

    tamil = (
        f"\n\n📊 நான் IC Markets Raw Spread account-ல் தான் trade பண்றேன். "
        f"ASIC + CySEC regulated. Every single trade. "
        f"Open: link in bio (IB #91936)"
    ) if lang == 'tamil' else ''

    return f"""Every trade I've made for 18+ months runs through one broker.

🏦 IC Markets — Raw Spread

WHAT YOU GET
Raw interbank spreads from 0.0 pips
No dealing desk  ·  ECN/STP execution
ASIC regulated (Australia)
CySEC regulated (Europe)

Every verified trade on Myfxbook #12044019 runs through this account.
That is not marketing. That is my live setup.

Open your account via the link in bio.
Important: you must use my link — opening icmarkets.com directly won't link us.
Costs you nothing extra. Spreads are identical either way.

IB #91936. Referral link. I earn a small commission at no cost to you.

{_RISK_DISCLAIMER}

{_TAGS_BROKER}{tamil}"""
