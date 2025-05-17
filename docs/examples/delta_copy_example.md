# Delta Copy Examples

This document provides examples of using the delta copy functionality in py-eacopy.

## What is Delta Copy?

Delta copy is a technique for efficiently copying files by only transferring the differences (deltas) between a source file and a reference file. This can significantly reduce the amount of data transferred when copying files that are similar to existing files.

## Basic Delta Copy

Here's a basic example of using delta copy:

```python
import py_eacopy

# Perform delta copy using a reference file
py_eacopy.delta_copy(
    "source_file.txt",      # Source file
    "destination_file.txt", # Destination file
    "reference_file.txt"    # Reference file
)
```

In this example:
- `source_file.txt` is the file you want to copy
- `destination_file.txt` is where you want to copy the file to
- `reference_file.txt` is a file that is similar to the source file

The delta copy algorithm will:
1. Compare the source file to the reference file
2. Identify the differences (deltas)
3. Create the destination file by applying the deltas to the reference file

## Using Delta Copy with EACopy Class

You can also use delta copy with the EACopy class:

```python
import py_eacopy

# Create an EACopy instance
eac = py_eacopy.EACopy(
    thread_count=8,
    compression_level=5,
    buffer_size=16 * 1024 * 1024
)

# Perform delta copy
eac.delta_copy(
    "source_file.txt",
    "destination_file.txt",
    "reference_file.txt"
)
```

## Asynchronous Delta Copy

You can use delta copy with asynchronous operations:

```python
import asyncio
import py_eacopy

async def delta_copy_async():
    # Perform delta copy asynchronously
    await py_eacopy.async_delta_copy(
        "source_file.txt",
        "destination_file.txt",
        "reference_file.txt"
    )

# Run the async function
asyncio.run(delta_copy_async())
```

## Practical Use Cases

### 1. Incremental Backups

Delta copy is ideal for incremental backups where most of the data remains unchanged between backup cycles:

```python
import py_eacopy
import os
from datetime import datetime

def incremental_backup(source_dir, backup_dir):
    # Get the latest backup as reference
    backups = sorted([d for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d))])
    
    # Create a new backup directory
    current_backup = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_backup_dir = os.path.join(backup_dir, current_backup)
    os.makedirs(current_backup_dir)
    
    if backups:
        # Use the latest backup as reference
        reference_dir = os.path.join(backup_dir, backups[-1])
        
        # Copy files using delta copy
        for root, dirs, files in os.walk(source_dir):
            rel_path = os.path.relpath(root, source_dir)
            dest_dir = os.path.join(current_backup_dir, rel_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            for file in files:
                source_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, file)
                reference_file = os.path.join(reference_dir, rel_path, file)
                
                if os.path.exists(reference_file):
                    # Use delta copy if reference file exists
                    py_eacopy.delta_copy(source_file, dest_file, reference_file)
                else:
                    # Use regular copy if reference file doesn't exist
                    py_eacopy.copy2(source_file, dest_file)
    else:
        # First backup, use regular copy
        py_eacopy.copytree(source_dir, current_backup_dir)
    
    return current_backup_dir

# Example usage
incremental_backup("my_documents", "backups")
```

### 2. Software Updates

Delta copy can be used to efficiently distribute software updates:

```python
import py_eacopy
import os

def apply_update(update_file, installed_version, output_dir):
    """Apply a software update using delta copy."""
    # Extract the update file
    # ...
    
    # Apply delta updates to each file
    for file in os.listdir(update_file):
        source_file = os.path.join(update_file, file)
        dest_file = os.path.join(output_dir, file)
        reference_file = os.path.join(installed_version, file)
        
        if os.path.exists(reference_file):
            # Use delta copy if the file exists in the installed version
            py_eacopy.delta_copy(source_file, dest_file, reference_file)
        else:
            # Use regular copy for new files
            py_eacopy.copy2(source_file, dest_file)
    
    return output_dir

# Example usage
apply_update("update_package", "installed_software", "updated_software")
```

## Performance Considerations

- **File Similarity**: Delta copy is most effective when the source and reference files are similar. If the files are very different, delta copy may be slower than a regular copy.
- **File Size**: Delta copy works best with large files where the differences are small relative to the file size.
- **Compression Level**: The `compression_level` parameter affects the compression of the delta data. Higher values provide better compression but use more CPU.
- **Reference File Selection**: Choose a reference file that is as similar as possible to the source file for best performance.

## Limitations

- **Binary Files**: Delta copy works with any file type, but is most effective with text files or structured binary files where changes are localized.
- **Very Large Files**: For extremely large files (multiple GB), consider splitting the file into smaller chunks for more efficient delta copying.
- **Memory Usage**: Delta copy requires enough memory to hold the delta information, which can be significant for large files with many differences.
