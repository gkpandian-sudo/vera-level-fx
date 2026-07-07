from __future__ import annotations
import textwrap
import numpy as np
from PIL import Image, ImageDraw
from moviepy.editor import VideoClip
from reels.animator import (
    W, H, EMERALD, WHITE, GREEN, RED, MUTED,
    logo_fade_frame, countup_frame, cascade_text_frame,
    fade_in_frame, cta_fade_frame, ease_out,
    bg_frame, draw_alpha_text, load_font,
)

FPS = 30
_VERIFY_CTA  = 'Myfxbook #12044019'
_IB_CTA      = 'https://www.icmarkets.com/global/en/?camp=91936'
_BANNER_URL  = ('https://promo.icmarkets.com/Banners/2021/English/'
                'EN_300x600_Cellphon_FSA.jpg')

_IB_BANNER_CACHE: dict = {}


def _get_ib_banner(width: int, height: int) -> 'np.ndarray | None':
    """Download IC Markets IB banner once, resize to (width, height), cache as float32."""
    key = (width, height)
    if key in _IB_BANNER_CACHE:
        return _IB_BANNER_CACHE[key]
    if 'original' not in _IB_BANNER_CACHE:
        try:
            import requests
            from io import BytesIO
            r = requests.get(_BANNER_URL, timeout=10)
            r.raise_for_status()
            _IB_BANNER_CACHE['original'] = Image.open(BytesIO(r.content)).convert('RGB')
        except Exception as e:
            print(f'[broker] IB banner fetch failed: {e}')
            _IB_BANNER_CACHE['original'] = None
    orig = _IB_BANNER_CACHE.get('original')
    if orig is None:
        _IB_BANNER_CACHE[key] = None
        return None
    arr = np.array(orig.resize((width, height), Image.LANCZOS), dtype=np.float32)
    _IB_BANNER_CACHE[key] = arr
    return arr


def make_broker_card_clip() -> VideoClip:
    """3s IC Markets broker card — full-screen dark theme + ticker tape."""
    from reels.effects import ticker_tape_overlay
    DUR = 3.0
    banner_arr = _get_ib_banner(W, H)  # full 1080×1920

    def frame(t):
        img = bg_frame(t)
        img_arr = np.array(img, dtype=np.float32)
        alp = min(t / 0.5, 1.0)

        if banner_arr is not None:
            # Dark theme: banner at 30% over dark bg keeps colours readable without washing out
            img_arr = img_arr * (1.0 - alp * 0.30) + banner_arr * (alp * 0.30)

        img = Image.fromarray(img_arr.astype(np.uint8))

        cx, cy = W // 2, H // 2

        img = draw_alpha_text(img, (cx, cy - 240),
                               'IC MARKETS', load_font(80, bold=True), WHITE, alp)
        img = draw_alpha_text(img, (cx, cy - 130),
                               'Raw Spread · No requotes', load_font(40), EMERALD, alp)
        img = draw_alpha_text(img, (cx, cy - 68),
                               'ASIC regulated · CySEC regulated', load_font(36), EMERALD, alp)

        draw = ImageDraw.Draw(img)
        draw.line([(80, cy), (W - 80, cy)], fill=EMERALD, width=2)

        img = draw_alpha_text(img, (cx, cy + 70),
                               'Same broker I trade with every day', load_font(36), MUTED, alp)
        img = draw_alpha_text(img, (cx, cy + 200),
                               _IB_CTA, load_font(30, bold=True), EMERALD, alp)
        img = draw_alpha_text(img, (cx, cy + 262),
                               'IB #91936  ·  Referral link', load_font(26), MUTED,
                               alp * 0.7)

        img = ticker_tape_overlay(img, t)
        return np.array(img)

    return _clip(frame, DUR)


def _clip(make_frame_fn, duration: float) -> VideoClip:
    """Wrap a make_frame function as a MoviePy VideoClip at 30 FPS."""
    return VideoClip(make_frame_fn, duration=duration).set_fps(FPS)


