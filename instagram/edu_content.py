# instagram/edu_content.py
# Educational content for rotating Instagram posts — Vera Level FX
# Methodology: quantitative multi-pair algorithmic system on IC Markets
# Source inspiration: LQS engine concepts (liquidity, quantitative sizing, structure)
# DO NOT reference external system names in captions

RISK_RULES = [
    {
        "rule_num": "01",
        "title": "Lot Sizing By Balance",
        "body": (
            "Professional algos never risk a fixed dollar amount — they risk a fixed "
            "percentage of current balance. At 0.01 lots per $333, your position "
            "scales with your account, so drawdowns shrink in real terms as balance drops."
        ),
        "example_account": 3000,
        "example_risk": 90,
        "example_rr": "1:2.5 RR",
        "example_target": 225,
        "tag": "SIZING",
    },
    {
        "rule_num": "02",
        "title": "Grid Spacing Discipline",
        "body": (
            "In a multi-position system, each additional level must have minimum 100-pip "
            "spacing. Tighter grids stack exposure too fast — you don't survive the "
            "recovery. Wide spacing buys time for the market to breathe and reverse."
        ),
        "example_account": 3000,
        "example_risk": 30,
        "example_rr": "Per grid level",
        "example_target": 0,
        "tag": "GRID CONTROL",
    },
    {
        "rule_num": "03",
        "title": "Balance vs Equity Drawdown",
        "body": (
            "Balance drawdown = realised closed losses. Equity drawdown = floating "
            "open positions. A 50% equity drawdown with 2% balance drawdown means the "
            "system is in recovery — not dead. Most retail traders panic-close right "
            "before the reversal."
        ),
        "example_account": 3000,
        "example_risk": 60,
        "example_rr": "Equity vs Balance",
        "example_target": 0,
        "tag": "PSYCHOLOGY",
    },
    {
        "rule_num": "04",
        "title": "Multi-Pair Diversification",
        "body": (
            "Never concentrate all positions in one pair. Running 4+ uncorrelated "
            "instruments means one pair's drawdown gets offset by others trending "
            "profitably. EURUSD, GBPJPY, XAUUSD and USDJPY each react differently to "
            "the same macro event."
        ),
        "example_account": 3000,
        "example_risk": 75,
        "example_rr": "Cross-pair hedge",
        "example_target": 0,
        "tag": "DIVERSIFICATION",
    },
    {
        "rule_num": "05",
        "title": "Win Rate vs Profit Factor",
        "body": (
            "A 76% win rate sounds great — but it means nothing without profit factor. "
            "Our system's 673 trades show that the 24% of losses are small and the 76% "
            "of wins are large. Profit Factor > 1.5 is institutional. Below 1.0 means "
            "you're bleeding slowly."
        ),
        "example_account": 3000,
        "example_risk": 100,
        "example_rr": "PF > 1.5 target",
        "example_target": 0,
        "tag": "METRICS",
    },
]

PAIRS = [
    {
        "pair": "EURUSD",
        "full_name": "Euro / US Dollar",
        "best_session": "London + NY Overlap (13:00–17:00 SGT)",
        "avg_spread": "0.0–0.2 pips (IC Raw)",
        "volatility": "Medium — 60–90 pips/day avg",
        "my_edge": (
            "Cleanest structure of all pairs. Algo reads the 4H trend and stacks "
            "positions in the direction of the dominant cycle. Best pair for "
            "trend-continuation grid entries."
        ),
        "quote": (
            "The most liquid instrument on earth. Institutional flow is visible in the "
            "price action if you know where to look."
        ),
    },
    {
        "pair": "GBPJPY",
        "full_name": "British Pound / Japanese Yen",
        "best_session": "London Open (15:00–18:00 SGT)",
        "avg_spread": "1.0–1.5 pips (IC Raw)",
        "volatility": "Very High — 150–200 pips/day avg",
        "my_edge": (
            "Wide daily range creates fast recovery windows for grid systems. "
            "When the trend is confirmed on H4, even a 3-level grid closes at "
            "breakeven or better within hours — not days."
        ),
        "quote": (
            "The Dragon moves fast and hard. It punishes indecision but rewards "
            "systematic entries at key structural levels."
        ),
    },
    {
        "pair": "XAUUSD",
        "full_name": "Gold / US Dollar",
        "best_session": "NY Open (21:30–00:00 SGT)",
        "avg_spread": "0.2–0.5 pips (IC Raw)",
        "volatility": "High — $15–$30 range per session",
        "my_edge": (
            "Gold reacts sharply to DXY and macro news. The algo avoids major news "
            "windows and targets the post-news continuation leg — where institutional "
            "flow completes its move without retail chasing it."
        ),
        "quote": (
            "Gold tells you what institutions think before equities do. Follow the "
            "smart money, not the headlines."
        ),
    },
    {
        "pair": "USDJPY",
        "full_name": "US Dollar / Japanese Yen",
        "best_session": "Asian Session (01:00–08:00 SGT)",
        "avg_spread": "0.0–0.3 pips (IC Raw)",
        "volatility": "Low–Med — 50–80 pips/day avg",
        "my_edge": (
            "Tight Asian ranges create high-probability mean-reversion zones. "
            "The algo identifies the session boundary, waits for a false break, "
            "then fades the spike back into range — clean, systematic, repeatable."
        ),
        "quote": (
            "In Tokyo hours, USDJPY is the most predictable pair on the board. "
            "Patience in Asia pays in London."
        ),
    },
]

