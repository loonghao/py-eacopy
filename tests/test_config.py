"""Tests for configuration options in py-eacopy using pytest features."""

# Import built-in modules
import os

# Import third-party modules
import pytest

# Import the package
import py_eacopy
from py_eacopy import ErrorStrategy, LogLevel


# Mark this module as containing configuration tests
pytestmark = pytest.mark.config

# Note: All test functions use the reset_config fixture from conftest.py
# This fixture ensures that py_eacopy.config is reset to defaults after each test
# We don't need to explicitly use it in the test functions, but it's included
# in the function parameters to ensure it runs


@pytest.mark.parametrize("thread_count", [1, 4, 8])
def test_thread_count(test_file, dest_dir, _reset_config, thread_count):
    """Test thread_count configuration with different values."""
    # _reset_config fixture ensures clean configuration state between tests
    # Set thread count
    py_eacopy.config.thread_count = thread_count

    # Copy the file
    py_eacopy.copy(test_file, dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, "test.txt")
    assert os.path.exists(dest_file)


@pytest.mark.parametrize("compression_level", [0, 5, 9])
def test_compression_level(test_file, dest_dir, _reset_config, compression_level):
    """Test compression_level configuration with different values."""
    # Set compression level
    py_eacopy.config.compression_level = compression_level

    # Copy the file
    py_eacopy.copy(test_file, dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, "test.txt")
    assert os.path.exists(dest_file)


@pytest.mark.parametrize("error_strategy", [
    ErrorStrategy.RAISE,
    ErrorStrategy.IGNORE,
    ErrorStrategy.RETRY
])
def test_error_strategy(source_dir, dest_dir, _reset_config, error_strategy):
    """Test error_strategy configuration with different values."""
    # Set error strategy
    py_eacopy.config.error_strategy = error_strategy

    # Create a non-existent file path
    non_existent_file = os.path.join(source_dir, "non_existent.txt")

    if error_strategy == ErrorStrategy.IGNORE:
        # Should not raise an exception with IGNORE strategy
        py_eacopy.copy(non_existent_file, dest_dir)
    else:
        # Should raise an exception with other strategies
        with pytest.raises(Exception):
            py_eacopy.copy(non_existent_file, dest_dir)


@pytest.mark.parametrize("log_level", [
    LogLevel.ERROR,
    LogLevel.WARNING,
    LogLevel.INFO,
    LogLevel.DEBUG
])
def test_log_level(test_file, dest_dir, _reset_config, log_level, caplog):
    """Test log_level configuration with different values."""
    # Set log level
    py_eacopy.config.log_level = log_level

    # Copy the file with log capture
    with caplog.at_level(log_level.name):
        py_eacopy.copy(test_file, dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, "test.txt")
    assert os.path.exists(dest_file)


def test_custom_eacopy_instance(test_file, dest_dir):
    """Test creating a custom EACopy instance with configuration."""
    # Create an EACopy instance with custom configuration
    eac = py_eacopy.EACopy(
        thread_count=8,
        compression_level=5,
        preserve_metadata=True,
        follow_symlinks=True,
        dirs_exist_ok=True
    )

    # Copy a file
    eac.copy(test_file, dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, "test.txt")
    assert os.path.exists(dest_file)


def test_global_config(test_file, dest_dir, _reset_config):
    """Test global configuration affects copy operations."""
    # Set global configuration
    py_eacopy.config.thread_count = 8
    py_eacopy.config.compression_level = 5
    py_eacopy.config.preserve_metadata = True
    py_eacopy.config.error_strategy = ErrorStrategy.RETRY
    py_eacopy.config.retry_count = 3
    py_eacopy.config.log_level = LogLevel.INFO

    # Copy the file
    py_eacopy.copy(test_file, dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, "test.txt")
    assert os.path.exists(dest_file)


def test_config_with_context_manager(test_file, dest_dir):
    """Test configuration with EACopy context manager."""
    # Create a custom EACopy instance with specific configuration
    with py_eacopy.EACopy(thread_count=3, compression_level=2) as eac:
        # Copy the file
        eac.copy(test_file, dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, "test.txt")
    assert os.path.exists(dest_file)
