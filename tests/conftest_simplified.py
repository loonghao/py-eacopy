"""Simplified pytest configuration for py-eacopy tests."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    dir_path = tempfile.mkdtemp()
    yield dir_path
    # Clean up after test
    try:
        shutil.rmtree(dir_path)
    except (OSError, PermissionError) as e:
        print(f"Warning: Failed to clean up {dir_path}: {e}")


@pytest.fixture
def source_dir(temp_dir):
    """Create a source directory with test files."""
    src_dir = Path(temp_dir) / "source"
    src_dir.mkdir(exist_ok=True)
    return src_dir


@pytest.fixture
def dest_dir(temp_dir):
    """Create a destination directory for testing."""
    dst_dir = Path(temp_dir) / "dest"
    dst_dir.mkdir(exist_ok=True)
    return dst_dir


@pytest.fixture
def test_file(source_dir):
    """Create a test file in the source directory."""
    file_path = source_dir / "test.txt"
    file_path.write_text("This is a test file.")
    return file_path


@pytest.fixture
def nested_dir_structure(source_dir):
    """Create a nested directory structure with files."""
    # Create a file in the root directory
    root_file = source_dir / "root.txt"
    root_file.write_text("This is a file in the root directory.")
    
    # Create a subdirectory
    sub_dir = source_dir / "subdir"
    sub_dir.mkdir(exist_ok=True)
    
    # Create a file in the subdirectory
    sub_file = sub_dir / "subfile.txt"
    sub_file.write_text("This is a file in a subdirectory.")
    
    # Create a deeper nested directory
    deep_dir = sub_dir / "deepdir"
    deep_dir.mkdir(exist_ok=True)
    
    # Create a file in the deeper directory
    deep_file = deep_dir / "deepfile.txt"
    deep_file.write_text("This is a file in a deeply nested directory.")
    
    return {
        "root": source_dir,
        "root_file": root_file,
        "sub_dir": sub_dir,
        "sub_file": sub_file,
        "deep_dir": deep_dir,
        "deep_file": deep_file
    }
