"""Performance tests for py-eacopy."""

# Import built-in modules
import os
import shutil
import tempfile
import unittest
import time
import random
import string
import sys

# Import the package
try:
    import py_eacopy
except ImportError:
    # If the package is not installed, try to import from the source directory
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import py_eacopy


class TestPerformance(unittest.TestCase):
    """Test performance of file copy operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.source_dir = os.path.join(cls.temp_dir, "source")
        cls.dest_dir = os.path.join(cls.temp_dir, "dest")

        # Create source directory
        os.makedirs(cls.source_dir, exist_ok=True)

        # Create a medium-sized file (1MB)
        cls.medium_file = os.path.join(cls.source_dir, "medium.dat")
        with open(cls.medium_file, "wb") as f:
            f.write(os.urandom(1024 * 1024))  # 1MB of random data

        # Create a directory with many small files
        cls.many_files_dir = os.path.join(cls.source_dir, "many_files")
        os.makedirs(cls.many_files_dir, exist_ok=True)

        # Create 100 small files
        cls.small_files = []
        for i in range(100):
            file_path = os.path.join(cls.many_files_dir, f"file{i:03d}.txt")
            with open(file_path, "w") as f:
                # Write 1KB of random text
                f.write(''.join(random.choices(string.ascii_letters + string.digits, k=1024)))
            cls.small_files.append(file_path)

        # Create a deep directory structure
        cls.deep_dir = os.path.join(cls.source_dir, "deep")
        current_dir = cls.deep_dir
        cls.deep_files = []

        # Create 10 levels of directories with files
        for i in range(10):
            os.makedirs(current_dir, exist_ok=True)
            file_path = os.path.join(current_dir, f"level{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"This is a file at level {i}")
            cls.deep_files.append(file_path)
            current_dir = os.path.join(current_dir, f"level{i+1}")

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        """Set up for each test."""
        # Create a fresh destination directory
        if os.path.exists(self.dest_dir):
            shutil.rmtree(self.dest_dir)
        os.makedirs(self.dest_dir, exist_ok=True)

        # Reset global configuration to defaults
        py_eacopy.config = py_eacopy.Config()

    def test_medium_file_performance(self):
        """Test performance with a medium-sized file."""
        # Time the copy operation
        start_time = time.time()
        py_eacopy.copy(self.medium_file, self.dest_dir)
        end_time = time.time()

        # Calculate throughput
        file_size_mb = os.path.getsize(self.medium_file) / (1024 * 1024)
        duration = end_time - start_time
        throughput = file_size_mb / duration if duration > 0 else 0

        # Log performance metrics
        print(f"\nMedium file copy: {file_size_mb:.2f} MB in {duration:.2f} seconds")
        print(f"Throughput: {throughput:.2f} MB/s")

        # Verify the file was copied correctly
        dest_file = os.path.join(self.dest_dir, "medium.dat")
        self.assertTrue(os.path.exists(dest_file))
        self.assertEqual(os.path.getsize(self.medium_file), os.path.getsize(dest_file))

    def test_many_small_files_performance(self):
        """Test performance with many small files."""
        # Time the copy operation
        start_time = time.time()
        py_eacopy.copytree(self.many_files_dir, os.path.join(self.dest_dir, "many_files"))
        end_time = time.time()

        # Calculate metrics
        duration = end_time - start_time
        files_per_second = len(self.small_files) / duration if duration > 0 else 0

        # Log performance metrics
        print(f"\nMany small files copy: {len(self.small_files)} files in {duration:.2f} seconds")
        print(f"Files per second: {files_per_second:.2f}")

        # Verify all files were copied
        for i in range(100):
            dest_file = os.path.join(self.dest_dir, "many_files", f"file{i:03d}.txt")
            self.assertTrue(os.path.exists(dest_file))

    def test_deep_directory_performance(self):
        """Test performance with a deep directory structure."""
        # Time the copy operation
        start_time = time.time()
        py_eacopy.copytree(self.deep_dir, os.path.join(self.dest_dir, "deep"))
        end_time = time.time()

        # Calculate metrics
        duration = end_time - start_time

        # Log performance metrics
        print(f"\nDeep directory copy: 10 levels in {duration:.2f} seconds")

        # Verify the directory structure was copied
        current_dir = os.path.join(self.dest_dir, "deep")
        for i in range(10):
            file_path = os.path.join(current_dir, f"level{i}.txt")
            self.assertTrue(os.path.exists(file_path))
            current_dir = os.path.join(current_dir, f"level{i+1}")

    def test_thread_count_impact(self):
        """Test the impact of thread count on performance."""
        results = []

        # Test with different thread counts
        thread_counts = [1, 2, 4, 8]
        for thread_count in thread_counts:
            # Clean destination
            if os.path.exists(os.path.join(self.dest_dir, "many_files")):
                shutil.rmtree(os.path.join(self.dest_dir, "many_files"))

            # Set thread count
            py_eacopy.config.thread_count = thread_count

            # Time the copy operation
            start_time = time.time()
            py_eacopy.copytree(self.many_files_dir, os.path.join(self.dest_dir, "many_files"))
            end_time = time.time()

            # Calculate metrics
            duration = end_time - start_time
            files_per_second = len(self.small_files) / duration if duration > 0 else 0

            results.append((thread_count, duration, files_per_second))

        # Log performance metrics
        print("\nThread count impact on performance:")
        for thread_count, duration, files_per_second in results:
            print(f"  {thread_count} threads: {duration:.2f} seconds, {files_per_second:.2f} files/s")

        # Verify all files were copied in the last run
        for i in range(100):
            dest_file = os.path.join(self.dest_dir, "many_files", f"file{i:03d}.txt")
            self.assertTrue(os.path.exists(dest_file))

    def test_server_copy_performance(self):
        """Test performance of copying files using a server."""
        # Create a large file (10MB)
        large_file = os.path.join(self.source_dir, "large.dat")
        with open(large_file, "wb") as f:
            f.write(os.urandom(10 * 1024 * 1024))  # 10MB of random data

        # Create a server
        server = py_eacopy.create_server(port=31337, thread_count=4)
        server.start()

        try:
            # Time the copy operation
            start_time = time.time()
            py_eacopy.copy_with_server(
                large_file,
                os.path.join(self.dest_dir, "large.dat"),
                "localhost",
                port=31337,
                compression_level=5
            )
            end_time = time.time()

            # Calculate throughput
            file_size_mb = os.path.getsize(large_file) / (1024 * 1024)
            duration = end_time - start_time
            throughput = file_size_mb / duration if duration > 0 else 0

            # Log performance metrics
            print(f"\nServer copy: {file_size_mb:.2f} MB in {duration:.2f} seconds")
            print(f"Throughput: {throughput:.2f} MB/s")

            # Verify the file was copied correctly
            dest_file = os.path.join(self.dest_dir, "large.dat")
            self.assertTrue(os.path.exists(dest_file))
            self.assertEqual(os.path.getsize(large_file), os.path.getsize(dest_file))
        finally:
            # Stop the server
            if server.is_running():
                server.stop()

    def test_compression_level_impact(self):
        """Test the impact of compression level on server copy performance."""
        # Create a large file (10MB)
        large_file = os.path.join(self.source_dir, "large.dat")
        with open(large_file, "wb") as f:
            f.write(os.urandom(10 * 1024 * 1024))  # 10MB of random data

        # Create a server
        server = py_eacopy.create_server(port=31337, thread_count=4)
        server.start()

        try:
            results = []

            # Test with different compression levels
            compression_levels = [0, 3, 6, 9]
            for level in compression_levels:
                # Clean destination
                dest_file = os.path.join(self.dest_dir, "large.dat")
                if os.path.exists(dest_file):
                    os.remove(dest_file)

                # Time the copy operation
                start_time = time.time()
                py_eacopy.copy_with_server(
                    large_file,
                    dest_file,
                    "localhost",
                    port=31337,
                    compression_level=level
                )
                end_time = time.time()

                # Calculate throughput
                file_size_mb = os.path.getsize(large_file) / (1024 * 1024)
                duration = end_time - start_time
                throughput = file_size_mb / duration if duration > 0 else 0

                results.append((level, duration, throughput))

            # Log performance metrics
            print("\nCompression level impact on performance:")
            for level, duration, throughput in results:
                print(f"  Level {level}: {duration:.2f} seconds, {throughput:.2f} MB/s")

            # Verify the file was copied correctly in the last run
            self.assertTrue(os.path.exists(dest_file))
            self.assertEqual(os.path.getsize(large_file), os.path.getsize(dest_file))
        finally:
            # Stop the server
            if server.is_running():
                server.stop()

    def test_delta_copy_performance(self):
        """Test performance of delta copy."""
        # Create a reference file (10MB)
        reference_file = os.path.join(self.source_dir, "reference.dat")
        with open(reference_file, "wb") as f:
            f.write(os.urandom(10 * 1024 * 1024))  # 10MB of random data

        # Create a source file that is similar to the reference file
        # but with a small change in the middle
        source_file = os.path.join(self.source_dir, "source.dat")
        shutil.copy(reference_file, source_file)

        # Modify a small part of the source file
        with open(source_file, "r+b") as f:
            f.seek(5 * 1024 * 1024)  # Go to the middle of the file
            f.write(b"X" * 1024)  # Write 1KB of different data

        # Create a destination path
        dest_file = os.path.join(self.dest_dir, "dest.dat")

        # Time the delta copy operation
        start_time = time.time()
        py_eacopy.delta_copy(source_file, dest_file, reference_file)
        end_time = time.time()

        # Calculate throughput
        file_size_mb = os.path.getsize(source_file) / (1024 * 1024)
        duration = end_time - start_time
        throughput = file_size_mb / duration if duration > 0 else 0

        # Log performance metrics
        print(f"\nDelta copy: {file_size_mb:.2f} MB in {duration:.2f} seconds")
        print(f"Throughput: {throughput:.2f} MB/s")

        # Verify the file was copied correctly
        self.assertTrue(os.path.exists(dest_file))
        self.assertEqual(os.path.getsize(source_file), os.path.getsize(dest_file))

        # Compare with regular copy for the same file
        regular_dest_file = os.path.join(self.dest_dir, "regular_dest.dat")

        # Time the regular copy operation
        start_time = time.time()
        py_eacopy.copy(source_file, regular_dest_file)
        end_time = time.time()

        # Calculate throughput
        regular_duration = end_time - start_time
        regular_throughput = file_size_mb / regular_duration if regular_duration > 0 else 0

        # Log performance comparison
        print(f"Regular copy: {file_size_mb:.2f} MB in {regular_duration:.2f} seconds")
        print(f"Regular throughput: {regular_throughput:.2f} MB/s")
        print(f"Delta copy speedup: {regular_duration / duration:.2f}x")

    def test_delta_copy_with_different_similarity(self):
        """Test delta copy performance with different levels of file similarity."""
        # Create a reference file (10MB)
        reference_file = os.path.join(self.source_dir, "reference.dat")
        with open(reference_file, "wb") as f:
            f.write(os.urandom(10 * 1024 * 1024))  # 10MB of random data

        # Test with different similarity levels
        similarity_levels = [
            (0.1, "10% different"),   # 10% different
            (0.5, "50% different"),   # 50% different
            (0.9, "90% different"),   # 90% different
        ]

        results = []

        for diff_ratio, label in similarity_levels:
            # Create a source file with the specified difference ratio
            source_file = os.path.join(self.source_dir, f"source_{int(diff_ratio * 100)}.dat")
            shutil.copy(reference_file, source_file)

            # Modify the source file
            with open(source_file, "r+b") as f:
                # Calculate how many bytes to modify
                total_size = os.path.getsize(source_file)
                bytes_to_modify = int(total_size * diff_ratio)

                # Modify random positions in the file
                for _ in range(0, bytes_to_modify, 1024):
                    # Choose a random position
                    pos = random.randint(0, total_size - 1024)
                    f.seek(pos)
                    f.write(os.urandom(1024))  # Write 1KB of random data

            # Create a destination path
            dest_file = os.path.join(self.dest_dir, f"dest_{int(diff_ratio * 100)}.dat")

            # Time the delta copy operation
            start_time = time.time()
            py_eacopy.delta_copy(source_file, dest_file, reference_file)
            end_time = time.time()

            # Calculate throughput
            file_size_mb = os.path.getsize(source_file) / (1024 * 1024)
            duration = end_time - start_time
            throughput = file_size_mb / duration if duration > 0 else 0

            results.append((diff_ratio, label, duration, throughput))

            # Verify the file was copied correctly
            self.assertTrue(os.path.exists(dest_file))
            self.assertEqual(os.path.getsize(source_file), os.path.getsize(dest_file))

        # Log performance metrics
        print("\nDelta copy performance with different similarity levels:")
        for diff_ratio, label, duration, throughput in results:
            print(f"  {label}: {duration:.2f} seconds, {throughput:.2f} MB/s")


if __name__ == "__main__":
    unittest.main()
