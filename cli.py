"""Command Line Interface for video file conversion.

Alternative option to the GUI implementation.
"""

# Python imports
import os
import sys
from enum import Enum

# Local imports
from utils.cli_utils import (
    read_cli_input,
    read_cli_input_with_default,
    read_cli_input_with_validation,
    get_cli_file_path,
)
from utils import ffmpeg_wrapper, config, cli_utils, file_merger, exceptions


# Config variables
class MenuState(Enum):
    """Enum for the menu state.

    Used to denote which menu is currently active and is used to control the
    flow of the CLI.
    """

    MAIN = 1
    FILE_CONVERTER = 2
    FILE_MERGER = 3


# --------------------------------------------------------------------------------------
#                                      Main Menu
# --------------------------------------------------------------------------------------
def __menu_main() -> MenuState:
    """Logic for the main menu.

    This menu is the entry point for the CLI and allows the user to select
    different options for file conversion, merging, etc.

    Returns:
        MenuState: The next menu state to transition to.
    """
    print("Welcome to the Command Line Interface (CLI) for video file conversion!")
    print("Please select an option:")
    print("1. File Converter")
    print("2. File Merger")
    print("\n[q/quit]. Exit\n")

    choice = read_cli_input_with_validation(
        prompt="Enter your choice: ",
        valid_values=["1", "2"],
        error_message="Invalid choice. Please try again.",
    )

    match choice:
        case "1":
            return MenuState.FILE_CONVERTER
        case "2":
            return MenuState.FILE_MERGER
        case _:
            # Failsafe: Validator should prevent this scenario
            print(f"Invalid choice: {choice}. Please try again.")
            return MenuState.MAIN


# --------------------------------------------------------------------------------------
#                                 File Converter Menu
# --------------------------------------------------------------------------------------
def __menu_file_converter() -> MenuState:
    """Logic for the file converter menu.

    Allows user to select an input file, an output directory, and
    desired file type for conversion. The user will be alerted
    if the output file already exists and will be prompted to
    overwrite it.

    This process can be repeated multiple times, until the user
    exits or returns to the main menu.

    Returns:
        MenuState: The next menu state to transition to.
    """
    input_file_path: str = ""
    # TODO read default outdir from the config file and allow overwriting here
    output_directory: str = ""
    file_type: str = ""
    output_file_path: str = ""
    # TODO Clear screen between each menu
    while True:
        print("\nFile Converter Menu")
        print(f"1. Select Input File: {input_file_path}")
        print(f"2. Select Output Directory: {output_directory}")
        print(f"3. Select File Type: {file_type}")

        conversion_ready = all(
            [
                input_file_path,
                output_directory,
                file_type,
            ]
        )

        if conversion_ready:
            input_file_name = os.path.basename(input_file_path)
            output_file_name = os.path.splitext(input_file_name)[0] + "." + file_type
            output_file_path = os.path.join(output_directory, output_file_name)
            print()
            print(f"4. RUN CONVERSION: Convert File to: {output_file_path}")
        print("\n[q/quit]. Exit")
        print("[m/main]. Return to main menu\n")

        choice = read_cli_input_with_validation(
            prompt="Enter your choice: ",
            valid_values=["1", "2", "3", "4"],
            error_message="Invalid choice. Please try again.",
        )
        match choice:
            case "1":  # Select input file
                input_file_path = __menu_file_converter_input_file()
            case "2":  # Select output directory
                output_directory = __menu_file_converter_output_directory()
            case "3":  # Select file type
                file_type = __menu_file_converter_file_type()
            case "4":  # Convert file
                if not conversion_ready:
                    # Failsafe as option does not display but is valid.
                    print("Please fill in all fields before converting.")
                    continue
                __menu_file_converter_convert_file(
                    input_file_path=input_file_path,
                    output_file_path=output_file_path,
                )
            case "m" | "main":  # Failsafe: should be handled by exception
                print("<Warning: Hit unreachable failsafe>")
                return MenuState.MAIN
            case "q" | "quit":  # Failsafe: should be handled by exception
                print("<Warning: Hit unreachable failsafe>")
                raise exceptions.CLIQuitSignal("User requested to quit.")
            case _:
                # Failsafe: Validator should prevent this scenario
                print(f"Invalid choice: {choice}. Please try again.")


