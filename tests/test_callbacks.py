"""Tests for callback functionality in py-eacopy."""

# Import built-in modules
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

# Import the package
import py_eacopy


class TestCallbacks(unittest.TestCase):
    """Test callback functionality."""

    def setUp(self):
        """Set up temporary directories for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.dest_dir = os.path.join(self.temp_dir, "dest")
        
        # Create source directory
        os.makedirs(self.source_dir, exist_ok=True)
        
        # Create test files of different sizes
        self.small_file = os.path.join(self.source_dir, "small.txt")
        with open(self.small_file, "w") as f:
            f.write("This is a small test file.")
        
        self.medium_file = os.path.join(self.source_dir, "medium.txt")
        with open(self.medium_file, "w") as f:
            f.write("X" * 1024)  # 1KB file
        
        self.large_file = os.path.join(self.source_dir, "large.txt")
        with open(self.large_file, "w") as f:
            f.write("X" * (1024 * 10))  # 10KB file
        
        # Create a directory with multiple files
        self.multi_dir = os.path.join(self.source_dir, "multi")
        os.makedirs(self.multi_dir, exist_ok=True)
        
        for i in range(5):
            file_path = os.path.join(self.multi_dir, f"file{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"This is test file {i}.")
        
        # Reset global configuration to defaults
        py_eacopy.config = py_eacopy.Config()

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)
        
        # Reset global configuration to defaults
        py_eacopy.config = py_eacopy.Config()

    def test_progress_callback_single_file(self):
        """Test progress callback with a single file."""
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Create a mock callback
        mock_callback = MagicMock()
        
        # Set the callback in the global configuration
        py_eacopy.config.progress_callback = mock_callback
        
        # Copy a file
        py_eacopy.copy(self.medium_file, self.dest_dir)
        
        # Check if the callback was called
        self.assertTrue(mock_callback.called)
        
        # Check if the callback was called with the correct arguments
        # At minimum, it should be called at the start and end
        self.assertGreaterEqual(mock_callback.call_count, 2)
        
        # The last call should have copied_bytes equal to total_bytes
        args, kwargs = mock_callback.call_args
        copied_bytes, total_bytes, filename = args
        self.assertEqual(copied_bytes, total_bytes)
        self.assertIn("medium.txt", filename)

    def test_progress_callback_directory(self):
        """Test progress callback with a directory."""
        # Create a mock callback
        mock_callback = MagicMock()
        
        # Set the callback in the global configuration
        py_eacopy.config.progress_callback = mock_callback
        
        # Copy a directory
        py_eacopy.copytree(self.multi_dir, os.path.join(self.dest_dir, "multi"))
        
        # Check if the callback was called
        self.assertTrue(mock_callback.called)
        
        # Should be called multiple times for multiple files
        self.assertGreater(mock_callback.call_count, 5)
        
        # Verify that the callback was called for each file
        filenames = set()
        for call in mock_callback.call_args_list:
            args, kwargs = call
            _, _, filename = args
            filenames.add(os.path.basename(filename))
        
        # Should have been called for each file in the directory
        for i in range(5):
            self.assertIn(f"file{i}.txt", filenames)

    def test_custom_callback_instance(self):
        """Test using a custom callback with an EACopy instance."""
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Create a mock callback
        mock_callback = MagicMock()
        
        # Create an EACopy instance with the callback
        eac = py_eacopy.EACopy(
            thread_count=4,
            progress_callback=mock_callback
        )
        
        # Copy a file
        eac.copy(self.large_file, self.dest_dir)
        
        # Check if the callback was called
        self.assertTrue(mock_callback.called)
        
        # The callback should be called multiple times for a large file
        self.assertGreater(mock_callback.call_count, 2)
        
        # The last call should have copied_bytes equal to total_bytes
        args, kwargs = mock_callback.call_args
        copied_bytes, total_bytes, filename = args
        self.assertEqual(copied_bytes, total_bytes)
        self.assertIn("large.txt", filename)

    def test_callback_batch_operations(self):
        """Test callback with batch operations."""
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Create a mock callback
        mock_callback = MagicMock()
        
        # Set the callback in the global configuration
        py_eacopy.config.progress_callback = mock_callback
        
        # Create file pairs
        file_pairs = [
            (self.small_file, os.path.join(self.dest_dir, "small.txt")),
            (self.medium_file, os.path.join(self.dest_dir, "medium.txt")),
            (self.large_file, os.path.join(self.dest_dir, "large.txt"))
        ]
        
        # Batch copy
        py_eacopy.batch_copy(file_pairs)
        
        # Check if the callback was called
        self.assertTrue(mock_callback.called)
        
        # Should be called for each file
        filenames = set()
        for call in mock_callback.call_args_list:
            args, kwargs = call
            _, _, filename = args
            filenames.add(os.path.basename(filename))
        
        self.assertIn("small.txt", filenames)
        self.assertIn("medium.txt", filenames)
        self.assertIn("large.txt", filenames)


if __name__ == "__main__":
    unittest.main()
