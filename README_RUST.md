# py-eacopy (Rust Edition)

[![License](https://img.shields.io/badge/license-BSD--3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python Versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/py-eacopy/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/ruff-enabled-brightgreen)](https://github.com/astral-sh/ruff)

**⚠️ Work In Progress ⚠️**
This project is currently under active development and not yet ready for production use.

Python bindings for Electronic Arts' high-performance file copy tool EACopy. This package provides direct access to EACopy's C++ functionality for exceptional file copy performance.

## Features

- High-performance file copying with Rust bindings to EACopy C++ library
- API compatible with Python's `shutil` module
- Support for EACopyService for accelerated network file transfers
- Cross-platform compatibility (Windows native, with fallbacks for other platforms)
- Multi-threaded file operations
- Memory safety through Rust's ownership system

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

async def copy_files():
    # Copy files asynchronously
    await py_eacopy.async_copy("source.txt", "destination.txt")
    await py_eacopy.async_copytree("source_dir", "destination_dir")

# Run the async function
asyncio.run(copy_files())
```

#### Progress Tracking

```python
def progress_callback(copied_bytes, total_bytes, filename):
    percent = (copied_bytes / total_bytes) * 100 if total_bytes > 0 else 0
    print(f"Copying {filename}: {percent:.1f}% ({copied_bytes}/{total_bytes} bytes)")

# Set the global progress callback
py_eacopy.config.progress_callback = progress_callback
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/loonghao/py-eacopy.git
cd py-eacopy

# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install development dependencies
pip install -e ".[dev]"
```

### Building from Source

This project uses maturin to build the Rust extension:

```bash
# Install maturin
pip install maturin

# Build in development mode
maturin develop

# Build wheel
maturin build --release
```

Or using nox:

```bash
# Install nox
pip install nox

# Build in development mode
nox -s develop

# Build wheel
nox -s build-wheel
```

### Testing

```bash
# Run tests with nox
nox -s pytest

# Run linting
nox -s lint

# Fix linting issues
nox -s lint-fix
```

### Documentation

```bash
# Build documentation
nox -s docs

# Serve documentation with live reloading
nox -s docs-serve
```

## Architecture

This project uses a hybrid architecture:

1. **Rust Core**: The core functionality is implemented in Rust, which provides memory safety and performance.
2. **FFI to EACopy**: Rust uses FFI (Foreign Function Interface) to call the EACopy C++ library.
3. **PyO3 Bindings**: The Rust code is exposed to Python using PyO3, which generates Python extension modules.
4. **Python API**: A thin Python layer provides a user-friendly API that matches the original py-eacopy interface.

This architecture provides several benefits:

- **Simplified Build System**: Cargo handles dependency management and build configuration.
- **Improved Cross-Platform Support**: Cargo provides consistent behavior across platforms.
- **Enhanced Memory Safety**: Rust's ownership system prevents memory leaks and segmentation faults.
- **Standardized CI/CD**: GitHub Actions workflows are simplified.
- **Better Error Handling**: Rust's Result type provides robust error handling.

## License

This project is licensed under the BSD 3-Clause License - see the LICENSE file for details.

## Acknowledgments

- Electronic Arts for developing the EACopy tool
- The Rust and PyO3 communities for their excellent tools and documentation
