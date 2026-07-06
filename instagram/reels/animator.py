"""
animator.py — PIL frame-generation primitives for Vera Level FX reels.

All public functions return np.ndarray of shape (1920, 1080, 3) uint8.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ── Canvas dimensions ──────────────────────────────────────────────────────────
W, H = 1080, 1920

# ── Brand palette — aligned with vera-level-forex.vercel.app ─────────────────
NAVY    = (0,   24,  53)   # site --primary #001835
EMERALD = (5,   150, 105)  # site bg-success #059669, sole accent
WHITE   = (255, 255, 255)
MUTED   = (107, 114, 128)  # site secondary text #6B7280
GREEN   = (5,   150, 105)  # positive P&L, matches EMERALD
RED     = (239, 68,  68)   # site error #EF4444

# ── Font helpers ──────────────────────────────────────────────────────────────
_FONT_DIR = Path(__file__).parent.parent / 'assets' / 'fonts'


def load_font(size: int, bold: bool = False):
    candidates = []
    if bold:
        candidates += [
            str(_FONT_DIR / 'Roboto-Bold.ttf'),
            '/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        ]
    candidates += [
        str(_FONT_DIR / 'Roboto-Regular.ttf'),
        '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            pass
    return ImageFont.load_default()


# ── Background cache ──────────────────────────────────────────────────────────
_BG_CACHE: np.ndarray | None = None


def radial_bg() -> np.ndarray:
    """Static navy radial gradient (H, W, 3) uint8, cached after first call."""
    global _BG_CACHE
    if _BG_CACHE is not None:
        return _BG_CACHE

    y, x = np.mgrid[0:H, 0:W]
    cx, cy = W // 2, H // 2
    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    t = np.clip(dist / max_dist, 0.0, 1.0)  # 0 = centre, 1 = corner

    core = np.array(NAVY, dtype=np.float32)
    edge = np.array((0, 8, 20), dtype=np.float32)  # near-black edges, proportional to NAVY

    img = (core * (1.0 - t[:, :, None]) + edge * t[:, :, None]).astype(np.uint8)
    _BG_CACHE = img
    return _BG_CACHE


# ── Easing ────────────────────────────────────────────────────────────────────

def ease_out(t: float, dur: float) -> float:
    """Ease-out cubic: smooth deceleration from 0 → 1 over dur seconds."""
    if dur <= 0:
        return 1.0
    x = min(t / dur, 1.0)
    return 1 - (1 - x) ** 3


def ease_spring(t: float, dur: float, stiffness: float = 2.5,
                damping: float = 1.5) -> float:
    """Damped spring: overshoots ~10-15% then settles at 1.0."""
    if dur <= 0:
        return 1.0
    x = min(10.0 * t / dur, 10.0)
    return 1.0 - (1.0 - x / 10.0) ** 3 * np.cos(stiffness * x) * np.exp(-damping * x)


# ── Particle overlay ──────────────────────────────────────────────────────────

def _particle_overlay(t: float, n: int = 8, opacity: float = 0.08,
                      seed: int = 42) -> Image.Image:
    """RGBA PIL image with n emerald ellipses drifting upward."""
    rng = np.random.default_rng(seed)
    x_positions = rng.integers(50, W - 50, n)
    y_starts    = rng.integers(0, H, n)
    speeds      = rng.uniform(20, 80, n)
    sizes       = rng.integers(10, 40, n)

    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    alpha_val = int(opacity * 255)

    for i in range(n):
        px = int(x_positions[i])
        py = int((y_starts[i] - speeds[i] * t) % H)
        r  = int(sizes[i])
        draw.ellipse([px - r, py - r, px + r, py + r],
                     fill=(EMERALD[0], EMERALD[1], EMERALD[2], alpha_val))

    return overlay


# ── Base frame ────────────────────────────────────────────────────────────────

def bg_frame(t: float) -> Image.Image:
    """PIL RGB Image: radial background + particle overlay."""
    bg_arr = radial_bg()
    img = Image.fromarray(bg_arr, 'RGB').convert('RGBA')
    particles = _particle_overlay(t)
    img = Image.alpha_composite(img, particles)
    return img.convert('RGB')


# ── Text drawing primitive ────────────────────────────────────────────────────

def draw_alpha_text(img: Image.Image, pos, text: str, font,
                     color, alpha: float) -> Image.Image:
    """
    Draw centre-anchored text with alpha onto an RGB PIL Image.

    color  — (R, G, B) 3-tuple
    alpha  — float 0.0–1.0
    Returns RGB PIL Image.
    """
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    r, g, b = int(color[0]), int(color[1]), int(color[2])
    a = int(alpha * 255)

    try:
        # FreeType fonts support the 'mm' anchor (middle-x, middle-y)
        draw.text(pos, text, font=font, fill=(r, g, b, a), anchor='mm')
    except (TypeError, ValueError, AttributeError):
        # Bitmap / default fonts: calculate centre offset manually
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        except AttributeError:
            # Very old Pillow: textsize fallback
            tw, th = draw.textsize(text, font=font)  # type: ignore[attr-defined]
        x = int(pos[0] - tw / 2)
        y = int(pos[1] - th / 2)
        draw.text((x, y), text, font=font, fill=(r, g, b, a))

    base = img.convert('RGBA')
    result = Image.alpha_composite(base, overlay)
    return result.convert('RGB')


def draw_glow_text(img: Image.Image, pos, text: str, fontsize: int,
                   color, glow_radius: int = 18, alpha: float = 1.0) -> Image.Image:
    """Render text with a soft outer glow of the same colour."""
    font = load_font(fontsize, bold=True)
    # 1. Draw text on transparent layer
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw  = ImageDraw.Draw(layer)
    r, g, b = int(color[0]), int(color[1]), int(color[2])
    a = int(alpha * 255)
    try:
        draw.text(pos, text, font=font, fill=(r, g, b, a), anchor='mm')
    except (TypeError, ValueError, AttributeError):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((pos[0] - tw // 2, pos[1] - th // 2), text,
                  font=font, fill=(r, g, b, a))
    # 2. Blur a copy for glow
    glow = layer.filter(ImageFilter.GaussianBlur(radius=glow_radius))
    # 3. Composite: glow first, sharp text on top
    base = img.convert('RGBA')
    base = Image.alpha_composite(base, glow)
    base = Image.alpha_composite(base, layer)
    return base.convert('RGB')


# ── Public animation primitives ───────────────────────────────────────────────

def countup_frame(t: float, start: float, end: float, dur: float,
                  fmt: str, color, fontsize: int, center) -> np.ndarray:
    """Ease-out animated number from start → end over dur seconds."""
    value = start + (end - start) * ease_out(t, dur)
    text  = fmt.format(value)
    img   = bg_frame(t)
    font  = load_font(fontsize, bold=True)
    img   = draw_alpha_text(img, center, text, font, color, 1.0)
    return np.array(img)


def cascade_text_frame(t: float, lines, dur: float, stagger: float,
                       color, fontsize: int, top_y: int) -> np.ndarray:
    """
    Lines slide up 20 px + fade in sequentially.

    Line i starts animating at t = i * stagger.
    Line height = fontsize + 20. All lines centred at W//2.
    """
    img = bg_frame(t)
    font = load_font(fontsize)
    line_height = fontsize + 20

    for i, line in enumerate(lines):
        line_t = t - i * stagger
        if line_t <= 0:
            continue
        progress = ease_out(line_t, dur)
        alpha    = progress
        y_offset = int(20 * (1.0 - progress))   # 20 px below → final position
        y = top_y + i * line_height + y_offset
        img = draw_alpha_text(img, (W // 2, y), line, font, color, alpha)

    return np.array(img)


def fade_in_frame(t: float, text: str, dur: float,
                  color, fontsize: int, center) -> np.ndarray:
    """Simple opacity 0 → 1 over dur seconds."""
    img   = bg_frame(t)
    font  = load_font(fontsize)
    alpha = ease_out(t, dur)
    img   = draw_alpha_text(img, center, text, font, color, alpha)
    return np.array(img)


def typewriter_frame(t: float, text: str, dur: float,
                     color, fontsize: int, center) -> np.ndarray:
    """Characters appear one-by-one; count driven by ease_out."""
    n_chars = int(len(text) * ease_out(t, dur))
    visible = text[:n_chars]
    img = bg_frame(t)
    if visible:
        font = load_font(fontsize)
        img  = draw_alpha_text(img, center, visible, font, color, 1.0)
    return np.array(img)


def slide_bar_frame(t: float, dur: float, y: int,
                    thickness: int = 8) -> np.ndarray:
    """Emerald horizontal bar sweeps left → right over dur seconds."""
    img   = bg_frame(t)
    bar_w = int(W * ease_out(t, dur))
    draw  = ImageDraw.Draw(img)
    draw.rectangle([0, y, bar_w, y + thickness], fill=EMERALD)
    return np.array(img)


def logo_fade_frame(t: float, brand: str = 'VERA LEVEL FX') -> np.ndarray:
    """
    1.5 s branded intro frame.

    0.0 s  — emerald sweep bar animates L→R (completes at 0.8 s)
    0.4 s  — brand name fades in (56 pt bold EMERALD, centred at W//2, H//2-80)
    0.7 s  — subtitle 'Live IC Markets Account' fades in (30 pt MUTED)
    """
    img = bg_frame(t)

    # Emerald sweep bar
    bar_w = int(W * ease_out(t, 0.8))
    bar_y = H // 2 - 10
    draw  = ImageDraw.Draw(img)
    draw.rectangle([0, bar_y, bar_w, bar_y + 8], fill=EMERALD)

    # Brand name
    if t > 0.4:
        brand_alpha = ease_out(t - 0.4, 0.8)   # full by ~1.2 s
        font_brand  = load_font(56, bold=True)
        img = draw_alpha_text(img, (W // 2, H // 2 - 80),
                               brand, font_brand, EMERALD, brand_alpha)

    # Subtitle
    if t > 0.7:
        sub_alpha = ease_out(t - 0.7, 0.8)
        font_sub  = load_font(30)
        img = draw_alpha_text(img, (W // 2, H // 2 + 50),
                               'Live IC Markets Account', font_sub, MUTED, sub_alpha)

    return np.array(img)


def cta_fade_frame(t: float, line1: str, line2: str = '') -> np.ndarray:
    """
    Two-line call-to-action fade-in.

    line1 — starts at t=0, 36 pt bold EMERALD,  centred at H//2-40
    line2 — starts at t=0.4, 30 pt MUTED, centred at H//2+40
    Both ease-out over 1.0 s.
    """
    img = bg_frame(t)

    # line1
    alpha1 = ease_out(t, 1.0)
    font1  = load_font(36, bold=True)
    img    = draw_alpha_text(img, (W // 2, H // 2 - 40),
                              line1, font1, EMERALD, alpha1)

    # line2
    if line2 and t > 0.4:
        alpha2 = ease_out(t - 0.4, 1.0)
        font2  = load_font(30)
        img    = draw_alpha_text(img, (W // 2, H // 2 + 40),
                                  line2, font2, MUTED, alpha2)

    return np.array(img)
