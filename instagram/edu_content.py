# instagram/edu_content.py
# Educational content for rotating Instagram posts — Vera Level FX
# Methodology: multi-timeframe confluence, ATR-based sizing, max 1% risk per trade
# H4/H1/M15 timeframes, 1:2.5+ avg RR, London/NY overlap sessions
# DO NOT reference external system names in captions

RISK_RULES = [
    {
        "rule_num": "01",
        "title": "Lot Sizing By Balance",
        "body": (
            "Fixed lots is how accounts die slowly. You lose 30%, keep trading 0.10, "
            "and now every stop-out hits 40% harder than it should. Pros risk a "
            "percentage of what's LEFT, not what you started with. My rule: 0.01 lots "
            "per $333 of current balance. On XAUUSD, 0.01 lots with a 30-pip stop "
            "costs $3 — that's 0.3% on a $1,000 account, well inside my 1% hard cap. "
            "When balance drops, size drops with it automatically. When volatility "
            "expands, ATR sizing cuts the position before the market cuts you. "
            "The account shrinks in dollars but never in survivability. That is the "
            "entire game."
        ),
        "example_account": 1000,
        "example_risk": 10,
        "example_rr": "1% max risk, ATR-sized per trade",
        "example_target": 25,
        "tag": "SIZING",
    },
    {
        "rule_num": "02",
        "title": "Grid Spacing Discipline",
        "body": (
            "Every blown grid account I've seen died the same way: levels too tight, "
            "stacked too fast, margin call before the reversal ever came. My minimum "
            "is 100 pips between levels. Non-negotiable. Here's why: XAUUSD can run "
            "1,000+ pips in one NFP session. At 100-pip spacing that's 10 levels of "
            "breathing room. At 50-pip spacing you've doubled your exposure and halved "
            "your survival distance — you're not trading, you're standing in front of "
            "a train counting on it to stop. Wide spacing feels slow and boring on "
            "green days. It's the only reason the account is still alive on red ones."
        ),
        "example_account": 3000,
        "example_risk": 30,
        "example_rr": "100-pip min spacing per grid level",
        "example_target": 0,
        "tag": "GRID CONTROL",
    },
    {
        "rule_num": "03",
        "title": "Balance vs Equity Drawdown",
        "body": (
            "Your balance says $3,000. Your equity says $2,400. Which one is real? "
            "The second one. Balance only counts losses you've admitted to. Equity "
            "counts the ones floating open right now, and that's the number your "
            "broker uses when it decides to liquidate you. Retail traders stare at "
            "balance to feel safe, then panic-close open positions at maximum pain — "
            "usually within hours of the reversal. I've done it. It costs more than "
            "any losing trade. That's why this system runs a hard daily equity "
            "drawdown limit: not to avoid losses, but to make sure no single ugly "
            "session can force me into an emotional decision. The limit decides "
            "before I have to."
        ),
        "example_account": 3000,
        "example_risk": 60,
        "example_rr": "Equity vs Balance, know the difference",
        "example_target": 0,
        "tag": "PSYCHOLOGY",
    },
    {
        "rule_num": "04",
        "title": "Multi-Pair Diversification",
        "body": (
            "Trading EURUSD and XAUUSD and calling it diversified is like buying two "
            "condos in the same building and calling it a property portfolio. Both "
            "fall when USD rips — same dollar, same drawdown, doubled. Real "
            "diversification means different DRIVERS, not different tickers. That's "
            "why AUDCAD is in this account: AUD moves on iron ore and gold demand, "
            "CAD moves on oil and the BoC rate cycle. Neither cares what the DXY did "
            "today. When my USD pairs are underwater together, AUDCAD is usually "
            "trading its own story. Four instruments, but only if their engines are "
            "different. Otherwise it's one trade wearing four costumes."
        ),
        "example_account": 3000,
        "example_risk": 75,
        "example_rr": "Cross-pair hedge, uncorrelated drivers",
        "example_target": 0,
        "tag": "DIVERSIFICATION",
    },
    {
        "rule_num": "05",
        "title": "Win Rate vs Profit Factor",
        "body": (
            "A 70% win rate with a Profit Factor of 0.8 loses money. Read that again. "
            "You can win 7 trades out of 10 and still bleed out, because the 3 losers "
            "were bigger than the 7 winners combined. Win rate is how often you're "
            "right. Profit Factor is whether being right actually pays: total wins "
            "divided by total losses. Below 1.0, your account is a slow donation to "
            "the market. Signal sellers advertise win rate because it's the vanity "
            "metric — it feels good and hides everything. I publish mine anyway, next "
            "to the PF, on Myfxbook #12044019. Go check the live number. If someone "
            "shows you win rate without profit factor, they're showing you half a "
            "report card and hoping you don't ask for the rest."
        ),
        "example_account": 3000,
        "example_risk": 100,
        "example_rr": "Win Rate vs PF — see live account on Myfxbook #12044019",
        "example_target": 0,
        "tag": "METRICS",
    },
]

