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

This project uses scikit-build-core to build the C++ extensions:

```bash
# Install build dependencies
pip install scikit-build-core pybind11 cmake

# Build the package
python -m pip install -e .
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

This project uses a hybrid approach for dependency management:

1. **EACopy**: The main dependency is managed as a Git submodule pointing to our fork of EACopy.
2. **Third-party libraries**: Critical dependencies like xdelta, zstd, and lzma are managed as separate Git submodules pointing to their official repositories.

### Dependency Structure

- `extern/EACopy`: Our fork of EACopy
- `extern/xdelta`: Official xdelta repository
- `extern/zstd`: Official zstd repository
- `extern/xz`: Official xz-utils (lzma) repository

Other dependencies:
- [pybind11](https://github.com/pybind/pybind11) - C++11 Python bindings

## License

BSD-3-Clause (same as EACopy)

## CI/CD Configuration

This project uses GitHub Actions for CI/CD with the following workflows:

- **Build and Test**: Tests the package on multiple Python versions and operating systems.
- **Release**: Builds and publishes wheels to PyPI when a new release is created.
- **Documentation**: Builds and deploys documentation to GitHub Pages.

The release workflow uses cibuildwheel to build platform-specific wheels with the C++ extensions properly compiled for each platform.

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