def _brand_watermark(img: 'Image.Image', alpha: float = 0.5) -> 'Image.Image':
    """Stamp @veralevel.fx handle as persistent lower-third on any frame."""
    return draw_alpha_text(img, (W // 2, H - 55),
                           '@veralevel.fx', load_font(28), MUTED, alpha)


def make_daily_reel(data: dict, recovery_day: int = 0) -> list:
    """Daily reel — hero (odometer) + equity curve + data + cta + broker."""
    from reels.effects import equity_curve_clip, ticker_tape_overlay, candlestick_bg_overlay
    from reels.animator import odometer_frame, draw_pulsing_dot, draw_glow_text

    acct        = data.get('account', {})
    open_trades = data.get('openTrades', [])[:5]
    daily_gain  = data.get('dailyGain', [])

    balance   = float(acct.get('balance') or 0)
    daily_pct = float(acct.get('daily')   or 0)
    win_rate  = float(acct.get('winRate') or 0)
    pips      = int(acct.get('pips')      or 0)
    pf        = float(acct.get('profitFactor') or 0)
    pnl_color = GREEN if daily_pct >= 0 else RED
    sign      = '+' if daily_pct >= 0 else ''

    # Hero (4s): odometer balance + pulsing live dot + glow daily %
    DUR_HERO = 4.0
    cx, cy   = W // 2, H // 2

    def hero_frame(t):
        img = Image.fromarray(
            odometer_frame(t, balance, DUR_HERO, '${:,.0f}', WHITE, 110, (cx, cy - 80))
        )
        img = draw_pulsing_dot(img, pos=(cx - 300, cy - 200), t=t,
                               positive=daily_pct >= 0)
        img = draw_alpha_text(img, (cx - 240, cy - 200), '● LIVE',
                              load_font(32, bold=True), RED, min(t * 2, 1.0))
        if t > 1.5:
            alp = min((t - 1.5) / 0.5, 1.0)
            img = draw_glow_text(img, (cx, cy + 80),
                                 f'{sign}{daily_pct:.2f}%', 72, pnl_color,
                                 glow_radius=20, alpha=alp)
        img = _brand_watermark(img)
        return np.array(img)

    hero = _clip(hero_frame, DUR_HERO)

    # Equity curve (3s)
    eq_clip = equity_curve_clip(daily_gain, duration=3.0,
                                plot_rect=(80, 1050, 1000, 1700))

    # Data (3.5s): open positions cascade + candlestick bg + ticker
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
    wr_str = f'{win_rate:.0f}%' if win_rate > 0 else 'see Myfxbook'
    lines.append(f'Win Rate: {wr_str}  PF: {pf:.2f}  Pips: +{pips:,}')

    def data_frame(t):
        img = Image.fromarray(cascade_text_frame(t, lines, 3.5, 0.3, WHITE, 38, 700))
        img = candlestick_bg_overlay(img)
        img = ticker_tape_overlay(img, t)
        return np.array(img)

    data_clip = _clip(data_frame, 3.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Verify my live account', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)

    return [hero, eq_clip, data_clip, cta, make_broker_card_clip()]


def make_weekly_reel(data: dict, recovery_day: int = 0) -> list:
    """Weekly reel — hero (spring gain) + equity curve + data + cta + broker."""
    from reels.effects import equity_curve_clip, candlestick_bg_overlay
    from reels.animator import ease_spring, draw_glow_text

    acct       = data.get('account', {})
    daily_gain = data.get('dailyGain', [])
    gain       = float(acct.get('gain')        or 0)
    wr         = float(acct.get('winRate')      or 0)
    pf         = float(acct.get('profitFactor') or 0)
    pips       = int(acct.get('pips')           or 0)
    trades     = int(acct.get('trades')         or 0)
    bal        = float(acct.get('balance')      or 0)

    gain_color = GREEN if gain >= 0 else RED
    sign       = '+' if gain >= 0 else ''

    # Hero (4s): gain % with spring bounce + glow
    def hero_frame(t):
        if gain >= 0:
            progress = ease_spring(t, 3.5)     # spring bounce for gains
        else:
            progress = ease_out(t, 1.5)         # fast hard settle for losses — no bounce
        value    = gain * progress
        text     = f'{sign}{value:.1f}%'
        img      = bg_frame(t)
        img      = draw_glow_text(img, (W // 2, H // 2), text, 130,
                                  gain_color, glow_radius=28,
                                  alpha=min(t * 1.5, 1.0))
        img = _brand_watermark(img)
        return np.array(img)

    hero = _clip(hero_frame, 4.0)

    # Equity curve (4s)
    eq_clip = equity_curve_clip(daily_gain, duration=4.0)

    # Data (4.5s): cascade + candlestick bg
    lines = []
    if recovery_day > 0:
        lines.append(f'Recovery Day {recovery_day}  |  Rebuild is live')
    wr_line = (f'Win Rate: {wr:.0f}%  across {trades:,} trades'
               if wr > 0 else 'Win Rate: Myfxbook #12044019')
    lines += [f'Balance:  ${bal:,.0f}', wr_line,
              f'Profit Factor:  {pf:.2f}', f'Total Pips:     +{pips:,}',
              'All verified on Myfxbook']

    def data_frame(t):
        img = Image.fromarray(cascade_text_frame(t, lines, 4.5, 0.4, WHITE, 42, 680))
        img = candlestick_bg_overlay(img)
        return np.array(img)

    data_clip = _clip(data_frame, 4.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Full track record:', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)
    return [hero, eq_clip, data_clip, cta, make_broker_card_clip()]


def make_trust_reel(data: dict) -> list:
    """Trust reel — progress ring hero + data + cta + broker."""
    from reels.effects import progress_ring_clip, candlestick_bg_overlay
    from reels.animator import draw_glow_text

    acct   = data.get('account', {})
    wr     = float(acct.get('winRate')      or 0)
    pf     = float(acct.get('profitFactor') or 0)
    gain   = float(acct.get('gain')         or 0)
    trades = int(acct.get('trades')         or 0)
    pips   = int(acct.get('pips')           or 0)
    sign   = '+' if gain >= 0 else ''

    # Hero: animated win-rate ring (5s) — only if we have real data
    if wr > 0:
        ring_clip = progress_ring_clip(win_rate=wr, duration=5.0)
    else:
        def verify_frame(t):
            img = bg_frame(t)
            alp = min(t * 1.5, 1.0)
            img = draw_alpha_text(img, (W // 2, H // 2 - 120),
                                   'WIN RATE', load_font(72, bold=True), EMERALD, alp)
            img = draw_alpha_text(img, (W // 2, H // 2 + 20),
                                   'Myfxbook #12044019', load_font(52), WHITE, alp)
            img = draw_alpha_text(img, (W // 2, H // 2 + 130),
                                   'Search "Vera Level" to verify', load_font(36), MUTED, alp)
            img = _brand_watermark(img)
            return np.array(img)
        ring_clip = _clip(verify_frame, 5.0)

    # Data (4.5s): cascade + candlestick bg
    trades_str = f'{trades:,} trades' if trades > 0 else 'Myfxbook #12044019'
    lines = [
        'Win Rate, verified',
        f'{trades_str}  |  Myfxbook #12044019',
        f'Profit Factor: {pf:.2f}',
        f'Total Pips:    +{pips:,}',
        f'Total Return:  {sign}{gain:.1f}%',
        'No screenshots. No cherry-picked months.',
        'Raw Spread  |  IC Markets  |  ASIC + CySEC',
    ]

    def data_frame(t):
        img = Image.fromarray(cascade_text_frame(t, lines, 4.5, 0.35, WHITE, 40, 640))
        img = candlestick_bg_overlay(img)
        return np.array(img)

    data_clip = _clip(data_frame, 4.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Search "Vera Level" on Myfxbook', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)
    return [ring_clip, data_clip, cta, make_broker_card_clip()]


def make_monthly_reel(data: dict) -> list:
    """Returns [hero, data, cta, broker] for monthly post."""
    from datetime import datetime as _dt
    from captions import monthly_pnl_from_daily
    from reels.effects import candlestick_bg_overlay

    acct = data.get('account', {})
    gain = float(acct.get('gain') or 0)

    # Build last-6-month P&L from dailyGain (Myfxbook MM/DD/YYYY dates)
    monthly_pnl: dict[str, float] = monthly_pnl_from_daily(data.get('dailyGain', []))

    months = list(monthly_pnl.items())[-6:]
    sign   = '+' if gain >= 0 else ''
    month_name = _dt.now().strftime('%B %Y')

    # Hero (3s): "Monthly P&L / {month_name}" fades in
    def hero_frame(t):
        return fade_in_frame(t, f'Monthly P&L\n{month_name}', 3.0, EMERALD, 72, (W // 2, H // 2))

    hero = _clip(hero_frame, 3.0)

    # Data: bars draw L→R one per bar_gap, value label appears after
    bar_dur    = 1.0
    bar_gap    = 0.5
    DUR_DATA   = len(months) * bar_gap + bar_dur + 1.5  # 6*0.5 + 1.0 + 1.5 = 5.5s
    start_y    = 550
    bar_h_px   = 60
    bar_spacing = bar_h_px + 40

    def data_frame(t):
        img  = bg_frame(t)
        img  = candlestick_bg_overlay(img)
        draw = ImageDraw.Draw(img)
        font_label = load_font(34)
        font_val   = load_font(32, bold=True)

        for i, (month, val) in enumerate(months):
            bar_start_t = i * bar_gap
            elapsed     = max(t - bar_start_t, 0)
            progress    = min(elapsed / bar_dur, 1.0)
            color       = GREEN if val >= 0 else RED

            y_top  = start_y + i * bar_spacing
            max_bw = 700
            bar_w  = int(max_bw * progress)

            draw.rectangle([180, y_top, max(180, 180 + bar_w), y_top + bar_h_px], fill=color)
            draw.text((165, y_top + bar_h_px // 2), month,
                      fill=WHITE, font=font_label, anchor='rm')

            if progress > 0.9:
                val_alpha = min((progress - 0.9) / 0.1, 1.0)
                val_sign  = '+' if val >= 0 else ''
                img = draw_alpha_text(img, (180 + max_bw + 90, y_top + bar_h_px // 2),
                                       f'{val_sign}{val:.1f}%', font_val, color, val_alpha)
                draw = ImageDraw.Draw(img)  # rebind so subsequent iterations draw on updated img

        end_t = len(months) * bar_gap + bar_dur
        if t > end_t:
            total_alpha = min((t - end_t) / 1.0, 1.0)
            img = draw_alpha_text(img, (W // 2, start_y + len(months) * bar_spacing + 60),
                                   f'Total: {sign}{gain:.1f}%',
                                   load_font(48, bold=True), EMERALD, total_alpha)

        return np.array(img)

    data_clip = _clip(data_frame, DUR_DATA)

    def cta_frame(t):
        return cta_fade_frame(t, 'Verify every month yourself:', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)
    return [hero, data_clip, cta, make_broker_card_clip()]


def make_transparency_reel(data: dict) -> list:
    """Transparency reel — hero (loss %) + data (what changed) + follow CTA."""
    from reels.effects import candlestick_bg_overlay

    acct = data.get('account', {})
    gain = float(acct.get('gain') or 0)
    dd   = float(acct.get('drawdown') or 0)
    bal  = float(acct.get('balance') or 0)

    # Hero (4s): loss % slams in red
    def hero_frame(t):
        return countup_frame(t, 0, gain, 2.0, '{:.1f}%', RED, 140, (W // 2, H // 2))

    hero = _clip(hero_frame, 4.0)

    # Data (9.5s): two-section cascade
    happened_lines = [
        'WHAT HAPPENED',
        'Position sizing errors compounded',
        'during a volatile XAUUSD run.',
        'Entry frequency was too high.',
        'Capital eroded faster than wins recovered.',
    ]
    changed_lines = [
        'WHAT CHANGED',
        'Reduced trade frequency.',
        'Tightened session filters.',
        'London/NY overlap only.',
        f'Balance: ${bal:,.0f}  |  Max DD: {dd:.1f}%',
    ]

    def data_frame(t):
        img = bg_frame(t)
        img = candlestick_bg_overlay(img)
        for i, line in enumerate(happened_lines):
            bold  = (line == 'WHAT HAPPENED')
            color = RED if bold else WHITE
            fs    = 44 if bold else 36
            s_t   = i * 0.6
            alp   = min(max(t - s_t, 0) / 0.4, 1.0)
            img   = draw_alpha_text(img, (W // 2, 600 + i * 70), line,
                                     load_font(fs, bold=bold), color, alp)
        for i, line in enumerate(changed_lines):
            bold  = (line == 'WHAT CHANGED')
            color = EMERALD if bold else WHITE
            fs    = 44 if bold else 36
            s_t   = 5.0 + i * 0.5
            alp   = min(max(t - s_t, 0) / 0.4, 1.0)
            img   = draw_alpha_text(img, (W // 2, 1150 + i * 70), line,
                                     load_font(fs, bold=bold), color, alp)
        return np.array(img)

    data_clip = _clip(data_frame, 9.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'The rebuild is live.', 'Follow @veralevel.fx')

    cta = _clip(cta_frame, 2.5)
    return [hero, data_clip, cta]


def make_recovery_plan_reel(recovery_day: int = 0, balance: float = 0.0,
                             pf: float = 0.0) -> list:
    """Actuals-only rebuild reel — no projection table, no targets."""
    from reels.effects import candlestick_bg_overlay
    from reels.animator import draw_glow_text, ease_spring

    def hero_frame(t):
        img = bg_frame(t)
        alp = min(t * 1.5, 1.0)
        if recovery_day > 0:
            progress = ease_spring(t, 2.5)
            disp_day = int(recovery_day * min(progress, 1.0))
            label    = f'Day {disp_day}'
        else:
            label    = 'Rebuild Live'
        img = draw_glow_text(img, (W // 2, H // 2 - 60),
                             label, 120, EMERALD, glow_radius=26, alpha=alp)
        img = _brand_watermark(img)
        return np.array(img)

    hero = _clip(hero_frame, 3.0)

    lines = [
        'WHAT THE REBUILD LOOKS LIKE',
        'London/NY overlap sessions only.',
        'ATR-based sizing  |  Max 1% per trade.',
        'Hard daily drawdown limit enforced.',
        '',
    ]
    if balance > 0:
        lines.append(f'Balance: ${balance:,.0f}')
    if pf > 0:
        pf_note = '  <- improving' if 0 < pf < 1.0 else ('  <- target reached'
                                                           if pf >= 1.2 else '')
        lines.append(f'Profit Factor: {pf:.2f}  (target: 1.2+){pf_note}')
    lines.append('All trades: Myfxbook #12044019')

    def data_frame(t):
        img = Image.fromarray(cascade_text_frame(t, lines, 4.5, 0.35, WHITE, 38, 580))
        img = candlestick_bg_overlay(img)
        return np.array(img)

    data_clip = _clip(data_frame, 4.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Every trade is public.', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)
    return [hero, data_clip, cta, make_broker_card_clip()]


def make_edu_reel(edu_type: str, content: dict) -> list:
    """Returns [hero, data, cta, broker] for edu post."""
    from reels.animator import typewriter_frame as _typewriter_frame
    from reels.effects import candlestick_bg_overlay

    if edu_type == 'risk':
        rule_num = content.get('rule_num', '')
        title = (f"Rule #{rule_num} - {content['title']}" if rule_num
                 else content['title'])

        def hero_frame(t):
            return _typewriter_frame(t, title, 5.0, EMERALD, 56, (W // 2, H // 2))

        hero = _clip(hero_frame, 5.0)

        body       = content.get('body', '')
        body_lines = textwrap.wrap(body, width=42)
        ex_lines: list = []
        if 'example_account' in content:
            ex_text = (f"${content['example_account']:,} account\n"
                       f"-> max ${content['example_risk']:,} per trade\n"
                       f"at {content['example_rr']}")
            ex_lines = ex_text.split('\n')

        all_lines = body_lines + ([''] + ex_lines if ex_lines else [])

        def data_frame(t):
            img = Image.fromarray(cascade_text_frame(t, all_lines, 8.0, 0.8, WHITE, 38, 620))
            img = candlestick_bg_overlay(img)
            return np.array(img)

        data_clip = _clip(data_frame, 8.0)

    elif edu_type == 'pairs':
        pair  = content.get('pair', 'XAUUSD')
        title = f'Pair Spotlight - {pair}'

        def hero_frame(t):  # noqa: F811
            return _typewriter_frame(t, title, 5.0, EMERALD, 60, (W // 2, H // 2))

        hero = _clip(hero_frame, 5.0)

        info_lines = [
            f"Best session: {content.get('best_session', '')}",
            f"IC Markets Raw spread: {content.get('avg_spread', '')}",
            f"Daily volatility: {content.get('volatility', '')}",
            '',
            f"My edge: {content.get('my_edge', '')}",
        ]

        def data_frame(t):  # noqa: F811
            img = Image.fromarray(cascade_text_frame(t, info_lines, 8.0, 0.8, WHITE, 36, 640))
            img = candlestick_bg_overlay(img)
            return np.array(img)

        data_clip = _clip(data_frame, 8.0)

    else:  # setup
        pair  = content.get('pair', 'XAUUSD')
        title = f"{pair} {content.get('direction', 'LONG')} Setup"

        def hero_frame(t):  # noqa: F811
            return _typewriter_frame(t, title, 5.0, EMERALD, 58, (W // 2, H // 2))

        hero = _clip(hero_frame, 5.0)

        steps = content.get('steps', [])
        step_lines = [f'{i+1}. {s[0]} - {s[1]}' for i, s in enumerate(steps)]

        def data_frame(t):  # noqa: F811
            img = Image.fromarray(cascade_text_frame(t, step_lines, 8.0, 0.6, WHITE, 36, 640))
            img = candlestick_bg_overlay(img)
            return np.array(img)

        data_clip = _clip(data_frame, 8.0)

    def cta_frame(t):
        return cta_fade_frame(t, 'Open IC Markets', _IB_CTA)

    cta = _clip(cta_frame, 2.0)
    return [hero, data_clip, cta, make_broker_card_clip()]


def make_broker_reel() -> list:
    """Standalone IC Markets broker spotlight reel (~17s)."""
    from reels.animator import typewriter_frame as _typewriter_frame

    # Pre-fetch banner at full-reel size (downloaded once, cached)
    banner_arr_full = _get_ib_banner(W, H)  # full 1080×1920

    def hero_frame(t):
        return _typewriter_frame(t, 'IC Markets', 4.0, EMERALD, 90, (W // 2, H // 2))

    hero = _clip(hero_frame, 4.0)

    lines = [
        'Raw Spread  ·  No requotes',
        'ECN / STP execution',
        'Spreads from 0.0 pips',
        'ASIC regulated  ·  CySEC regulated',
        '',
        'Every Vera Level trade runs here.',
    ]

    def data_frame(t):
        return cascade_text_frame(t, lines, 6.0, 0.6, WHITE, 42, 680)

    data_clip = _clip(data_frame, 6.0)

    def banner_frame(t):
        img = bg_frame(t)
        img_arr = np.array(img, dtype=np.float32)
        alp = min(t / 0.5, 1.0)

        if banner_arr_full is not None:
            img_arr = img_arr * (1.0 - alp * 0.30) + banner_arr_full * (alp * 0.30)

        img = Image.fromarray(img_arr.astype(np.uint8))
        img = draw_alpha_text(img, (W // 2, H // 2 + 200),
                               _IB_CTA, load_font(34, bold=True), EMERALD, alp)
        img = draw_alpha_text(img, (W // 2, H // 2 + 265),
                               'IB #91936  ·  Referral link', load_font(26), MUTED,
                               alp * 0.7)
        return np.array(img)

    banner_scene = _clip(banner_frame, 3.5)
    return [hero, data_clip, banner_scene]


def make_signup_reel() -> list:
    """IB sign-up walkthrough reel — 4 steps, high-conversion."""
    from reels.effects import candlestick_bg_overlay
    from reels.animator import draw_glow_text

    def hero_frame(t):
        img = bg_frame(t)
        alp = min(t * 1.5, 1.0)
        img = draw_glow_text(img, (W // 2, H // 2 - 100),
                             'Open your account', 68, EMERALD,
                             glow_radius=20, alpha=alp)
        img = draw_alpha_text(img, (W // 2, H // 2 + 60),
                               'Same broker. Same setup.', load_font(40), WHITE, alp)
        img = _brand_watermark(img)
        return np.array(img)

    hero = _clip(hero_frame, 3.0)

    step_lines = [
        '1.  Link in bio  (not icmarkets.com direct)',
        '2.  Choose: Raw Spread account',
        '3.  Verify ID — 10 min  (ASIC + CySEC)',
        '4.  DM me "DONE" — I will walk you through',
        '',
        'Referral link  ·  IB #91936',
        'I earn commission  ·  zero extra cost to you',
    ]

    def data_frame(t):
        img = Image.fromarray(cascade_text_frame(t, step_lines, 6.0, 0.5, WHITE, 38, 520))
        img = candlestick_bg_overlay(img)
        return np.array(img)

    data_clip = _clip(data_frame, 6.0)

    def cta_frame(t):
        return cta_fade_frame(t, 'Link is in bio.', 'DM me DONE after you open.')

    cta = _clip(cta_frame, 2.5)
    return [hero, data_clip, cta, make_broker_card_clip()]


def make_milestone_reel(data: dict, milestone_label: str) -> list:
    """Event-driven milestone reel — label + actuals + verify CTA."""
    from reels.effects import candlestick_bg_overlay
    from reels.animator import draw_glow_text, ease_spring

    acct = data.get('account', {})
    pf   = float(acct.get('profitFactor') or 0)
    gain = float(acct.get('gain') or 0)
    sign = '+' if gain >= 0 else ''

    def hero_frame(t):
        img = bg_frame(t)
        alp = min(t * 1.2, 1.0)
        img = draw_glow_text(img, (W // 2, H // 2),
                             milestone_label, 64, EMERALD,
                             glow_radius=22, alpha=alp)
        img = _brand_watermark(img)
        return np.array(img)

    hero = _clip(hero_frame, 4.0)

    lines = [
        f'{sign}{gain:.1f}% total return',
        f'Profit Factor: {pf:.2f}',
        '',
        'Verified on Myfxbook #12044019',
        'Not projections.',
        'Milestones are real.',
        'Follow to watch the next one live.',
    ]

    def data_frame(t):
        img = Image.fromarray(cascade_text_frame(t, lines, 4.5, 0.4, WHITE, 42, 580))
        img = candlestick_bg_overlay(img)
        return np.array(img)

    data_clip = _clip(data_frame, 4.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Verify this now:', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)
    return [hero, data_clip, cta, make_broker_card_clip()]


def make_thumbnail(post_type: str, data: dict, recovery_day: int = 0) -> Image.Image:
    """Static 1080x1920 PIL Image thumbnail for the given post type."""
    acct = data.get('account', {})
    img  = bg_frame(0.0)

    # Top emerald accent bar
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 8], fill=EMERALD)

    # Brand label
    img = draw_alpha_text(img, (W // 2, 80),
                           'VERA LEVEL FX', load_font(36, bold=True), EMERALD, 1.0)

    if post_type == 'weekly':
        gain  = float(acct.get('gain') or 0)
        gc    = GREEN if gain >= 0 else RED
        sign  = '+' if gain >= 0 else ''
        wr    = float(acct.get('winRate') or 0)
        pips  = int(acct.get('pips') or 0)
        img = draw_alpha_text(img, (W // 2, H // 2 - 160),
                               'WEEKLY P&L', load_font(52), MUTED, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 40),
                               f'{sign}{gain:.1f}%', load_font(160, bold=True), gc, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 230),
                               f'WR {wr:.0f}%  ·  +{pips:,} pips', load_font(40), WHITE, 1.0)

    elif post_type == 'daily':
        balance   = float(acct.get('balance') or 0)
        daily_pct = float(acct.get('daily')   or 0)
        pc        = GREEN if daily_pct >= 0 else RED
        sign      = '+' if daily_pct >= 0 else ''
        img = draw_alpha_text(img, (W // 2, H // 2 - 220),
                               '● LIVE', load_font(52, bold=True), RED, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2),
                               f'${balance:,.0f}', load_font(120, bold=True), WHITE, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 170),
                               f'{sign}{daily_pct:.2f}% today', load_font(60), pc, 1.0)
        if recovery_day > 0:
            img = draw_alpha_text(img, (W // 2, H // 2 + 280),
                                   f'Recovery Day {recovery_day}', load_font(40), MUTED, 1.0)

    elif post_type == 'monthly':
        from captions import monthly_pnl_from_daily as _mpd
        from datetime import datetime as _dt
        monthly_pnl = _mpd(data.get('dailyGain', []))
        months = list(monthly_pnl.items())[-3:]
        month_name = _dt.now().strftime('%B %Y')
        img = draw_alpha_text(img, (W // 2, H // 2 - 320),
                               'MONTHLY P&L', load_font(52), MUTED, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 - 220),
                               month_name, load_font(60, bold=True), EMERALD, 1.0)
        for i, (month, val) in enumerate(months):
            color = GREEN if val >= 0 else RED
            s = '+' if val >= 0 else ''
            img = draw_alpha_text(img, (W // 2, H // 2 - 60 + i * 100),
                                   f'{month}  {s}{val:.1f}%',
                                   load_font(52, bold=True), color, 1.0)

    elif post_type == 'trust':
        wr     = float(acct.get('winRate') or 0)
        trades = int(acct.get('trades') or 0)
        img = draw_alpha_text(img, (W // 2, H // 2 - 180),
                               'WIN RATE', load_font(56), MUTED, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 40),
                               f'{wr:.0f}%', load_font(180, bold=True), EMERALD, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 230),
                               f'{trades:,} trades verified', load_font(40), WHITE, 1.0)

    elif post_type == 'transparency':
        gain = float(acct.get('gain') or 0)
        img = draw_alpha_text(img, (W // 2, H // 2 - 220),
                               'FULL DISCLOSURE', load_font(52, bold=True), WHITE, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 20),
                               f'{gain:.1f}%', load_font(160, bold=True), RED, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 230),
                               'Nothing hidden', load_font(44), MUTED, 1.0)

    elif post_type == 'recovery-plan':
        img = draw_alpha_text(img, (W // 2, H // 2 - 230),
                               'REBUILD LIVE', load_font(56, bold=True), EMERALD, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 - 60),
                               'All trades on Myfxbook', load_font(52), WHITE, 1.0)
        if recovery_day > 0:
            img = draw_alpha_text(img, (W // 2, H // 2 + 120),
                                   f'Day {recovery_day}', load_font(80, bold=True), EMERALD, 1.0)

    elif post_type == 'edu':
        img = draw_alpha_text(img, (W // 2, H // 2 - 120),
                               'RISK MANAGEMENT', load_font(56, bold=True), EMERALD, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 80),
                               'Education', load_font(72), WHITE, 1.0)

    elif post_type == 'broker':
        banner_arr = _get_ib_banner(W, H)  # full 1080×1920
        if banner_arr is not None:
            img_arr = np.array(img, dtype=np.float32)
            img_arr = img_arr * 0.70 + banner_arr * 0.30  # dark theme blend
            img = Image.fromarray(img_arr.astype(np.uint8))
        img = draw_alpha_text(img, (W // 2, H // 2 - 240),
                               'IC MARKETS', load_font(80, bold=True), WHITE, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 - 120),
                               'Raw Spread  ·  ASIC + CySEC', load_font(44), EMERALD, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 60),
                               _IB_CTA, load_font(34, bold=True), EMERALD, 1.0)

    # Footer handle (skip for broker where IB URL is at bottom)
    if post_type != 'broker':
        img = draw_alpha_text(img, (W // 2, H - 50),
                               '@veralevel.fx', load_font(30), MUTED, 0.7)

    return img
