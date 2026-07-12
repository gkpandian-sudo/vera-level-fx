# instagram/higgsfield/composer.py
"""Download Higgsfield videos, stitch clips, composite data card PNG overlay."""
import tempfile
import requests
from pathlib import Path
from PIL import Image
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip


def download_video(url: str, dest: Path) -> Path:
    """Stream-download url to dest, or copy if url is a local path. Returns dest."""
    if not url.startswith('http'):
        import shutil
        shutil.copy2(url, dest)
        return dest
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    return dest


def stitch_videos(clip_paths: list[Path], out_path: Path) -> Path:
    """Concatenate MP4 clips in order. Returns out_path."""
    if not clip_paths:
        raise ValueError('clip_paths must not be empty')
    clips = [VideoFileClip(str(p)) for p in clip_paths]
    try:
        final = concatenate_videoclips(clips, method='compose')
        final.write_videofile(
            str(out_path), codec='libx264', audio_codec='aac', logger=None,
            ffmpeg_params=['-pix_fmt', 'yuv420p'],
        )
    finally:
        for c in clips:
            c.close()
        try:
            final.close()
        except Exception:
            pass
    return out_path


def add_audio_to_video(video_path: Path, audio_source: str, out_path: Path) -> Path:
    """Mix audio onto video. audio_source may be a local file path or http/https URL."""
    with tempfile.TemporaryDirectory() as tmp:
        suffix = Path(audio_source).suffix if not audio_source.startswith('http') else '.mp3'
        audio_dest = Path(tmp) / f'audio{suffix}'
        if audio_source.startswith('http'):
            with requests.get(audio_source, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(audio_dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        f.write(chunk)
        else:
            import shutil
            shutil.copy2(audio_source, audio_dest)
        video = VideoFileClip(str(video_path))
        audio = AudioFileClip(str(audio_dest))
        try:
            final = video.set_audio(audio)
            final.write_videofile(
                str(out_path), codec='libx264', audio_codec='aac', logger=None,
                ffmpeg_params=['-pix_fmt', 'yuv420p'],
            )
        finally:
            audio.close()
            video.close()
    return out_path


def composite_data_card(
    video_url: str,
    data_card_path: Path,
    out_path: Path,
    overlay_start: float = 3.0,
    overlay_end: float = 25.0,
    card_opacity: float = 0.88,
) -> Path:
    """Download video_url, overlay data_card_path PNG from overlay_start to overlay_end.

    Card scaled to 32% width, pinned bottom-right corner — leaves the animation visible.
    Raises ValueError if the video is not 9:16 portrait.
    Returns out_path (MP4).
    """
    with tempfile.TemporaryDirectory() as tmp:
        raw_path = Path(tmp) / 'raw.mp4'
        download_video(video_url, raw_path)

        video = VideoFileClip(str(raw_path))
        try:
            W, H  = video.w, video.h
            if abs(W / H - 9 / 16) > 0.02:
                raise ValueError(f'Video is not 9:16 ({W}×{H}) — Instagram Reels require portrait 1080×1920')
            card_img = Image.open(data_card_path).convert('RGBA')
            target_w = int(W * 0.32)
            ratio    = target_w / card_img.width
            target_h = int(card_img.height * ratio)
            card_img = card_img.resize((target_w, target_h), Image.LANCZOS)
            card_arr = np.array(card_img)

            pos = (W - target_w - 20, H - target_h - 20)

            overlay_start = min(overlay_start, max(0.0, video.duration - 0.1))
            card_clip = (
                ImageClip(card_arr, ismask=False)
                .set_opacity(card_opacity)
                .set_start(overlay_start)
                .set_end(min(overlay_end, video.duration))
                .set_position(pos)
                .crossfadein(0.3)
            )

            final = CompositeVideoClip([video, card_clip], size=(W, H))
            safe_fps = max(23, min(round(video.fps or 24), 60))
            final.write_videofile(
                str(out_path),
                codec='libx264',
                audio_codec='aac',
                fps=safe_fps,
                logger=None,
                ffmpeg_params=['-pix_fmt', 'yuv420p'],
            )
        finally:
            video.close()
            try:
                final.close()
            except Exception:
                pass
    return out_path
