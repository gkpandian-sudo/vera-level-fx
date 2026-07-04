import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_reels_package_imports():
    from reels import animator, audio, render, scenes  # noqa: F401
