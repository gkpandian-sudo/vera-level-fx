# instagram/tests/conftest.py
"""pytest configuration to inject compatibility aliases for moviepy v2.x."""
import sys
import moviepy
sys.modules['moviepy.editor'] = moviepy

# Patch moviepy Clip class to support old moviepy v1.x setter methods
from moviepy.Clip import Clip
for name in ('fps', 'duration', 'audio', 'position', 'start', 'end', 'opacity', 'mask'):
    with_name = f"with_{name}"
    set_name = f"set_{name}"
    if hasattr(Clip, with_name):
        setattr(Clip, set_name, getattr(Clip, with_name))
