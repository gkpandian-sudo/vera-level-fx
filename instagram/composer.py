"""
PIL-based image composition utilities for Vera Level FX post backgrounds.

All functions accept and return float32 numpy arrays with shape (1080, 1080, 3)
and values in [0, 1]. This matches the format expected by matplotlib imshow.

Functions fall back to dark_bg() if the input image file is missing,
so the pipeline works before AI background images are generated.
"""

import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter

_NAVY_RGB = np.array([0.004, 0.055, 0.122], dtype=np.float32)
_SIZE = (1080, 1080)


def dark_bg() -> np.ndarray:
    """Return a solid dark navy 1080x1080 background as float32 [0,1]."""
    arr = np.empty((_SIZE[1], _SIZE[0], 3), dtype=np.float32)
    arr[:] = _NAVY_RGB
    return arr


def load_background(path: 'str | Path', size: tuple = _SIZE) -> np.ndarray:
    """Load AI background, center-crop to square, resize to size.

    Returns dark_bg() if path does not exist.
    """
    path = Path(path)
    if not path.exists():
        return dark_bg()
    try:
        img = Image.open(path).convert('RGB')
        w, h = img.size
        if w != h:
            m = min(w, h)
            left = (w - m) // 2
            top = (h - m) // 2
            img = img.crop((left, top, left + m, top + m))
        img = img.resize(size, Image.LANCZOS)
        return np.array(img, dtype=np.float32) / 255.0
    except Exception:
        # PIL raises various undocumented exceptions on corrupt/truncated images;
        # fall back to dark background rather than crashing the posting pipeline
        return dark_bg()


def gradient_panel(arr: np.ndarray, height_frac: float = 0.50) -> np.ndarray:
    """Fade the bottom height_frac of the image to black for text overlay."""
    arr = arr.copy()
    H = arr.shape[0]
    start_y = int(H * (1.0 - height_frac))
    for y in range(start_y, H):
        progress = (y - start_y) / max(H - start_y, 1)
        # exponent > 1 creates slow fade at top of panel, fast at bottom
        alpha = progress ** 1.4
        arr[y] = arr[y] * (1.0 - alpha)
    return np.clip(arr, 0.0, 1.0)


def frosted_glass_region(
    arr: np.ndarray,
    y_frac: float = 0.58,
    h_frac: float = 0.42,
    blur_r: int = 14,
    darkness: float = 0.78,
) -> np.ndarray:
    """Blur and darken a horizontal band to simulate frosted glass."""
    H, W = arr.shape[:2]
    y_px = int(H * y_frac)
    h_px = int(H * h_frac)
    h_px = min(h_px, H - y_px)

    img = Image.fromarray((np.clip(arr, 0.0, 1.0) * 255).astype(np.uint8))
    region = img.crop((0, y_px, W, y_px + h_px))
    blurred = region.filter(ImageFilter.GaussianBlur(blur_r))
    img.paste(blurred, (0, y_px))

    result = np.array(img, dtype=np.float32) / 255.0
    result[y_px:y_px + h_px] *= (1.0 - darkness)
    return np.clip(result, 0.0, 1.0)


def split_layout(
    arr: np.ndarray,
    split_frac: float = 0.50,
) -> tuple[np.ndarray, float]:
    """Paint the bottom (1 - split_frac) of the image solid black.

    Returns:
        result: modified numpy array
        split_y_axes: split position in matplotlib axes coordinates [0,1]
                      where 0=bottom, 1=top
    """
    arr = arr.copy()
    H = arr.shape[0]
    split_px = int(H * split_frac)

    arr[split_px:] = 0.0

    gold = np.array([0.941, 0.753, 0.251], dtype=np.float32)
    arr[split_px:split_px + 3] = gold

    split_y_axes = 1.0 - (split_px / H)
    return arr, split_y_axes


def vignette(arr: np.ndarray, strength: float = 0.65) -> np.ndarray:
    """Apply a radial darkening vignette toward image edges."""
    H, W = arr.shape[:2]
    cx, cy = W / 2.0, H / 2.0
    Y, X = np.mgrid[0:H, 0:W]
    dist = np.sqrt(((X - cx) / cx) ** 2 + ((Y - cy) / cy) ** 2)
    dist = np.clip(dist, 0.0, 1.0)
    mask = 1.0 - dist * strength
    mask = np.clip(mask, 0.0, 1.0).astype(np.float32)
    result = arr.copy() * mask[:, :, np.newaxis]
    return np.clip(result, 0.0, 1.0)
