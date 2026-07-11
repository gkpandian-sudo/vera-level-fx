# instagram/higgsfield/hashtags.py
_TIER_1_EN = [
    "#forexsingapore", "#sgtrader", "#xauusd", "#forexsg", "#sgforex",
    "#forextrader", "#goldfx", "#eurusd", "#myfxbook", "#icmarkets",
]
_TIER_2 = [
    "#forexeducation", "#riskmanagement", "#tradingpsychology",
    "#learnforex", "#forexanalysis", "#positionsizing",
    "#forexstrategy", "#tradingmindset",
]
_TIER_3 = ["#forex", "#trading", "#gold", "#financialfreedom", "#invest"]

_TAMIL_PIN = "#tamiltrader"
_TIER_1_TAMIL = [
    "#tamilforex", "#forexsingapore", "#sgtrader",
    "#xauusd", "#forexsg", "#goldfx", "#eurusd", "#myfxbook",
    "#icmarkets", "#sgforex",
]


def _rotate(pool: list[str], start: int, count: int) -> list[str]:
    n = len(pool)
    return [pool[(start + i) % n] for i in range(count)]


def get_hashtags(reel_index: int) -> list[str]:
    """Return 11 unique hashtags (5 T1 + 4 T2 + 2 T3), rotated by reel_index."""
    t1 = _rotate(_TIER_1_EN, reel_index * 3, 5)
    t2 = _rotate(_TIER_2,    reel_index * 2, 4)
    t3 = _rotate(_TIER_3,    reel_index,     2)
    # De-duplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for tag in t1 + t2 + t3:
        if tag not in seen:
            seen.add(tag)
            result.append(tag)
    # If duplication removed some, pad from tier 3
    extras = [t for t in _TIER_3 if t not in seen]
    result.extend(extras[:max(0, 11 - len(result))])
    return result[:11]


def get_hashtags_tamil(reel_index: int) -> list[str]:
    """Tamil-specific hashtag set — always includes #tamiltrader."""
    t1_rest = _rotate(_TIER_1_TAMIL, reel_index * 3, 4)
    t1 = [_TAMIL_PIN] + t1_rest
    t2 = _rotate(_TIER_2, reel_index * 2, 4)
    t3 = _rotate(_TIER_3, reel_index, 2)
    seen: set[str] = set()
    result: list[str] = []
    for tag in t1 + t2 + t3:
        if tag not in seen:
            seen.add(tag)
            result.append(tag)
    extras = [t for t in _TIER_3 if t not in seen]
    result.extend(extras[:max(0, 11 - len(result))])
    return result[:11]
