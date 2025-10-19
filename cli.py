"""Command Line Interface for video file conversion.

Alternative option to the GUI implementation.
"""

# Python imports
import os
import sys
import time
from enum import Enum

# Local imports
from utils.exceptions import CLIMainMenuSignal, CLIQuitSignal
from utils.cli_utils import (
    read_cli_input,
    read_cli_input_with_default,
    read_cli_input_with_validation,
    get_cli_file_path,
    get_cli_directory_path,
)
from utils import ffmpeg_wrapper
from utils import config


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
        print("\n")
        print("File Converter Menu")
        print(f"1. Select Input File: {input_file_path}")
        print(f"2. Select Output Directory: {output_directory}")
        print(f"3. Select File Type: {file_type}")

        if input_file_path and output_directory and file_type:
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
                __menu_file_converter_convert_file(
                    input_file_path=input_file_path,
                    output_file_path=output_file_path,
                )
            case "m" | "main":  # Failsafe: should be handled by exception
                print("<Warning: Hit unreachable failsafe>")
                return MenuState.MAIN
            case "q" | "quit":  # Failsafe: should be handled by exception
                print("<Warning: Hit unreachable failsafe>")
                raise CLIQuitSignal("User requested to quit.")
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
    result = get_cli_directory_path(
        prompt="Select output directory",
        title="Select Output Directory",
        default="*",
    )
    if not result:
        print("No directory selected.")
        output_directory = ""
    else:
        output_directory = result
    return output_directory


def __menu_file_converter_file_type() -> str:
    """Get the file type from the user.

    Returns:
        str: The file type provided by the user.
    """
    print("\nAvailable output file types:")
    mapping = {
        "1": "mp4",
        "2": "mov",
        "3": "avi",
        "4": "mkv",
    }
    for key, value in mapping.items():
        print(f"{key}. {value}")
    print()

    file_type_int = read_cli_input_with_validation(
        prompt="Select output file type: ",
        valid_values=list(mapping.keys()),
        error_message="Unsupported file type. Please try again.",
    )
    file_type = mapping[file_type_int]
    # if file type starts with ., strip it (failsafe)
    if file_type and file_type.startswith("."):
        file_type = file_type[1:]
    return file_type


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
    ffmpeg_wrapper.convert_file(
        input_filepath=input_file_path,
        output_filepath=output_file_path,
    )
    print(f"File conversion completed. See {output_file_path} for results.")


# --------------------------------------------------------------------------------------
#                                 File Merger Menu
# --------------------------------------------------------------------------------------
def __menu_file_merger() -> MenuState:
    """Logic for the file merger menu.

    # TODO explain more

    Returns:
        MenuState: The next menu state to transition to.
    """
    print("File Merger Menu")
    # TODO continue here
    print("\n\nUNIMPLEMENTED!\n\n")

    return MenuState.MAIN


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
        except CLIQuitSignal:
            print("\nExiting, have a good day!")
            # Delay to allow the user to see the message
            sys.exit(0)
        except CLIMainMenuSignal:
            print("\nReturning to main menu...")
            menu_state = MenuState.MAIN


if __name__ == "__main__":
    main()

# TODO have a conf.json that stores output directory, etc, and
# a menu to allow editing of conf.json
