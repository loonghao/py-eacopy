"""Pytest configuration and shared fixtures for py-eacopy tests."""

# Import built-in modules
import os
import shutil
import tempfile
import stat

# Import third-party modules
import pytest

# Import the package
import py_eacopy


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
    src_dir = os.path.join(temp_dir, "source")
    os.makedirs(src_dir, exist_ok=True)
    return src_dir


@pytest.fixture
def dest_dir(temp_dir):
    """Create a destination directory for testing."""
    dst_dir = os.path.join(temp_dir, "dest")
    os.makedirs(dst_dir, exist_ok=True)
    return dst_dir


@pytest.fixture
def test_file(source_dir):
    """Create a test file in the source directory."""
    file_path = os.path.join(source_dir, "test.txt")
    with open(file_path, "w") as f:
        f.write("This is a test file.")
    return file_path


@pytest.fixture
def test_files(source_dir):
    """Create multiple test files in the source directory."""
    files = []
    for i in range(5):
        file_path = os.path.join(source_dir, f"file{i}.txt")
        with open(file_path, "w") as f:
            f.write(f"This is test file {i}.")
        files.append(file_path)
    return files


@pytest.fixture
def nested_dir_structure(source_dir):
    """Create a nested directory structure with files."""
    # Create a subdirectory
    sub_dir = os.path.join(source_dir, "subdir")
    os.makedirs(sub_dir, exist_ok=True)

    # Create a file in the subdirectory
    sub_file = os.path.join(sub_dir, "subfile.txt")
    with open(sub_file, "w") as f:
        f.write("This is a file in a subdirectory.")

    # Create a deeper nested directory
    deep_dir = os.path.join(sub_dir, "deepdir")
    os.makedirs(deep_dir, exist_ok=True)

    # Create a file in the deeper directory
    deep_file = os.path.join(deep_dir, "deepfile.txt")
    with open(deep_file, "w") as f:
        f.write("This is a file in a deeply nested directory.")

    return {
        "root": source_dir,
        "sub_dir": sub_dir,
        "sub_file": sub_file,
        "deep_dir": deep_dir,
        "deep_file": deep_file
    }


@pytest.fixture
def large_file(source_dir):
    """Create a larger test file (100KB) for performance testing."""
    file_path = os.path.join(source_dir, "large.txt")
    with open(file_path, "w") as f:
        # Write 100KB of data
        f.write("X" * (100 * 1024))
    return file_path


@pytest.fixture
def binary_file(source_dir):
    """Create a binary test file for testing binary data handling."""
    file_path = os.path.join(source_dir, "binary.dat")
    with open(file_path, "wb") as f:
        # Write 10KB of binary data
        f.write(os.urandom(10 * 1024))
    return file_path


@pytest.fixture
def unicode_filename(source_dir):
    """Create a file with Unicode characters in the filename."""
    # Use a mix of characters from different scripts
    filename = "unicode_测试_тест_テスト.txt"
    file_path = os.path.join(source_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("This is a file with Unicode in its name.")
    return file_path


@pytest.fixture
def reset_config():
    """Reset global configuration to defaults after test."""
    yield
    # No config to reset in simplified implementation


@pytest.fixture
def mock_progress_callback(mocker):
    """Create a mock progress callback function."""
    return mocker.Mock()


@pytest.fixture
def read_only_file(source_dir):
    """Create a read-only file for testing permission handling."""
    file_path = os.path.join(source_dir, "readonly.txt")
    with open(file_path, "w") as f:
        f.write("This is a read-only file.")

    # Make the file read-only (platform-specific)
    # Windows needs different permissions
    os.chmod(file_path, stat.S_IREAD if os.name == 'nt' else 0o444)

    yield file_path

    # Make the file writable again for cleanup
    try:
        # Set appropriate permissions based on platform
        os.chmod(file_path, (stat.S_IWRITE | stat.S_IREAD) if os.name == 'nt' else 0o644)
    except Exception as e:
        print(f"Warning: Failed to restore permissions for {file_path}: {e}")


@pytest.fixture
def many_small_files(source_dir):
    """Create many small files for testing batch operations."""
    files = []
    # Create a subdirectory for the small files
    small_files_dir = os.path.join(source_dir, "many_files")
    os.makedirs(small_files_dir, exist_ok=True)

    # Create 50 small files
    for i in range(50):
        file_path = os.path.join(small_files_dir, f"small_file_{i:03d}.txt")
        with open(file_path, "w") as f:
            f.write(f"Small file content {i}")
        files.append(file_path)

    return {
        "dir": small_files_dir,
        "files": files
    }
