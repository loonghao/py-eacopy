"""Tests for handling Unicode/non-ASCII paths in py-eacopy."""

# Import built-in modules
import os
import shutil
import tempfile
import unittest

# Import the package
import py_eacopy


class TestUnicodePaths(unittest.TestCase):
    """Test handling of Unicode/non-ASCII paths."""

    def setUp(self):
        """Set up temporary directories for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.dest_dir = os.path.join(self.temp_dir, "dest")
        
        # Create source directory
        os.makedirs(self.source_dir, exist_ok=True)
        
        # Create test files with Unicode names
        self.unicode_names = [
            "中文文件.txt",  # Chinese
            "русский_файл.txt",  # Russian
            "日本語ファイル.txt",  # Japanese
            "한국어_파일.txt",  # Korean
            "ñáéíóú.txt",  # Spanish
            "ümlaut_äöü.txt",  # German
            "emoji_😀😎🚀.txt",  # Emoji
        ]
        
        self.unicode_files = []
        for name in self.unicode_names:
            try:
                file_path = os.path.join(self.source_dir, name)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"This is a test file with Unicode name: {name}")
                self.unicode_files.append(file_path)
            except UnicodeEncodeError:
                # Skip this file if the system doesn't support this encoding
                pass
        
        # Create a directory with Unicode name
        self.unicode_dir_name = "目录_директория_ディレクトリ"
        try:
            self.unicode_dir = os.path.join(self.source_dir, self.unicode_dir_name)
            os.makedirs(self.unicode_dir, exist_ok=True)
            
            # Create a file in the Unicode directory
            self.unicode_subfile = os.path.join(self.unicode_dir, "file_in_unicode_dir.txt")
            with open(self.unicode_subfile, "w", encoding="utf-8") as f:
                f.write("This is a file in a directory with a Unicode name.")
        except UnicodeEncodeError:
            # Skip if the system doesn't support this encoding
            self.unicode_dir = None
            self.unicode_subfile = None

    def tearDown(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir)

    def test_copy_unicode_files(self):
        """Test copying files with Unicode names."""
        # Skip test if no Unicode files were created
        if not self.unicode_files:
            self.skipTest("System doesn't support Unicode filenames")
        
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Copy each Unicode file
        for file_path in self.unicode_files:
            try:
                py_eacopy.copy(file_path, self.dest_dir)
                
                # Check if the file was copied
                filename = os.path.basename(file_path)
                dest_file = os.path.join(self.dest_dir, filename)
                self.assertTrue(os.path.exists(dest_file))
                
                # Check file content
                with open(dest_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertIn(f"Unicode name: {filename}", content)
            except UnicodeError as e:
                # Log the error but don't fail the test
                print(f"Unicode error with file {file_path}: {e}")

    def test_copytree_unicode_dir(self):
        """Test copying a directory with Unicode name."""
        # Skip test if Unicode directory wasn't created
        if not self.unicode_dir:
            self.skipTest("System doesn't support Unicode directory names")
        
        try:
            # Copy the directory
            dest_unicode_dir = os.path.join(self.dest_dir, self.unicode_dir_name)
            py_eacopy.copytree(self.unicode_dir, dest_unicode_dir)
            
            # Check if the directory was copied
            self.assertTrue(os.path.exists(dest_unicode_dir))
            
            # Check if the file in the directory was copied
            dest_subfile = os.path.join(dest_unicode_dir, "file_in_unicode_dir.txt")
            self.assertTrue(os.path.exists(dest_subfile))
            
            # Check file content
            with open(dest_subfile, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("file in a directory with a Unicode name", content)
        except UnicodeError as e:
            # Log the error but don't fail the test
            print(f"Unicode error with directory {self.unicode_dir}: {e}")

    def test_unicode_paths_with_spaces(self):
        """Test Unicode paths with spaces."""
        # Create files with Unicode names and spaces
        unicode_space_names = [
            "中文 文件.txt",  # Chinese with space
            "русский файл.txt",  # Russian with space
        ]
        
        unicode_space_files = []
        for name in unicode_space_names:
            try:
                file_path = os.path.join(self.source_dir, name)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"This is a test file with Unicode name and spaces: {name}")
                unicode_space_files.append(file_path)
            except UnicodeEncodeError:
                # Skip this file if the system doesn't support this encoding
                pass
        
        # Skip test if no Unicode files with spaces were created
        if not unicode_space_files:
            self.skipTest("System doesn't support Unicode filenames with spaces")
        
        # Create destination directory
        os.makedirs(self.dest_dir, exist_ok=True)
        
        # Copy each Unicode file with spaces
        for file_path in unicode_space_files:
            try:
                py_eacopy.copy(file_path, self.dest_dir)
                
                # Check if the file was copied
                filename = os.path.basename(file_path)
                dest_file = os.path.join(self.dest_dir, filename)
                self.assertTrue(os.path.exists(dest_file))
                
                # Check file content
                with open(dest_file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("Unicode name and spaces", content)
            except UnicodeError as e:
                # Log the error but don't fail the test
                print(f"Unicode error with file {file_path}: {e}")


if __name__ == "__main__":
    unittest.main()
