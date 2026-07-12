# instagram/higgsfield/client.py
"""Gemini AI client — free tier, no paid API required.

TTS:        edge-tts (Microsoft neural voices, no key needed)
Visuals:    PIL data cards + MoviePy Ken Burns (no API)
Virality:   gemini-2.5-flash text rubric (free tier)
Tamil dub:  gemini-2.5-flash translate → edge-tts (free tier)

To switch to Higgsfield paid stack later: see _client_hf.py.
"""
from higgsfield._client_gemini import (  # noqa: F401
    register_script_text,
    generate_cinematic_clip,
    generate_audio_track,
    predict_virality,
    dub_to_tamil,
    get_soul_id,
    generate_soul_clip,
)
