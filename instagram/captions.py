import os
from datetime import datetime

# --- CTAs ---
_TELEGRAM = os.environ.get('BRAND_TELEGRAM', 't.me/pandiangk')
_WEBSITE  = os.environ.get('BRAND_WEBSITE', 'vera-level-forex.vercel.app')
_IB_URL   = os.environ.get('BRAND_IB_URL', 'https://www.icmarkets.com/global/en/?camp=91936')

_CTA_TELEGRAM = f"\n📲 Every trade alert, free, as it happens → {_TELEGRAM}"
_CTA_IB       = f"\n🏦 Trade where I trade — IC Markets Raw Spread (ASIC + CySEC regulated) → {_IB_URL}"
_CTA_VERIFY   = f"\n🔍 Don't take my word for it — audit me → Myfxbook #12044019"
_CTA_ALL      = f"\n📲 {_TELEGRAM}  |  🌐 {_WEBSITE}  |  🏦 {_IB_URL}"

_CTA_IB_BIO  = (
    f"\n🏦 IC Markets Raw Spread (ASIC + CySEC) — the account behind every number above"
    f"\n👉 Opening an account anyway? Link in bio. Same spreads, same cost — my link just means I get credited"
    f"\n💬 Comment BROKER and my 4-step setup lands in your DMs"
)
_CTA_ALERTS  = f"\n📲 I post entries in Telegram before they close, not after → {_TELEGRAM}  ·  DM me anytime"
_CTA_EDU_SOFT = (
    f"\n\n💾 Save this — you'll want it mid-trade, not mid-scroll. Comment RULES and I'll DM you the full library.\n"
    f"📲 Live trades as they happen → {_TELEGRAM}  ·  DM me anytime"
)

# Required on all posts citing live P&L (daily, weekly, trust, transparency, monthly, recovery-plan)
_RISK_DISCLAIMER = (
    "Trading FX on margin carries high risk. "
    "Past performance is not indicative of future results. IB #91936."
)

# --- Hashtags (consolidated: 8 core + edu variant + campaign) ---
_TAGS_BRAND    = "#veralevelFX #icmarkets #myfxbook"
_TAGS_NICHE    = "#xauusd #gold #eurusd #forexsingapore #sgtrader"
_TAGS_EDU_ONLY = "#forexeducation #riskmanagement #tradingpsychology #learnforex"
_TAGS_REBUILD  = "#180dayrebuild"

TAGS      = f"{_TAGS_BRAND} {_TAGS_NICHE}"         # 8 tags: core posts
TAGS_EDU  = f"{_TAGS_BRAND} {_TAGS_NICHE} {_TAGS_EDU_ONLY}"  # 12 tags: edu posts


def _rebuild_tag(recovery_day: int) -> str:
    """Append campaign tag when account is in recovery mode."""
    return f" {_TAGS_REBUILD}" if recovery_day > 0 else ""