PAIRS = [
    {
        "pair": "EURUSD",
        "full_name": "Euro / US Dollar",
        "best_session": "London+NY 1300-1700 SGT",
        "avg_spread": "0.0-0.2 pips (IC Raw)",
        "volatility": "Medium, 60-90 pips/day",
        "my_edge": (
            "EURUSD is where I learned that boring is profitable. It's the deepest "
            "market in the world, so it respects structure better than anything else "
            "I trade — when the 4H trend is set, pullbacks actually hold where they "
            "should. The algo reads that 4H bias and stacks entries with the dominant "
            "cycle during the London-NY overlap, when real institutional flow is in "
            "the book. I deliberately shut it off in Asian hours. I paid the tuition "
            "on that one: thin liquidity, wider spreads, and false breaks that look "
            "perfect right up until they trap you. No overlap, no trade."
        ),
        "quote": (
            "EURUSD doesn't hide anything. If you can't read this chart, "
            "the problem isn't the chart."
        ),
    },
    {
        "pair": "AUDCAD",
        "full_name": "Australian Dollar / Canadian Dollar",
        "best_session": "Asian-London overlap 0800-1100 SGT",
        "avg_spread": "0.5-1.0 pips (IC Raw)",
        "volatility": "Low-Med, 40-70 pips/day",
        "my_edge": (
            "Nobody brags about trading AUDCAD, which is exactly why I do. It's my "
            "insurance policy: AUD runs on iron ore and gold demand out of China, CAD "
            "runs on oil and the Bank of Canada. No USD leg at all — so on the days "
            "when a dollar move puts my XAUUSD and EURUSD positions underwater "
            "together, AUDCAD is off trading its own macro story. The algo works the "
            "0800-1100 SGT window when Sydney flow is still live and London desks are "
            "waking up. Risk stays small and defined: 0.01 lots with a 50-pip stop is "
            "about $4. Slow pair, small moves, but it's kept the equity curve "
            "breathing through more than one USD storm. Every position is live on "
            "Myfxbook #12044019."
        ),
        "quote": (
            "Diversification isn't owning more pairs. It's owning "
            "different reasons to be right."
        ),
    },
    {
        "pair": "XAUUSD",
        "full_name": "Gold / US Dollar",
        "best_session": "NY Open 2130-0000 SGT",
        "avg_spread": "0.2-0.5 pips (IC Raw)",
        "volatility": "High, $15-30 USD/session",
        "my_edge": (
            "Gold is the pair that punishes ego fastest, so I took my ego out of it. "
            "The algo never trades the news candle — that spike is a coin flip with "
            "slippage. What it waits for is the second move: retail chases the "
            "headline, gets exhausted, and then institutional flow finishes the real "
            "leg over the next few hours. That continuation is the trade. NY open, "
            "2130 SGT onwards, is when it's cleanest. The math is honest at this "
            "size: gold's session range runs $15-30, so 0.01 lots means $15-30 of P&L "
            "swing per position. Enough to matter, small enough to survive being "
            "wrong. No manual overrides on news nights. Especially on news nights."
        ),
        "quote": (
            "The headline is the bait. The move after the move "
            "is the trade."
        ),
    },
    {
        "pair": "USDJPY",
        "full_name": "US Dollar / Japanese Yen",
        "best_session": "Asian 0100-0800 SGT",
        "avg_spread": "0.0-0.3 pips (IC Raw)",
        "volatility": "Low-Med, 50-80 pips/day",
        "my_edge": (
            "This is my home-timezone edge. While London sleeps, Tokyo keeps USDJPY "
            "in a 30-60 pip box from 0100-0800 SGT — and the market knows retail "
            "stops are parked just outside it. So it goes and gets them: a spike "
            "through the range high or low that reverses within a candle or two. "
            "Most traders get stopped by that move. The algo is built to trade it — "
            "mark the box, wait for the false break, fade the spike back inside. "
            "It's not glamorous and it won't make a highlight reel, but it repeats "
            "week after week, and repeatable is the only edge that compounds."
        ),
        "quote": (
            "Tokyo builds the range, London raids it. Decide which "
            "side of that trade you're on."
        ),
    },
]

