@echo off
REM Build script for py-eacopy on Windows

echo Building wheels for py-eacopy...
echo.

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found in PATH. Please install Python or add it to your PATH.
    exit /b 1
)

REM Install build dependencies if needed
echo Installing build dependencies...
python -m pip install --upgrade pip wheel setuptools scikit-build-core pybind11 cmake ninja

REM Create wheelhouse directory if it doesn't exist
if not exist wheelhouse mkdir wheelhouse

REM Try different build methods
echo.
echo Attempting to build with cibuildwheel...
python -m pip install cibuildwheel
python -m cibuildwheel --platform windows --output-dir wheelhouse

if %ERRORLEVEL% NEQ 0 (
    echo cibuildwheel failed, trying with pip wheel...
    python -m pip wheel . -w wheelhouse --no-deps
)

echo.
echo Build completed. Check the wheelhouse directory for the built wheels.
echo.

REM List the built wheels
echo Built wheels:
dir /b wheelhouse\*.whl

exit /b 0
