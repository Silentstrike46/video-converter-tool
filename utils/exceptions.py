"""Custom exceptions for the application."""


class CLIQuitSignal(Exception):
    """Exception to signal a quit request from the CLI."""

    pass


class CLIMainMenuSignal(Exception):
    """Exception to signal a return to the main menu from the CLI."""

    pass