SETUPS = [
    {
        "pair": "EURUSD",
        "direction": "LONG",
        "setup_type": "Trend Continuation: Liquidity Sweep + Reentry",
        "timeframe": "H4 Bias · H1 Structure · M15 Entry",
        "rr": "1:2.5",
        "steps": [
            (
                "H4 Bias Confirmed",
                "Open the H4 chart first, always. Price holding above the key EMA with a clean "
                "staircase of higher highs and higher lows. If you have to squint to see the "
                "uptrend, there isn't one — skip the day. You are only ever hunting longs while "
                "this holds."
            ),
            (
                "Liquidity Sweep Identified",
                "Price dips below the most recent H1 swing low — the level where every breakout "
                "trader parked their stop — then snaps back above it within one or two candles. "
                "That wick isn't weakness; it's institutions filling size on retail stop-losses. "
                "A close BACK above the old low is what makes it a sweep and not a breakdown."
            ),
            (
                "Structure Break on M15",
                "Drop to M15. After the sweep, wait for price to break and close above the last "
                "M15 lower high. This is the market confirming the reversal in real time — not "
                "you predicting it. No break of structure, no trade. Ever. The sweep alone is a "
                "guess; the BOS makes it a setup."
            ),
            (
                "Entry + Risk Parameters",
                "Enter long on the close of the M15 break-of-structure candle. Stop goes below "
                "the sweep wick — if price returns there, the whole idea is invalid. Target the "
                "next H4 resistance. Size the position off M15 ATR so risk is max 1% of account, "
                "never a fixed lot. If the distance to target isn't at least 2.5x the distance "
                "to your stop, pass. The setup will come again; the capital might not."
            ),
        ],
    },
    {
        "pair": "XAUUSD",
        "direction": "SHORT",
        "setup_type": "Institutional Rejection: Premium Zone Short",
        "timeframe": "H4 Supply · H1 Confirmation · M15 Entry",
        "rr": "1:2.0",
        "steps": [
            (
                "H4 Supply Zone",
                "Find the last H4 candle cluster where a strong bearish impulse launched from — "
                "the origin, not the middle of the move. That's where institutional sell orders "
                "sat, and unfilled orders tend to still be waiting there. Draw the zone from the "
                "candle bodies to the wick highs. Draw it once, before price gets there, and "
                "don't redraw it to fit your bias later."
            ),
            (
                "Price Returns to Supply",
                "Gold rallies back into the zone. This is where the trade gets psychologically "
                "hard: the chart looks bullish, and you're preparing to short. That's the point. "
                "Retail sees a rally into the zone; institutions see their earlier prices back "
                "on sale. Do nothing yet — being inside the zone is location, not a trigger."
            ),
            (
                "H1 Rejection Candle",
                "Wait for the H1 to print rejection inside the zone: a bearish engulfing or a "
                "shooting star with the wick stabbing into supply and the close pushed back out. "
                "A volume spike on that candle is the bonus tell that real size is selling. No "
                "rejection candle means no sellers showed up — a supply zone without sellers is "
                "just a rectangle you drew."
            ),
            (
                "M15 Short Entry",
                "Short on the M15 break below the H1 rejection candle's low. Stop above the "
                "supply zone's wick high — beyond it, the zone has failed. Target the next H4 "
                "demand zone. Risk max 1% of account, ATR-sized on M15. Minimum 1:2 or skip it. "
                "Gold moves fast in both directions; the stop is not optional and it is not mental."
            ),
        ],
    },
    {
        "pair": "AUDCAD",
        "direction": "LONG",
        "setup_type": "Commodity Correlation: AUD Strength on Macro Tailwind",
        "timeframe": "H4 Bias · H1 Structure · M15 Entry",
        "rr": "1:2.0",
        "steps": [
            (
                "H4 Macro Alignment",
                "This trade starts away from the chart. Check the drivers: gold and iron ore bid "
                "(AUD tailwind), oil pulling back or BoC turning dovish (CAD headwind). You need "
                "BOTH legs pushing the same way — one strong currency against one weak one, not "
                "two neutrals. Then confirm the H4 chart agrees with higher lows on AUDCAD. "
                "Macro says why, chart says when. If they disagree, believe the chart and stand down."
            ),
            (
                "H1 Structure Break",
                "Wait for H1 to close cleanly above the last significant resistance — a full "
                "candle body through the level, not a wick poking over it. Wicks are noise; "
                "closes are commitment. This close is the footprint that says positioned money "
                "agrees with your macro read. Chasing the breakout candle itself is how you buy "
                "the top of the move."
            ),
            (
                "M15 Pullback Entry",
                "Let the breakout come back to you. Price retraces to retest the broken H1 "
                "resistance, which should now act as support. On M15, wait for a bullish "
                "confirmation candle to close at that level — that's your trigger. If price "
                "closes back below the old resistance instead, the breakout failed: cancel the "
                "idea completely, don't 'wait and see' your way into a loss."
            ),
            (
                "Entry + Risk Parameters",
                "Long on the M15 confirmation close. Stop below the H1 structural support. "
                "Target the next H4 resistance, minimum 1:2 or no trade. Risk capped at 1% of "
                "account, ATR-sized on M15. One hard rule: stand aside around BoC rate decisions "
                "and Australian employment data. AUDCAD spreads can triple in those minutes and "
                "slippage will eat a good entry alive. Missing a trade costs nothing; forcing one "
                "costs plenty."
            ),
        ],
    },
    {
        "pair": "USDJPY",
        "direction": "SHORT",
        "setup_type": "Asian False Break: Mean Reversion",
        "timeframe": "H1 Range · M15 Signal · M5 Trigger",
        "rr": "1:2.0",
        "steps": [
            (
                "Define Tight Asia Range",
                "From 0100 SGT, mark the developing high and low of the Tokyo session on H1. "
                "You're looking for a tight, well-respected box of roughly 30-60 pips with "
                "multiple touches on each side. If the session is trending or the range is "
                "sloppy and wide, this setup doesn't exist today. A bad range fades into a "
                "fake edge — most losses on this play come from forcing a box that isn't there."
            ),
            (
                "Spot the False Break",
                "Before or around London open, price spikes above the range high — straight "
                "into the cluster of retail buy stops sitting there — then closes back INSIDE "
                "the range. That close back inside is everything. A spike still holding above "
                "the high is a breakout you leave alone; a spike swallowed back into the box "
                "is a liquidity hunt, and the fuel above the range is now spent."
            ),
            (
                "M15 Bearish Confirmation",
                "Don't short the spike itself — let it prove it's dead. On M15, wait for price "
                "to attempt higher and fail, printing a lower high below the range high. That "
                "lower high is the confirmation that the buyers who chased the break are trapped "
                "and there's nobody left to push. It costs a few pips of entry price and saves "
                "you from the double-spike that wrecks impatient fades."
            ),
            (
                "Short Entry + Parameters",
                "Short at the M15 lower high. Stop above the false-break wick — if price takes "
                "that out, it was a real breakout and you're wrong, cleanly and cheaply. First "
                "target is the Asia range low; stretch to the next H1 support if structure "
                "allows, minimum 1:2. Risk max 1% of account, ATR-sized on M15. Mean reversion "
                "pays the patient and punishes the eager — this whole setup is a patience test "
                "with an entry attached."
            ),
        ],
    },
]

