# util functions for interacting with ffmpeg binaries
import ffmpeg
import moviepy


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
