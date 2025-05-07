#!/usr/bin/env python
"""Example of using EACopy with a server for accelerated file copying."""

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
    """Main function to demonstrate EACopy with server."""
    print(f"Using py-eacopy version {eacopy.__version__}")
    print(f"EACopy version: {eacopy.__eacopy_version__}")
    
    # Note: This example assumes that an EACopyService is running on localhost
    # You would need to start the service separately before running this example
    server_addr = "localhost"
    server_port = 31337
    
    print(f"\nUsing EACopyService at {server_addr}:{server_port}")
    print("Note: This example requires an EACopyService to be running.")
    print("If the service is not running, this example will fail.")
    
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as dst_dir:
        src_dir_path = Path(src_dir)
        dst_dir_path = Path(dst_dir)
        
        # Create a test file
        test_file = src_dir_path / "test.txt"
        with open(test_file, "w") as f:
            f.write("This is a test file for EACopy with server.")
        
        # Create a subdirectory with files
        sub_dir = src_dir_path / "subdir"
        sub_dir.mkdir()
        for i in range(5):
            with open(sub_dir / f"file{i}.txt", "w") as f:
                f.write(f"This is file {i} in the subdirectory for server test.")
        
        try:
            # Copy a single file using the server
            print("\nCopying a single file using EACopyService...")
            dst_file = dst_dir_path / "test_copy.txt"
            eacopy.copy_with_server(str(test_file), str(dst_file), server_addr, server_port)
            print(f"File copied to {dst_file}")
            
            # Copy a directory tree using the server
            print("\nCopying a directory tree using EACopyService...")
            dst_subdir = dst_dir_path / "subdir_copy"
            eacopy.copy_with_server(str(sub_dir), str(dst_subdir), server_addr, server_port)
            print(f"Directory tree copied to {dst_subdir}")
            
            # List the copied files
            print("\nFiles in destination directory:")
            for path in dst_dir_path.glob("**/*"):
                if path.is_file():
                    print(f"  {path.relative_to(dst_dir_path)}")
            
            print("\nAll operations completed successfully!")
            return 0
        except Exception as e:
            print(f"\nError: {e}")
            print("\nMake sure EACopyService is running on the specified address and port.")
            return 1


if __name__ == "__main__":
    sys.exit(main())
