"""Tests for the Rust implementation of py-eacopy."""

# Import built-in modules
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Import third-party modules
import pytest

# Import the package
try:
    import py_eacopy
except ImportError:
    # If the package is not installed, try to import from the source directory
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import py_eacopy

# Mark this module as containing Rust binding tests
pytestmark = pytest.mark.rust_binding


def test_version():
    """Test that version information is available."""
    assert isinstance(py_eacopy.__version__, str)
    assert py_eacopy.__version__ != ""
    assert isinstance(py_eacopy.__eacopy_version__, str)
    assert py_eacopy.__eacopy_version__ != ""


def test_copy_file():
    """Test copying a file using the Rust implementation."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a source file
        source_path = os.path.join(temp_dir, "source.txt")
        with open(source_path, "w") as f:
            f.write("This is a test file.")
        
        # Create a destination path
        dest_path = os.path.join(temp_dir, "dest.txt")
        
        # Copy the file
        py_eacopy.copy(source_path, dest_path)
        
        # Check if the file was copied
        assert os.path.exists(dest_path)
        
        # Check the content
        with open(dest_path, "r") as f:
            content = f.read()
        assert content == "This is a test file."


def test_copy_directory():
    """Test copying a directory using the Rust implementation."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a source directory structure
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir)
        
        # Create some files in the source directory
        file1_path = os.path.join(source_dir, "file1.txt")
        with open(file1_path, "w") as f:
            f.write("This is file 1.")
        
        file2_path = os.path.join(source_dir, "file2.txt")
        with open(file2_path, "w") as f:
            f.write("This is file 2.")
        
        # Create a subdirectory
        subdir_path = os.path.join(source_dir, "subdir")
        os.makedirs(subdir_path)
        
        file3_path = os.path.join(subdir_path, "file3.txt")
        with open(file3_path, "w") as f:
            f.write("This is file 3.")
        
        # Create a destination directory
        dest_dir = os.path.join(temp_dir, "dest")
        
        # Copy the directory
        py_eacopy.copytree(source_dir, dest_dir)
        
        # Check if the directory was copied
        assert os.path.exists(dest_dir)
        assert os.path.exists(os.path.join(dest_dir, "file1.txt"))
        assert os.path.exists(os.path.join(dest_dir, "file2.txt"))
        assert os.path.exists(os.path.join(dest_dir, "subdir"))
        assert os.path.exists(os.path.join(dest_dir, "subdir", "file3.txt"))
        
        # Check the content
        with open(os.path.join(dest_dir, "file1.txt"), "r") as f:
            content1 = f.read()
        assert content1 == "This is file 1."
        
        with open(os.path.join(dest_dir, "file2.txt"), "r") as f:
            content2 = f.read()
        assert content2 == "This is file 2."
        
        with open(os.path.join(dest_dir, "subdir", "file3.txt"), "r") as f:
            content3 = f.read()
        assert content3 == "This is file 3."


def test_eacopy_class():
    """Test using the EACopy class from the Rust implementation."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a source file
        source_path = os.path.join(temp_dir, "source.txt")
        with open(source_path, "w") as f:
            f.write("This is a test file.")
        
        # Create a destination path
        dest_path = os.path.join(temp_dir, "dest.txt")
        
        # Create an EACopy instance
        eacopy = py_eacopy.EACopy(
            thread_count=4,
            compression_level=0,
            buffer_size=8 * 1024 * 1024,
            preserve_metadata=True,
            follow_symlinks=False,
            dirs_exist_ok=False
        )
        
        # Copy the file
        eacopy.copy(source_path, dest_path)
        
        # Check if the file was copied
        assert os.path.exists(dest_path)
        
        # Check the content
        with open(dest_path, "r") as f:
            content = f.read()
        assert content == "This is a test file."


def test_batch_operations():
    """Test batch operations using the Rust implementation."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create source files
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir)
        
        file1_path = os.path.join(source_dir, "file1.txt")
        with open(file1_path, "w") as f:
            f.write("This is file 1.")
        
        file2_path = os.path.join(source_dir, "file2.txt")
        with open(file2_path, "w") as f:
            f.write("This is file 2.")
        
        # Create a destination directory
        dest_dir = os.path.join(temp_dir, "dest")
        os.makedirs(dest_dir)
        
        # Create file pairs
        file_pairs = [
            (file1_path, os.path.join(dest_dir, "file1.txt")),
            (file2_path, os.path.join(dest_dir, "file2.txt")),
        ]
        
        # Batch copy
        py_eacopy.batch_copy(file_pairs)
        
        # Check if the files were copied
        assert os.path.exists(os.path.join(dest_dir, "file1.txt"))
        assert os.path.exists(os.path.join(dest_dir, "file2.txt"))
        
        # Check the content
        with open(os.path.join(dest_dir, "file1.txt"), "r") as f:
            content1 = f.read()
        assert content1 == "This is file 1."
        
        with open(os.path.join(dest_dir, "file2.txt"), "r") as f:
            content2 = f.read()
        assert content2 == "This is file 2."


def test_config():
    """Test configuration options in the Rust implementation."""
    # Test global configuration
    py_eacopy.config.thread_count = 8
    assert py_eacopy.config.thread_count == 8
    
    py_eacopy.config.compression_level = 5
    assert py_eacopy.config.compression_level == 5
    
    # Test instance configuration
    eacopy = py_eacopy.EACopy(thread_count=4, compression_level=3)
    assert eacopy.thread_count == 4
    assert eacopy.compression_level == 3
    
    # Update instance configuration
    eacopy.thread_count = 6
    assert eacopy.thread_count == 6
    
    eacopy.compression_level = 7
    assert eacopy.compression_level == 7


def test_progress_callback():
    """Test progress callback in the Rust implementation."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a source file (100KB)
        source_path = os.path.join(temp_dir, "source.txt")
        with open(source_path, "w") as f:
            f.write("X" * (100 * 1024))
        
        # Create a destination path
        dest_path = os.path.join(temp_dir, "dest.txt")
        
        # Create a callback function
        callback_called = False
        def progress_callback(copied_bytes, total_bytes, filename):
            nonlocal callback_called
            callback_called = True
            assert copied_bytes <= total_bytes
            assert filename == source_path or filename == dest_path
        
        # Set the callback
        py_eacopy.config.progress_callback = progress_callback
        
        # Copy the file
        py_eacopy.copy(source_path, dest_path)
        
        # Check if the callback was called
        assert callback_called
        
        # Reset the callback
        py_eacopy.config.progress_callback = None