# Tamil summary lines (appended when lang='tamil')
# Translation note: "Recovery Day", "PF", and metric labels may need transliteration
# rather than direct translation — flag for native speaker review before going live.
_TAMIL = {
    'daily':   "📊 இன்றைய live positions. Fake screenshot இல்லை — IC Markets real account, Myfxbook-ல் இப்பவே verify பண்ணலாம்.",
    'weekly':  "📈 இந்த வார P&L — win-um loss-um எல்லாமே. Live account, Myfxbook-ல் verify பண்ணுங்க.",
    'monthly': "📅 இந்த மாத full P&L breakdown. Red month-ah இருந்தாலும் hide பண்ண மாட்டேன் — Myfxbook-ல் நேரடியா பாருங்க.",
    'trust':   "✅ Real track record, edited screenshots இல்லை. Myfxbook-ல் 'Vera Level' search பண்ணி நீங்களே check பண்ணுங்க.",
    'edu':     "📚 இந்த ஒரு rule follow பண்ணா உங்க capital safe-ஆ இருக்கும். Save பண்ணி வச்சுக்கோங்க.",
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


def weekly_gain_from_daily(daily_gain: list, today=None) -> float | None:
    """Compute week-to-date gain % from the cumulative dailyGain series.

    Finds the last cumulative value strictly before this week's Monday (Sunday
    close) and the last cumulative value on or before today, then returns the
    time-weighted change. Returns None when either baseline is missing.
    """
    from datetime import date as _date, timedelta
    if today is None:
        today = _date.today()
    last_monday = today - timedelta(days=today.weekday())

    pre_monday_cum: float | None = None
    latest_cum: float | None = None

    for item in daily_gain:
        ds  = item[0] if isinstance(item, list) else item.get('date', '')
        val = item[1] if isinstance(item, list) else item.get('value', 0)
        d   = None
        for fmt in ('%m/%d/%Y', '%Y-%m-%d'):
            try:
                d = datetime.strptime(str(ds)[:10], fmt).date()
                break
            except ValueError:
                continue
        if d is None:
            continue
        if d < last_monday:
            pre_monday_cum = float(val)
        elif d <= today:
            latest_cum = float(val)

    if pre_monday_cum is None or latest_cum is None:
        return None
    base = 100.0 + pre_monday_cum
    if base <= 0:
        return None
    return ((100.0 + latest_cum) / base - 1.0) * 100.0


def weekly(account: dict, lang: str = 'en', recovery_day: int = 0,
           recovery_total: int = 180, weekly_gain: float | None = None) -> str:
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
        f"Day {recovery_day}/{recovery_total} of the rebuild. Account is live — numbers below, nothing cropped out.\n\n"
        if recovery_day > 0 else ''
    )
    if recovery_day > 0 and weekly_gain is not None:
        wg_sign = '+' if weekly_gain >= 0 else ''
        hook = (f"Day {recovery_day}/{recovery_total} of rebuilding a losing account in public. "
                f"This week: {wg_sign}{weekly_gain:.1f}%.")
    elif recovery_day > 0:
        hook = (f"Day {recovery_day}/{recovery_total} of rebuilding in public. "
                f"Running total: {sign}{gain:.1f}% {gain_label}.")
    elif weekly_gain is not None:
        wg_sign = '+' if weekly_gain >= 0 else ''
        hook = f"{wg_sign}{weekly_gain:.1f}% this week. You can audit every trade behind that number — most pages can't say that."
    else:
        hook = f"{sign}{gain:.1f}% {gain_label} after {trades:,} trades — and every single one is public."

    return f"""{hook}

📊 Week ending {now}

{recovery_line}{sign}{gain:.1f}% {gain_label}{trades_part}. {wr_str}.
Not a screenshot. Not a demo. Myfxbook pulls these figures straight from my broker — account #12044019. Go check.

Same rules as every week: IC Markets Raw Spread, max 1% risk per trade, 1:2.5+ RR or the trade doesn't happen.

💰 Balance: ${bal:,.0f}
{wr_line}
⚡ Profit Factor: {pf:.2f}
💹 Total Pips: +{pips:,}
{_CTA_IB_BIO}{_CTA_VERIFY}
Green or red for you this week? Comment G or R — I pin the honest ones next Monday.{_tamil_line('weekly', lang)}

{_RISK_DISCLAIMER}

{TAGS}{_rebuild_tag(recovery_day)}"""


def monthly(account: dict, monthly_pnl: dict, lang: str = 'en') -> str:
    last_months = list(monthly_pnl.items())[-6:]
    lines = '\n'.join(
        f"{'🟢' if v >= 0 else '🔴'} {k}: {v:+.1f}%"
        for k, v in last_months
    )
    gain      = account.get('gain', 0)
    sign      = '+' if gain >= 0 else ''
    month_now = datetime.now().strftime('%B %Y')

    return f"""Most traders delete their red months. Here are mine — every one of them.

📅 {month_now}

{lines}

{sign}{gain:.1f}% total return since inception — and that number includes every red row above.

No cherry-picked entries. No "demo results". This is pulled from my live IC Markets account through an authenticated API. I couldn't edit it if I wanted to.

Save this post. On the 1st of next month, one more row goes up — green or red. Hold me to it.
{_CTA_IB}{_CTA_VERIFY}{_tamil_line('monthly', lang)}

{_RISK_DISCLAIMER}

{TAGS}"""


