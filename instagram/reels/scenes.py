from __future__ import annotations
from moviepy.editor import VideoClip
from reels.animator import (
    W, H, GOLD, WHITE, GREEN, RED, MUTED,
    logo_fade_frame, countup_frame, cascade_text_frame,
    fade_in_frame, cta_fade_frame, _ease_out,
)

FPS = 30
_VERIFY_CTA = 'Myfxbook #12044019'
_IB_CTA     = 'icmarkets.com/?camp=91936'


def _clip(make_frame_fn, duration: float) -> VideoClip:
    """Wrap a make_frame function as a MoviePy VideoClip at 30 FPS."""
    return VideoClip(make_frame_fn, duration=duration).set_fps(FPS)


def _intro_clip() -> VideoClip:
    """1.5s branded intro — logo + gold bar sweep."""
    return _clip(logo_fade_frame, 1.5)


def make_daily_reel(data: dict, recovery_day: int = 0) -> list:
    """Daily reel — ~10s: 1.5s intro + 3s hero + 3.5s data + 2s cta."""
    acct        = data.get('account', {})
    open_trades = data.get('openTrades', [])[:5]

    balance   = float(acct.get('balance') or 0)
    daily_pct = float(acct.get('daily')   or 0)
    win_rate  = float(acct.get('winRate') or 0)
    pips      = int(acct.get('pips')   or 0)
    trades    = int(acct.get('trades') or 0)
    pf        = float(acct.get('profitFactor') or 0)
    pnl_color = GREEN if daily_pct >= 0 else RED
    sign      = '+' if daily_pct >= 0 else ''

    intro = _intro_clip()

    # Hero (3s): balance counts up + daily P&L fades in after 1.5s
    DUR_HERO = 3.0
    cx, cy   = W // 2, H // 2

    def hero_frame(t):
        import numpy as np
        from PIL import Image
        from reels.animator import _bg_frame, _draw_alpha_text, _load_font
        f   = countup_frame(t, 0, balance, 2.0, '${:,.0f}', WHITE, 110, (cx, cy - 80))
        img = Image.fromarray(f)
        if t > 1.5:
            alp = min((t - 1.5) / 0.5, 1.0)  # float 0.0–1.0
            img = _draw_alpha_text(img, (cx, cy + 80),
                                   f'{sign}{daily_pct:.2f}%',
                                   _load_font(72, bold=True), pnl_color, alp)
        return np.array(img)

    hero = _clip(hero_frame, DUR_HERO)

    # Data (3.5s): open positions + stats cascade up
    lines = []
    if recovery_day > 0:
        lines.append(f'Recovery Day {recovery_day}')
    for trade in open_trades:
        sym    = trade.get('symbol', '')
        action = trade.get('action', '').upper()
        profit = float(trade.get('profit') or 0)
        icon   = '+ ' if profit >= 0 else '- '
        lines.append(f'{sym}  {action}  {icon}${abs(profit):.2f}')
    if not open_trades and recovery_day == 0:
        lines.append('No open positions')
    lines.append(f'Win Rate: {win_rate:.0f}%  PF: {pf:.2f}  Pips: +{pips:,}')

    def data_frame(t):
        return cascade_text_frame(t, lines, 3.5, 0.3, WHITE, 38, 700)

    data_clip = _clip(data_frame, 3.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Verify my live account', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta]


def make_weekly_reel(data: dict, recovery_day: int = 0) -> list:
    """Weekly reel — ~12s: 1.5s intro + 4s hero + 4.5s data + 2s cta."""
    acct   = data.get('account', {})
    gain   = float(acct.get('gain')         or 0)
    wr     = float(acct.get('winRate')       or 0)
    pf     = float(acct.get('profitFactor')  or 0)
    pips   = int(acct.get('pips')            or 0)
    trades = int(acct.get('trades')          or 0)
    bal    = float(acct.get('balance')       or 0)

    gain_color = GREEN if gain >= 0 else RED
    # If gain >= 0, prepend '+'; if negative, the value itself carries the minus sign.
    fmt = ('+{:.1f}%' if gain >= 0 else '{:.1f}%')

    intro = _intro_clip()

    def hero_frame(t):
        return countup_frame(t, 0, gain, 4.0, fmt, gain_color, 120, (W // 2, H // 2))

    hero = _clip(hero_frame, 4.0)

    lines = []
    if recovery_day > 0:
        lines.append(f'Recovery Day {recovery_day}  |  Rebuild is live')
    lines += [
        f'Balance:  ${bal:,.0f}',
        f'Win Rate: {wr:.0f}%  across {trades:,} trades',
        f'Profit Factor:  {pf:.2f}',
        f'Total Pips:     +{pips:,}',
        'All verified on Myfxbook',
    ]

    def data_frame(t):
        return cascade_text_frame(t, lines, 4.5, 0.4, WHITE, 42, 680)

    data_clip = _clip(data_frame, 4.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Full track record:', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta]


def make_trust_reel(data: dict) -> list:
    """Trust reel — ~12s: 1.5s intro + 4s hero + 4.5s data + 2s cta."""
    acct   = data.get('account', {})
    wr     = float(acct.get('winRate')       or 0)
    pf     = float(acct.get('profitFactor')  or 0)
    gain   = float(acct.get('gain')          or 0)
    trades = int(acct.get('trades')          or 0)
    pips   = int(acct.get('pips')            or 0)
    sign   = '+' if gain >= 0 else ''

    intro = _intro_clip()

    def hero_frame(t):
        return countup_frame(t, 0, wr, 4.0, '{:.0f}%', GOLD, 160, (W // 2, H // 2 - 40))

    hero = _clip(hero_frame, 4.0)

    lines = [
        'Win Rate — verified',
        f'{trades:,} trades  |  Myfxbook #12044019',
        f'Profit Factor: {pf:.2f}',
        f'Total Pips:    +{pips:,}',
        f'Total Gain:    {sign}{gain:.1f}%',
        'Not a screenshot. Not a demo.',
        'Live IC Markets. ASIC regulated.',
    ]

    def data_frame(t):
        return cascade_text_frame(t, lines, 4.5, 0.35, WHITE, 40, 640)

    data_clip = _clip(data_frame, 4.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Search "Vera Level" on Myfxbook', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta]