def __menu_file_converter_input_file() -> str:
    """Get the input file path from the user.

    Returns:
        str: The input file path provided by the user.
    """
    input_file_path: str = ""
    result = get_cli_file_path(
        prompt="Select input file",
        title="Select Input File",
        default="*",
        multiple=False,
    )
    if not result:
        print("No file selected.")
        input_file_path = ""
    else:
        if isinstance(result, list):
            input_file_path = result[0]
        else:
            input_file_path = result
    return input_file_path


def __menu_file_converter_output_directory() -> str:
    """Get the output directory path from the user.

    Returns:
        str: The output directory path provided by the user.
    """
    return cli_utils.get_directory(
        title="Select Output Directory",
        prompt="Select output directory",
        default="*",
    )


def __menu_file_converter_file_type() -> str:
    """Get the file type from the user.

    Returns:
        str: The file type provided by the user.
    """
    return cli_utils.get_video_output_file_type()


def __menu_file_converter_convert_file(input_file_path: str, output_file_path: str):
    """Get the file type from the user.

    Returns:
        str: The file type provided by the user.
    """
    if not input_file_path:
        print("No input file selected. Please select an input file first.")
        return
    if not output_file_path:
        print("Please fill in all output fields before converting.")

    # Check if output file already exists
    if os.path.exists(output_file_path):
        overwrite = read_cli_input_with_validation(
            prompt=f"Output file {output_file_path} already exists. "
            "Do you want to overwrite it? (y/n): ",
            valid_values=["y", "n"],
            error_message="Invalid choice. Please try again.",
        )
        if overwrite == "n":
            print("File conversion cancelled.")
            return
        else:
            print("Overwriting existing file.")
    # Call converter
    print(f"Converting {input_file_path} to {output_file_path}...")
    try:
        ffmpeg_wrapper.convert_file(
            input_filepath=input_file_path,
            output_filepath=output_file_path,
        )
    except ffmpeg_wrapper.ffmpeg.Error:
        # Error would have already been logged to terminal by ffmpeg
        print("An error occurred during file conversion")
        print("File conversion failed. Please fix the issue and try again.")
        return
    print(f"File conversion completed. See {output_file_path} for results.")