def edu(edu_type: str, content: dict, lang: str = 'en') -> str:
    cta = _CTA_EDU_SOFT

    if edu_type == 'risk':
        return (
            f"⚠️ Risk Rule #{content['rule_num']} · {content['title']}\n\n"
            f"{content['body']}\n\n"
            f"Put real money on it: ${content['example_account']:,} account → "
            f"never more than ${content['example_risk']:,} on the line per trade.\n"
            f"At {content['example_rr']}, you can be wrong half the time and still grow. "
            f"That is the entire game — not predictions.\n\n"
            f"This isn't theory. Every open position in my live IC Markets account is sized by this exact rule — check it yourself."
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
            f"Here's the part nobody tells beginners: if you're paying wide spreads on {content['pair']}, "
            f"you're handing your edge to the broker before the chart even moves. Fix the spread first, then work on the strategy."
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
        f"Max risk: 1% of account, sized by ATR — never by feeling\n\n"
        f"{steps_text}\n\n"
        f"No secret indicator. No paid course behind this. This exact checklist sits behind every position "
        f"in my verified IC Markets account — match this post against the Myfxbook history yourself."
        f"{cta}{_tamil_line('edu', lang)}\n\n{TAGS_EDU}"
    )


def daily_status(account: dict, open_trades: list, lang: str = 'en', recovery_day: int = 0, recovery_total: int = 180) -> str:
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
        f"Day {recovery_day}/{recovery_total} of the rebuild. Every position capped at 1% account risk — no revenge sizing.\n\n"
        if recovery_day > 0 else ''
    )

    if open_trades:
        first  = open_trades[0]
        pair   = first.get('symbol', 'XAUUSD')
        action = first.get('action', '').upper()
        profit = float(first.get('profit') or 0)
        hook   = f"🔴 LIVE: {pair} {action} · ${profit:+.2f} floating as you read this. Not a replay."
    else:
        hook = f"🔵 Flat. No positions, no forced trades. {direction_emoji} {daily_sign}{daily_pct:.2f}% today — sitting out is a position too."

    return f"""{hook}

{recovery_line}This is my real account, mid-session — {now}. Open Myfxbook #12044019 in another tab and match every row.

💰 Balance: ${balance:,.0f}
⚖️ Equity: ${equity:,.0f}
📊 Daily: {daily_sign}{daily_pct:.2f}%

On the book right now:
{positions_block}

Running record: {wr_line}
{_CTA_IB_BIO}{_CTA_VERIFY}{_CTA_ALERTS}{_tamil_line('daily', lang)}

{_RISK_DISCLAIMER}

{TAGS}{_rebuild_tag(recovery_day)}"""


def trust(account: dict, lang: str = 'en', recovery_day: int = 0, recovery_total: int = 180) -> str:
    wr     = account.get('winRate') or 0
    pf     = account.get('profitFactor') or 0
    gain   = account.get('gain') or 0
    trades = int(account.get('trades') or 0)
    pips   = int(account.get('pips') or 0)
    sign   = '+' if gain >= 0 else ''

    wr_str    = f'{wr:.0f}% win rate across {trades:,} trades.' if wr > 0 else 'Full trade history on Myfxbook.'
    gain_note = ' (deep drawdown, fully disclosed)' if gain < -50 else ''
    wr_line   = f'🎯 Win Rate: {wr:.0f}%' if wr > 0 else '🎯 Win Rate: Myfxbook #12044019'
    win_rate  = wr

    days_str = f"Day {recovery_day}/{recovery_total} —" if recovery_day > 0 else ""
    return f"""{days_str} Try to catch me lying. One live account, one public link. I'll wait.

✅ Vera Level FX  ·  IC Markets  ·  Myfxbook #12044019

{wr_str}
But a {win_rate:.0f}% win rate on its own means nothing — scammers run 95% win rate with martingale, right up until the account explodes.
Mine comes with 1:2.5 avg RR and max 1% risk per trade. That combination is the only number that matters.

DON'T TRUST ME — AUDIT ME. 3 steps:
1. Myfxbook.com → search "Vera Level" → look for "Track Record Verified" + "Trading Privileges Verified". Those badges come from the broker, not from me.
2. Open Trades tab → updates live → nothing can be edited after the fact
3. Deposit History → every top-up on record → no hidden refills, no quietly reset accounts

{wr_line}
⚡ Profit Factor: {pf:.2f}
📈 Total Return: {sign}{gain:.1f}%{gain_note}
💹 Pips: +{pips:,}
{_CTA_IB_BIO}{_CTA_VERIFY}{_tamil_line('trust', lang)}

{_RISK_DISCLAIMER}

{TAGS}{_rebuild_tag(recovery_day)}"""


