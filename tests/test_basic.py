"""Basic tests for py-eacopy."""

# Import built-in modules
import os
import shutil
import tempfile
import unittest
import asyncio
from pathlib import Path

# Import the package
import py_eacopy


class TestBasicFunctions(unittest.TestCase):
    """Test basic file copy functions."""

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
        
        # Create a subdirectory with files
        self.sub_dir = os.path.join(self.source_dir, "subdir")
        os.makedirs(self.sub_dir, exist_ok=True)
        
        self.sub_file = os.path.join(self.sub_dir, "subfile.txt")
        with open(self.sub_file, "w") as f:
            f.write("This is a file in a subdirectory.")

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)

    def test_copyfile(self):
        """Test copyfile function."""
        dest_file = os.path.join(self.dest_dir, "test.txt")
        
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Copy the file
        py_eacopy.copyfile(self.test_file, dest_file)
        
        # Check if the file was copied
        self.assertTrue(os.path.exists(dest_file))
        
        # Check file content
        with open(dest_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "This is a test file.")

    def test_copy(self):
        """Test copy function."""
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Copy the file
        py_eacopy.copy(self.test_file, self.dest_dir)
        
        # Check if the file was copied
        dest_file = os.path.join(self.dest_dir, "test.txt")
        self.assertTrue(os.path.exists(dest_file))
        
        # Check file content
        with open(dest_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "This is a test file.")

    def test_copy2(self):
        """Test copy2 function."""
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Copy the file with metadata
        py_eacopy.copy2(self.test_file, self.dest_dir)
        
        # Check if the file was copied
        dest_file = os.path.join(self.dest_dir, "test.txt")
        self.assertTrue(os.path.exists(dest_file))
        
        # Check file content
        with open(dest_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "This is a test file.")
        
        # Check if metadata was preserved (modification time)
        src_stat = os.stat(self.test_file)
        dst_stat = os.stat(dest_file)
        self.assertEqual(src_stat.st_mtime, dst_stat.st_mtime)

    def test_copytree(self):
        """Test copytree function."""
        # Copy the directory tree
        py_eacopy.copytree(self.source_dir, self.dest_dir)
        
        # Check if the directory was copied
        self.assertTrue(os.path.exists(self.dest_dir))
        
        # Check if the file was copied
        dest_file = os.path.join(self.dest_dir, "test.txt")
        self.assertTrue(os.path.exists(dest_file))
        
        # Check if the subdirectory was copied
        dest_sub_dir = os.path.join(self.dest_dir, "subdir")
        self.assertTrue(os.path.exists(dest_sub_dir))
        
        # Check if the file in the subdirectory was copied
        dest_sub_file = os.path.join(dest_sub_dir, "subfile.txt")
        self.assertTrue(os.path.exists(dest_sub_file))
        
        # Check file content
        with open(dest_sub_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "This is a file in a subdirectory.")


class TestEACopyClass(unittest.TestCase):
    """Test EACopy class."""

    def setUp(self):
        """Set up temporary directories for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.dest_dir = os.path.join(self.temp_dir, "dest")
        
        # Create source directory
        os.makedirs(self.source_dir, exist_ok=True)
        
        # Create test files
        self.files = []
        for i in range(5):
            file_path = os.path.join(self.source_dir, f"file{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"This is test file {i}.")
            self.files.append(file_path)

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)

    def test_eacopy_instance(self):
        """Test creating an EACopy instance."""
        eac = py_eacopy.EACopy(thread_count=8, compression_level=5)
        
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Copy a file
        eac.copy(self.files[0], self.dest_dir)
        
        # Check if the file was copied
        dest_file = os.path.join(self.dest_dir, "file0.txt")
        self.assertTrue(os.path.exists(dest_file))

    def test_context_manager(self):
        """Test using EACopy as a context manager."""
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        with py_eacopy.EACopy() as eac:
            eac.copy(self.files[0], self.dest_dir)
            eac.copy2(self.files[1], self.dest_dir)
        
        # Check if the files were copied
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "file0.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "file1.txt")))

    def test_batch_operations(self):
        """Test batch operations."""
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Create file pairs
        file_pairs = [(file, os.path.join(self.dest_dir, os.path.basename(file))) 
                      for file in self.files[:3]]
        
        # Batch copy
        py_eacopy.batch_copy(file_pairs)
        
        # Check if all files were copied
        for _, dest in file_pairs:
            self.assertTrue(os.path.exists(dest))


if __name__ == "__main__":
    unittest.main()
