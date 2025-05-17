"""
Example demonstrating how to use py-eacopy with Unicode paths and callbacks.

This example shows:
1. How to copy files with Unicode characters in their paths
2. How to use progress callbacks to monitor copy operations
3. How to use the EACopy class with custom configuration
"""

import os
import sys
import tempfile
import time
from pathlib import Path

import py_eacopy


def progress_callback(copied_bytes, total_bytes, filename):
    """Progress callback function that displays a progress bar."""
    if total_bytes == 0:
        percent = 0
    else:
        percent = (copied_bytes / total_bytes) * 100
    
    # Create a simple progress bar
    bar_length = 40
    filled_length = int(bar_length * copied_bytes // total_bytes)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    # Print the progress bar
    print(f'\r{os.path.basename(filename)}: |{bar}| {percent:.1f}% ({copied_bytes}/{total_bytes} bytes)', end='')
    
    # Print a newline when complete
    if copied_bytes == total_bytes:
        print()


def main():
    """Main function demonstrating Unicode path handling and callbacks."""
    # Set the global progress callback
    py_eacopy.config.progress_callback = progress_callback
    
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = os.path.join(temp_dir, "source")
        dest_dir = os.path.join(temp_dir, "destination")
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Create files with Unicode names
        unicode_files = [
            "unicode_测试_тест_テスト.txt",  # Mixed scripts
            "中文文件.txt",                 # Chinese
            "русский файл.txt",            # Russian
            "日本語ファイル.txt",            # Japanese
            "한국어 파일.txt",              # Korean
            "ملف عربي.txt",                # Arabic
            "αρχείο.txt",                 # Greek
            "file with spaces and 特殊字符.txt"  # Mixed with spaces
        ]
        
        # Create the files with content
        created_files = []
        for i, filename in enumerate(unicode_files):
            try:
                file_path = os.path.join(source_dir, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    # Write 100KB of data to make the progress visible
                    f.write(f"This is file {i+1} with Unicode name.\n" * 5000)
                created_files.append(file_path)
                print(f"Created: {filename}")
            except Exception as e:
                print(f"Error creating {filename}: {e}")
        
        # Create a subdirectory with Unicode name
        unicode_dir = os.path.join(source_dir, "目录_директория_ディレクトリ")
        os.makedirs(unicode_dir, exist_ok=True)
        
        # Create a file in the Unicode directory
        unicode_dir_file = os.path.join(unicode_dir, "file_in_unicode_dir.txt")
        with open(unicode_dir_file, "w", encoding="utf-8") as f:
            f.write("This is a file in a directory with Unicode name.\n" * 1000)
        
        print("\n--- Copying individual files ---")
        for file_path in created_files:
            try:
                # Copy each file individually
                py_eacopy.copy(file_path, dest_dir)
                time.sleep(0.5)  # Small delay to see each progress bar
            except Exception as e:
                print(f"Error copying {file_path}: {e}")
        
        print("\n--- Copying directory with Unicode name ---")
        try:
            # Copy the Unicode directory
            unicode_dest_dir = os.path.join(dest_dir, os.path.basename(unicode_dir))
            py_eacopy.copytree(unicode_dir, unicode_dest_dir)
        except Exception as e:
            print(f"Error copying directory: {e}")
        
        print("\n--- Using EACopy class with custom configuration ---")
        # Create an EACopy instance with custom configuration
        eac = py_eacopy.EACopy(
            thread_count=8,
            compression_level=5,
            buffer_size=4 * 1024 * 1024,  # 4MB buffer
            preserve_metadata=True,
            progress_callback=progress_callback
        )
        
        # Use the instance to copy files
        for file_path in created_files[:3]:  # Copy first 3 files
            try:
                eac.copy2(file_path, dest_dir)
                time.sleep(0.5)  # Small delay
            except Exception as e:
                print(f"Error copying with EACopy instance: {e}")
        
        # Verify the copied files
        print("\n--- Verifying copied files ---")
        for file_path in created_files:
            src_file = file_path
            dst_file = os.path.join(dest_dir, os.path.basename(file_path))
            
            if os.path.exists(dst_file):
                src_size = os.path.getsize(src_file)
                dst_size = os.path.getsize(dst_file)
                print(f"✓ {os.path.basename(file_path)}: {dst_size} bytes (expected: {src_size} bytes)")
            else:
                print(f"✗ {os.path.basename(file_path)}: File not found!")


if __name__ == "__main__":
    main()
