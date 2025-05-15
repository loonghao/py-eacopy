# Import built-in modules
import os
import platform
import shutil
import time

# Import third-party modules
import nox

# Import local modules
from nox_actions.utils import MODULE_NAME, THIS_ROOT, build_cpp_extension, retry_command


def build(session: nox.Session) -> None:
    """Build the package using scikit-build-core."""
    # Install build dependencies with pip cache
    start_time = time.time()
    retry_command(session, session.install, "-e", ".[build]", max_retries=3)
    retry_command(session, session.install, "-e", ".", max_retries=3)
    session.log(f"Dependencies installed in {time.time() - start_time:.2f}s")

    # Clean previous build files
    clean_dirs = ["build", "dist", "_skbuild", f"{MODULE_NAME}.egg-info"]
    for dir_name in clean_dirs:
        dir_path = os.path.join(THIS_ROOT, dir_name)
        if os.path.exists(dir_path):
            session.log(f"Cleaning {dir_path}")
            shutil.rmtree(dir_path)

    # Build the package
    build_cpp_extension(session)


def install(session: nox.Session) -> None:
    """Install the package in development mode."""
    # Install build dependencies
    retry_command(session, session.install, "-e", ".[build]", max_retries=3)
    
    # Set environment variables for faster builds
    env = {
        # Enable parallel build with CMake
        "CMAKE_BUILD_PARALLEL_LEVEL": str(os.cpu_count() or 4),
        # Enable parallel compilation with MSVC
        "CL": "/MP",
        # Configure zstd options
        "ZSTD_BUILD_PROGRAMS": "OFF",
        "ZSTD_BUILD_SHARED": "OFF",
        "ZSTD_BUILD_TESTS": "OFF",
        "ZSTD_STATIC_LINKING_ONLY": "ON",
        # Configure EACopy options
        "EACOPY_BUILD_AS_LIBRARY": "ON",
        "EACOPY_INSTALL": "ON",
    }

    # Clean build directory if it exists
    if os.path.exists("_skbuild"):
        session.log("Cleaning previous build directory...")
        shutil.rmtree("_skbuild")

    # Build in development mode with optimizations
    session.log("Building in development mode with optimizations...")
    session.run(
        "pip",
        "install",
        "-e",
        ".",
        "--config-settings=cmake.define.CMAKE_BUILD_TYPE=Release",
        "--config-settings=cmake.define.ZSTD_BUILD_PROGRAMS=OFF",
        "--config-settings=cmake.define.ZSTD_BUILD_SHARED=OFF",
        "--config-settings=cmake.define.ZSTD_BUILD_TESTS=OFF",
        "--config-settings=cmake.define.ZSTD_STATIC_LINKING_ONLY=ON",
        "--config-settings=cmake.define.EACOPY_BUILD_AS_LIBRARY=ON",
        "--config-settings=cmake.define.EACOPY_INSTALL=ON",
        env=env,
    )

    session.log("Installation completed successfully!")
    session.log(f"You can now import the package in Python: import {MODULE_NAME}")


