# util functions for interacting with ffmpeg binaries
import ffmpeg
import moviepy
from utils import config


def convert_file(input_filepath: str, output_filepath: str) -> None:
    """Convert input file to output file using ffmpeg.

    Can be used to convert video files of one format to another, or video
    files to audio files.

    Args:
        input_filepath: str
            Path to input file.
        output_filepath (str):
            Path to save the output file in.
    """
    ffmpeg.input(input_filepath).output(output_filepath).run()


def trim_video_file(
    input_filepath: str, output_filepath: str, start_time: str, end_time: str
):
    """Trim a video file using ffmpeg.

    Args:
        input_filepath: str
            Path to input video file.
        output_filepath: str
            Path to save the trimmed video file in.
        start_time: str
            Start time for the trimmed video.
        end_time: str
            End time for the trimmed video.
    """
    ffmpeg.input(input_filepath).trip(start=start_time, end=end_time).output(
        output_filepath
    ).run()


def merge_images_to_video(
    input_directory: str,
    input_pattern: str,
    output_filepath: str,
    frame_rate: int = config.DEFAULT_MERGING_OUTPUT_FRAME_RATE,
) -> None:
    """Merge images into a video file using ffmpeg.

    Args:
        input_directory: str
            Path to the directory containing input image files.
        input_pattern: str
            Pattern to match input image files.
            E.g. "image_%03d.png" to match files named
            image_001.png, image_002.png, etc.
        output_filepath: str
            Path to save the output video file in.
        frame_rate: int
            Frame rate for the output video file. Defaults to
            config.DEFAULT_MERGING_OUTPUT_FRAME_RATE.
    """
    input_file = f"{input_directory}/{input_pattern}"
    # See https://ffmpeg.org/ffmpeg.html#Main-options and
    # https://ahmadrosid.com/cheatsheet/ffmpeg/convert-images-to-video
    # for details on these options
    kwargs = {
        "framerate": frame_rate,
        "c:v": "libx264",
        "profile:v": "high",
        "crf": "20",
        "pix_fmt": "yuv420p",
    }
    ffmpeg.input(input_file).output(output_filepath, **kwargs).run()
