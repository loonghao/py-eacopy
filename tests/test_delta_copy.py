"""Tests for the delta copy functionality."""

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

# Mark this module as containing delta copy tests
pytestmark = pytest.mark.delta_copy

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

def test_delta_copy_basic(temp_dir):
    """Test basic delta copy functionality."""
    # Create a reference file
    reference_path = os.path.join(temp_dir, "reference.txt")
    with open(reference_path, "w") as f:
        f.write("This is a reference file with some content.\n")
        f.write("It has multiple lines of text.\n")
        f.write("This line will be the same in both files.\n")
        f.write("This line will be different in the source file.\n")
        f.write("This line will also be the same.\n")
    
    # Create a source file that is similar to the reference file
    source_path = os.path.join(temp_dir, "source.txt")
    with open(source_path, "w") as f:
        f.write("This is a reference file with some content.\n")
        f.write("It has multiple lines of text.\n")
        f.write("This line will be the same in both files.\n")
        f.write("This line is different in the source file.\n")  # Changed line
        f.write("This line will also be the same.\n")
    
    # Create a destination path
    dest_path = os.path.join(temp_dir, "dest.txt")
    
    # Perform delta copy
    py_eacopy.delta_copy(source_path, dest_path, reference_path)
    
    # Check if the file was copied
    assert os.path.exists(dest_path)
    
    # Check the content
    with open(dest_path, "r") as f:
        content = f.read()
    
    with open(source_path, "r") as f:
        source_content = f.read()
    
    assert content == source_content

def test_delta_copy_binary(temp_dir):
    """Test delta copy with binary files."""
    # Create a reference binary file
    reference_path = os.path.join(temp_dir, "reference.bin")
    with open(reference_path, "wb") as f:
        f.write(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09")
        f.write(b"\x0A\x0B\x0C\x0D\x0E\x0F\x10\x11\x12\x13")
    
    # Create a source binary file that is similar to the reference file
    source_path = os.path.join(temp_dir, "source.bin")
    with open(source_path, "wb") as f:
        f.write(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09")
        f.write(b"\x0A\x0B\xFF\xFF\x0E\x0F\x10\x11\x12\x13")  # Changed bytes
    
    # Create a destination path
    dest_path = os.path.join(temp_dir, "dest.bin")
    
    # Perform delta copy
    py_eacopy.delta_copy(source_path, dest_path, reference_path)
    
    # Check if the file was copied
    assert os.path.exists(dest_path)
    
    # Check the content
    with open(dest_path, "rb") as f:
        content = f.read()
    
    with open(source_path, "rb") as f:
        source_content = f.read()
    
    assert content == source_content

def test_delta_copy_large_file(temp_dir):
    """Test delta copy with large files."""
    # Create a reference file (1MB)
    reference_path = os.path.join(temp_dir, "reference.dat")
    with open(reference_path, "wb") as f:
        # Write 1MB of data
        for i in range(1024):
            f.write(b"A" * 1024)
    
    # Create a source file that is similar to the reference file
    # but with a small change in the middle
    source_path = os.path.join(temp_dir, "source.dat")
    with open(source_path, "wb") as f:
        # Write first 512KB
        for i in range(512):
            f.write(b"A" * 1024)
        
        # Write 1KB of different data
        f.write(b"B" * 1024)
        
        # Write remaining data
        for i in range(511):
            f.write(b"A" * 1024)
    
    # Create a destination path
    dest_path = os.path.join(temp_dir, "dest.dat")
    
    # Perform delta copy
    py_eacopy.delta_copy(source_path, dest_path, reference_path)
    
    # Check if the file was copied
    assert os.path.exists(dest_path)
    
    # Check the content
    with open(dest_path, "rb") as f:
        content = f.read()
    
    with open(source_path, "rb") as f:
        source_content = f.read()
    
    assert content == source_content

def test_delta_copy_with_eacopy_class(temp_dir):
    """Test delta copy using the EACopy class."""
    # Create an EACopy instance
    eac = py_eacopy.EACopy(
        thread_count=4,
        compression_level=5,
        buffer_size=8 * 1024 * 1024
    )
    
    # Create a reference file
    reference_path = os.path.join(temp_dir, "reference.txt")
    with open(reference_path, "w") as f:
        f.write("This is a reference file with some content.\n")
        f.write("It has multiple lines of text.\n")
    
    # Create a source file that is similar to the reference file
    source_path = os.path.join(temp_dir, "source.txt")
    with open(source_path, "w") as f:
        f.write("This is a reference file with some content.\n")
        f.write("It has multiple lines of text and an extra line.\n")  # Changed line
    
    # Create a destination path
    dest_path = os.path.join(temp_dir, "dest.txt")
    
    # Perform delta copy
    eac.delta_copy(source_path, dest_path, reference_path)
    
    # Check if the file was copied
    assert os.path.exists(dest_path)
    
    # Check the content
    with open(dest_path, "r") as f:
        content = f.read()
    
    with open(source_path, "r") as f:
        source_content = f.read()
    
    assert content == source_content

def test_async_delta_copy(temp_dir):
    """Test asynchronous delta copy."""
    import asyncio
    
    # Create a reference file
    reference_path = os.path.join(temp_dir, "reference.txt")
    with open(reference_path, "w") as f:
        f.write("This is a reference file with some content.\n")
    
    # Create a source file that is similar to the reference file
    source_path = os.path.join(temp_dir, "source.txt")
    with open(source_path, "w") as f:
        f.write("This is a reference file with some modified content.\n")
    
    # Create a destination path
    dest_path = os.path.join(temp_dir, "dest.txt")
    
    # Define an async function to test
    async def test_async():
        await py_eacopy.async_delta_copy(source_path, dest_path, reference_path)
        
        # Check if the file was copied
        assert os.path.exists(dest_path)
        
        # Check the content
        with open(dest_path, "r") as f:
            content = f.read()
        
        with open(source_path, "r") as f:
            source_content = f.read()
        
        assert content == source_content
    
    # Run the async function
    asyncio.run(test_async())
