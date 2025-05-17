"""Tests for asynchronous functions in py-eacopy."""

# Import built-in modules
import os
import shutil
import tempfile
import unittest
import asyncio

# Import the package
import py_eacopy


class TestAsyncFunctions(unittest.TestCase):
    """Test asynchronous file copy functions."""

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
        
        # Create a subdirectory with files
        self.sub_dir = os.path.join(self.source_dir, "subdir")
        os.makedirs(self.sub_dir, exist_ok=True)
        
        self.sub_file = os.path.join(self.sub_dir, "subfile.txt")
        with open(self.sub_file, "w") as f:
            f.write("This is a file in a subdirectory.")

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)

    def test_async_copy(self):
        """Test async_copy function."""
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Run the async function
        async def run_test():
            await py_eacopy.async_copy(self.files[0], self.dest_dir)
        
        # Run the event loop
        asyncio.run(run_test())
        
        # Check if the file was copied
        dest_file = os.path.join(self.dest_dir, "file0.txt")
        self.assertTrue(os.path.exists(dest_file))
        
        # Check file content
        with open(dest_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "This is test file 0.")

    def test_async_copy2(self):
        """Test async_copy2 function."""
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Run the async function
        async def run_test():
            await py_eacopy.async_copy2(self.files[1], self.dest_dir)
        
        # Run the event loop
        asyncio.run(run_test())
        
        # Check if the file was copied
        dest_file = os.path.join(self.dest_dir, "file1.txt")
        self.assertTrue(os.path.exists(dest_file))
        
        # Check file content
        with open(dest_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "This is test file 1.")
        
        # Check if metadata was preserved (modification time)
        src_stat = os.stat(self.files[1])
        dst_stat = os.stat(dest_file)
        self.assertEqual(src_stat.st_mtime, dst_stat.st_mtime)

    def test_async_copyfile(self):
        """Test async_copyfile function."""
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        dest_file = os.path.join(self.dest_dir, "file2.txt")
        
        # Run the async function
        async def run_test():
            await py_eacopy.async_copyfile(self.files[2], dest_file)
        
        # Run the event loop
        asyncio.run(run_test())
        
        # Check if the file was copied
        self.assertTrue(os.path.exists(dest_file))
        
        # Check file content
        with open(dest_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "This is test file 2.")

    def test_async_copytree(self):
        """Test async_copytree function."""
        # Run the async function
        async def run_test():
            await py_eacopy.async_copytree(self.source_dir, self.dest_dir)
        
        # Run the event loop
        asyncio.run(run_test())
        
        # Check if the directory was copied
        self.assertTrue(os.path.exists(self.dest_dir))
        
        # Check if the files were copied
        for i in range(5):
            dest_file = os.path.join(self.dest_dir, f"file{i}.txt")
            self.assertTrue(os.path.exists(dest_file))
        
        # Check if the subdirectory was copied
        dest_sub_dir = os.path.join(self.dest_dir, "subdir")
        self.assertTrue(os.path.exists(dest_sub_dir))
        
        # Check if the file in the subdirectory was copied
        dest_sub_file = os.path.join(dest_sub_dir, "subfile.txt")
        self.assertTrue(os.path.exists(dest_sub_file))

    def test_parallel_async_copy(self):
        """Test running multiple async copy operations in parallel."""
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Run multiple async functions in parallel
        async def run_test():
            tasks = [
                py_eacopy.async_copy(self.files[i], self.dest_dir)
                for i in range(5)
            ]
            await asyncio.gather(*tasks)
        
        # Run the event loop
        asyncio.run(run_test())
        
        # Check if all files were copied
        for i in range(5):
            dest_file = os.path.join(self.dest_dir, f"file{i}.txt")
            self.assertTrue(os.path.exists(dest_file))


if __name__ == "__main__":
    unittest.main()
