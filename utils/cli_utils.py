"""Utility functions for the CLI."""

# Python imports

# Package imports
import easygui

# Local imports
from utils import config
from utils import exceptions


# --------------------------------------------------------------------------------------
#                                    Utility Functions
# --------------------------------------------------------------------------------------
def read_cli_input(
    prompt: str, strip: bool = True, lower: bool = False, upper: bool = False
) -> str:
    """Read input from the command line.

    Args:
        prompt: str
            The prompt to display to the user.
        strip: bool
            Whether to strip the input. Defaults to True.
        lower: bool
            Whether to convert the input to lowercase. Defaults to False.
        upper: bool
            Whether to convert the input to uppercase. Defaults to False.

    Returns:
        str: The input provided by the user.
    """
    inp = input(prompt)
    if not inp:
        return inp
    if strip:
        inp = inp.strip()
    if lower:
        inp = inp.lower()
    if upper:
        inp = inp.upper()
    return inp


def read_cli_input_with_default(
    prompt: str,
    default: str,
    strip: bool = True,
    lower: bool = False,
    upper: bool = False,
) -> str:
    """Read input from the command line with a default value.

    Args:
        prompt: str
            The prompt to display to the user.
        default: str
            The default value to display in the prompt.
        strip: bool
            Whether to strip the input. Defaults to True.
        lower: bool
            Whether to convert the input to lowercase. Defaults to False.
        upper: bool
            Whether to convert the input to uppercase. Defaults to False.


    Returns:
        str: The input provided by the user.
    """
    prompt = f"{prompt} [{default}]: "
    inp = read_cli_input(prompt, strip=strip, lower=lower, upper=upper)
    if not inp:
        return default
    return inp


def read_cli_input_with_validation(
    prompt: str,
    valid_values: list[str],
    error_message: str,
    strip: bool = True,
    lower: bool = False,
    upper: bool = False,
) -> str:
    """Read input from the command line with validation.

    Wil loop over the prompt until a valid value is provided, OR
    an exit command is given.

    Args:
        prompt: str
            The prompt to display to the user.
        valid_values: list[str]
            A list of valid values.
        error_message: str
            The error message to display if the input is invalid.
        strip: bool
            Whether to strip the input. Defaults to True.
        lower: bool
            Whether to convert the input to lowercase. Defaults to False.
        upper: bool
            Whether to convert the input to uppercase. Defaults to False.

    Returns:
        str: The input provided by the user.
    """
    while True:
        value = read_cli_input(prompt, strip=strip, lower=lower, upper=upper)
        # Check if the user wants to exit
        if value.lower().strip() in config.QUIT_SIGNALS:
            raise exceptions.CLIQuitSignal("User requested to quit.")
        # Check for valid input
        if value in valid_values:
            return value
        else:
            print(error_message)


def get_cli_file_path(
    prompt: str, title: str = "Select File", default="*", multiple: bool = False
) -> str | list[str] | None:
    """Get a file path from the user.

    Args:
        prompt: str
            The prompt to display to the user.
        title: str
            The title of the file selection dialog.
        default: str
            The default file path to display in the file selection dialog.
            Defaults to "*", which allows any file type.
            You can specify a specific file type, e.g. "*.mp4" for MP4 files.
            If you want to allow all file types, use "*".
        multiple: bool
            Whether to allow multiple file selection. Defaults to False.
            If set to True, the user can select multiple files.
            If set to False, the user can select only one file.

    Returns:
        str: The file path provided by the user, if multiple is False.
        list[str]: A list of file paths provided by the user, if multiple is True.
        None: If the user cancels the file selection.

    Raises:
        CLIQuitSignal: If the user cancels the file selection.
    """
    # File select should return valid file, or None if GUI was closed
    file_path = easygui.fileopenbox(
        msg=prompt, title=title, default=default, multiple=multiple
    )

    return file_path


def get_cli_directory_path(
    prompt: str, title: str = "Select Directory", default="*"
) -> str | None:
    """Get a directory path from the user.

    Args:
        prompt: str
            The prompt to display to the user.
        title: str
            The title of the directory selection dialog.
        default: str
            The default directory path to display in the directory selection dialog.
            Defaults to "*", which allows any directory type.
            You can specify a specific directory type, e.g. "*.mp4" for MP4 files.
            If you want to allow all directory types, use "*".

    Returns:
        str: The directory path provided by the user.
        None: If the user cancels the directory selection.

    Raises:
        CLIQuitSignal: If the user cancels the directory selection.
    """
    # Directory select should return valid dir, or None if GUI was closed
    dir_path = easygui.diropenbox(msg=prompt, title=title, default=default)

    return dir_path
