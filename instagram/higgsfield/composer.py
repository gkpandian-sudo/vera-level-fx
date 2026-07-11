# instagram/higgsfield/composer.py
"""Download Higgsfield videos, stitch clips, composite data card PNG overlay."""
import tempfile
import requests
from pathlib import Path
from PIL import Image
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip


def download_video(url: str, dest: Path) -> Path:
    """Stream-download url to dest. Returns dest."""
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    return dest


def stitch_videos(clip_paths: list[Path], out_path: Path) -> Path:
    """Concatenate MP4 clips in order. Returns out_path."""
    clips = [VideoFileClip(str(p)) for p in clip_paths]
    final = concatenate_videoclips(clips, method='compose')
    final.write_videofile(str(out_path), codec='libx264', audio_codec='aac', logger=None)
    for c in clips:
        c.close()
    return out_path


def add_audio_to_video(video_path: Path, audio_url: str, out_path: Path) -> Path:
    """Download audio from audio_url and set it as the video's audio track. Returns out_path."""
    with tempfile.TemporaryDirectory() as tmp:
        audio_dest = Path(tmp) / 'audio.mp3'
        with requests.get(audio_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(audio_dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
        video = VideoFileClip(str(video_path))
        audio = AudioFileClip(str(audio_dest))
        final = video.set_audio(audio)
        final.write_videofile(str(out_path), codec='libx264', audio_codec='aac', logger=None)
    return out_path


def composite_data_card(
    video_url: str,
    data_card_path: Path,
    out_path: Path,
    overlay_start: float = 3.0,
    overlay_end: float = 25.0,
    card_opacity: float = 0.92,
) -> Path:
    """Download video_url, overlay data_card_path PNG from overlay_start to overlay_end.

    Card is centred vertically in the lower half of the frame, fades in over 0.3s.
    Returns out_path (MP4).
    """
    with tempfile.TemporaryDirectory() as tmp:
        raw_path = Path(tmp) / 'raw.mp4'
        download_video(video_url, raw_path)

        video = VideoFileClip(str(raw_path))
        W, H  = video.w, video.h

        card_img = Image.open(data_card_path).convert('RGBA')
        target_w = int(W * 0.90)
        ratio    = target_w / card_img.width
        target_h = int(card_img.height * ratio)
        card_img = card_img.resize((target_w, target_h), Image.LANCZOS)
        card_arr = np.array(card_img)

        card_clip = (
            ImageClip(card_arr, ismask=False)
            .set_opacity(card_opacity)
            .set_start(overlay_start)
            .set_end(min(overlay_end, video.duration))
            .set_position(('center', H // 2 - target_h // 2))
            .crossfadein(0.3)
        )

        final = CompositeVideoClip([video, card_clip])
        final.write_videofile(
            str(out_path),
            codec='libx264',
            audio_codec='aac',
            fps=video.fps,
            logger=None,
        )
    return out_path
