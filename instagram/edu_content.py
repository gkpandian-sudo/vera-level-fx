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
            "Professional algos never risk a fixed dollar amount. They risk a fixed "
            "percentage of current balance. At 0.01 lots per $333, your position "
            "scales with your account, so drawdowns shrink in real terms as balance drops. "
            "On XAUUSD at 0.01 lots, a 30-pip stop costs $3. At $1,000 balance that is "
            "0.3% risk, inside the 1% hard cap with room for recovery positions. "
            "This system sizes by ATR, not fixed lots, so position size adjusts as "
            "XAUUSD volatility expands."
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
            "In a multi-position system, each additional level must have minimum 100-pip "
            "spacing. Tighter grids stack exposure too fast. You do not survive the "
            "recovery. Wide spacing buys time for the market to breathe and reverse. "
            "XAUUSD can run more than 1,000 pips in a single high-impact news session. "
            "At 100-pip spacing that is 10 levels of room before margin pressure. "
            "At 50-pip spacing, half the room and double the exposure."
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
            "Balance drawdown counts realised, closed losses. Equity drawdown counts "
            "floating open positions. The two can diverge sharply: an account can show "
            "a stable balance while equity floats deep underwater on open trades. "
            "Most retail traders panic-close at maximum pain, right before the reversal. "
            "This is why the system has a hard daily drawdown limit: not to avoid losses, "
            "but to prevent a single session from forcing irrational closes."
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
            "Never concentrate all positions in one pair. Running 4+ uncorrelated "
            "instruments means one pair's drawdown gets offset by others trending "
            "profitably. EURUSD and XAUUSD both fall on USD strength because they share "
            "dollar exposure. AUDCAD is driven by commodity prices and the RBA rate "
            "differential, not the DXY. That makes it a genuine diversification pair "
            "alongside the major USD crosses."
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
            "Profit Factor below 1.0 means the account pays out more in losses than "
            "it collects in wins. Check the current PF on Myfxbook #12044019 — that "
            "live number is the benchmark. Win rate tells you how often you win. "
            "Profit Factor tells you whether it matters. A 70% win rate with PF 0.8 "
            "still loses money."
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
            "Cleanest structure of all pairs. The algo reads the 4H trend and stacks "
            "positions in the direction of the dominant cycle. Best pair for "
            "trend-continuation entries during London and NY overlap. "
            "Asian session excluded. Spreads widen and false breaks are frequent "
            "when institutional flow is absent."
        ),
        "quote": (
            "The most traded pair in the world. Institutional flow leaves "
            "visible footprints in its price action."
        ),
    },
    {
        "pair": "GBPJPY",
        "full_name": "British Pound / Japanese Yen",
        "best_session": "London Open 1500-1800 SGT",
        "avg_spread": "1.0-1.5 pips (IC Raw)",
        "volatility": "Very High, 150-200 pips/day",
        "my_edge": (
            "The London open (1500-1800 SGT) regularly prints 80-100 pip directional "
            "moves. The Asia session range (0100-0800) acts as the reference zone. "
            "Breakout above or below the range at London open defines the day's "
            "directional bias. When the trend is confirmed on H4, a 3-level "
            "grid can close at breakeven or better within hours."
        ),
        "quote": (
            "High volatility is not the risk. Sizing that ignores it is. "
            "GBPJPY demands wider stops and smaller lots."
        ),
    },
    {
        "pair": "XAUUSD",
        "full_name": "Gold / US Dollar",
        "best_session": "NY Open 2130-0000 SGT",
        "avg_spread": "0.2-0.5 pips (IC Raw)",
        "volatility": "High, $15-30 USD/session",
        "my_edge": (
            "Gold reacts sharply to DXY and macro news. The algo avoids major news "
            "windows and targets the post-news continuation leg. Institutional flow "
            "completes its move after retail chasing has exhausted. "
            "Gold's ATR per session runs $15-30. At 0.01 lots that is $15-30 P&L "
            "per position per session. No news-event overrides, by design."
        ),
        "quote": (
            "Gold prices in macro sentiment faster than most instruments. "
            "Trade the reaction, not the headline."
        ),
    },
    {
        "pair": "USDJPY",
        "full_name": "US Dollar / Japanese Yen",
        "best_session": "Asian 0100-0800 SGT",
        "avg_spread": "0.0-0.3 pips (IC Raw)",
        "volatility": "Low-Med, 50-80 pips/day",
        "my_edge": (
            "The Tokyo session holds USDJPY in a 30-60 pip range from 0100-0800 SGT. "
            "False breaks above or below this range before London open are "
            "high-probability mean-reversion setups. The algo identifies the session "
            "boundary, waits for the false break, then fades the spike back into range. "
            "Clean, systematic, repeatable."
        ),
        "quote": (
            "In Tokyo hours, USDJPY is one of the most range-bound pairs on the board. "
            "Patience in Asia pays in London."
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
                "Price above key EMA. Higher highs, higher lows intact. "
                "Institutional trend is bullish."
            ),
            (
                "Liquidity Sweep Identified",
                "Price dips below previous H1 swing low, sweeps retail stop-losses, "
                "then immediately reverses. Smart money accumulation signal."
            ),
            (
                "Structure Break on M15",
                "After sweep, M15 breaks the last lower high. Confirms reversal and "
                "trend resumption. This is the entry trigger."
            ),
            (
                "Entry + Risk Parameters",
                "Long entry on M15 BOS candle close. SL below liquidity sweep wick. "
                "TP at next H4 resistance level. Max risk: 1% of account, sized by "
                "ATR on M15, not fixed lots. Minimum 1:2.5 RR required to take the trade."
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
                "Identify the last strong bearish impulse origin. This is the "
                "institutional supply zone. Mark the body and wicks."
            ),
            (
                "Price Returns to Supply",
                "Gold rallies back into the supply zone. Retail traders see "
                "a breakout. Institutions see a reloading opportunity."
            ),
            (
                "H1 Rejection Candle",
                "Bearish engulfing or shooting star inside the zone confirms "
                "institutional selling pressure. Volume spike is ideal."
            ),
            (
                "M15 Short Entry",
                "Short on break of H1 rejection candle low. SL above supply zone. "
                "TP at next H4 demand zone. Max risk: 1% of account, sized by ATR "
                "on M15. Minimum 1:2 RR required."
            ),
        ],
    },
    {
        "pair": "GBPJPY",
        "direction": "LONG",
        "setup_type": "London Open Momentum: Breakout + Retest",
        "timeframe": "H1 Range · M15 Break · M5 Entry",
        "rr": "1:2.5",
        "steps": [
            (
                "Define Asia Session Range",
                "Mark GBPJPY high and low from 01:00-08:00 SGT. "
                "This range becomes the battle zone at London open."
            ),
            (
                "London Open Candle",
                "At 15:00 SGT, watch for a strong directional candle breaking "
                "the Asia range with momentum. This is institutional London flow."
            ),
            (
                "Retest Entry",
                "Price breaks the Asia high then pulls back to test it as support. "
                "M5 bullish confirmation candle at that level = high probability entry."
            ),
            (
                "Entry + Management",
                "Long at retest. SL below Asia range high (now support). "
                "TP = 2x the Asia range height projected upward. Trail stop at 1:1. "
                "Max risk: 1% of account, sized by ATR. No entry if spread exceeds 2 pips."
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
                "USDJPY during 01:00-08:00 SGT typically holds a 30-60 pip range. "
                "Mark the high and low clearly."
            ),
            (
                "Spot the False Break",
                "Price spikes above the range high (triggering retail buy stops) "
                "then closes back below. Classic liquidity hunt. This is the signal."
            ),
            (
                "M15 Bearish Confirmation",
                "After the false break, wait for M15 to form a lower high below the "
                "range high. This confirms reversal and institutional direction."
            ),
            (
                "Short Entry + Parameters",
                "Short at M15 lower high. SL above the false break wick. "
                "TP at Asia range low or next H1 support for 1:2+. "
                "Max risk: 1% of account, sized by ATR on M15."
            ),
        ],
    },
]

# 12-slot, 6-week rotation: every Tue + Thu gets one slot
ROTATION_SEQUENCE = [
    ("risk",  0),   # Week 1 Tue  — Lot Sizing By Balance
    ("pairs", 0),   # Week 1 Thu  — Pair: EURUSD
    ("setup", 0),   # Week 2 Tue  — Setup: EURUSD Liquidity Sweep Long
    ("risk",  1),   # Week 2 Thu  — Grid Spacing Discipline
    ("pairs", 2),   # Week 3 Tue  — Pair: XAUUSD
    ("setup", 1),   # Week 3 Thu  — Setup: XAUUSD Premium Zone Short
    ("risk",  2),   # Week 4 Tue  — Balance vs Equity Drawdown
    ("pairs", 1),   # Week 4 Thu  — Pair: GBPJPY
    ("setup", 2),   # Week 5 Tue  — Setup: GBPJPY London Breakout
    ("risk",  3),   # Week 5 Thu  — Multi-Pair Diversification
    ("pairs", 3),   # Week 6 Tue  — Pair: USDJPY
    ("setup", 3),   # Week 6 Thu  — Setup: USDJPY Asian False Break
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
