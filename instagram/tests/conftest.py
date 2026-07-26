# instagram/tests/conftest.py
"""pytest configuration to inject compatibility aliases for moviepy v2.x."""
import sys
import moviepy

# Only alias moviepy.editor if it doesn't already exist (v2.x only).
# In v1.x, moviepy.editor is a real module — clobbering it breaks imports.
try:
    import moviepy.editor  # noqa: F401 — v1.x: already exists, nothing to do
except ImportError:
    sys.modules['moviepy.editor'] = moviepy  # v2.x: alias top-level as editor

# Patch Clip to backport v1.x setter methods into v2.x (no-op on v1.x)
try:
    from moviepy.Clip import Clip
    for name in ('fps', 'duration', 'audio', 'position', 'start', 'end', 'opacity', 'mask'):
        with_name = f"with_{name}"
        set_name = f"set_{name}"
        if hasattr(Clip, with_name):
            setattr(Clip, set_name, getattr(Clip, with_name))
except (ImportError, AttributeError):
    pass
