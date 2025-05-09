"""Tests for configuration options in py-eacopy."""

# Import built-in modules
import os
import shutil
import tempfile
import unittest

# Import the package
import py_eacopy
from py_eacopy import ErrorStrategy, LogLevel


class TestConfig(unittest.TestCase):
    """Test configuration options."""

    def setUp(self):
        """Set up temporary directories for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.dest_dir = os.path.join(self.temp_dir, "dest")
        
        # Create source directory
        os.makedirs(self.source_dir, exist_ok=True)
        
        # Create a test file
        self.test_file = os.path.join(self.source_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("This is a test file.")

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)
        
        # Reset global configuration to defaults
        py_eacopy.config = py_eacopy.Config()

    def test_global_config(self):
        """Test global configuration."""
        # Modify global configuration
        py_eacopy.config.thread_count = 8
        py_eacopy.config.compression_level = 5
        py_eacopy.config.preserve_metadata = True
        py_eacopy.config.error_strategy = ErrorStrategy.RETRY
        py_eacopy.config.retry_count = 3
        py_eacopy.config.log_level = LogLevel.INFO
        
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Copy a file
        py_eacopy.copy(self.test_file, self.dest_dir)
        
        # Check if the file was copied
        dest_file = os.path.join(self.dest_dir, "test.txt")
        self.assertTrue(os.path.exists(dest_file))

    def test_custom_eacopy_instance(self):
        """Test creating a custom EACopy instance with configuration."""
        # Create an EACopy instance with custom configuration
        eac = py_eacopy.EACopy(
            thread_count=8,
            compression_level=5,
            buffer_size=16 * 1024 * 1024,  # 16MB buffer
            preserve_metadata=True,
            follow_symlinks=True,
            dirs_exist_ok=True
        )
        
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Copy a file
        eac.copy(self.test_file, self.dest_dir)
        
        # Check if the file was copied
        dest_file = os.path.join(self.dest_dir, "test.txt")
        self.assertTrue(os.path.exists(dest_file))

    def test_error_strategies(self):
        """Test different error strategies."""
        # Test RAISE strategy (default)
        py_eacopy.config.error_strategy = ErrorStrategy.RAISE
        
        # Try to copy a non-existent file
        non_existent_file = os.path.join(self.source_dir, "non_existent.txt")
        
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # This should raise an exception
        with self.assertRaises(Exception):
            py_eacopy.copy(non_existent_file, self.dest_dir)
        
        # Test IGNORE strategy
        py_eacopy.config.error_strategy = ErrorStrategy.IGNORE
        
        # This should not raise an exception
        try:
            py_eacopy.copy(non_existent_file, self.dest_dir)
        except Exception as e:
            self.fail(f"copy() raised {type(e).__name__} unexpectedly!")


if __name__ == "__main__":
    unittest.main()
