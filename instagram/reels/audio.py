from __future__ import annotations
from pathlib import Path

AUDIO_DIR = Path(__file__).parent.parent / 'assets' / 'audio'

TRACK_MAP: dict[str, str] = {
    'daily':         'pulse.mp3',
    'weekly':        'momentum.mp3',
    'trust':         'momentum.mp3',
    'monthly':       'reflect.mp3',
    'transparency':  'tension.mp3',
    'recovery-plan': 'rise.mp3',
    'edu':           'calm.mp3',
}


def get_track(post_type: str) -> Path | None:
    """Return Path to the audio file for this post type, or None if missing."""
    filename = TRACK_MAP.get(post_type)
    if not filename:
        return None
    path = AUDIO_DIR / filename
    return path if path.exists() else None


def build_audio_clip(track_path: 'Path | None', duration: float):
    """Return a MoviePy AudioFileClip trimmed to duration, or None.

    Returns None (silently) if track_path is None or if any error occurs
    (e.g., missing file, codec error, MoviePy issue).
    """
    if track_path is None:
        return None
    try:
        from moviepy.editor import AudioFileClip
        source = AudioFileClip(str(track_path))
        trim_dur = min(duration, source.duration)
        clip = (source
                .subclip(0, trim_dur)
                .volumex(0.15)
                .audio_fadein(0.5)
                .audio_fadeout(1.0)
                .set_duration(duration))
        source.close()
        return clip
    except Exception:
        return None
