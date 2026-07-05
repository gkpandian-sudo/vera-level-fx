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
_IB_CTA      = 'icmarkets.com/?camp=91936'
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
    """3s IC Markets broker card — official IB banner right, brand text left."""
    DUR = 3.0
    BW, BH = 480, 960
    BX = W - BW - 40          # 560 — right column
    BY = (H - BH) // 2        # 480 — vertically centred
    TCX = BX // 2             # 280 — centre of left column
    banner_arr = _get_ib_banner(BW, BH)

    def frame(t):
        img = bg_frame(t)
        img_arr = np.array(img, dtype=np.float32)
        alp = min(t / 0.5, 1.0)

        if banner_arr is not None:
            img_arr[BY:BY + BH, BX:BX + BW] = (
                img_arr[BY:BY + BH, BX:BX + BW] * (1.0 - alp) + banner_arr * alp
            )

        img = Image.fromarray(img_arr.astype(np.uint8))

        img = draw_alpha_text(img, (TCX, H // 2 - 220),
                               'IC MARKETS', load_font(60, bold=True), WHITE, alp)
        img = draw_alpha_text(img, (TCX, H // 2 - 120),
                               'Raw Spread', load_font(34), EMERALD, alp)
        img = draw_alpha_text(img, (TCX, H // 2 - 72),
                               'ASIC + CySEC', load_font(34), EMERALD, alp)

        draw = ImageDraw.Draw(img)
        draw.line([(40, H // 2 - 20), (BX - 40, H // 2 - 20)], fill=EMERALD, width=2)

        img = draw_alpha_text(img, (TCX, H // 2 + 50),
                               'Same broker I trade', load_font(30), MUTED, alp)
        img = draw_alpha_text(img, (TCX, H // 2 + 95),
                               'with every day', load_font(30), MUTED, alp)
        img = draw_alpha_text(img, (TCX, H // 2 + 190),
                               _IB_CTA, load_font(24, bold=True), EMERALD, alp)
        img = draw_alpha_text(img, (TCX, H // 2 + 250),
                               'IB #91936  ·  Referral link', load_font(22), MUTED,
                               alp * 0.7)

        return np.array(img)

    return _clip(frame, DUR)


def _clip(make_frame_fn, duration: float) -> VideoClip:
    """Wrap a make_frame function as a MoviePy VideoClip at 30 FPS."""
    return VideoClip(make_frame_fn, duration=duration).set_fps(FPS)


def _intro_clip() -> VideoClip:
    """1.5s branded intro — logo + emerald bar sweep."""
    return _clip(logo_fade_frame, 1.5)


def make_daily_reel(data: dict, recovery_day: int = 0) -> list:
    """Daily reel — ~10s: 1.5s intro + 3s hero + 3.5s data + 2s cta."""
    acct        = data.get('account', {})
    open_trades = data.get('openTrades', [])[:5]

    balance   = float(acct.get('balance') or 0)
    daily_pct = float(acct.get('daily')   or 0)
    win_rate  = float(acct.get('winRate') or 0)
    pips      = int(acct.get('pips')   or 0)
    pf        = float(acct.get('profitFactor') or 0)
    pnl_color = GREEN if daily_pct >= 0 else RED
    sign      = '+' if daily_pct >= 0 else ''

    intro = _intro_clip()

    # Hero (3s): balance counts up + daily P&L fades in after 1.5s
    DUR_HERO = 3.0
    cx, cy   = W // 2, H // 2

    def hero_frame(t):
        f   = countup_frame(t, 0, balance, 2.0, '${:,.0f}', WHITE, 110, (cx, cy - 80))
        img = Image.fromarray(f)
        if t > 1.5:
            alp = min((t - 1.5) / 0.5, 1.0)  # float 0.0–1.0
            img = draw_alpha_text(img, (cx, cy + 80),
                                   f'{sign}{daily_pct:.2f}%',
                                   load_font(72, bold=True), pnl_color, alp)
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
    wr_str = f'{win_rate:.0f}%' if win_rate > 0 else 'see Myfxbook'
    lines.append(f'Win Rate: {wr_str}  PF: {pf:.2f}  Pips: +{pips:,}')

    def data_frame(t):
        return cascade_text_frame(t, lines, 3.5, 0.3, WHITE, 38, 700)

    data_clip = _clip(data_frame, 3.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Verify my live account', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta, make_broker_card_clip()]


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
    wr_line = (f'Win Rate: {wr:.0f}%  across {trades:,} trades'
               if wr > 0 else 'Win Rate: Myfxbook #12044019')
    lines += [
        f'Balance:  ${bal:,.0f}',
        wr_line,
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

    return [intro, hero, data_clip, cta, make_broker_card_clip()]


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

    if wr > 0:
        def hero_frame(t):
            return countup_frame(t, 0, wr, 4.0, '{:.0f}%', EMERALD, 160, (W // 2, H // 2 - 40))
    else:
        def hero_frame(t):
            return fade_in_frame(t, 'Verified', 4.0, EMERALD, 120, (W // 2, H // 2 - 40))

    hero = _clip(hero_frame, 4.0)

    trades_str = f'{trades:,} trades' if trades > 0 else 'Myfxbook #12044019'
    wr_header  = 'Win Rate, verified' if wr > 0 else 'Full history, verified'
    lines = [
        wr_header,
        f'{trades_str}  |  Myfxbook #12044019',
        f'Profit Factor: {pf:.2f}',
        f'Total Pips:    +{pips:,}',
        f'Total Return:  {sign}{gain:.1f}%',
        'No screenshots. No cherry-picked months.',
        'Raw Spread  |  IC Markets  |  ASIC + CySEC',
    ]

    def data_frame(t):
        return cascade_text_frame(t, lines, 4.5, 0.35, WHITE, 40, 640)

    data_clip = _clip(data_frame, 4.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Search "Vera Level" on Myfxbook', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)

    return [intro, hero, data_clip, cta, make_broker_card_clip()]


def make_monthly_reel(data: dict) -> list:
    """Returns [intro, hero, data, cta] for monthly post (~28s)."""
    from datetime import datetime as _dt
    from captions import monthly_pnl_from_daily

    acct = data.get('account', {})
    gain = float(acct.get('gain') or 0)

    # Build last-6-month P&L from dailyGain (Myfxbook MM/DD/YYYY dates)
    monthly_pnl: dict[str, float] = monthly_pnl_from_daily(data.get('dailyGain', []))

    months = list(monthly_pnl.items())[-6:]
    sign   = '+' if gain >= 0 else ''
    month_name = _dt.now().strftime('%B %Y')

    intro = _intro_clip()

    # Hero (3s): "Monthly P&L / {month_name}" fades in
    def hero_frame(t):
        return fade_in_frame(t, f'Monthly P&L\n{month_name}', 3.0, EMERALD, 72, (W // 2, H // 2))

    hero = _clip(hero_frame, 3.0)

    # Data (21.5s): bars draw L→R one per ~3s, value label appears after
    DUR_DATA   = 21.5
    bar_dur    = 2.0
    bar_gap    = 1.5
    start_y    = 550
    bar_h_px   = 60
    bar_spacing = bar_h_px + 40

    def data_frame(t):
        img  = bg_frame(t)
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
        return cta_fade_frame(t, 'Open IC Markets', _IB_CTA)

    cta = _clip(cta_frame, 2.0)
    return [intro, hero, data_clip, cta, make_broker_card_clip()]


def make_transparency_reel(data: dict) -> list:
    """Returns [intro, hero, data, cta] for transparency post (~25s)."""
    acct = data.get('account', {})
    gain = float(acct.get('gain') or 0)
    dd   = float(acct.get('drawdown') or 0)
    bal  = float(acct.get('balance') or 0)

    intro = _intro_clip()

    # Hero (4s): loss % slams in red
    def hero_frame(t):
        return countup_frame(t, 0, gain, 2.0, '{:.1f}%', RED, 140, (W // 2, H // 2))

    hero = _clip(hero_frame, 4.0)

    # Data (17.5s): two-section cascade
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
            s_t   = 9.0 + i * 0.6
            alp   = min(max(t - s_t, 0) / 0.4, 1.0)
            img   = draw_alpha_text(img, (W // 2, 1150 + i * 70), line,
                                     load_font(fs, bold=bold), color, alp)
        return np.array(img)

    data_clip = _clip(data_frame, 17.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Full history on Myfxbook', _VERIFY_CTA)

    cta = _clip(cta_frame, 2.0)
    return [intro, hero, data_clip, cta, make_broker_card_clip()]


_RECOVERY_MONTHS = [
    ('July',      1000, 1500.00),
    ('August',    1000, 3750.00),
    ('September', 1000, 7125.00),
    ('October',   1000, 12187.50),
    ('November',  1000, 19781.25),
    ('December',  1000, 31171.88),
]


def make_recovery_plan_reel() -> list:
    """Returns [intro, hero, data, cta] for recovery-plan post (~28s)."""
    from datetime import datetime as _dt
    now_month = _dt.now().strftime('%B')

    intro = _intro_clip()

    def hero_frame(t):
        return fade_in_frame(t, '$1,000/month  50% target', 3.0, EMERALD, 56, (W // 2, H // 2))

    hero = _clip(hero_frame, 3.0)

    ROW_DUR  = 3.0
    GAP      = 0.4
    DUR_DATA = len(_RECOVERY_MONTHS) * (ROW_DUR + GAP) + 2.5

    def data_frame(t):
        img   = bg_frame(t)
        font  = load_font(36)
        fontb = load_font(36, bold=True)
        start_y = 460

        header_alp = min(t / 0.5, 1.0)
        img = draw_alpha_text(img, (W // 2, start_y - 60),
                               'Month  +$1,000  Balance', font, MUTED, header_alp)

        for i, (month, topup, end_bal) in enumerate(_RECOVERY_MONTHS):
            row_start = i * (ROW_DUR + GAP)
            elapsed   = max(t - row_start, 0)
            progress  = min(elapsed / ROW_DUR, 1.0)
            if progress <= 0:
                continue

            is_now = (month == now_month)
            prefix = '> ' if is_now else '  '
            color  = EMERALD if is_now else WHITE
            current_bal = end_bal * ease_out(elapsed, ROW_DUR)
            row_text = f'{prefix}{month}  +${topup:,}  ->  ${current_bal:,.0f}'
            y = start_y + i * 70

            alp = min(elapsed / 0.3, 1.0)
            img = draw_alpha_text(img, (W // 2, y), row_text,
                                   fontb if is_now else font, color, alp)

        end_t = len(_RECOVERY_MONTHS) * (ROW_DUR + GAP) + 0.5
        if t > end_t:
            proj_alp = min((t - end_t) / 0.5, 1.0)
            img = draw_alpha_text(img, (W // 2, start_y + len(_RECOVERY_MONTHS) * 70 + 60),
                                   'Projected: $31,171',
                                   load_font(48, bold=True), EMERALD, proj_alp)
        return np.array(img)

    data_clip = _clip(data_frame, DUR_DATA)

    def cta_frame(t):
        return cta_fade_frame(t, 'Open IC Markets', _IB_CTA)

    cta = _clip(cta_frame, 2.0)
    return [intro, hero, data_clip, cta, make_broker_card_clip()]


def make_edu_reel(edu_type: str, content: dict) -> list:
    """Returns [intro, hero, data, cta] for edu post (~22s)."""
    from reels.animator import typewriter_frame as _typewriter_frame

    intro = _intro_clip()

    if edu_type == 'risk':
        title = f"Rule #{content['rule_num']} - {content['title']}"

        def hero_frame(t):
            return _typewriter_frame(t, title, 5.0, EMERALD, 56, (W // 2, H // 2))

        hero = _clip(hero_frame, 5.0)

        body  = content.get('body', '')
        body_lines = textwrap.wrap(body, width=42)
        ex_text = (f"${content['example_account']:,} account\n"
                   f"-> max ${content['example_risk']:,} per trade\n"
                   f"at {content['example_rr']}")
        ex_lines = ex_text.split('\n')

        def data_frame(t):
            return cascade_text_frame(t, body_lines + [''] + ex_lines,
                                      13.5, 0.8, WHITE, 38, 620)

        data_clip = _clip(data_frame, 13.5)

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
            return cascade_text_frame(t, info_lines, 13.5, 0.8, WHITE, 36, 640)

        data_clip = _clip(data_frame, 13.5)

    else:  # setup
        pair  = content.get('pair', 'XAUUSD')
        title = f"{pair} {content.get('direction', 'LONG')} Setup"

        def hero_frame(t):  # noqa: F811
            return _typewriter_frame(t, title, 5.0, EMERALD, 58, (W // 2, H // 2))

        hero = _clip(hero_frame, 5.0)

        steps = content.get('steps', [])
        step_lines = [f'{i+1}. {s[0]} - {s[1]}' for i, s in enumerate(steps)]

        def data_frame(t):  # noqa: F811
            return cascade_text_frame(t, step_lines, 13.5, 0.6, WHITE, 36, 640)

        data_clip = _clip(data_frame, 13.5)

    def cta_frame(t):
        return cta_fade_frame(t, 'Open IC Markets', _IB_CTA)

    cta = _clip(cta_frame, 2.0)
    return [intro, hero, data_clip, cta, make_broker_card_clip()]


def make_broker_reel() -> list:
    """Standalone IC Markets broker spotlight reel (~17s)."""
    from reels.animator import typewriter_frame as _typewriter_frame

    # Pre-fetch banner at full-reel size (downloaded once, cached)
    BW_F, BH_F = 660, 1320
    BX_F = (W - BW_F) // 2   # 210 — horizontally centred
    BY_F = 60
    banner_arr_full = _get_ib_banner(BW_F, BH_F)

    intro = _intro_clip()

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

    # Banner scene — official IB promo image fills most of the canvas
    text_y = BY_F + BH_F + 55  # 1435

    def banner_frame(t):
        img = bg_frame(t)
        img_arr = np.array(img, dtype=np.float32)
        alp = min(t / 0.5, 1.0)

        if banner_arr_full is not None:
            img_arr[BY_F:BY_F + BH_F, BX_F:BX_F + BW_F] = (
                img_arr[BY_F:BY_F + BH_F, BX_F:BX_F + BW_F] * (1.0 - alp)
                + banner_arr_full * alp
            )

        img = Image.fromarray(img_arr.astype(np.uint8))
        img = draw_alpha_text(img, (W // 2, text_y),
                               _IB_CTA, load_font(34, bold=True), EMERALD, alp)
        img = draw_alpha_text(img, (W // 2, text_y + 60),
                               'IB #91936  ·  Referral link', load_font(26), MUTED,
                               alp * 0.7)
        return np.array(img)

    banner_scene = _clip(banner_frame, 3.5)
    return [intro, hero, data_clip, banner_scene]


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
                               'RECOVERY PLAN', load_font(56, bold=True), EMERALD, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 - 80),
                               '$1,000 / month', load_font(80, bold=True), WHITE, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 110),
                               'Target: $31,171', load_font(56), EMERALD, 1.0)
        if recovery_day > 0:
            img = draw_alpha_text(img, (W // 2, H // 2 + 250),
                                   f'Day {recovery_day}', load_font(48), MUTED, 1.0)

    elif post_type == 'edu':
        img = draw_alpha_text(img, (W // 2, H // 2 - 120),
                               'RISK MANAGEMENT', load_font(56, bold=True), EMERALD, 1.0)
        img = draw_alpha_text(img, (W // 2, H // 2 + 80),
                               'Education', load_font(72), WHITE, 1.0)

    elif post_type == 'broker':
        banner_arr = _get_ib_banner(600, 1200)
        if banner_arr is not None:
            img_arr = np.array(img, dtype=np.float32)
            bx = (W - 600) // 2   # 240
            by = (H - 1200) // 2  # 360
            img_arr[by:by + 1200, bx:bx + 600] = banner_arr
            img = Image.fromarray(img_arr.astype(np.uint8))
        img = draw_alpha_text(img, (W // 2, 180),
                               'IC MARKETS', load_font(64, bold=True), WHITE, 1.0)
        img = draw_alpha_text(img, (W // 2, H - 130),
                               'Raw Spread  ·  ASIC + CySEC', load_font(40), EMERALD, 1.0)
        img = draw_alpha_text(img, (W // 2, H - 65),
                               _IB_CTA, load_font(32, bold=True), EMERALD, 1.0)

    # Footer handle (skip for broker where IB URL is at bottom)
    if post_type != 'broker':
        img = draw_alpha_text(img, (W // 2, H - 50),
                               '@veralevel.fx', load_font(30), MUTED, 0.7)

    return img
