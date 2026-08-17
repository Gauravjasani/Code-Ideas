import os
import math
import imageio_ffmpeg

# Tell MoviePy where FFmpeg is
os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()

from yt_dlp import YoutubeDL
from moviepy import VideoFileClip, TextClip, CompositeVideoClip


def find_android_font():
    """Find a usable Android font."""
    possible_fonts = [
        "/system/fonts/Roboto-Regular.ttf",
        "/system/fonts/Roboto-Medium.ttf",
        "/system/fonts/Roboto-Bold.ttf",
    ]

    for font in possible_fonts:
        if os.path.exists(font):
            return font

    return None


def download_video(url, output_folder="downloads"):
    """Download a YouTube video using yt-dlp."""
    os.makedirs(output_folder, exist_ok=True)

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
        "noplaylist": True,
    }

    print("Downloading video...")

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    # yt-dlp may change the extension after merging
    if not os.path.exists(filename):
        mp4_filename = os.path.splitext(filename)[0] + ".mp4"
        if os.path.exists(mp4_filename):
            filename = mp4_filename

    return filename


def split_into_shorts(video_path, chunk_length=60, output_folder="shorts"):
    """Split video into chunks and add Part X text."""
    os.makedirs(output_folder, exist_ok=True)

    print("Opening video...")

    clip = VideoFileClip(video_path)

    total_duration = clip.duration
    num_chunks = math.ceil(total_duration / chunk_length)

    print(
        f"Video duration: {total_duration:.1f} seconds "
        f"-> {num_chunks} shorts"
    )

    # Find Android font
    font_path = find_android_font()

    if font_path:
        print(f"Using font: {font_path}")
    else:
        print("Warning: Android font not found.")
        font_path = None

    for i in range(num_chunks):

        start = i * chunk_length
        end = min((i + 1) * chunk_length, total_duration)

        print(f"\nProcessing Part {i + 1}/{num_chunks}")
        print(f"Time: {start:.1f}s - {end:.1f}s")

        chunk = clip.subclipped(start, end)

        watermark_text = f"Part {i + 1}"

        # Create text
        text_options = {
            "text": watermark_text,
            "font_size": 50,
            "color": "white",
            "stroke_color": "black",
            "stroke_width": 2,
        }

        if font_path:
            text_options["font"] = font_path

        watermark = (
            TextClip(**text_options)
            .with_duration(chunk.duration)
            .with_position(("center", "top"))
        )

        final_chunk = CompositeVideoClip(
            [chunk, watermark]
        )

        output_file = os.path.join(
            output_folder,
            f"short_{i + 1}.mp4"
        )

        print(f"Saving: {output_file}")

        final_chunk.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac",
            threads=2,
        )

        final_chunk.close()
        chunk.close()

        print(f"Saved: {output_file}")

    clip.close()

    print("\nAll shorts completed!")


def main():

    print("=" * 40)
    print("       YouTube Shorts Splitter")
    print("=" * 40)

    user_input = input(
        "\nPaste a YouTube link OR a local video file path:\n"
    ).strip()

    if user_input.lower().startswith("http"):

        print("\nDetected YouTube link.")
        print("Downloading...")

        video_file = download_video(user_input)

    else:

        # Remove accidental quotes
        video_file = user_input.strip('"').strip("'")

        if not os.path.exists(video_file):
            print(
                f"\nError: File not found:\n{video_file}"
            )
            return

        print(
            f"\nDetected local video:\n{video_file}"
        )

    if not os.path.exists(video_file):
        print(
            f"\nError: Video file does not exist:\n{video_file}"
        )
        return

    print("\nStarting video processing...")

    split_into_shorts(
        video_file,
        chunk_length=60,
        output_folder="shorts"
    )


if __name__ == "__main__":
    main()