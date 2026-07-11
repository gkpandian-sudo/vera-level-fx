# instagram/higgsfield/cinematic.py
"""Provider router: Gemini (free) when GEMINI_API_KEY is set, Higgsfield (paid) otherwise."""
import os as _os

_BACKEND = 'gemini' if _os.environ.get('GEMINI_API_KEY') else 'higgsfield'

if _BACKEND == 'gemini':
    from higgsfield._cinematic_gemini import generate_broker_reel  # noqa: F401
else:
    from higgsfield._cinematic_hf import generate_broker_reel  # noqa: F401
