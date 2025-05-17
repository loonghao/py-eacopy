# py-eacopy

<div align="center">

[![PyPI version](https://badge.fury.io/py/py-eacopy.svg)](https://badge.fury.io/py/py-eacopy)
[![Build Status](https://github.com/loonghao/py-eacopy/workflows/Build%20and%20Release/badge.svg)](https://github.com/loonghao/py-eacopy/actions)
[![Documentation Status](https://readthedocs.org/projects/py-eacopy/badge/?version=latest)](https://py-eacopy.readthedocs.io/en/latest/?badge=latest)
[![Python Version](https://img.shields.io/pypi/pyversions/py-eacopy.svg)](https://pypi.org/project/py-eacopy/)
[![License](https://img.shields.io/github/license/loonghao/py-eacopy.svg)](https://github.com/loonghao/py-eacopy/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/badge/py-eacopy)](https://pepy.tech/project/py-eacopy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/ruff-enabled-brightgreen)](https://github.com/astral-sh/ruff)

**⚠️ WORK IN PROGRESS ⚠️**
This project is currently under active development and not yet ready for production use.

</div>

Python bindings for EACopy, a high-performance file copy tool developed by Electronic Arts. This package provides direct access to EACopy's C++ functionality, offering superior performance for file copying operations.

## Features

- High-performance file copying with direct C++ bindings
- API compatible with Python's `shutil` module
- Support for EACopyService for accelerated network file transfers
- Cross-platform compatibility (Windows native, with fallbacks for other platforms)
- Multi-threaded file operations

## Installation

```bash
pip install py-eacopy
```

Or with Poetry:

```bash
poetry add py-eacopy
```

## Usage

### Basic Usage

```python
import py_eacopy

# Copy a file (similar to shutil.copy)
py_eacopy.copy("source.txt", "destination.txt")

# Copy a file with metadata (similar to shutil.copy2)
py_eacopy.copy2("source.txt", "destination.txt")

# Copy a directory tree (similar to shutil.copytree)
py_eacopy.copytree("source_dir", "destination_dir")

# Use EACopyService for accelerated network transfers
py_eacopy.copy_with_server("source_dir", "destination_dir", "server_address", port=31337)

# Configure global settings
py_eacopy.config.thread_count = 8  # Use 8 threads for copying
py_eacopy.config.compression_level = 5  # Use compression level 5 for network transfers
```

### Advanced Usage

#### Using the EACopy Class

```python
from py_eacopy import EACopy

# Create an EACopy instance with custom configuration
eac = EACopy(
    thread_count=8,
    compression_level=5,
    buffer_size=16 * 1024 * 1024,  # 16MB buffer
    preserve_metadata=True,
    follow_symlinks=True,
    dirs_exist_ok=True
)

# Use the instance for copying
eac.copy("source.txt", "destination.txt")
eac.copytree("source_dir", "destination_dir")
```

#### Using as a Context Manager

```python
with py_eacopy.EACopy() as eac:
    eac.copy("source1.txt", "destination1.txt")
    eac.copy("source2.txt", "destination2.txt")
    eac.copytree("source_dir", "destination_dir")
```

#### Batch Operations

```python
# Batch copy multiple files
py_eacopy.batch_copy([
    ("source1.txt", "destination1.txt"),
    ("source2.txt", "destination2.txt"),
    ("source3.txt", "destination3.txt"),
])

# Batch copy multiple directories
py_eacopy.batch_copytree([
    ("source_dir1", "destination_dir1"),
    ("source_dir2", "destination_dir2"),
])
```

#### Asynchronous Operations

```python
import asyncio
import py_eacopy

async def copy_files():
    # Copy files asynchronously
    await py_eacopy.async_copy("source.txt", "destination.txt")

    # Copy multiple files in parallel
    tasks = [
        py_eacopy.async_copy(f"source{i}.txt", f"destination{i}.txt")
        for i in range(10)
    ]
    await asyncio.gather(*tasks)

# Run the async function
asyncio.run(copy_files())
```

#### Advanced Configuration

```python
from py_eacopy import ErrorStrategy, LogLevel

# Configure error handling
py_eacopy.config.error_strategy = ErrorStrategy.RETRY
py_eacopy.config.retry_count = 3
py_eacopy.config.retry_delay = 1.0  # seconds

# Configure logging
py_eacopy.config.log_level = LogLevel.INFO

# Define a progress callback
def progress_callback(copied_bytes, total_bytes, filename):
    percent = (copied_bytes / total_bytes) * 100 if total_bytes > 0 else 0
    print(f"Copying {filename}: {percent:.1f}% ({copied_bytes}/{total_bytes} bytes)")

py_eacopy.config.progress_callback = progress_callback
```

## Development

### Setup

```bash
# Clone the repository with submodules
git clone https://github.com/loonghao/py-eacopy.git
cd py-eacopy
git submodule update --init --recursive

# Install dependencies with Poetry
poetry install
```

### Building from Source

This project uses nox to standardize the build process across local development and CI environments:

#### Using CPM.cmake (Recommended)

CPM.cmake is now the recommended way to build py-eacopy, as it simplifies dependency management:

```bash
# Install nox
pip install nox

# Build with CPM.cmake
nox -s build-cpm

# Build and test with CPM.cmake
nox -s build-test-cpm

# Build wheels with CPM.cmake
nox -s build-wheels-cpm
```

For faster builds, you can set the CPM cache directory to avoid re-downloading dependencies:

```bash
# Windows
set CPM_SOURCE_CACHE=C:/Users/username/.cache/CPM

# Linux/macOS
export CPM_SOURCE_CACHE=~/.cache/CPM
```

See the [CPM.cmake Build Guide](docs/cpm_build_guide.md) for more details.

#### Legacy Build Methods

The following build methods are still supported but are being phased out:

```bash
# Standard build
nox -s build

# Fast development build
nox -s fast-build

# Build using static library
nox -s build-static

# Build wheels for distribution
nox -s build-wheels

# Build with vcpkg
nox -s build-vcpkg
```

You can also use the following environment variables to customize the build:

```bash
# Set number of parallel build jobs
export CMAKE_BUILD_PARALLEL_LEVEL=8

# Enable parallel compilation with MSVC (Windows only)
set CL=/MP
```

### Testing

```bash
# Run tests with nox
nox -s pytest

# Run linting
nox -s lint

# Fix linting issues
nox -s lint_fix
```

### Documentation

```bash
# Build documentation
nox -s docs

# Serve documentation with live reloading
nox -s docs-serve
```

## Dependencies

This project now uses CPM.cmake for dependency management, which simplifies the build process and eliminates the need for Git submodules.

### Managed Dependencies

CPM.cmake automatically manages the following dependencies:

- **EACopy**: The main dependency, automatically downloaded from our fork.
- **pybind11**: Used for creating Python bindings.
- **Boost**: Used for file system operations and signal handling.
- **utf8cpp**: Used for UTF-8 encoding handling.
- **zstd**: Used for data compression.
- **xz/lzma**: Used for LZMA compression.
- **xdelta**: Used for incremental copying.

### Legacy Dependency Structure (Being Phased Out)

The following Git submodule structure is still supported but is being phased out:

- `extern/EACopy`: Our fork of EACopy
- `extern/xdelta`: Official xdelta repository
- `extern/zstd`: Official zstd repository
- `extern/xz`: Official xz-utils (lzma) repository

## License

BSD-3-Clause (same as EACopy)

## CI/CD Configuration

This project uses GitHub Actions for CI/CD with the following workflows:

- **Build and Test**: Tests the package on multiple Python versions and operating systems using CPM.cmake and nox.
- **Release**: Builds and publishes wheels to PyPI when a new release is created.
- **Documentation**: Builds and deploys documentation to GitHub Pages.

The CI/CD pipeline uses the same nox-based build process as local development, ensuring consistency between development and production environments. When a tag is pushed, the workflow automatically builds wheels for all supported platforms and Python versions, then uploads them to PyPI.

The CI configuration has been simplified to use CPM.cmake for dependency management, eliminating the need for Git submodules and complex dependency setup steps.

### Release Process

To create a new release:

1. Update the version in `pyproject.toml` and `src/py_eacopy/__version__.py`
2. Update the `CHANGELOG.md` with the new version and changes
3. Commit and push the changes
4. Create a new tag with the version number (e.g., `0.1.0`)
5. Push the tag to GitHub

```bash
# Example release process
git add pyproject.toml src/py_eacopy/__version__.py CHANGELOG.md
git commit -m "Release 0.1.0"
git tag 0.1.0
git push && git push --tags
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
