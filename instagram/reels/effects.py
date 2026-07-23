"""
effects.py — Complex animated overlays for Vera Level FX reels.

All public clip-returning functions return MoviePy VideoClip instances at 30 FPS.
"""
from __future__ import annotations

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from moviepy.editor import VideoClip

from reels.animator import (
    W, H, FPS, EMERALD, WHITE, GREEN, RED, MUTED,
    bg_frame, draw_alpha_text, draw_glow_text, load_font, ease_out, ease_spring,
)


# ── Equity curve ──────────────────────────────────────────────────────────────

def equity_curve_clip(daily_gain: list, duration: float,
                      plot_rect: tuple = (80, 1100, 1000, 1750)) -> VideoClip:
    """Animate an equity curve drawing itself left → right over `duration` seconds.

    daily_gain — list of [date_str, cumulative_pct, dollar] from vera-snapshot.json
    plot_rect  — (x0, y0, x1, y1) pixel bounds of the chart area
    """
    values = []
    for row in daily_gain:
        try:
            values.append(float(row[1]))
        except (IndexError, TypeError, ValueError):
            continue
    if len(values) < 2:
        values = [0.0, 0.0]

    x0, y0, x1, y1 = plot_rect
    chart_w = x1 - x0
    chart_h = y1 - y0

    v_min   = min(values)
    v_max   = max(values)
    v_range = max(v_max - v_min, 0.01)

    def _norm_y(v: float) -> int:
        return y1 - int((v - v_min) / v_range * chart_h)

    points = [
        (x0 + int(i / (len(values) - 1) * chart_w), _norm_y(v))
        for i, v in enumerate(values)
    ]
    is_positive = values[-1] >= values[0]
    line_color  = GREEN if is_positive else RED

    def make_frame(t: float) -> np.ndarray:
        img      = bg_frame(t)
        progress = ease_out(t, duration)
        n_pts    = max(2, int(progress * len(points)))
        visible  = points[:n_pts]

        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw    = ImageDraw.Draw(overlay)

        # Faint grid lines
        for row_i in range(5):
            gy = y0 + int(row_i / 4 * chart_h)
            draw.line([(x0, gy), (x1, gy)], fill=(255, 255, 255, 18), width=1)

        # Shaded area + curve
        if len(visible) >= 2:
            poly = list(visible) + [(visible[-1][0], y1), (visible[0][0], y1)]
            r, g, b = line_color
            draw.polygon(poly, fill=(r, g, b, 28))
            draw.line(visible, fill=(*line_color, 220), width=3)
            tx, ty = visible[-1]
            draw.ellipse([tx - 6, ty - 6, tx + 6, ty + 6],
                         fill=(*line_color, 255))

        glow   = overlay.filter(ImageFilter.GaussianBlur(radius=4))
        base   = img.convert('RGBA')
        base   = Image.alpha_composite(base, glow)
        base   = Image.alpha_composite(base, overlay)
        result = base.convert('RGB')

        sign = '+' if v_max >= 0 else ''
        s2   = '+' if values[-1] >= 0 else ''
        alp  = min(progress * 3, 1.0)
        result = draw_alpha_text(result, (x0 - 10, y0),
                                 f'{sign}{v_max:.1f}%', load_font(24), MUTED, alp)
        result = draw_alpha_text(result, (x0 + chart_w // 2, y1 + 30),
                                 f'Current: {s2}{values[-1]:.1f}%',
                                 load_font(28, bold=True), line_color, alp)
        return np.array(result)

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ── Win rate progress ring ────────────────────────────────────────────────────

def progress_ring_clip(win_rate: float, duration: float,
                       center: tuple = (W // 2, H // 2),
                       radius: int = 320) -> VideoClip:
    """Circular arc fills from 0° to win_rate % (of 360°) with emerald glow."""

    def make_frame(t: float) -> np.ndarray:
        img      = bg_frame(t)
        progress = ease_spring(t, duration)   # slight overshoot, then settles
        target   = (win_rate / 100.0) * 360.0
        current  = progress * target

        cx, cy = center
        bb = [cx - radius, cy - radius, cx + radius, cy + radius]

        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw    = ImageDraw.Draw(overlay)

        draw.arc(bb, start=0, end=360, fill=(*MUTED, 60), width=18)

        if current > 0:
            draw.arc(bb, start=-90, end=-90 + current,
                     fill=(*EMERALD, 220), width=18)

        # Tick marks every 10% around the ring
        for pct in range(0, 101, 10):
            angle_deg = -90 + pct / 100 * 360
            angle_rad = np.radians(angle_deg)
            tick_r_inner = radius - 18
            tick_r_outer = radius - 5
            x1 = int(cx + tick_r_inner * np.cos(angle_rad))
            y1 = int(cy + tick_r_inner * np.sin(angle_rad))
            x2 = int(cx + tick_r_outer * np.cos(angle_rad))
            y2 = int(cy + tick_r_outer * np.sin(angle_rad))
            draw.line([(x1, y1), (x2, y2)], fill=(*MUTED, 80), width=2)

        glow   = overlay.filter(ImageFilter.GaussianBlur(radius=8))
        base   = img.convert('RGBA')
        base   = Image.alpha_composite(base, glow)
        base   = Image.alpha_composite(base, overlay)
        result = base.convert('RGB')

        alpha = min(progress * 2, 1.0)
        shown = min(progress * win_rate, win_rate)  # counts up, synced to arc
        result = draw_glow_text(result, center, f'{shown:.0f}%',
                                fontsize=160, color=EMERALD,
                                glow_radius=24, alpha=alpha)
        result = draw_alpha_text(result, (cx, cy + 190),
                                 'Win Rate  ·  Verified', load_font(36), MUTED,
                                 alpha)
        return np.array(result)

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


# ── Ticker tape ───────────────────────────────────────────────────────────────

_TICKER_TEXT = (
    'EURUSD  ·  XAUUSD  ·  GBPJPY  ·  USDJPY  ·  GBPUSD  ·  '
    'AUDUSD  ·  USDCAD  ·  NZDUSD  ·  EURJPY  ·  XAGUSD  ·  '
)
_TICKER_SPEED = 120   # px/second
_TICKER_H     = 52    # strip height px
_TICKER_Y     = H - _TICKER_H - 10   # vertical position

_TICKER_BG_CACHE: 'Image.Image | None' = None


def ticker_tape_overlay(img: Image.Image, t: float) -> Image.Image:
    """Render a scrolling currency-pair ticker at the bottom of img."""
    font   = load_font(28)
    text   = _TICKER_TEXT * 4
    offset = int(t * _TICKER_SPEED) % (W * 2)

    strip = Image.new('RGBA', (W, _TICKER_H), (0, 10, 25, 200))
    draw  = ImageDraw.Draw(strip)
    draw.line([(0, 0), (W, 0)], fill=(*EMERALD, 120), width=1)

    x = -offset
    while x < W + 20:
        draw.text((x, _TICKER_H // 2), text,
                  font=font, fill=(*MUTED, 200), anchor='lm')
        try:
            tw = draw.textlength(text, font=font)
        except AttributeError:
            bbox = draw.textbbox((0, 0), text, font=font)
            tw   = bbox[2] - bbox[0]
        x += max(int(tw), W)

    base = img.convert('RGBA')
    base.paste(strip, (0, _TICKER_Y), strip)
    return base.convert('RGB')


# ── Candlestick background ────────────────────────────────────────────────────

_CANDLE_CACHE: 'Image.Image | None' = None


def candlestick_bg_overlay(img: Image.Image) -> Image.Image:
    """Stamp a ghost candlestick chart pattern at 5% opacity (cached)."""
    global _CANDLE_CACHE

    if _CANDLE_CACHE is None:
        overlay   = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw      = ImageDraw.Draw(overlay)
        rng       = np.random.default_rng(7)
        n_candles = 22
        candle_w  = 36
        gap       = (W - n_candles * candle_w) // (n_candles + 1)
        base_y    = int(H * 0.72)
        price     = 100.0
        alpha     = int(0.05 * 255)

        for i in range(n_candles):
            x     = gap + i * (candle_w + gap)
            chg   = rng.uniform(-4, 4)
            open_ = price
            close = price + chg
            high  = max(open_, close) + rng.uniform(1, 3)
            low   = min(open_, close) - rng.uniform(1, 3)
            price = close

            scale  = 6.0
            cy_mid = base_y - int(price * scale * 0.1)

            top_body = cy_mid - int(abs(chg) * scale)
            bot_body = cy_mid + int(abs(chg) * scale)
            top_wick = cy_mid - int((high - min(open_, close)) * scale)
            bot_wick = cy_mid + int((max(open_, close) - low) * scale)
            color    = GREEN if chg >= 0 else RED

            draw.line([(x + candle_w // 2, top_wick),
                       (x + candle_w // 2, bot_wick)],
                      fill=(*color, alpha), width=2)
            draw.rectangle([x + 4, top_body, x + candle_w - 4, bot_body],
                           fill=(*color, alpha))

        _CANDLE_CACHE = overlay

    base = img.convert('RGBA')
    return Image.alpha_composite(base, _CANDLE_CACHE).convert('RGB')


# ── Glowing border ────────────────────────────────────────────────────────────

def glow_border_overlay(img: Image.Image, t: float,
                        rect: tuple = (40, 200, W - 40, H - 200),
                        pulse_period: float = 2.0) -> Image.Image:
    """Draw a pulsing emerald neon rectangle border."""
    x0, y0, x1, y1 = rect
    pulse   = 0.6 + 0.4 * math.sin(2 * math.pi * t / pulse_period) ** 2
    alpha   = int(180 * pulse)
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    draw.rectangle([x0, y0, x1, y1], outline=(*EMERALD, alpha), width=3)
    glow  = overlay.filter(ImageFilter.GaussianBlur(radius=6))
    base  = img.convert('RGBA')
    base  = Image.alpha_composite(base, glow)
    base  = Image.alpha_composite(base, overlay)
    return base.convert('RGB')