# --------------------------------------------------------------------------------------
#                                 File Merger Menu
# --------------------------------------------------------------------------------------
def __menu_file_merger() -> MenuState:
    """Logic for the file merger menu.

    Allows the user to select a directory of input image files, an
    output directory, and desired output file name and type for
    the merged video file, as well as frame rate, and condenses
    the images into a video file.

    Returns:
        MenuState: The next menu state to transition to.
    """
    input_directory_path: str = ""
    output_directory_path: str = ""
    output_file_name: str = "output_video"
    output_file_type: str = "mp4"
    default_frame_rate = config.DEFAULT_MERGING_OUTPUT_FRAME_RATE
    frame_rate: int = default_frame_rate
    matching_pattern: str = ""

    while True:
        print("\nFile Merger Menu")
        print(f"1. Select Input Directory: {input_directory_path}")
        print(f"2. Select Output Directory: {output_directory_path}")
        print(f"3. Select Output File Name: {output_file_name}")
        print(f"4. Select Output File Type: {output_file_type}")
        print(f"5. Select Frame Rate: {frame_rate}")
        if input_directory_path:
            print(f"6. Select Matching Pattern: {matching_pattern}")

        merge_ready = all(
            [
                input_directory_path,
                output_directory_path,
                output_file_name,
                output_file_type,
                frame_rate,
                matching_pattern,
            ]
        )

        if merge_ready:
            output_file_path = os.path.join(
                output_directory_path,
                f"{output_file_name}.{output_file_type}",
            )
            print()
            print(f"7. RUN MERGE: Merge Files to: {output_file_path}")

        print("\n[q/quit]. Exit")
        print("[m/main]. Return to main menu\n")

        choice = read_cli_input_with_validation(
            prompt="Enter your choice: ",
            valid_values=["1", "2", "3", "4", "5", "6", "7"],
            error_message="Invalid choice. Please try again.",
        )
        match choice:
            case "1":  # Select input file directory
                input_directory_path, matching_pattern = (
                    __menu_file_merger_input_directory_path()
                )
            case "2":  # Select output directory
                output_directory_path = __menu_file_merger_output_directory_path()
            case "3":  # Select output file name
                output_file_name = __menu_file_merger_output_file_name()
            case "4":  # Select output file type
                output_file_type = __menu_file_merger_output_file_type()
            case "5":  # Select frame rate
                frame_rate = __menu_file_merger_frame_rate(
                    default_framerate=default_frame_rate
                )
            case "6":  # Select matching pattern
                matching_pattern = __menu_file_merger_get_matching_pattern()
            case "7":  # Merge files
                if not merge_ready:
                    # Failsafe as option does not display but is valid.
                    print("Please fill in all fields before merging.")
                    continue
                __menu_file_merger_merge_files(
                    input_directory_path=input_directory_path,
                    output_directory_path=output_directory_path,
                    output_file_name=output_file_name,
                    output_file_type=output_file_type,
                    frame_rate=frame_rate,
                    matching_pattern=matching_pattern,
                )
            case "m" | "main":  # Failsafe: should be handled by exception
                print("<Warning: Hit unreachable failsafe>")
                return MenuState.MAIN
            case "q" | "quit":  # Failsafe: should be handled by exception
                print("<Warning: Hit unreachable failsafe>")
                raise exceptions.CLIQuitSignal("User requested to quit.")
            case _:
                # Failsafe: Validator should prevent this scenario
                print(f"Invalid choice: {choice}. Please try again.")


def __menu_file_merger_input_directory_path() -> tuple[str, str]:
    """Get the input directory path from the user, and predict matching pattern.

    If there are no files in the directory, a blank string is returned for both values.
    If the matching pattern cannot be predicted, a blank string is returned for
    the pattern.

    Returns:
        tuple[str, str]: The input directory path and the predicted matching pattern.
    """
    dir_str = cli_utils.get_directory(
        title="Select Input Directory (Containing Image Files)",
        prompt="Select input directory (containing image files)",
        default="*",
    )
    if not dir_str:
        return "", ""
    try:
        matching_pattern = file_merger.predict_matching_pattern(dir_str)
        return dir_str, matching_pattern
    except exceptions.NoFilesException:
        print("No files found in the selected directory.")
        return "", ""
    except exceptions.CannotPredictPatternException:
        print("Could not predict matching pattern from files in directory.")
        return dir_str, ""


def __menu_file_merger_output_directory_path() -> str:
    """Get the output directory path from the user.

    Returns:
        str: The output directory path provided by the user.
    """
    return cli_utils.get_directory(
        title="Select Output Directory",
        prompt="Select output directory",
        default="*",
    )


def __menu_file_merger_output_file_name() -> str:
    """Get the output file name from the user.

    Returns:
        str: The output file name provided by the user.
    """
    return cli_utils.get_file_name(
        prompt="Enter output file name (without extension): ",
        strip_extension=True,
    )


def __menu_file_merger_output_file_type() -> str:
    """Get the output file type from the user.

    Returns:
        str: The output file type provided by the user.
    """

    return cli_utils.get_video_output_file_type()


