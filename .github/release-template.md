# py-eacopy $RELEASE_VERSION

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

## 🚀 What's New

$CHANGES

For detailed release notes, see the [CHANGELOG.md](https://github.com/loonghao/py-eacopy/blob/main/CHANGELOG.md).

## 📦 Installation

### Using pip

```bash
pip install py-eacopy==$RELEASE_VERSION
```

### Using Poetry

```bash
poetry add py-eacopy==$RELEASE_VERSION
```

### From source

```bash
git clone https://github.com/loonghao/py-eacopy.git
cd py-eacopy
git checkout v$RELEASE_VERSION
git submodule update --init --recursive
pip install -e .
```

## 💻 Supported Platforms

- Windows (native support)
- Linux (fallback implementation)
- macOS (fallback implementation)

## 🐍 Python Compatibility

- Python 3.8+

## ✨ Key Features

- High-performance file copying with direct C++ bindings
- API compatible with Python's `shutil` module
- Support for EACopyService for accelerated network file transfers
- Multi-threaded file operations

## 📚 Documentation

For detailed documentation, visit [https://py-eacopy.readthedocs.io/](https://py-eacopy.readthedocs.io/)
