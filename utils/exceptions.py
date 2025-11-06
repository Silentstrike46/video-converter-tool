"""Custom exceptions for the application."""


class CLIQuitSignal(Exception):
    """Exception to signal a quit request from the CLI."""

    pass


class CLIMainMenuSignal(Exception):
    """Exception to signal a return to the main menu from the CLI."""

    pass


class NoFilesException(Exception):
    """Exception raised when there are no files to merge in the specified directory."""

    pass


class CannotPredictPatternException(Exception):
    """Exception raised when the matching pattern cannot be predicted from the files."""

    pass
