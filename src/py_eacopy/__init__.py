"""Python bindings for EACopy, a high-performance file copy tool."""

# Import built-in modules
import os
import sys
import asyncio
from typing import Optional, Union, List, Tuple, Dict, Any, Callable

# Import local modules
from .__version__ import __version__

# Import C++ bindings
from ._eacopy_binding import (
    EACopy,
    copy,
    copy2,
    copyfile,
    copytree,
    copy_with_server,
    __eacopy_version__,
)

from .config import Config, ErrorStrategy, LogLevel, ProgressCallback

# Initialize global configuration
config = Config()

# Define async versions of the copy functions
async def async_copy(src: str, dst: str) -> None:
    """Asynchronous version of copy function."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: copy(src, dst))

async def async_copy2(src: str, dst: str) -> None:
    """Asynchronous version of copy2 function."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: copy2(src, dst))

async def async_copyfile(src: str, dst: str) -> None:
    """Asynchronous version of copyfile function."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: copyfile(src, dst))

async def async_copytree(
    src: str,
    dst: str,
    symlinks: bool = False,
    ignore_dangling_symlinks: bool = False,
    dirs_exist_ok: bool = False
) -> None:
    """Asynchronous version of copytree function."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: copytree(src, dst, symlinks, ignore_dangling_symlinks, dirs_exist_ok)
    )

async def async_copy_with_server(
    src: str,
    dst: str,
    server_addr: str,
    port: int = 31337,
    compression_level: int = 0
) -> None:
    """Asynchronous version of copy_with_server function."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: copy_with_server(src, dst, server_addr, port, compression_level)
    )

# Batch operations using the standalone functions
def batch_copy(file_pairs: List[Tuple[str, str]]) -> None:
    """Copy multiple files in batch."""
    eac = EACopy()
    eac.batch_copy(file_pairs)

def batch_copy2(file_pairs: List[Tuple[str, str]]) -> None:
    """Copy multiple files with metadata in batch."""
    eac = EACopy()
    eac.batch_copy2(file_pairs)

def batch_copytree(
    dir_pairs: List[Tuple[str, str]],
    symlinks: bool = False,
    ignore_dangling_symlinks: bool = False,
    dirs_exist_ok: bool = False
) -> None:
    """Copy multiple directory trees in batch."""
    eac = EACopy()
    eac.batch_copytree(dir_pairs, symlinks, ignore_dangling_symlinks, dirs_exist_ok)

__all__ = [
    "__version__",
    "__eacopy_version__",
    "config",
    "copy",
    "copy2",
    "copyfile",
    "copytree",
    "copy_with_server",
    "async_copy",
    "async_copy2",
    "async_copyfile",
    "async_copytree",
    "async_copy_with_server",
    "batch_copy",
    "batch_copy2",
    "batch_copytree",
    "Config",
    "ErrorStrategy",
    "LogLevel",
    "ProgressCallback",
    "EACopy",
]
