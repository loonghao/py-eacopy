# Import built-in modules
import os
import sys

# Import third-party modules
import nox

# Configure nox
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_missing_interpreters = False
# Enable pip cache to speed up dependency installation
os.environ["PIP_NO_CACHE_DIR"] = "0"

ROOT = os.path.dirname(__file__)

# Ensure py_eacopy is importable.
if ROOT not in sys.path:
    sys.path.append(ROOT)

# Import local modules
from nox_actions import build, codetest, docs, lint  # noqa: E402


def custom_build(session: nox.Session) -> None:
    """Custom build for development with toolchain file."""
    # Get the toolchain file path from environment
    toolchain_file = os.environ.get("CMAKE_TOOLCHAIN_FILE", "")
    if not toolchain_file:
        session.log("Warning: CMAKE_TOOLCHAIN_FILE not set, using default build")
        build.install(session)
        return

    session.log(f"Using custom toolchain file: {toolchain_file}")

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
        # Set toolchain file
        "CMAKE_TOOLCHAIN_FILE": toolchain_file,
    }

    # Install build dependencies
    session.install(
        "wheel",
        "setuptools>=42.0.0",
        "setuptools_scm>=8.0.0",
        "scikit-build-core>=0.5.0",
        "pybind11>=2.10.0",
        "cmake>=3.15.0",
    )

    # Clean build directory if it exists
    if os.path.exists("_skbuild"):
        session.log("Cleaning previous build directory...")
        import shutil
        shutil.rmtree("_skbuild")

    # Build in development mode with custom toolchain
    session.log("Building in development mode with custom toolchain...")

    config_settings = [
        "--config-settings=cmake.define.CMAKE_BUILD_TYPE=Release",
        "--config-settings=cmake.define.ZSTD_BUILD_PROGRAMS=OFF",
        "--config-settings=cmake.define.ZSTD_BUILD_SHARED=OFF",
        "--config-settings=cmake.define.ZSTD_BUILD_TESTS=OFF",
        "--config-settings=cmake.define.ZSTD_STATIC_LINKING_ONLY=ON",
        f"--config-settings=cmake.define.CMAKE_TOOLCHAIN_FILE={toolchain_file}",
    ]

    session.run(
        "pip",
        "install",
        "-e",
        ".",
        *config_settings,
        env=env,
    )

    session.log("Custom build completed successfully!")
    session.log("You can now import the package in Python: import eacopy")


# Define a session for running tests without reinstalling the package
def pytest_skip_install(session: nox.Session) -> None:
    """Run tests without reinstalling the package.

    This is useful for CI where we've already installed the wheel.
    """
    session.install("pytest", "pytest-cov")
    session.run("pytest", "tests", "--cov=py_eacopy", "--cov-report=term", "--cov-report=xml")


# Register nox sessions
nox.session(lint.lint, name="lint", reuse_venv=True)
nox.session(lint.lint_fix, name="lint-fix", reuse_venv=True)
nox.session(codetest.pytest, name="pytest")
nox.session(codetest.basic_test, name="basic-test")
nox.session(docs.docs, name="docs")
nox.session(docs.docs_serve, name="docs-serve")
nox.session(build.build, name="build")
nox.session(build.build_wheels, name="build-wheels")
nox.session(build.build_with_static_lib, name="build-static")  # Added: Build using static library
nox.session(build.verify_wheels, name="verify-wheels")
nox.session(build.clean, name="clean")
nox.session(codetest.build_test, name="build-test")
nox.session(codetest.build_no_test, name="build-no-test")
nox.session(codetest.coverage, name="coverage")
nox.session(build.install, name="fast-build")
nox.session(custom_build, name="custom-build")
nox.session(pytest_skip_install, name="pytest_skip_install")
