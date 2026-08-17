"""
yt_shorts_termux.py
--------------------
Android/Termux version of the YouTube/local video splitter.
Splits a video into 1-minute "shorts" with a 'Part X' watermark.

Setup required (run once in Termux):
  pkg install python ffmpeg fontconfig-utils
  pip install yt-dlp moviepy

Usage:
  python yt_shorts_termux.py
"""

import os
import math
from yt_dlp import YoutubeDL
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# Folder where downloads/shorts will be saved (adjust if needed)
BASE_FOLDER = "/storage/downloads/code"


def download_video(url, output_folder=None):
    """Download the YouTube video using yt-dlp, saving with a unique filename."""
    output_folder = output_folder or os.path.join(BASE_FOLDER, "downloads")
    os.makedirs(output_folder, exist_ok=True)
    ydl_opts = {
        "format": "best[ext=mp4]",
        "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename


def split_into_shorts(video_path, chunk_length=60, output_folder=None):
    """Split a video into chunks of chunk_length seconds each, with a 'Part X' watermark."""
    output_folder = output_folder or os.path.join(BASE_FOLDER, "shorts")
    os.makedirs(output_folder, exist_ok=True)

    clip = VideoFileClip(video_path)
    total_duration = clip.duration
    num_chunks = math.ceil(total_duration / chunk_length)

    print(f"Video duration: {total_duration:.1f}s -> {num_chunks} chunks")

    # Android/Termux font path (DejaVu, installed via fontconfig-utils)
    font_path = "/data/data/com.termux/files/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    for i in range(num_chunks):
        start = i * chunk_length
        end = min((i + 1) * chunk_length, total_duration)
        chunk = clip.subclipped(start, end)

        watermark_text = f"Part {i+1}"
        watermark = (
            TextClip(
                text=watermark_text,
                font=font_path,
                font_size=50,
                color="white",
                stroke_color="black",
                stroke_width=2,
            )
            .with_duration(chunk.duration)
            .with_position(("center", "top"))
        )

        final_chunk = CompositeVideoClip([chunk, watermark])

        output_file = os.path.join(output_folder, f"short_{i+1}.mp4")
        final_chunk.write_videofile(output_file, codec="libx264", audio_codec="aac")
        print(f"Saved: {output_file}")

    clip.close()


if __name__ == "__main__":
    user_input = input("Paste a YouTube link OR a local video file path: ").strip()

    if user_input.lower().startswith("http"):
        print("Detected a YouTube link. Downloading...")
        video_file = download_video(user_input)
    else:
        video_file = user_input.strip('"')
        if not os.path.exists(video_file):
            print(f"Error: File not found at '{video_file}'")
            exit(1)
        print(f"Detected a local file: {video_file}")

    split_into_shorts(video_file, chunk_length=60)