def transparency(account: dict, lang: str = 'en', recovery_day: int = 0) -> str:
    bal  = account.get('balance') or 0
    gain = account.get('gain') or 0
    dd   = account.get('drawdown') or 0

    return f"""{gain:.1f}%. That's my real account. And I'm posting it anyway.

Every other page would have deleted this account and opened a fresh one.
Mine stays public — because you deserve to see what losing actually looks like, and what fixing it looks like.

WHAT HAPPENED
I broke my own rules. Position sizing errors compounded during volatile XAUUSD sessions.
Entry frequency ran past system parameters.
Capital eroded faster than wins could recover it.

WHAT CHANGED
Trade frequency cut hard.
London and NY overlap sessions only.
Position sizing now ATR-based — no more manual overrides.
Hard daily drawdown limit, enforced before emotion gets a vote.

The rebuild is live on Myfxbook. Watch it work — or watch it fail. Either way, it's public.

💰 Current balance: ${bal:,.0f}
📉 Max drawdown: {dd:.1f}%
🔍 Full history, including this: Myfxbook #12044019
{_CTA_IB_BIO}{_CTA_VERIFY}{_tamil_line('trust', lang)}

{_RISK_DISCLAIMER}

{TAGS}{_rebuild_tag(recovery_day)}"""


def recovery_plan(lang: str = 'en', recovery_day: int = 0, recovery_total: int = 180,
                  recovery_start_str: str = '', balance: float = 0.0, pf: float = 0.0,
                  gain: float = -999.0) -> str:
    """Actuals-only rebuild report. No projections, no targets."""
    tamil = (
        "\n\n📈 Rebuild live-ஆ நடக்குது. "
        "ஒவ்வொரு trade-um Myfxbook-ல் verify பண்ணலாம். #12044019"
    ) if lang == 'tamil' else ''

    if recovery_day > 0 and recovery_start_str:
        day_line = f"Day {recovery_day}/{recovery_total} since {recovery_start_str}.\n"
    elif recovery_day > 0:
        day_line = f"Day {recovery_day}/{recovery_total}.\n"
    else:
        day_line = ''

    bal_str = f"\n💰 Current balance: ${balance:,.0f}" if balance > 0 else ''
    if pf > 0:
        pf_note = ('  ← improving' if 0 < pf < 1.0
                   else '  ← target reached' if pf >= 1.2 else '')
        pf_str  = f"\n⚡ Profit Factor: {pf:.2f}  (target: 1.2+){pf_note}"
    else:
        pf_str = ''

    # Milestone checklist — auto-computed from live pf and gain
    def _ms(done: bool, label: str) -> str:
        return f"{'☑' if done else '☐'} {label}"

    checklist = '\n'.join([
        _ms(pf >= 1.0,  'Profit Factor above 1.0'),
        _ms(pf >= 1.2,  'Profit Factor 1.2+ (target)'),
        _ms(gain >= 0,  'Total return back to breakeven'),
        _ms(gain > 5,   'New equity high'),
    ])

    # Failure condition line with computed end date
    if recovery_start_str and recovery_total > 0:
        try:
            from datetime import timedelta as _td
            end_dt  = datetime.strptime(recovery_start_str, '%Y-%m-%d') + _td(days=recovery_total - 1)
            end_str = end_dt.strftime('%d %b %Y')
            commit_line = f"\nDay 180 is {end_str}. The final result gets posted that day — recovered or not. No quiet exit, no fresh account."
        except Exception:
            commit_line = f"\nDay {recovery_total} · Final result posted — recovered or not. No quiet exit."
    elif recovery_total > 0:
        commit_line = f"\nDay {recovery_total} · Final result posted — recovered or not. No quiet exit."
    else:
        commit_line = ''

    return f"""📈 The Rebuild · Vera Level FX

{day_line}No projections. No "trust the process" fluff. Every top-up and every trade hits Myfxbook the moment it happens.

THE RULES OF THIS REBUILD
Sessions: London/NY overlap only — no boredom trades.
Sizing: ATR-based, max 1% risk per trade. No exceptions, especially on red days.
Top-ups: documented on Myfxbook the day they land.
Milestones: announced when reached — never before.
{bal_str}{pf_str}

MILESTONES — ticked by live data, not by me
{checklist}
{commit_line}

Full 180-day plan → pinned post. Follow to see whether this works — most pages would never let you.
{_CTA_VERIFY}

{_RISK_DISCLAIMER}

{TAGS} {_TAGS_REBUILD}{tamil}"""


