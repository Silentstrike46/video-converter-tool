# video-converter-tool

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python CLI and GUI wrapper for FFmpeg to help with conversions. CLI is first priority and GUI is for later.

## Installation

### FFmpeg

This project requires a working copy of ffmpeg to be installed on your system, with the binaries accessable via the PATH environment variable. This differs depending on operating system, but generally:

#### Windows

1. Download the latest version of FFmpeg from the offical [FFmpeg website](https://www.ffmpeg.org/download.html).
2. Extract the downloaded ZIP file.
3. Copy the bin folder from the extracted files to a safe place.
4. Add the path of the bin folder to your system's PATH environment variable:
    1. Right-click on "**This PC**" or "**My Computer**" and select "**Properties**".
    2. Click "**Advanced System Settings**".
    3. Click "**Environment Variables**" and under "**System Variables**", find "**Path**" variable, and click "**Edit**", "**New**", and add the FFmpeg bin directory path (from step 3) to the variable.
5. Open a Command Prompt window and type `ffpmeg` to verify the installation. If installed correctly, it should display the version and available commands.

#### MacOS

The easiest way to install on MacOS is via Homebrew:

```bash
brew install ffmpeg
```

Once the installation is complete, you can check the version of FFmpeg installed by running:

```bash
ffmpeg -version
```

#### Linux

On most Linux distributions, FFmpeg is offered in the official repositories, and can be installed with the package manager. For example, on Ubuntu/Debian-based systems, you can use:

```bash
sudo apt update
sudo apt install ffmpeg
```

Once the installation is complete, you can check the version of FFmpeg installed by running:

```bash
ffmpeg -version
```

### Project - Source

Currently the project must be run via source.

`git-lfs` was used when creating this project. While there are currently no large files currently, it is safest to install it. You can install it from the [git-lfs website](https://git-lfs.com/).

This project uses uv to manage the python dependencies and virtual environments. The install instructions can be found at the [uv website](https://docs.astral.sh/uv/#installation).

Once installed, the packages can be installed and virtual environment created with:

```bash
uv sync
```

The project runs on python 3.13.6 (managed by uv). The project also makes use of `black` formatting, `flake8` for linting and `bandit` for security checks. These are installed as part of the `uv sync` command.

## Execution

### Command Line Interface (CLI)

The CLI can be run with `uv` via:

```bash
uv run cli.py
```

which will create the virtual environment, install the python packages, and run the CLI.

### Graphical User Interface (GUI)

WIP

TODO
TODO add doc here for python version and black formatting.
TODO add black and flake8 and settings

### Release

WIP. TODO create release for GUI.

## Development

TODO discuss development tricks etc.

For GUI, pyside6?

```
pyside6-designer
```

TODO add option where we can select a local install of FFmpeg and use that instead of the system one?

TODO do we need to ignore ui files?

TODO issue with running inside uv on older python versions: <https://github.com/astral-sh/python-build-standalone/issues/146>