def build_wheels(session: nox.Session) -> None:
    """Build wheels for the current platform using cibuildwheel.

    This function uses cibuildwheel to build wheels for the current platform.
    Configuration is read from .cibuildwheel.toml.
    """
    # Install cibuildwheel and dependencies
    session.log("Installing cibuildwheel and dependencies...")
    retry_command(
        session,
        session.install,
        "cibuildwheel",
        "wheel",
        "setuptools>=42.0.0",
        "setuptools_scm>=8.0.0",
        "scikit-build-core>=0.5.0",
        "pybind11>=2.10.0",
        "cmake>=3.15.0",
        "ninja",
        max_retries=3,
    )

    # Create output directory if it doesn't exist
    os.makedirs("wheelhouse", exist_ok=True)

    # Determine current platform for cibuildwheel
    system = platform.system().lower()
    if system == "linux":
        current_platform = "linux"
    elif system == "darwin":
        current_platform = "macos"
    elif system == "windows":
        current_platform = "windows"
    else:
        session.error(f"Unsupported platform: {system}")

    # Set environment variables
    env = {
        "CIBW_BUILD_VERBOSITY": "3",
        # Limit to Python 3.8-3.12, exclude 3.13 which has compatibility issues with pybind11
        "CIBW_BUILD": "cp38-* cp39-* cp310-* cp311-* cp312-*",
        "CIBW_SKIP": "cp313-*",  # Explicitly skip Python 3.13
        # Enable parallel build with CMake
        "CMAKE_BUILD_PARALLEL_LEVEL": str(os.cpu_count() or 4),
        # Enable parallel compilation with MSVC
        "CL": "/MP",
        # Configure zstd options
        "ZSTD_BUILD_PROGRAMS": "OFF",
        "ZSTD_BUILD_SHARED": "OFF",
        "ZSTD_BUILD_TESTS": "OFF",
        "ZSTD_STATIC_LINKING_ONLY": "ON",
        # Configure EACopy options
        "EACOPY_BUILD_AS_LIBRARY": "ON",
        "EACOPY_INSTALL": "ON",
    }

    # On Windows, we need special handling
    if current_platform == "windows":
        session.log("Building wheels on Windows...")
        
        # Use cibuildwheel directly with environment variables
        try:
            session.run(
                "python",
                "-m",
                "cibuildwheel",
                "--platform",
                current_platform,
                "--output-dir",
                "wheelhouse",
                env=env,
            )
        except Exception as e:
            session.log(f"cibuildwheel failed: {e}")
            session.log("Falling back to pip wheel...")

            # Try direct pip wheel as a fallback
            session.run(
                "pip",
                "wheel",
                ".",
                "-w",
                "wheelhouse",
                "--no-deps",
                "-v",
                "--config-settings=cmake.define.EACOPY_BUILD_AS_LIBRARY=ON",
                "--config-settings=cmake.define.EACOPY_INSTALL=ON",
            )
    else:
        # On other platforms, use cibuildwheel
        session.log(f"Building wheels on {current_platform}...")
        try:
            session.run(
                "python",
                "-m",
                "cibuildwheel",
                "--platform",
                current_platform,
                "--output-dir",
                "wheelhouse",
                env=env,
            )
        except Exception as e:
            session.log(f"cibuildwheel failed: {e}")
            session.log("Falling back to pip wheel...")

            # Try direct pip wheel as a fallback
            session.run(
                "pip",
                "wheel",
                ".",
                "-w",
                "wheelhouse",
                "--no-deps",
                "-v",
                "--config-settings=cmake.define.EACOPY_BUILD_AS_LIBRARY=ON",
                "--config-settings=cmake.define.EACOPY_INSTALL=ON",
            )

    # List the built wheels
    session.log("Built wheels:")
    for wheel in os.listdir("wheelhouse"):
        if wheel.endswith(".whl"):
            session.log(f"  - {wheel}")


def verify_wheels(session: nox.Session) -> None:
    """Verify the built wheels."""
    session.install("wheel", "setuptools")

    # Check if wheelhouse directory exists
    if not os.path.exists("wheelhouse"):
        session.error("No wheelhouse directory found. Run build_wheels first.")

    # List and verify wheels
    wheels = [f for f in os.listdir("wheelhouse") if f.endswith(".whl")]
    if not wheels:
        session.error("No wheels found in wheelhouse directory.")

    session.log(f"Found {len(wheels)} wheels:")
    for wheel in wheels:
        session.log(f"  - {wheel}")

        # Try to install the wheel
        try:
            with session.chdir("wheelhouse"):
                session.run("pip", "install", wheel, "--force-reinstall")
            session.log(f"Successfully installed {wheel}")
        except Exception as e:
            session.error(f"Failed to install {wheel}: {e}")

    # Try to import the package
    session.run("python", "-c", f"import {MODULE_NAME}; print(f'{MODULE_NAME} version: ' + {MODULE_NAME}.__version__)")
    session.log("All wheels verified successfully!")


def clean(session: nox.Session) -> None:
    """Clean build artifacts."""
    dirs_to_clean = [
        "build",
        "dist",
        f"{MODULE_NAME}.egg-info",
        "_skbuild",
        ".pytest_cache",
        "wheelhouse",
    ]
    for dir_name in dirs_to_clean:
        dir_path = os.path.join(THIS_ROOT, dir_name)
        if os.path.exists(dir_path):
            session.log(f"Removing {dir_path}")
            shutil.rmtree(dir_path)

    # Also clean __pycache__ directories
    for root, dirs, _ in os.walk(THIS_ROOT):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_dir = os.path.join(root, dir_name)
                session.log(f"Removing {cache_dir}")
                shutil.rmtree(cache_dir)