def __menu_file_merger_frame_rate(default_framerate: int) -> int:
    """Get the frame rate from the user.

    Args:
        default_framerate: int
            The default frame rate to use if the user does
            not provide a valid one.

    Returns:
        int: The frame rate provided by the user.
    """
    frame_rate_str = read_cli_input_with_default(
        prompt=f"Enter frame rate (frames per second) [default: {default_framerate}]: ",
        default=str(default_framerate),
    )
    try:
        frame_rate = int(frame_rate_str)
    except ValueError:
        print(f"Invalid frame rate. Using default of {default_framerate} fps.")
        frame_rate = default_framerate
    return frame_rate


def __menu_file_merger_get_matching_pattern() -> str:
    """Get the matching pattern from the user.

    This is required for FFMPEG to know which files to include, and in which order.
    E.g.  output_%03d.png for files named output_001.png, output_002.png, etc.

    Returns:
        str: The matching pattern provided by the user.
    """
    prompt = (
        "Enter matching pattern for input files. E.g. output_%03d.png "
        "for files named output_001.png, output_002.png, etc.: "
    )
    pattern = read_cli_input(prompt=prompt, strip=True, lower=False, upper=False)
    return pattern


def __menu_file_merger_merge_files(
    input_directory_path: str,
    output_directory_path: str,
    output_file_name: str,
    output_file_type: str,
    frame_rate: int,
    matching_pattern: str,
):
    """Merge the files in the input directory into a video file.

    Args:
        input_directory_path: str
            The input directory path containing the image files.
        output_directory_path: str
            The output directory path to save the merged video file.
        output_file_name: str
            The output file name (without extension).
        output_file_type: str
            The output file type (e.g., mp4, mov, avi, mkv).
        frame_rate: int
            The frame rate for the output video file.
        matching_pattern: str
            The matching pattern to filter input files. Required for
            FFMPEG to know which files to include, and in which order.
            E.g. output_%03d.png for files named output_001.png, output_002.png, etc.
    Returns:
        None
    """
    output_file_path = os.path.join(
        output_directory_path,
        f"{output_file_name}.{output_file_type}",
    )
    print("Merging files...")
    try:
        ffmpeg_wrapper.merge_images_to_video(
            input_directory=input_directory_path,
            input_pattern=matching_pattern,
            output_filepath=output_file_path,
            frame_rate=frame_rate,
        )
    except ffmpeg_wrapper.ffmpeg.Error:
        # Error would have already been logged to terminal by ffmpeg
        print("An error occurred during file merging")
        print("File merging failed. Please fix the issue and try again.")
        return
    print(f"File merging completed. See {output_file_path} for results.")


# --------------------------------------------------------------------------------------
#                                     Coordinator
# --------------------------------------------------------------------------------------
def main():
    """Main function to run the CLI."""
    menu_state: MenuState = MenuState.MAIN
    # Main loop
    # TODO write command for the file trimmer, with prompts.
    # TODO write command for the file merger, with prompts.
    while True:
        # TODO clear screen each time
        try:
            match menu_state:
                case MenuState.MAIN:
                    menu_state = __menu_main()
                case MenuState.FILE_CONVERTER:
                    menu_state = __menu_file_converter()
                case MenuState.FILE_MERGER:
                    menu_state = __menu_file_merger()
                case _:
                    print(f"Internal error: Invalid menu state: {menu_state}. Exiting")
                    sys.exit(1)
        except KeyboardInterrupt:
            print("\nExiting, have a good day!")
            # Delay to allow the user to see the message
            sys.exit(0)
        except exceptions.CLIQuitSignal:
            print("\nExiting, have a good day!")
            # Delay to allow the user to see the message
            sys.exit(0)
        except exceptions.CLIMainMenuSignal:
            print("\nReturning to main menu...")
            menu_state = MenuState.MAIN


if __name__ == "__main__":
    main()

# TODO have a conf.json that stores output directory, etc, and
# a menu to allow editing of conf.json