def broker(lang: str = 'en') -> str:
    _TAGS_BROKER = (f"{_TAGS_BRAND} {_TAGS_NICHE} "
                    "#icmarkets #rawspread #forexbroker #asicregulated #forexsg #sgforex")

    tamil = (
        f"\n\n📊 நான் IC Markets Raw Spread account-ல் தான் trade பண்றேன் — ஒவ்வொரு trade-um. "
        f"ASIC + CySEC regulated. "
        f"Account open பண்ண: link in bio (IB #91936)"
    ) if lang == 'tamil' else ''

    return f"""The question I get most: "Which broker do you actually use?" Here's the answer — with 18+ months of proof attached.

🏦 IC Markets — Raw Spread

WHAT YOU GET
Raw interbank spreads from 0.0 pips
No dealing desk  ·  ECN/STP execution
ASIC regulated (Australia)
CySEC regulated (Europe)

Every verified trade on Myfxbook #12044019 runs through this exact account.
That's not a sponsorship line. That's my live setup, auditable down to the trade.

If you're opening an account anyway, open it through the link in my bio.
Important: opening icmarkets.com directly won't link us — it has to be my link.
Costs you nothing extra. Spreads are identical either way. The only difference is I get credited for sending you.

IB #91936. Referral link. IC Markets pays me a small commission — you pay nothing extra. Full stop.

{_RISK_DISCLAIMER}

{_TAGS_BROKER}{tamil}"""


def ib_signup(lang: str = 'en') -> str:
    """4-step IC Markets IB sign-up walkthrough. Highest-converting post type."""
    tamil = (
        f"\n\n📲 IC Markets account open பண்ண:\n"
        f"Bio-ல் இருக்கற link மூலமா மட்டும் open பண்ணுங்க — direct-ஆ போனா நமக்கு link ஆகாது.\n"
        f"IB #91936"
    ) if lang == 'tamil' else ''

    return f"""Want to trade on the exact setup behind Myfxbook #12044019? Here's the whole process — 10 minutes, nothing hidden.

1️⃣  Go to the link in my bio
     (this matters — opening icmarkets.com directly won't link us)
2️⃣  Choose the Raw Spread account
3️⃣  Verify your identity (about 10 min, ASIC + CySEC regulated)
4️⃣  DM me "DONE" and I'll personally walk you through what to do before your first trade

Full disclosure, because that's the whole point of this page: it's my referral link. IC Markets pays me a small commission.
You pay nothing extra — spreads are identical either way. The commission just keeps this page free.
IB #91936.

Same broker, same account type, same spreads as every trade you can audit on Myfxbook.{tamil}

{_RISK_DISCLAIMER}

{TAGS}"""


def milestone(account: dict, milestone_label: str, lang: str = 'en') -> str:
    """Event-driven milestone post. Report actuals; never project."""
    pf     = account.get('profitFactor', 0)
    gain   = account.get('gain', 0)
    trades = int(account.get('trades') or 0)
    sign   = '+' if gain >= 0 else ''

    tamil = (
        f"\n\n🏆 Milestone: {milestone_label}\n"
        f"Promise இல்லை — already நடந்தது. Myfxbook #12044019-ல் இப்பவே verify பண்ணுங்க."
    ) if lang == 'tamil' else ''

    return f"""{milestone_label}

Not a projection. Not a target. It already happened — and you can check it right now:
{sign}{gain:.1f}% total return  ·  {trades:,} trades  ·  PF {pf:.2f}
All live on Myfxbook #12044019.

I don't announce milestones before they're reached. I post them when they're verifiable — that's the entire point of this page.
The next one goes up the same way: when it happens, where you can check it.

Follow so you see it live, not in someone's recap.
{_CTA_VERIFY}{tamil}

{_RISK_DISCLAIMER}

{TAGS}"""
