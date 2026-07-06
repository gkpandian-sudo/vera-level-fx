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
    bg_frame, draw_alpha_text, draw_glow_text, load_font, ease_out,
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
        progress = ease_out(t, duration)
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

        glow   = overlay.filter(ImageFilter.GaussianBlur(radius=8))
        base   = img.convert('RGBA')
        base   = Image.alpha_composite(base, glow)
        base   = Image.alpha_composite(base, overlay)
        result = base.convert('RGB')

        alpha  = min(progress * 2, 1.0)
        result = draw_glow_text(result, center, f'{win_rate:.0f}%',
                                fontsize=160, color=EMERALD,
                                glow_radius=24, alpha=alpha)
        result = draw_alpha_text(result, (cx, cy + 190),
                                 'Win Rate  ·  Verified', load_font(36), MUTED,
                                 alpha)
        return np.array(result)

    return VideoClip(make_frame, duration=duration).set_fps(FPS)
