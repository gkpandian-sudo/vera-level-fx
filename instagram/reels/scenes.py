from __future__ import annotations
import textwrap
import numpy as np
from PIL import Image, ImageDraw
from moviepy.editor import VideoClip, ImageClip
from reels.animator import (
    W, H, EMERALD, WHITE, GREEN, RED, MUTED,
    logo_fade_frame, countup_frame, cascade_text_frame,
    fade_in_frame, cta_fade_frame, ease_out,
    bg_frame, draw_alpha_text, load_font,
)

FPS = 30
_VERIFY_CTA  = 'Myfxbook #12044019'
_IB_CTA      = 'icmarkets.com/?camp=91936'
_IB_CTA_FULL = 'https://www.icmarkets.com/global/en/?camp=91936'

# Precomputed radial vignette mask — shape (H, W, 1) float32.
# Values: 0.0 at centre → 1.0 at corners. Computed once per process.
_Y_grid, _X_grid = np.ogrid[:H, :W]
_VIGN_BASE = np.clip(
    np.sqrt(((_X_grid - W / 2) / W) ** 2 + ((_Y_grid - H / 2) / H) ** 2) / 0.5,
    0.0, 1.0,
).astype(np.float32)[:, :, np.newaxis]


def make_broker_card_clip() -> VideoClip:
    """4s IC Markets broker card — pure dark NAVY theme, no external banner dependency."""
    from reels.effects import ticker_tape_overlay
    DUR = 4.0

    def frame(t):
        img = bg_frame(t)
        alp = min(t / 0.5, 1.0)

        cx, cy = W // 2, H // 2

        # Top label
        img = draw_alpha_text(img, (cx, cy - 400),
                               'TRADING WITH', load_font(32), MUTED, alp * 0.8)

        # Headline — WHITE on NAVY for maximum contrast
        img = draw_alpha_text(img, (cx, cy - 310),
                               'IC MARKETS', load_font(96, bold=True), WHITE, alp)

        # Credentials — emerald on dark bg is always readable
        img = draw_alpha_text(img, (cx, cy - 190),
                               'Raw Spread  ·  No requotes  ·  ASIC + CySEC',
                               load_font(34), EMERALD, alp)

        draw = ImageDraw.Draw(img)
        draw.line([(80, cy - 130), (W - 80, cy - 130)], fill=EMERALD, width=1)

        img = draw_alpha_text(img, (cx, cy - 60),
                               'The broker behind every number on this page.',
                               load_font(36), WHITE, alp)
        img = draw_alpha_text(img, (cx, cy + 20),
                               'Same account I trade every day. No demo.',
                               load_font(34), MUTED, alp)

        draw2 = ImageDraw.Draw(img)
        draw2.line([(80, cy + 100), (W - 80, cy + 100)], fill=EMERALD, width=1)

        # URL — emerald pill background, white text = always readable on dark bg
        url_y = cy + 200
        pill_w, pill_h = 720, 82
        px, py = cx - pill_w // 2, url_y - pill_h // 2
        draw3 = ImageDraw.Draw(img)
        if alp > 0.05:
            draw3.rounded_rectangle(
                [px, py, px + pill_w, py + pill_h],
                radius=12,
                fill=EMERALD,
            )
        img = draw_alpha_text(img, (cx, url_y),
                               _IB_CTA, load_font(34, bold=True), WHITE, alp)

        img = draw_alpha_text(img, (cx, cy + 310),
                               'IB #91936  ·  This is a referral link',
                               load_font(26), MUTED, alp * 0.65)

        img = ticker_tape_overlay(img, t)
        return np.array(img)

    return _clip(frame, DUR)


def _clip(make_frame_fn, duration: float) -> VideoClip:
    """Wrap a make_frame function as a MoviePy VideoClip at 30 FPS."""
    return VideoClip(make_frame_fn, duration=duration).set_fps(FPS)


