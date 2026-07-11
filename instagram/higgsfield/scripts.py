# instagram/higgsfield/scripts.py
from dataclasses import dataclass, field

_PROOF   = "Don't take my word for it. Myfxbook account 12044019 — open it right now and check every single trade."
_CTA_EN  = "Follow this account for the weekly P&L update. IC Markets link in bio — same broker, same account, same spreads as every trade you just saw. IB number 91936."
_CTA_EDU = "Save this post — you'll want it mid-trade, not mid-scroll. IC Markets link in bio for the broker setup behind these numbers."


@dataclass
class ReelScript:
    hook: str
    content: str
    proof: str
    cta: str
    language: str = 'en'
    reel_type: str = ''
    full_text: str = field(init=False)

    def __post_init__(self):
        self.full_text = f"{self.hook} {self.content} {self.proof} {self.cta}"


def _edu_script(edu_type: str, edu_content: dict) -> tuple[str, str]:
    title = edu_content.get('title', 'Risk Rule')
    body  = edu_content.get('body', '')
    ex_acc  = edu_content.get('example_account', 1000)
    ex_risk = edu_content.get('example_risk', 10)

    if edu_type == 'risk':
        hook    = f"Most traders blow their account doing this one thing. Rule {edu_content.get('rule_num','')}: {title}."
        content = (f"{body} "
                   f"On a ${ex_acc:,} account that means never more than ${ex_risk} on any single trade. "
                   f"Every position in my live IC Markets account is sized this exact way — you can verify it yourself.")
    elif edu_type == 'pairs':
        pair = edu_content.get('pair', 'XAUUSD')
        hook    = f"If you're trading {pair} and still paying wide spreads, you're handing your edge to the broker before the chart even moves."
        content = (f"Best session: {edu_content.get('best_session','')}. "
                   f"Average spread on IC Markets Raw: {edu_content.get('avg_spread','')}. "
                   f"Why I trade it: {edu_content.get('my_edge','')}.")
    else:  # setup
        pair      = edu_content.get('pair', 'XAUUSD')
        direction = edu_content.get('direction', '')
        rr        = edu_content.get('rr', '1:2.5')
        steps     = edu_content.get('steps', [])
        steps_str = ' '.join(f"Step {i+1}: {t} — {d}." for i, (t, d) in enumerate(steps[:3]))
        hook    = f"This exact setup on {pair} is behind every entry in my Myfxbook history. Here's the full checklist."
        content = f"{direction} setup, {rr} risk reward. {steps_str} Max risk one percent, ATR-sized, no exceptions."

    return hook, content


def build_script(
    reel_type: str,
    *,
    account: dict,
    edu_type: str = '',
    edu_content: dict | None = None,
    weekly_gain: float | None = None,
    language: str = 'en',
) -> ReelScript:
    """Assemble a 4-part ReelScript from live account data."""
    wr    = account.get('winRate') or 0
    pf    = account.get('profitFactor') or 0
    gain  = account.get('gain') or 0
    trades = int(account.get('trades') or 0)

    if reel_type == 'edu':
        if edu_content is None:
            raise ValueError("edu_content required for edu reel_type")
        hook, content = _edu_script(edu_type, edu_content)
        cta = _CTA_EDU

    elif reel_type == 'trust':
        hook    = ("Try to find a fake screenshot on this account. "
                   "One live broker. One public Myfxbook link. I'll wait.")
        content = (f"{wr:.0f} percent win rate across {trades:,} trades with a {pf:.2f} profit factor. "
                   f"But win rate alone means nothing — scammers run 95 percent using martingale right up until the account explodes. "
                   f"Mine comes with max one percent risk per trade and a one point two five average risk reward. "
                   f"Three steps to audit me: Myfxbook dot com, search Vera Level, check Track Record Verified and Trading Privileges Verified. "
                   f"Then open the Open Trades tab — it updates live, nothing can be edited after the fact.")
        cta = _CTA_EN

    elif reel_type == 'weekly':
        sign    = '+' if (weekly_gain or gain) >= 0 else ''
        figure  = f"{sign}{weekly_gain:.1f}" if weekly_gain is not None else f"{sign}{gain:.1f}"
        hook    = f"{figure} percent this week. Here are the two trades that made it — and the one I wish I hadn't taken."
        content = (f"Same rules as every week: IC Markets Raw Spread, max one percent risk per trade, "
                   f"one point two five risk reward minimum or the trade doesn't happen. "
                   f"Running total: {wr:.0f} percent win rate, {pf:.2f} profit factor, all live on Myfxbook.")
        cta = _CTA_EN

    elif reel_type == 'broker':
        hook    = ("The question I get most: which broker do you actually use? "
                   "Here's the answer — with eighteen months of live trades attached.")
        content = ("IC Markets Raw Spread. Zero point zero pips interbank spread. "
                   "No dealing desk, ECN execution, ASIC regulated. "
                   "Every verified trade on Myfxbook 12044019 runs through this exact account — "
                   "that's not a sponsorship line, that's my live setup, auditable down to the trade. "
                   "Step one: go to the link in my bio — opening IC Markets directly won't link us. "
                   "Step two: choose Raw Spread. Step three: verify identity, ten minutes. "
                   "Step four: DM me DONE and I'll walk you through your first trade setup.")
        cta = ("Link in bio, IB number 91936. IC Markets pays me a small commission — "
               "you pay nothing extra, spreads are identical either way. Full stop.")

    else:
        raise ValueError(f"Unknown reel_type: {reel_type!r}. Expected: edu|trust|weekly|broker")

    return ReelScript(
        hook=hook,
        content=content,
        proof=_PROOF,
        cta=cta,
        language=language,
        reel_type=reel_type,
    )