SETUPS = [
    {
        "pair": "EURUSD",
        "direction": "LONG",
        "setup_type": "Trend Continuation — Liquidity Sweep + Reentry",
        "timeframe": "H4 Bias · H1 Structure · M15 Entry",
        "rr": "1:2.5",
        "steps": [
            (
                "H4 Bias Confirmed",
                "Price above key EMA — higher highs, higher lows intact. "
                "Institutional trend is bullish."
            ),
            (
                "Liquidity Sweep Identified",
                "Price dips below previous H1 swing low, sweeps retail stop-losses, "
                "then immediately reverses — smart money accumulation signal."
            ),
            (
                "Structure Break on M15",
                "After sweep, M15 breaks the last lower high — confirms reversal and "
                "trend resumption. This is the entry trigger."
            ),
            (
                "Entry + Risk Parameters",
                "Long entry on M15 BOS candle close. SL below liquidity sweep wick. "
                "TP at next H4 resistance level — minimum 1:2.5 RR required."
            ),
        ],
    },
    {
        "pair": "XAUUSD",
        "direction": "SHORT",
        "setup_type": "Institutional Rejection — Premium Zone Short",
        "timeframe": "H4 Supply · H1 Confirmation · M15 Entry",
        "rr": "1:2.0",
        "steps": [
            (
                "H4 Supply Zone",
                "Identify the last strong bearish impulse origin — this is the "
                "institutional supply zone. Mark the body and wicks."
            ),
            (
                "Price Returns to Supply",
                "Gold rallies back into the supply zone — retail traders see "
                "'breakout', institutions see a reloading opportunity."
            ),
            (
                "H1 Rejection Candle",
                "Bearish engulfing or shooting star inside the zone confirms "
                "institutional selling pressure. Volume spike is ideal."
            ),
            (
                "M15 Short Entry",
                "Short on break of H1 rejection candle low. SL above supply zone. "
                "TP at next H4 demand zone — 1:2 minimum."
            ),
        ],
    },
    {
        "pair": "GBPJPY",
        "direction": "LONG",
        "setup_type": "London Open Momentum — Breakout + Retest",
        "timeframe": "H1 Range · M15 Break · M5 Entry",
        "rr": "1:2.5",
        "steps": [
            (
                "Define Asia Session Range",
                "Mark GBPJPY high and low from 01:00–08:00 SGT. "
                "This range becomes the battle zone at London open."
            ),
            (
                "London Open Candle",
                "At 15:00 SGT, watch for a strong directional candle breaking "
                "the Asia range with momentum — this is institutional London flow."
            ),
            (
                "Retest Entry",
                "Price breaks the Asia high then pulls back to test it as support. "
                "M5 bullish confirmation candle at that level = high probability entry."
            ),
            (
                "Entry + Management",
                "Long at retest. SL below Asia range high (now support). "
                "TP = 2× the Asia range height projected upward. Trail stop at 1:1."
            ),
        ],
    },
    {
        "pair": "USDJPY",
        "direction": "SHORT",
        "setup_type": "Asian False Break — Mean Reversion",
        "timeframe": "H1 Range · M15 Signal · M5 Trigger",
        "rr": "1:2.0",
        "steps": [
            (
                "Define Tight Asia Range",
                "USDJPY during 01:00–08:00 SGT typically holds a 30–60 pip range. "
                "Mark the high and low clearly."
            ),
            (
                "Spot the False Break",
                "Price spikes above the range high (triggering retail buy stops) "
                "then closes back below — classic liquidity hunt. This is the signal."
            ),
            (
                "M15 Bearish Confirmation",
                "After the false break, wait for M15 to form a lower high below the "
                "range high. This confirms reversal and smart money direction."
            ),
            (
                "Short Entry + Parameters",
                "Short at M15 lower high. SL above the false break wick. "
                "TP at Asia range low — or extend to next H1 support for 1:2+."
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
