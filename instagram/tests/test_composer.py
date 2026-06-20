import numpy as np
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from instagram.composer import (
    dark_bg, load_background, gradient_panel,
    frosted_glass_region, split_layout, vignette
)

SIZE = (1080, 1080)


def test_dark_bg_shape():
    arr = dark_bg()
    assert arr.shape == (1080, 1080, 3)
    assert arr.dtype == np.float32


def test_dark_bg_is_dark():
    arr = dark_bg()
    assert arr.mean() < 0.15


def test_gradient_panel_darkens_bottom():
    arr = dark_bg() + 0.5
    arr = np.clip(arr, 0, 1)
    result = gradient_panel(arr, height_frac=0.50)
    assert result.shape == (1080, 1080, 3)
    assert result[-1].mean() < result[0].mean()


def test_frosted_glass_region_shape():
    arr = dark_bg() + 0.4
    result = frosted_glass_region(arr, y_frac=0.58, h_frac=0.42)
    assert result.shape == (1080, 1080, 3)
    assert result.dtype == np.float32


def test_frosted_glass_darkens_region():
    arr = np.ones((1080, 1080, 3), dtype=np.float32) * 0.8
    result = frosted_glass_region(arr, y_frac=0.58, h_frac=0.42)
    top_mean = result[:int(1080 * 0.58)].mean()
    bot_mean = result[int(1080 * 0.58):].mean()
    assert bot_mean < top_mean


def test_split_layout_bottom_is_black():
    arr = np.ones((1080, 1080, 3), dtype=np.float32)
    result, split_y = split_layout(arr, split_frac=0.50)
    assert result.shape == (1080, 1080, 3)
    assert 0.0 < split_y < 1.0
    split_px = int(1080 * (1 - split_y))
    bottom = result[split_px + 5:]
    assert bottom.mean() < 0.05


def test_vignette_dims_edges():
    arr = np.ones((1080, 1080, 3), dtype=np.float32)
    result = vignette(arr)
    assert result.shape == (1080, 1080, 3)
    centre = result[480:600, 480:600].mean()
    corner = result[:50, :50].mean()
    assert centre > corner


def test_load_background_missing_falls_back_to_dark():
    result = load_background(Path('nonexistent.jpg'))
    assert result.shape == (1080, 1080, 3)
    assert result.mean() < 0.15
