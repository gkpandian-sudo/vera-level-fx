"""Preview script — generates all 3 Path E motion clips locally.

Run from repo root:
    cd instagram/higgsfield && python ../../preview_motion.py

Output: previews/motion-performance.mp4, motion-equity.mp4, motion-trust.mp4
"""
import os
import sys
import shutil
from pathlib import Path

# Make higgsfield importable
sys.path.insert(0, str(Path(__file__).parent / 'instagram'))
sys.path.insert(0, str(Path(__file__).parent / 'instagram' / 'higgsfield'))

# Ensure snapshot exists
snap = Path(__file__).parent / 'data' / 'vera-snapshot.json'
if not snap.exists():
    print(f'ERROR: {snap} not found. Run fetch_snapshot.py first, or copy a snapshot there.')
    sys.exit(1)

from higgsfield._scenes import (
    make_performance_clip_motion,
    make_equity_clip_motion,
    make_trust_clip_motion,
)

out_dir = Path(__file__).parent / 'previews'
out_dir.mkdir(exist_ok=True)

clips = [
    ('motion-performance.mp4', make_performance_clip_motion, 15.0),
    ('motion-equity.mp4',      make_equity_clip_motion,      12.0),
    ('motion-trust.mp4',       make_trust_clip_motion,       15.0),
]

for name, fn, dur in clips:
    print(f'\nGenerating {name} ({dur}s)…')
    tmp = fn(duration=dur)
    dest = out_dir / name
    shutil.move(tmp, dest)
    print(f'  saved: {dest}')

print('\nDone! Open previews/ in Windows Explorer to view the MP4s.')
