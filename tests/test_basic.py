"""Basic tests for py-eacopy using pytest features."""

# Import built-in modules
import os

# Import third-party modules
import pytest

# Import the package
import py_eacopy


# Mark this module as containing basic tests
pytestmark = pytest.mark.basic


def test_copyfile(test_file, dest_dir):
    """Test copyfile function."""
    dest_file = os.path.join(dest_dir, "test.txt")

    # Copy the file
    py_eacopy.copyfile(test_file, dest_file)

    # Check if the file was copied
    assert os.path.exists(dest_file)

    # Check file content
    with open(dest_file, "r") as f:
        content = f.read()
    assert content == "This is a test file."


def test_copy(test_file, dest_dir):
    """Test copy function."""
    # Copy the file
    py_eacopy.copy(test_file, dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, "test.txt")
    assert os.path.exists(dest_file)

    # Check file content
    with open(dest_file, "r") as f:
        content = f.read()
    assert content == "This is a test file."


def test_copy2(test_file, dest_dir):
    """Test copy2 function."""
    # Copy the file with metadata
    py_eacopy.copy2(test_file, dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, "test.txt")
    assert os.path.exists(dest_file)

    # Check file content
    with open(dest_file, "r") as f:
        content = f.read()
    assert content == "This is a test file."

    # Check if metadata was preserved (modification time)
    src_stat = os.stat(test_file)
    dst_stat = os.stat(dest_file)
    assert src_stat.st_mtime == pytest.approx(dst_stat.st_mtime, abs=1)  # Allow 1 second difference


def test_copytree(nested_dir_structure, dest_dir):
    """Test copytree function."""
    source_dir = nested_dir_structure["root"]

    # Copy the directory tree
    py_eacopy.copytree(source_dir, dest_dir)

    # Check if the directory was copied
    assert os.path.exists(dest_dir)

    # Check if the file was copied
    assert os.path.exists(os.path.join(dest_dir, "test.txt"))

    # Check if the subdirectory was copied
    dest_sub_dir = os.path.join(dest_dir, "subdir")
    assert os.path.exists(dest_sub_dir)

    # Check if the file in the subdirectory was copied
    dest_sub_file = os.path.join(dest_sub_dir, "subfile.txt")
    assert os.path.exists(dest_sub_file)

    # Check file content
    with open(dest_sub_file, "r") as f:
        content = f.read()
    assert content == "This is a file in a subdirectory."

    # Check if the deep directory was copied
    dest_deep_dir = os.path.join(dest_sub_dir, "deepdir")
    assert os.path.exists(dest_deep_dir)

    # Check if the file in the deep directory was copied
    dest_deep_file = os.path.join(dest_deep_dir, "deepfile.txt")
    assert os.path.exists(dest_deep_file)


@pytest.mark.parametrize("thread_count,compression_level", [
    (1, 0),    # Minimum values
    (4, 5),    # Medium values
    (8, 9),    # Maximum values
])
def test_eacopy_instance_with_params(test_files, dest_dir, thread_count, compression_level):
    """Test creating an EACopy instance with different parameters."""
    eac = py_eacopy.EACopy(
        thread_count=thread_count,
        compression_level=compression_level
    )

    # Copy a file
    eac.copy(test_files[0], dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, "file0.txt")
    assert os.path.exists(dest_file)

    # Clean up for next parametrized test
    if os.path.exists(dest_file):
        os.unlink(dest_file)


def test_context_manager(test_files, dest_dir):
    """Test using EACopy as a context manager."""
    with py_eacopy.EACopy() as eac:
        eac.copy(test_files[0], dest_dir)
        eac.copy2(test_files[1], dest_dir)

    # Check if the files were copied
    assert os.path.exists(os.path.join(dest_dir, "file0.txt"))
    assert os.path.exists(os.path.join(dest_dir, "file1.txt"))


def test_batch_operations(test_files, dest_dir):
    """Test batch operations."""
    # Create file pairs
    file_pairs = [(file, os.path.join(dest_dir, os.path.basename(file)))
                  for file in test_files[:3]]

    # Batch copy
    py_eacopy.batch_copy(file_pairs)

    # Check if all files were copied
    for _, dest in file_pairs:
        assert os.path.exists(dest)


@pytest.mark.parametrize("copy_func", [
    py_eacopy.copy,
    py_eacopy.copy2,
])
def test_copy_functions(test_file, dest_dir, copy_func):
    """Test different copy functions with the same test."""
    # Copy the file using the provided function
    copy_func(test_file, dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, "test.txt")
    assert os.path.exists(dest_file)

    # Check file content
    with open(dest_file, "r") as f:
        content = f.read()
    assert content == "This is a test file."

    # Clean up for next parametrized test
    if os.path.exists(dest_file):
        os.unlink(dest_file)


@pytest.mark.parametrize("file_type,expected_content", [
    ("text", "This is a test file."),
    ("binary", None),  # Binary content will be checked differently
])
def test_different_file_types(source_dir, dest_dir, file_type, expected_content):
    """Test copying different types of files."""
    # Create the appropriate file based on type
    if file_type == "text":
        src_file = os.path.join(source_dir, "text_file.txt")
        with open(src_file, "w") as f:
            f.write(expected_content)
    else:  # binary
        src_file = os.path.join(source_dir, "binary_file.dat")
        with open(src_file, "wb") as f:
            f.write(os.urandom(1024))  # 1KB of random binary data

    # Copy the file
    py_eacopy.copy(src_file, dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, os.path.basename(src_file))
    assert os.path.exists(dest_file)

    # Check content based on file type
    if file_type == "text":
        with open(dest_file, "r") as f:
            content = f.read()
        assert content == expected_content
    else:  # binary
        # For binary files, just check that the file sizes match
        assert os.path.getsize(src_file) == os.path.getsize(dest_file)
