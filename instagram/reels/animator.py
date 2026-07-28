"""
animator.py — PIL frame-generation primitives for Vera Level FX reels.

All public functions return np.ndarray of shape (1920, 1080, 3) uint8.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ── Canvas dimensions ──────────────────────────────────────────────────────────
W, H = 1080, 1920
FPS = 30

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
_SCANLINE_CACHE: 'Image.Image | None' = None


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


def scanline_overlay() -> Image.Image:
    """Cached RGBA PIL image: black horizontal lines every 4 px at 6% opacity."""
    global _SCANLINE_CACHE
    if _SCANLINE_CACHE is not None:
        return _SCANLINE_CACHE
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    alpha   = int(0.06 * 255)
    for y in range(0, H, 4):
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    _SCANLINE_CACHE = overlay
    return _SCANLINE_CACHE


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


def ease_out_back(x: float, c1: float = 1.5) -> float:
    """Ease-out with overshoot. c1 controls overshoot amount (1.5 = mild)."""
    x = min(max(x, 0.0), 1.0)
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


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

def animated_bg_frame(t: float) -> Image.Image:
    """PIL RGB Image: drifting radial bg + particles + scanlines + grain + vignette.

    Centre brightness pulses gently on a 4s sine cycle. The gradient centre
    wanders on a slow Lissajous path so long holds never feel static.
    """
    # Cached pixel-coordinate grid (computed once)
    if not hasattr(animated_bg_frame, '_grid'):
        animated_bg_frame._grid = np.mgrid[0:H, 0:W].astype(np.float32)
    ys, xs = animated_bg_frame._grid

    # Gradient drift — Lissajous wander of the radial centre
    cx = W / 2 + 80 * np.sin(2 * np.pi * t / 13.0)
    cy = H / 2 + 120 * np.sin(2 * np.pi * t / 17.0)

    dist     = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    max_dist = np.sqrt((W / 2) ** 2 + (H / 2) ** 2)
    frac     = np.clip(dist / max_dist, 0.0, 1.0)  # 0 = centre, 1 = corner

    core   = np.array(NAVY, dtype=np.float32)
    edge   = np.array((0, 8, 20), dtype=np.float32)  # near-black edges
    bg_arr = core * (1.0 - frac[:, :, None]) + edge * frac[:, :, None]

    pulse  = 1.0 + 0.08 * np.sin(2 * np.pi * t / 4.0)
    bg_arr = np.clip(bg_arr * pulse, 0, 255).astype(np.uint8)
    img    = Image.fromarray(bg_arr, 'RGB').convert('RGBA')
    img    = Image.alpha_composite(img, _particle_overlay(t))
    img    = Image.alpha_composite(img, scanline_overlay())

    arr = np.array(img.convert('RGB'), dtype=np.uint8)
    if arr.shape == (H, W, 3):
        # Film grain — prevents H.264 banding after IG re-encode
        rng   = np.random.default_rng(seed=int(t * 30))
        grain = rng.integers(-4, 5, (*arr.shape[:2], 1), dtype=np.int16)
        arr   = np.clip(arr.astype(np.int16) + grain, 0, 255).astype(np.uint8)

        # Vignette — darken edges 25%, cached as a float mask
        if not hasattr(animated_bg_frame, '_vignette'):
            v_dist = np.sqrt(((xs - W / 2) / (W / 2)) ** 2 +
                             ((ys - H / 2) / (H / 2)) ** 2)
            animated_bg_frame._vignette = \
                (1 - 0.25 * np.clip(v_dist, 0, 1) ** 2)[..., np.newaxis]
        arr = (arr * animated_bg_frame._vignette).clip(0, 255).astype(np.uint8)

    return Image.fromarray(arr, 'RGB')


def bg_frame(t: float) -> Image.Image:
    """Alias kept for backward compat — delegates to animated_bg_frame."""
    return animated_bg_frame(t)


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


def draw_pulsing_dot(img: Image.Image, pos, t: float,
                     positive: bool = True) -> Image.Image:
    """Draw a pulsing circle (GREEN if positive, RED if not) at pos.

    Radius oscillates between 8 and 16 px on a 1.2 s cycle.
    An outer ring fades out (sonar ping effect).
    """
    color   = GREEN if positive else RED
    r_inner = int(8 + 4 * np.sin(2 * np.pi * t / 1.2) ** 2)
    r_outer = int(r_inner + 10 + 14 * ((t * 0.8) % 1.0))
    ping_alp = int(180 * (1.0 - (t * 0.8) % 1.0))

    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    cx, cy  = pos
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer],
                 outline=(*color, ping_alp), width=2)
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner],
                 fill=(*color, 230))
    base = img.convert('RGBA')
    return Image.alpha_composite(base, overlay).convert('RGB')


def odometer_frame(t: float, value: float, dur: float, fmt: str,
                   color, fontsize: int, center) -> np.ndarray:
    """Digits roll through 0-9 before snapping to the final value."""
    img      = bg_frame(t)
    progress = ease_out(t, dur)
    text     = fmt.format(value)

    result_chars = []
    digit_idx    = 0
    n_digits     = sum(ch.isdigit() for ch in text)
    for ch in text:
        if ch.isdigit():
            target        = int(ch)
            # Left→right lock: big (leftmost) digits settle first
            digit_progress = min(progress * (1.0 + (n_digits - 1 - digit_idx) * 0.15), 1.0)
            if digit_progress < 0.95:
                rolled = int((digit_progress * 10 * (digit_idx + 1)) % 10)
            else:
                rolled = target
            result_chars.append(str(rolled))
            digit_idx += 1
        else:
            result_chars.append(ch)

    display = ''.join(result_chars)
    img = draw_glow_text(img, center, display, fontsize, color,
                         glow_radius=20, alpha=min(progress * 2, 1.0))
    return np.array(img)


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
    Lines slide up 20px + fade in sequentially with Direction C aesthetic.

    Line 0 is the headline: bold, slightly larger, no accent bar.
    Lines 1+ get a 3px emerald left-edge accent bar before text.
    Easing: ease_out_back(1.5) — mild overshoot.
    """
    img = bg_frame(t)
    font = load_font(fontsize)
    font_headline = load_font(fontsize + 10, bold=True)
    line_height = fontsize + 24

    for i, line in enumerate(lines):
        line_t = t - i * stagger
        if line_t <= 0:
            continue
        x = min(line_t / dur, 1.0)
        progress = ease_out_back(x, c1=1.5)
        alpha = min(max(progress, 0.0), 1.0)
        y_offset = int(20 * (1.0 - min(progress, 1.0)))
        y = top_y + i * line_height + y_offset

        if i == 0:
            img = draw_alpha_text(img, (W // 2, y), line, font_headline, color, alpha)
        else:
            if alpha > 0.05:
                bar_x = 80
                bar_y = y - fontsize // 2
                bar_alpha_int = int(alpha * 220)
                bar_rgba = img.convert('RGBA')
                bar_layer = Image.new('RGBA', bar_rgba.size, (0, 0, 0, 0))
                bar_draw = ImageDraw.Draw(bar_layer)
                bar_draw.rectangle([bar_x, bar_y, bar_x + 3, bar_y + fontsize],
                                   fill=(*EMERALD, bar_alpha_int))
                img = Image.alpha_composite(bar_rgba, bar_layer).convert('RGB')
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


def _glow_text_layer(w: int, h: int, text: str, fontsize: int,
                     text_rgba, glow_rgb, glow_radius: int) -> Image.Image:
    """RGBA layer: centred text in text_rgba with a blurred glow in glow_rgb."""
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(layer)
    font  = load_font(max(int(fontsize), 1), bold=True)

    glow_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gdraw      = ImageDraw.Draw(glow_layer)
    glow_fill  = (int(glow_rgb[0]), int(glow_rgb[1]), int(glow_rgb[2]),
                  int(text_rgba[3]))

    try:
        gdraw.text((w // 2, h // 2), text, font=font, fill=glow_fill, anchor='mm')
        draw.text((w // 2, h // 2), text, font=font, fill=text_rgba, anchor='mm')
    except (TypeError, ValueError, AttributeError):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pos = (w // 2 - tw // 2, h // 2 - th // 2)
        gdraw.text(pos, text, font=font, fill=glow_fill)
        draw.text(pos, text, font=font, fill=text_rgba)

    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=glow_radius))
    return Image.alpha_composite(glow_layer, layer)


def number_punch_frame(t: float, dur: float, text: str, fontsize: int = 140,
                       color=WHITE, glow_color=EMERALD, final_color=None,
                       w: int = W, h: int = H) -> Image.Image:
    """
    High-impact number reveal (returns transparent RGBA overlay):
      0–40%    scale 1.5→0.96 with ease_out, alpha 0→1, ghost motion-blur layers
      at 40%   impact frame: triple glow radius + white flash for ~2 frames
      40–80%   shockwave ellipse expands + fades
      60–100%  colour crossfades from `color` to final_color (if given)
    """
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))

    p = min(t / dur, 1.0) if dur > 0 else 1.0
    punch_end  = 0.40
    settle_end = 0.80

    if p <= punch_end:
        scale = 1.5 - 0.54 * ease_out(p, punch_end)
        alpha = int(255 * min(p / 0.15, 1.0))
        # Ghost layers for motion-blur feel
        for ghost_scale, ghost_alpha in [(scale + 0.10, 60), (scale + 0.05, 100)]:
            ghost = _glow_text_layer(w, h, text, int(fontsize * ghost_scale),
                                     (*color[:3], min(ghost_alpha, alpha)),
                                     glow_color, glow_radius=20)
            img = Image.alpha_composite(img, ghost)
        # Impact frames (last ~2 frames of punch phase): white flash, triple glow
        frames_left = (punch_end - p) * dur * FPS
        if frames_left < 2:
            layer = _glow_text_layer(w, h, text, int(fontsize * scale),
                                     (*WHITE[:3], alpha), WHITE, glow_radius=60)
        else:
            layer = _glow_text_layer(
                w, h, text, int(fontsize * scale), (*color[:3], alpha),
                glow_color, glow_radius=int(18 + 12 * (1 - p / punch_end)))
        img = Image.alpha_composite(img, layer)
    else:
        # Shockwave ellipse expands + fades
        shock_p = ease_out(min((p - punch_end) / (settle_end - punch_end), 1.0), 1.0)
        shock_r = int(60 + shock_p * 300)
        shock_a = int(180 * (1 - shock_p))
        if shock_a > 0:
            shock_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            sd = ImageDraw.Draw(shock_layer)
            sd.ellipse(
                (w // 2 - shock_r, h // 2 - shock_r,
                 w // 2 + shock_r, h // 2 + shock_r),
                outline=(*EMERALD, shock_a), width=3)
            shock_layer = shock_layer.filter(ImageFilter.GaussianBlur(4))
            img = Image.alpha_composite(img, shock_layer)

        # Settled text with optional colour crossfade
        text_color = color
        if final_color is not None:
            fade_p = min((p - punch_end) / 0.30, 1.0)
            text_color = tuple(
                int(color[i] * (1 - fade_p) + final_color[i] * fade_p)
                for i in range(3)
            )
        layer = _glow_text_layer(w, h, text, int(fontsize * 0.96),
                                 (*text_color[:3], 255), glow_color,
                                 glow_radius=24)
        img = Image.alpha_composite(img, layer)

    return img


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
    Two-line call-to-action with Direction C aesthetic.

    Letterbox bars sweep in (0–400ms).
    line1: 48pt bold EMERALD, centred at H//2 - 60. Animated underline grows L→R.
    line2: 30pt MUTED, centred at H//2 + 60.
    """
    img = bg_frame(t)

    # Letterbox bars sweep in from 0 → full width over 400ms
    bar_progress = ease_out(t, 0.4)
    bar_w = int(W * bar_progress)
    if bar_w > 0:
        draw0 = ImageDraw.Draw(img)
        draw0.rectangle([0, 0, bar_w, 4], fill=EMERALD)
        draw0.rectangle([W - bar_w, H - 4, W, H], fill=EMERALD)

    # line1: 48pt bold EMERALD
    alpha1 = ease_out(t, 1.0)
    font1 = load_font(48, bold=True)
    img = draw_alpha_text(img, (W // 2, H // 2 - 60), line1, font1, EMERALD, alpha1)

    # Animated underline: emerald rect grows L→R under line1 starting at t=0.3
    if t > 0.3:
        ul_progress = ease_out(t - 0.3, 0.4)
        ul_w = int(600 * ul_progress)
        ul_x = W // 2 - 300
        ul_y = H // 2 - 20
        draw1 = ImageDraw.Draw(img)
        draw1.rectangle([ul_x, ul_y, ul_x + ul_w, ul_y + 3], fill=EMERALD)

    # line2: 30pt MUTED
    if line2 and t > 0.4:
        alpha2 = ease_out(t - 0.4, 1.0)
        font2 = load_font(30)
        img = draw_alpha_text(img, (W // 2, H // 2 + 60), line2, font2, MUTED, alpha2)

    return np.array(img)


def cta_comment_pill_frame(t: float, dur: float, action_text: str = 'BROKER',
                           subtitle: str | None = None,
                           handle: str = '@veralevel.fx',
                           w: int = W, h: int = H) -> Image.Image:
    """
    Instagram comment-field CTA (returns transparent RGBA overlay):
    - Rounded pill with placeholder → typewriter of action_text → blinking cursor
    - Emerald send-arrow pulses on the right
    - Handle + subtitle text above
    """
    img  = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pill_w, pill_h = 700, 72
    pill_x = (w - pill_w) // 2
    pill_y = h // 2 + 60

    # Pill background (rounded_rectangle needs Pillow >= 8.2 — plain rect fallback)
    pill_box = [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h]
    try:
        draw.rounded_rectangle(pill_box, radius=pill_h // 2,
                               fill=(20, 30, 50, 220),
                               outline=(*MUTED, 120), width=1)
    except AttributeError:
        draw.rectangle(pill_box, fill=(20, 30, 50, 220),
                       outline=(*MUTED, 120), width=1)

    # Typewriter progress
    type_start = 0.3
    type_dur   = 0.8
    type_p  = (max(0.0, min((t / dur - type_start) / type_dur, 1.0))
               if dur > 0 else 1.0)
    n_chars = int(type_p * len(action_text))
    typed   = action_text[:n_chars]

    font_pill   = load_font(32, bold=True)
    font_label  = load_font(28)
    font_handle = load_font(36, bold=True)

    text_x = pill_x + 32
    text_y = pill_y + pill_h // 2

    if typed:
        draw.text((text_x, text_y), typed, font=font_pill,
                  fill=(*WHITE, 255), anchor='lm')
        # Blinking cursor
        cursor_bbox = draw.textbbox((text_x, text_y - 16), typed, font=font_pill)
        cursor_x    = cursor_bbox[2] + 3
        if int(t * 2.5) % 2 == 0:
            draw.rectangle([cursor_x, pill_y + 18,
                            cursor_x + 3, pill_y + pill_h - 18],
                           fill=(*WHITE, 255))
    else:
        draw.text((text_x, text_y), 'Comment below...', font=font_pill,
                  fill=(*MUTED, 180), anchor='lm')

    # Send arrow (paper-plane triangle) on the right, pulsing
    arrow_cx = pill_x + pill_w - 36
    arrow_cy = pill_y + pill_h // 2
    pulse    = 0.85 + 0.15 * np.sin(2 * np.pi * t / 0.9)
    arrow_r  = int(16 * pulse)
    pts = [
        (arrow_cx + arrow_r, arrow_cy),
        (arrow_cx - arrow_r // 2, arrow_cy - arrow_r // 2),
        (arrow_cx - arrow_r // 2, arrow_cy + arrow_r // 2),
    ]
    draw.polygon(pts, fill=(*EMERALD, int(200 * min(t / 0.5, 1.0))))

    # Handle above
    handle_y = pill_y - 60
    draw.text((w // 2, handle_y), handle, font=font_handle,
              fill=(*WHITE, 255), anchor='mm')

    # Subtitle
    if subtitle:
        draw.text((w // 2, handle_y - 44), subtitle, font=font_label,
                  fill=(*MUTED, 200), anchor='mm')

    return img
