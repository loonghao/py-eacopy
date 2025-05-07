#!/usr/bin/env python
"""Basic usage example for py-eacopy."""

# Import built-in modules
import os
import sys
import tempfile
from pathlib import Path

# Add the parent directory to sys.path to import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the package
import eacopy


def main():
    """Main function to demonstrate basic usage."""
    print(f"Using py-eacopy version {eacopy.__version__}")
    print(f"EACopy version: {eacopy.__eacopy_version__}")

    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as dst_dir:
        src_dir_path = Path(src_dir)
        dst_dir_path = Path(dst_dir)

        # Create a test file
        test_file = src_dir_path / "test.txt"
        with open(test_file, "w") as f:
            f.write("This is a test file for EACopy.")

        # Create a subdirectory with files
        sub_dir = src_dir_path / "subdir"
        sub_dir.mkdir()
        for i in range(5):
            with open(sub_dir / f"file{i}.txt", "w") as f:
                f.write(f"This is file {i} in the subdirectory.")

        # Copy a single file
        print("\nCopying a single file...")
        dst_file = dst_dir_path / "test_copy.txt"
        eacopy.copy(str(test_file), str(dst_file))
        print(f"File copied to {dst_file}")

        # Copy a file with metadata
        print("\nCopying a file with metadata...")
        dst_file2 = dst_dir_path / "test_copy2.txt"
        eacopy.copy2(str(test_file), str(dst_file2))
        print(f"File copied with metadata to {dst_file2}")

        # Copy a directory tree
        print("\nCopying a directory tree...")
        dst_subdir = dst_dir_path / "subdir_copy"
        eacopy.copytree(str(sub_dir), str(dst_subdir))
        print(f"Directory tree copied to {dst_subdir}")

        # List the copied files
        print("\nFiles in destination directory:")
        for path in dst_dir_path.glob("**/*"):
            if path.is_file():
                print(f"  {path.relative_to(dst_dir_path)}")

    print("\nAll operations completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
