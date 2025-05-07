#!/bin/bash
# Build script for py-eacopy on Linux and macOS

set -e

echo "Building wheels for py-eacopy..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3 or add it to your PATH."
    exit 1
fi

# Install build dependencies if needed
echo "Installing build dependencies..."
python3 -m pip install --upgrade pip wheel setuptools scikit-build-core pybind11 cmake ninja

# Create wheelhouse directory if it doesn't exist
mkdir -p wheelhouse

# Determine platform
PLATFORM="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
fi

# Try different build methods
echo
echo "Attempting to build with cibuildwheel..."
python3 -m pip install cibuildwheel
python3 -m cibuildwheel --platform $PLATFORM --output-dir wheelhouse

if [ $? -ne 0 ]; then
    echo "cibuildwheel failed, trying with pip wheel..."
    python3 -m pip wheel . -w wheelhouse --no-deps
fi

echo
echo "Build completed. Check the wheelhouse directory for the built wheels."
echo

# List the built wheels
echo "Built wheels:"
ls -la wheelhouse/*.whl

exit 0
