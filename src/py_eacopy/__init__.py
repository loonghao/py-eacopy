"""Python bindings for EACopy, a high-performance file copy tool."""

import os
import sys
from pathlib import Path
from typing import Union, Optional

# Import Rust bindings
from ._eacopy_binding import (
    copy_file as _copy_file,
    copy_directory as _copy_directory,
    version as _version,
    __version__,
    __eacopy_version__,
)

def copy_file(source: Union[str, Path], destination: Union[str, Path]) -> bool:
    """
    Copy a file from source to destination.

    Args:
        source: Source file path
        destination: Destination file path

    Returns:
        bool: True if the copy was successful

    Raises:
        RuntimeError: If the copy operation fails
    """
    return _copy_file(str(source), str(destination))

def copy_directory(
    source: Union[str, Path],
    destination: Union[str, Path],
    recursive: bool = True,
) -> bool:
    """
    Copy a directory from source to destination.

    Args:
        source: Source directory path
        destination: Destination directory path
        recursive: Whether to copy subdirectories recursively (default: True)

    Returns:
        bool: True if the copy was successful

    Raises:
        RuntimeError: If the copy operation fails
    """
    return _copy_directory(str(source), str(destination), recursive)

# Alias for copy_directory
copy_tree = copy_directory

def version() -> str:
    """
    Get the version of the EACopy library.

    Returns:
        str: Version string
    """
    return _version()

__all__ = [
    "copy_file",
    "copy_directory",
    "copy_tree",
    "version",
    "__version__",
    "__eacopy_version__",
]
