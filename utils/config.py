"""Configuration file for the project."""

# --------------------------------------------------------------------------------------
#                              Command Line Interface (CLI)
# --------------------------------------------------------------------------------------
QUIT_SIGNALS = ["q", "quit"]
"""List of signals to quit the CLI (lower case only as it input will be lower()'d)."""

MAIN_MENU_SIGNALS = ["m", "main"]
"""
List of signals to return to the main menu (lower case only as it input
will be lower()'d).
"""

DEFAULT_MERGING_OUTPUT_FRAME_RATE = 24
"""Default output frame rate for output of video files during merging."""