# 14-slot, 7-week rotation: every Tue + Thu gets one slot
ROTATION_SEQUENCE = [
    ("risk",  0),   # Week 1 Tue  — Lot Sizing By Balance
    ("pairs", 0),   # Week 1 Thu  — Pair: EURUSD
    ("setup", 0),   # Week 2 Tue  — Setup: EURUSD Liquidity Sweep Long
    ("risk",  1),   # Week 2 Thu  — Grid Spacing Discipline
    ("pairs", 2),   # Week 3 Tue  — Pair: XAUUSD
    ("setup", 1),   # Week 3 Thu  — Setup: XAUUSD Premium Zone Short
    ("risk",  2),   # Week 4 Tue  — Balance vs Equity Drawdown
    ("pairs", 1),   # Week 4 Thu  — Pair: AUDCAD
    ("setup", 2),   # Week 5 Tue  — Setup: AUDCAD Commodity Correlation Long
    ("risk",  3),   # Week 5 Thu  — Multi-Pair Diversification
    ("pairs", 3),   # Week 6 Tue  — Pair: USDJPY
    ("setup", 3),   # Week 6 Thu  — Setup: USDJPY Asian False Break
    ("risk",  4),   # Week 7 Tue  — Win Rate vs Profit Factor
    ("setup", 0),   # Week 7 Thu  — Setup: EURUSD Liquidity Sweep (high-value repeat)
]


def get_edu_content(index: int) -> tuple[str, dict]:
    """Return (post_type, content_dict) for the given rotation index."""
    slot = ROTATION_SEQUENCE[index % len(ROTATION_SEQUENCE)]
    post_type, content_index = slot
    if post_type == "risk":
        return post_type, RISK_RULES[content_index]
    if post_type == "pairs":
        return post_type, PAIRS[content_index]
    return post_type, SETUPS[content_index]
