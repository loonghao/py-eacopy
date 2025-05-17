"""Tests for the EACopy server functionality."""

# Import built-in modules
import os
import sys
import tempfile
import shutil
import time
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

# Mark this module as containing server tests
pytestmark = pytest.mark.server

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def server():
    """Create and start an EACopy server for testing."""
    server = py_eacopy.create_server(port=31337, thread_count=4)
    server.start()
    try:
        yield server
    finally:
        if server.is_running():
            server.stop()

def test_server_creation():
    """Test creating an EACopy server."""
    server = py_eacopy.create_server(port=31337, thread_count=4)
    assert server is not None
    assert server.port == 31337
    assert server.thread_count == 4
    assert not server.is_running()

def test_server_start_stop():
    """Test starting and stopping an EACopy server."""
    server = py_eacopy.create_server(port=31337, thread_count=4)
    
    # Start the server
    server.start()
    assert server.is_running()
    
    # Get server statistics
    stats = server.get_stats()
    assert isinstance(stats, dict)
    assert "connections" in stats
    assert "active_connections" in stats
    assert "bytes_sent" in stats
    assert "bytes_received" in stats
    assert "files_sent" in stats
    assert "files_received" in stats
    
    # Stop the server
    server.stop()
    assert not server.is_running()

def test_server_context_manager():
    """Test using an EACopy server as a context manager."""
    with py_eacopy.create_server(port=31337, thread_count=4) as server:
        assert server.is_running()
        assert server.port == 31337
        assert server.thread_count == 4
    
    # Server should be stopped after exiting the context
    assert not server.is_running()

def test_copy_with_server(temp_dir, server):
    """Test copying a file using an EACopy server."""
    # Create a source file
    source_path = os.path.join(temp_dir, "source.txt")
    with open(source_path, "w") as f:
        f.write("This is a test file.")
    
    # Create a destination path
    dest_path = os.path.join(temp_dir, "dest.txt")
    
    # Copy the file using the server
    py_eacopy.copy_with_server(
        source_path,
        dest_path,
        "localhost",
        port=31337,
        compression_level=5
    )
    
    # Check if the file was copied
    assert os.path.exists(dest_path)
    
    # Check the content
    with open(dest_path, "r") as f:
        content = f.read()
    assert content == "This is a test file."

def test_copy_directory_with_server(temp_dir, server):
    """Test copying a directory using an EACopy server."""
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
    
    # Copy the directory using the server
    py_eacopy.copy_with_server(
        source_dir,
        dest_dir,
        "localhost",
        port=31337,
        compression_level=5
    )
    
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

def test_eacopy_class_with_server(temp_dir):
    """Test using the EACopy class with a server."""
    # Create an EACopy instance
    eac = py_eacopy.EACopy(
        thread_count=4,
        compression_level=5,
        buffer_size=8 * 1024 * 1024
    )
    
    # Create a server
    server = eac.create_server(port=31337)
    server.start()
    
    try:
        # Create a source file
        source_path = os.path.join(temp_dir, "source.txt")
        with open(source_path, "w") as f:
            f.write("This is a test file.")
        
        # Create a destination path
        dest_path = os.path.join(temp_dir, "dest.txt")
        
        # Copy the file using the server
        eac.copy_with_server(
            source_path,
            dest_path,
            "localhost",
            port=31337
        )
        
        # Check if the file was copied
        assert os.path.exists(dest_path)
        
        # Check the content
        with open(dest_path, "r") as f:
            content = f.read()
        assert content == "This is a test file."
    finally:
        # Stop the server
        if server.is_running():
            server.stop()
