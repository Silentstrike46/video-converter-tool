"""Command Line Interface for video file conversion.

Alternative option to the GUI implementation.
"""

# Python imports
import sys
import time
from enum import Enum

# Local imports
from utils.exceptions import CLIQuitSignal
from utils.cli_utils import (
    read_cli_input_with_validation,
    get_cli_file_path,
    get_cli_directory_path,
)


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
    print("[q/quit]. Exit")

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

    # TODO explain more

    Returns:
        MenuState: The next menu state to transition to.
    """
    print("File Converter Menu")
    # TODO continue here
    print("\n\nUNIMPLEMENTED!\n\n")

    return MenuState.MAIN


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
    try:
        # TODO for each return, return 2 things: 1) a status code (e.g. success, missing or EXIT), and then the input data
        # TODO write command for the file converter, with prompts.
        # TODO write command for the file trimmer, with prompts.
        # TODO write command for the file merger, with prompts.
        while True:
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
        sys.exit(0)
    except CLIQuitSignal:
        print("\nExiting, have a good day!")
        sys.exit(0)


if __name__ == "__main__":
    main()
