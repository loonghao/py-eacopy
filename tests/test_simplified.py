"""Basic tests for py-eacopy simplified implementation."""

import os
import tempfile
import shutil
from pathlib import Path

import pytest

import py_eacopy


def test_version():
    """Test that version information is available."""
    assert py_eacopy.__version__ is not None
    assert isinstance(py_eacopy.__version__, str)
    assert py_eacopy.__eacopy_version__ is not None
    assert isinstance(py_eacopy.__eacopy_version__, str)
    
    # Test version() function
    version = py_eacopy.version()
    assert version is not None
    assert isinstance(version, str)


def test_copy_file():
    """Test copying a file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create source file
        source_path = Path(temp_dir) / "source.txt"
        with open(source_path, "w") as f:
            f.write("Hello, world!")
        
        # Create destination path
        dest_path = Path(temp_dir) / "dest.txt"
        
        # Copy the file
        result = py_eacopy.copy_file(source_path, dest_path)
        
        # Check result
        assert result is True
        assert dest_path.exists()
        
        # Check content
        with open(dest_path, "r") as f:
            content = f.read()
        assert content == "Hello, world!"


def test_copy_directory():
    """Test copying a directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create source directory structure
        source_dir = Path(temp_dir) / "source"
        source_dir.mkdir()
        
        # Create some files in the source directory
        (source_dir / "file1.txt").write_text("File 1 content")
        (source_dir / "file2.txt").write_text("File 2 content")
        
        # Create a subdirectory
        subdir = source_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("File 3 content")
        
        # Create destination directory path
        dest_dir = Path(temp_dir) / "dest"
        
        # Copy the directory
        result = py_eacopy.copy_directory(source_dir, dest_dir)
        
        # Check result
        assert result is True
        assert dest_dir.exists()
        assert (dest_dir / "file1.txt").exists()
        assert (dest_dir / "file2.txt").exists()
        assert (dest_dir / "subdir").exists()
        assert (dest_dir / "subdir" / "file3.txt").exists()
        
        # Check content
        assert (dest_dir / "file1.txt").read_text() == "File 1 content"
        assert (dest_dir / "file2.txt").read_text() == "File 2 content"
        assert (dest_dir / "subdir" / "file3.txt").read_text() == "File 3 content"


def test_copy_tree_alias():
    """Test that copy_tree is an alias for copy_directory."""
    assert py_eacopy.copy_tree is py_eacopy.copy_directory


def test_path_objects():
    """Test that Path objects are accepted."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create source file
        source_path = Path(temp_dir) / "source.txt"
        with open(source_path, "w") as f:
            f.write("Path object test")
        
        # Create destination path
        dest_path = Path(temp_dir) / "dest.txt"
        
        # Copy the file using Path objects
        result = py_eacopy.copy_file(source_path, dest_path)
        
        # Check result
        assert result is True
        assert dest_path.exists()
        
        # Check content
        with open(dest_path, "r") as f:
            content = f.read()
        assert content == "Path object test"


def test_error_handling():
    """Test error handling for non-existent files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create non-existent source path
        source_path = Path(temp_dir) / "nonexistent.txt"
        
        # Create destination path
        dest_path = Path(temp_dir) / "dest.txt"
        
        # Copy should raise an exception
        with pytest.raises(RuntimeError):
            py_eacopy.copy_file(source_path, dest_path)
