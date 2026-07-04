from __future__ import annotations


def render(clips: list, audio_path: 'Path | None', out_path: str,
           fps: int = 30) -> None:
    """Concatenate VideoClips, add optional audio, write MP4.

    clips      — list of MoviePy VideoClip (each has .fps set)
    audio_path — Path to MP3/WAV file, or None for silent
    out_path   — output file path (string)
    """
    from moviepy.editor import concatenate_videoclips

    final = concatenate_videoclips(clips, method='compose')

    if audio_path is not None:
        from reels.audio import build_audio_clip
        audio = build_audio_clip(audio_path, final.duration)
        if audio is not None:
            final = final.set_audio(audio)

    final.write_videofile(
        out_path,
        fps=fps,
        codec='libx264',
        audio_codec='aac',
        preset='fast',
        threads=4,
        logger=None,
    )
