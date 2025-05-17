"""Tests for error handling in py-eacopy using pytest features."""

# Import built-in modules
import os
import stat
from unittest.mock import patch

# Import third-party modules
import pytest

# Import the package
import py_eacopy
from py_eacopy import ErrorStrategy, LogLevel


# Mark this module as containing error handling tests
pytestmark = pytest.mark.error_handling


@pytest.fixture
def locked_dir(temp_dir):
    """Create a directory for locked file tests."""
    locked_dir = os.path.join(temp_dir, "locked")
    os.makedirs(locked_dir, exist_ok=True)
    return locked_dir


@pytest.fixture
def locked_file(locked_dir):
    """Create a file that will be used for lock testing."""
    locked_file = os.path.join(locked_dir, "locked.txt")
    with open(locked_file, "w") as f:
        f.write("This file will be locked.")
    return locked_file


@pytest.fixture
def read_only_dir(temp_dir):
    """Create a read-only directory for permission testing."""
    read_only_dir = os.path.join(temp_dir, "read_only")
    os.makedirs(read_only_dir, exist_ok=True)

    # Make the directory read-only on Windows
    if os.name == 'nt':
        os.chmod(read_only_dir, stat.S_IREAD)

    yield read_only_dir

    # Reset permissions for cleanup
    if os.name == 'nt':
        os.chmod(read_only_dir, stat.S_IRWXU)


@pytest.mark.parametrize("error_strategy,should_raise", [
    (ErrorStrategy.RAISE, True),
    (ErrorStrategy.IGNORE, False),
    (ErrorStrategy.RETRY, True),  # RETRY will eventually raise after max retries
])
def test_nonexistent_source(source_dir, dest_dir, reset_config, error_strategy, should_raise):
    """Test copying a non-existent source file with different error strategies."""
    # Set the error strategy (reset_config fixture ensures clean state between tests)
    py_eacopy.config.error_strategy = error_strategy

    # Create a non-existent file path
    non_existent_file = os.path.join(source_dir, "non_existent.txt")

    # Test the copy operation
    if should_raise:
        with pytest.raises(Exception):
            py_eacopy.copy(non_existent_file, dest_dir)
    else:
        # Should not raise an exception
        py_eacopy.copy(non_existent_file, dest_dir)
        # Verify the destination doesn't have the file
        assert not os.path.exists(os.path.join(dest_dir, "non_existent.txt"))


@pytest.mark.skipif(os.name != 'nt', reason="Permission tests are Windows-specific")
def test_permission_denied(test_file, read_only_dir, reset_config):
    """Test copying to a location with insufficient permissions."""
    # Try to copy with RAISE strategy
    py_eacopy.config.error_strategy = ErrorStrategy.RAISE

    with pytest.raises(Exception):
        py_eacopy.copy(test_file, os.path.join(read_only_dir, "test.txt"))

    # Try with IGNORE strategy
    py_eacopy.config.error_strategy = ErrorStrategy.IGNORE
    py_eacopy.copy(test_file, os.path.join(read_only_dir, "test.txt"))

    # File should not exist since the copy should have been ignored
    assert not os.path.exists(os.path.join(read_only_dir, "test.txt"))


def test_retry_strategy(locked_file, dest_dir, reset_config):
    """Test the RETRY error strategy."""
    # Set up retry strategy
    py_eacopy.config.error_strategy = ErrorStrategy.RETRY
    py_eacopy.config.retry_count = 3
    py_eacopy.config.retry_delay = 0.1  # Short delay for testing

    # Create a counter to track failure attempts
    failure_count = [0]

    # Mock the copyfile function to simulate failures and then success
    def mock_copyfile(_, dst):
        if failure_count[0] < 2:
            failure_count[0] += 1
            raise PermissionError("Simulated permission error")
        # After 2 failures, create the destination file to simulate success
        with open(dst, "w") as f:
            f.write("File copied after retries")
        return True

    # Apply the mock using pytest's monkeypatch
    with patch('py_eacopy.copyfile', side_effect=mock_copyfile):
        # This should succeed after 2 retries
        dest_file = os.path.join(dest_dir, "locked.txt")
        py_eacopy.copy(locked_file, dest_dir)

        # Verify the file was copied
        assert os.path.exists(dest_file)
        assert failure_count[0] == 2


@pytest.mark.parametrize("error_strategy,should_raise", [
    (ErrorStrategy.RAISE, True),
    (ErrorStrategy.IGNORE, False),
])
def test_batch_operations_with_errors(test_files, dest_dir, reset_config, error_strategy, should_raise):
    """Test batch operations with different error strategies."""
    # Set the error strategy
    py_eacopy.config.error_strategy = error_strategy

    # Create a non-existent file path
    non_existent = os.path.join(os.path.dirname(test_files[0]), "non_existent.txt")

    # Create file pairs with one non-existent file
    file_pairs = [(file, os.path.join(dest_dir, os.path.basename(file)))
                  for file in test_files[:3]]
    file_pairs.append((non_existent, os.path.join(dest_dir, "non_existent.txt")))

    # Test the batch copy operation
    if should_raise:
        with pytest.raises(Exception):
            py_eacopy.batch_copy(file_pairs)
    else:
        # Should not raise an exception
        py_eacopy.batch_copy(file_pairs)

        # Check that valid files were copied
        for file in test_files[:3]:
            dest_file = os.path.join(dest_dir, os.path.basename(file))
            assert os.path.exists(dest_file)

        # Check that the non-existent file was not created
        assert not os.path.exists(os.path.join(dest_dir, "non_existent.txt"))


def test_error_logging(test_file, dest_dir, reset_config, caplog):
    """Test that errors are properly logged."""
    # Set up logging
    py_eacopy.config.log_level = LogLevel.DEBUG

    # Create a non-existent file path
    non_existent = os.path.join(os.path.dirname(test_file), "non_existent.txt")

    # Try to copy a non-existent file with IGNORE strategy
    py_eacopy.config.error_strategy = ErrorStrategy.IGNORE

    # Capture logs
    with caplog.at_level("DEBUG"):
        py_eacopy.copy(non_existent, dest_dir)

    # Check that the error was logged
    assert any("non_existent" in record.message for record in caplog.records)


@pytest.mark.parametrize("retry_count,retry_delay", [
    (1, 0.1),
    (3, 0.2),
    (5, 0.05),
])
def test_retry_configuration(locked_file, dest_dir, reset_config, retry_count, retry_delay):
    """Test different retry configurations."""
    # Set up retry strategy with different parameters
    py_eacopy.config.error_strategy = ErrorStrategy.RETRY
    py_eacopy.config.retry_count = retry_count
    py_eacopy.config.retry_delay = retry_delay

    # Create a counter to track failure attempts
    failure_count = [0]

    # Mock the copyfile function to simulate failures and then success
    def mock_copyfile(_, dst):
        if failure_count[0] < retry_count - 1:
            failure_count[0] += 1
            raise PermissionError(f"Simulated permission error {failure_count[0]}")
        # After retry_count-1 failures, create the destination file to simulate success
        with open(dst, "w") as f:
            f.write("File copied after retries")
        return True

    # Apply the mock using pytest's monkeypatch
    with patch('py_eacopy.copyfile', side_effect=mock_copyfile):
        # This should succeed after retry_count-1 retries
        dest_file = os.path.join(dest_dir, "locked.txt")
        py_eacopy.copy(locked_file, dest_dir)

        # Verify the file was copied
        assert os.path.exists(dest_file)
        assert failure_count[0] == retry_count - 1