def _with_stinger(clips: list) -> list:
    """Loop stinger — last 0.6s mirrors the hero so IG auto-loop reads as seamless."""
    if clips:
        hero_frame = clips[0].get_frame(min(1.2, clips[0].duration - 0.1))
        stinger = ImageClip(hero_frame).set_duration(0.6).set_fps(clips[0].fps or 30)
        clips.append(stinger)
    return clips


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
    daily_pct = float(acct.get('todayDaily') or acct.get('daily') or 0)
    win_rate  = float(acct.get('winRate') or 0)
    pips      = int(acct.get('pips')      or 0)
    pf        = float(acct.get('profitFactor') or 0)
    pnl_color = GREEN if daily_pct >= 0 else RED
    sign      = '+' if daily_pct >= 0 else ''

    # Hero (4s): odometer balance + pulsing live dot + glow daily %
    # Roll settles by 1.2s so the main figure is readable early
    DUR_HERO = 4.0
    ROLL_DUR = 1.2
    cx, cy   = W // 2, H // 2

    def hero_frame(t):
        img = Image.fromarray(
            odometer_frame(t, balance, ROLL_DUR, '${:,.0f}', WHITE, 110, (cx, cy - 80))
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
        lines.append(f'Day {recovery_day}/180 — the rebuild is live')
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

    return _with_stinger([hero, eq_clip, data_clip, cta, make_broker_card_clip()])


def make_weekly_reel(data: dict, recovery_day: int = 0,
                     weekly_gain: float | None = None) -> list:
    """Weekly reel — hero (this week's gain) + equity curve + data + cta + broker."""
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

    # Hero shows this week's actual gain; fall back to total gain only if unavailable
    hero_val   = weekly_gain if weekly_gain is not None else gain
    hero_color = GREEN if hero_val >= 0 else RED
    hero_sign  = '+' if hero_val >= 0 else ''
    hero_label = 'THIS WEEK' if weekly_gain is not None else 'TOTAL RETURN'

    # Hero (4s): weekly gain % with spring/settle animation + label
    def hero_frame(t):
        # Number revealed by 1.2s — readable early, not at the end of a long roll
        if hero_val >= 0:
            progress = ease_spring(t, 1.2)
        else:
            progress = ease_out(t, 1.2)
        value = hero_val * progress
        text  = f'{hero_sign}{value:.1f}%'
        img   = bg_frame(t)
        alp   = min(t * 1.5, 1.0)
        img   = draw_alpha_text(img, (W // 2, H // 2 - 120),
                                hero_label, load_font(36), MUTED, alp * 0.8)
        img   = draw_glow_text(img, (W // 2, H // 2 + 20), text, 130,
                               hero_color, glow_radius=28, alpha=alp)
        img = _brand_watermark(img)
        return np.array(img)

    hero = _clip(hero_frame, 4.0)

    # Equity curve (4s)
    eq_clip = equity_curve_clip(daily_gain, duration=4.0)

    # Data (4.5s): cascade + candlestick bg
    lines = []
    if recovery_day > 0:
        lines.append(f'Day {recovery_day}/180 — rebuilding in public')
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
    return _with_stinger([hero, eq_clip, data_clip, cta, make_broker_card_clip()])


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
    contradiction = (f'{wr:.0f}% win rate. {sign}{gain:.1f}% return. Both real.'
                     if wr > 0 else 'Win Rate, verified')
    lines = [
        contradiction,
        f'{trades_str}  |  Myfxbook #12044019',
        f'Profit Factor: {pf:.2f}',
        f'Total Pips:    +{pips:,}',
        f'Total Return:  {sign}{gain:.1f}%',
        'Win rate is nothing without risk control.',
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
    return _with_stinger([ring_clip, data_clip, cta, make_broker_card_clip()])


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
    return _with_stinger([hero, data_clip, cta, make_broker_card_clip()])


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
    return _with_stinger([hero, data_clip, cta])


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
    return _with_stinger([hero, data_clip, cta, make_broker_card_clip()])


def make_edu_reel(edu_type: str, content: dict) -> list:
    """Returns [hero, data, cta, broker] for edu post."""
    from reels.animator import typewriter_frame as _typewriter_frame
    from reels.effects import candlestick_bg_overlay

    if edu_type == 'risk':
        rule_num = content.get('rule_num', '')
        title = (f"Rule #{rule_num} - {content['title']}" if rule_num
                 else content['title'])

        def hero_frame(t):
            return _typewriter_frame(t, title, 1.8, EMERALD, 56, (W // 2, H // 2))

        hero = _clip(hero_frame, 2.5)

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
            return _typewriter_frame(t, title, 1.8, EMERALD, 60, (W // 2, H // 2))

        hero = _clip(hero_frame, 2.5)

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
            return _typewriter_frame(t, title, 1.8, EMERALD, 58, (W // 2, H // 2))

        hero = _clip(hero_frame, 2.5)

        steps = content.get('steps', [])
        step_lines = [f'{i+1}. {s[0]} - {s[1]}' for i, s in enumerate(steps)]

        def data_frame(t):  # noqa: F811
            img = Image.fromarray(cascade_text_frame(t, step_lines, 8.0, 0.6, WHITE, 36, 640))
            img = candlestick_bg_overlay(img)
            return np.array(img)

        data_clip = _clip(data_frame, 8.0)

    def cta_frame(t):
        return cta_fade_frame(t, 'Comment BROKER', 'My IC Markets setup → straight to your DMs')

    cta = _clip(cta_frame, 2.0)
    return _with_stinger([hero, data_clip, cta, make_broker_card_clip()])


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
    return _with_stinger([hero, data_clip, banner_scene])


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
    return _with_stinger([hero, data_clip, cta, make_broker_card_clip()])


def make_milestone_reel(data: dict, milestone_label: str) -> list:
    """Event-driven milestone reel — label + actuals + verify CTA."""
    from reels.effects import candlestick_bg_overlay
    from reels.animator import draw_glow_text

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
    return _with_stinger([hero, data_clip, cta, make_broker_card_clip()])


def make_trades_reel(data: dict) -> list:
    """Cinematic last-5-trades reel — 10s chart clip + 4s IC Markets broker CTA."""
    from reels.effects import ticker_tape_overlay
    from reels.chart   import get_ohlc, draw_chart_frame

    history = data.get('history', [])
    trades  = list(history[-5:]) if history else []
    ohlc_df = get_ohlc(trades)

    CHART_DUR  = 7.5
    CHART_RECT = (40, 200, W - 40, 1500)
    cx, cy     = W // 2, H // 2

    def cinematic_frame(t: float):
        img = bg_frame(t)

        # Header fades in over t=0–0.5s
        h_alp = min(t / 0.5, 1.0)
        img = draw_alpha_text(img, (cx, 120),
                               'LAST 5 TRADES', load_font(36, bold=True), MUTED, h_alp)
        img = draw_alpha_text(img, (cx, 168),
                               'Myfxbook #12044019', load_font(26), EMERALD, h_alp * 0.9)

        # Chart draws L→R starting at t=0.5
        if t >= 0.5:
            img = draw_chart_frame(img, ohlc_df, trades,
                                    t - 0.5, CHART_DUR, CHART_RECT)

        # Radial vignette ramps in t=7.0–8.0
        if t >= 7.0:
            vign_strength = ease_out(t - 7.0, 1.0) * 0.72
            arr = np.array(img, dtype=np.float32)
            arr *= (1.0 - _VIGN_BASE * vign_strength)
            img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))

        # NET P&L counts up t=7.5–10.0
        if t >= 7.5 and trades:
            net_total = sum(
                float(tr.get('profit', 0)) + float(tr.get('commission', 0))
                for tr in trades
            )
            wins     = sum(1 for tr in trades
                           if float(tr.get('profit', 0)) + float(tr.get('commission', 0)) > 0)
            losses   = len(trades) - wins
            progress = ease_out(t - 7.5, 1.5)
            net_disp = abs(net_total) * progress
            net_sign = '+' if net_total >= 0 else '-'
            nc       = EMERALD if net_total >= 0 else RED
            net_alp  = min((t - 7.5) / 0.4, 1.0)

            img = draw_alpha_text(img, (cx, cy - 60),
                                   f'{net_sign}${net_disp:.2f}',
                                   load_font(120, bold=True), nc, net_alp)
            img = draw_alpha_text(img, (cx, cy + 90),
                                   f'{wins}W / {losses}L  ·  {len(trades)} trades',
                                   load_font(38), WHITE, net_alp)
            img = draw_alpha_text(img, (cx, cy + 160),
                                   _IB_CTA, load_font(26), MUTED, net_alp * 0.8)

        img = _brand_watermark(img)
        img = ticker_tape_overlay(img, t)
        return np.array(img)

    chart_clip = _clip(cinematic_frame, 10.0)
    return _with_stinger([chart_clip, make_broker_card_clip()])


def make_thumbnail(post_type: str, data: dict, recovery_day: int = 0,
                   weekly_gain: float | None = None) -> Image.Image:
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
        disp_val  = weekly_gain if weekly_gain is not None else float(acct.get('gain') or 0)
        disp_lbl  = 'THIS WEEK' if weekly_gain is not None else 'TOTAL RETURN'
        gc        = GREEN if disp_val >= 0 else RED
        sign      = '+' if disp_val >= 0 else ''
        wr        = float(acct.get('winRate') or 0)
        pips      = int(acct.get('pips') or 0)
        img = draw_alpha_text(img, (W // 2, H // 2 - 200),
                               'WEEKLY P&L', load_font(52), MUTED, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 - 120),
                               disp_lbl, load_font(36), MUTED, 0.7)
        img = draw_alpha_text(img, (W // 2, H // 2 + 40),
                               f'{sign}{disp_val:.1f}%', load_font(160, bold=True), gc, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 230),
                               f'WR {wr:.0f}%  ·  +{pips:,} pips', load_font(40), WHITE, 1.0)

    elif post_type == 'daily':
        balance   = float(acct.get('balance') or 0)
        daily_pct = float(acct.get('todayDaily') or acct.get('daily') or 0)
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

    elif post_type == 'trades':
        history  = data.get('history', [])
        trades_5 = list(history[-5:]) if history else []
        net_total = sum(
            float(tr.get('profit', 0)) + float(tr.get('commission', 0))
            for tr in trades_5
        )
        wins   = sum(1 for tr in trades_5
                     if float(tr.get('profit', 0)) + float(tr.get('commission', 0)) > 0)
        losses = len(trades_5) - wins

        arr = np.array(img, dtype=np.float32)
        arr *= (1.0 - _VIGN_BASE * 0.72)
        img = Image.fromarray(arr.clip(0, 255).astype(np.uint8))

        net_sign = '+' if net_total >= 0 else '-'
        nc       = GREEN if net_total >= 0 else RED

        img = draw_alpha_text(img, (W // 2, H // 2 - 200),
                               'LAST 5 TRADES', load_font(44, bold=True), MUTED, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 - 60),
                               f'{net_sign}${abs(net_total):.2f}',
                               load_font(160, bold=True), nc, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 180),
                               f'{wins}W / {losses}L  ·  {len(trades_5)} trades',
                               load_font(44), WHITE, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 280),
                               'Myfxbook #12044019', load_font(32), EMERALD, 0.9)

    # Footer handle (skip for broker where IB URL is at bottom)
    if post_type != 'broker':
        img = draw_alpha_text(img, (W // 2, H - 50),
                               '@veralevel.fx', load_font(30), MUTED, 0.7)

    return img
