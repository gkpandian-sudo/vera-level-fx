# instagram/edu_content.py

RISK_RULES = [
    {
        "rule_num": "01",
        "title": "The 1% Rule",
        "body": "Never risk more than 1% of your account on a single trade. One bad trade should never wipe your week.",
        "example_account": 10000,
        "example_risk": 100,
        "example_rr": "1:2.5",
        "example_target": 250,
        "tag": "ESSENTIAL",
    },
    {
        "rule_num": "02",
        "title": "Daily Drawdown Limit",
        "body": "If you're down 3% in a single day, close everything and stop trading. Protect the week, not the session.",
        "example_account": 10000,
        "example_risk": 300,
        "example_rr": "Daily limit",
        "example_target": 0,
        "tag": "PROTECTION",
    },
    {
        "rule_num": "03",
        "title": "ATR-Based Position Sizing",
        "body": "Let the market's volatility decide your lot size — not your gut. High ATR = smaller lots. Low ATR = larger lots.",
        "example_account": 10000,
        "example_risk": 100,
        "example_rr": "ATR x multiplier",
        "example_target": 0,
        "tag": "SIZING",
    },
    {
        "rule_num": "04",
        "title": "Minimum Risk:Reward",
        "body": "Only take trades offering at least 1:2 RR. If the reward doesn't justify the risk, skip the trade. Always.",
        "example_account": 10000,
        "example_risk": 100,
        "example_rr": "1:2 minimum",
        "example_target": 200,
        "tag": "SELECTION",
    },
    {
        "rule_num": "05",
        "title": "No News Trading",
        "body": "High-impact news (NFP, CPI, FOMC) creates random spikes that invalidate technical setups. Sit out or close early.",
        "example_account": 10000,
        "example_risk": 0,
        "example_rr": "Skip the trade",
        "example_target": 0,
        "tag": "DISCIPLINE",
    },
]

PAIRS = [
    {
        "pair": "EURUSD",
        "full_name": "Euro / US Dollar",
        "best_session": "London/NY",
        "avg_spread": "0.1 pip",
        "volatility": "Medium",
        "my_edge": "H4 Trend",
        "quote": "Most liquid pair in the world. Clean structure, respects levels — my bread and butter.",
    },
    {
        "pair": "GBPJPY",
        "full_name": "British Pound / Japanese Yen",
        "best_session": "London Open",
        "avg_spread": "1.2 pips",
        "volatility": "Very High",
        "my_edge": "Breakout",
        "quote": "The Dragon. Volatile, aggressive, and rewarding when you read the momentum right.",
    },
    {
        "pair": "XAUUSD",
        "full_name": "Gold / US Dollar",
        "best_session": "NY Open",
        "avg_spread": "0.3 pip",
        "volatility": "High",
        "my_edge": "S&R Levels",
        "quote": "Gold rewards patience. Wait for the key level — then strike with full conviction.",
    },
    {
        "pair": "USDJPY",
        "full_name": "US Dollar / Japanese Yen",
        "best_session": "Asian Session",
        "avg_spread": "0.2 pip",
        "volatility": "Low-Med",
        "my_edge": "Range Play",
        "quote": "The Asian session king. Predictable ranges when Tokyo is in control.",
    },
]

SETUPS = [
    {
        "pair": "GBPJPY",
        "direction": "LONG",
        "setup_type": "Trend Continuation",
        "timeframe": "H4 · H1 · M15",
        "rr": "1:2.5",
        "steps": [
            ("H4 Bias — Bullish", "Price above 20 EMA, higher highs structure confirmed"),
            ("H1 Entry Zone", "Pullback to key support + bullish engulfing candle"),
            ("M15 Trigger", "Momentum entry — SL below swing low, TP next H4 resistance"),
        ],
    },
    {
        "pair": "XAUUSD",
        "direction": "SHORT",
        "setup_type": "S&R Reversal",
        "timeframe": "H4 · H1 · M15",
        "rr": "1:2.0",
        "steps": [
            ("H4 Key Resistance", "Price rejected from major resistance zone — bearish wick"),
            ("H1 Confirmation", "Lower high formed + bearish engulfing below zone"),
            ("M15 Entry", "Momentum entry short — SL above wick, TP next S1 level"),
        ],
    },
    {
        "pair": "EURUSD",
        "direction": "LONG",
        "setup_type": "London Breakout",
        "timeframe": "H1 · M15 · M5",
        "rr": "1:2.5",
        "steps": [
            ("Pre-London Range", "Identify Asia session high/low — mark both levels"),
            ("Breakout Candle", "London open breaks Asia high with strong momentum candle"),
            ("Retest Entry", "Wait for pullback to broken level — enter on M5 confirmation"),
        ],
    },
    {
        "pair": "USDJPY",
        "direction": "SHORT",
        "setup_type": "Asian Range Break",
        "timeframe": "H1 · M15",
        "rr": "1:2.0",
        "steps": [
            ("Define Range", "Mark Asian session high and low (typically 30-60 pip range)"),
            ("False Break Check", "Price spikes above range then reverses — bearish signal"),
            ("Short on Retest", "Enter short on retest of range low — SL above range high"),
        ],
    },
]

# 12-slot rotation sequence: (type, index_into_type_list)
ROTATION_SEQUENCE = [
    ("risk",  0),   # Week 1 Tue  — Risk: 1% Rule
    ("pairs", 0),   # Week 1 Thu  — Pair: EURUSD
    ("setup", 0),   # Week 2 Tue  — Setup: GBPJPY Trend
    ("risk",  1),   # Week 2 Thu  — Risk: Daily DD Limit
    ("pairs", 2),   # Week 3 Tue  — Pair: XAUUSD
    ("setup", 1),   # Week 3 Thu  — Setup: XAUUSD S&R
    ("risk",  2),   # Week 4 Tue  — Risk: ATR Sizing
    ("pairs", 1),   # Week 4 Thu  — Pair: GBPJPY
    ("setup", 2),   # Week 5 Tue  — Setup: EURUSD Breakout
    ("risk",  3),   # Week 5 Thu  — Risk: RR Minimum
    ("pairs", 3),   # Week 6 Tue  — Pair: USDJPY
    ("setup", 3),   # Week 6 Thu  — Setup: USDJPY Range
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
