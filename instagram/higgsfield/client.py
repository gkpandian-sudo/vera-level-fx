# instagram/higgsfield/client.py
"""Provider router: Gemini (free) when GEMINI_API_KEY is set, Higgsfield (paid) otherwise.

To use Gemini:    set GEMINI_API_KEY in GitHub secrets.
To use Higgsfield: unset GEMINI_API_KEY, set HIGGSFIELD_API_KEY + HIGGSFIELD_API_SECRET.
Both keys present: Gemini wins (free takes priority).
"""
import os as _os

_BACKEND = 'gemini' if _os.environ.get('GEMINI_API_KEY') else 'higgsfield'
print(f'  [client] backend={_BACKEND}')

if _BACKEND == 'gemini':
    from higgsfield._client_gemini import (  # noqa: F401
        register_script_text,
        generate_cinematic_clip,
        generate_audio_track,
        predict_virality,
        dub_to_tamil,
        get_soul_id,
        generate_soul_clip,
    )
else:
    from higgsfield._client_hf import (  # noqa: F401
        generate_cinematic_clip,
        generate_audio_track,
        predict_virality,
        dub_to_tamil,
        get_soul_id,
        generate_soul_clip,
    )

    def register_script_text(script: str) -> None:  # noqa: F811
        """No-op for Higgsfield backend — dubbing uses the API, not a local script stash."""
        pass
