# Import built-in modules
import os

# Import third-party modules
import nox

# Import local modules
from nox_actions.utils import MODULE_NAME, retry_command


def pytest(session: nox.Session) -> None:
    """Run tests."""
    session.install("pytest", "pytest-cov")
    session.install("-e", ".")
    session.run(
        "pytest",
        "tests/",
        f"--cov={MODULE_NAME}",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing"
    )


def basic_test(session: nox.Session) -> None:
    """Run a basic test to verify that the package structure is valid."""
    # Check if the package directory exists
    import os

    package_dir = os.path.join("src", MODULE_NAME)
    if not os.path.exists(package_dir):
        session.error(f"Package directory {package_dir} does not exist")

    # Check if __init__.py exists
    init_file = os.path.join(package_dir, "__init__.py")
    if not os.path.exists(init_file):
        session.error(f"__init__.py file not found in {package_dir}")

    # Check if setup.py or pyproject.toml exists
    if not os.path.exists("pyproject.toml"):
        session.error("pyproject.toml file not found")

    session.log("Basic structure test passed!")
    session.log(f"Package directory: {package_dir}")
    session.log(f"Init file: {init_file}")
    session.log("pyproject.toml: Found")


def build_test(session: nox.Session) -> None:
    """Build the project and run unit tests."""
    # Install build dependencies
    retry_command(session, session.install, "-e", ".[build,test]", max_retries=3)

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

    # Build the package
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

    # Run tests
    session.run(
        "pytest",
        "tests/",
        f"--cov={MODULE_NAME}",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing"
    )


def build_no_test(session: nox.Session) -> None:
    """Build the project without running tests (for faster development)."""
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

    # Build the package
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

    session.log("Build completed successfully!")


def coverage(session: nox.Session) -> None:
    """Generate code coverage reports for CI."""
    # Install dependencies
    retry_command(session, session.install, "-e", ".[test]", max_retries=3)
    retry_command(session, session.install, "coverage[toml]", "pytest", "pytest-cov", max_retries=3)

    # Run tests with coverage
    session.run(
        "pytest",
        "tests/",
        f"--cov={MODULE_NAME}",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing"
    )

    # Generate HTML report
    session.run("coverage", "html")
    session.log("Coverage report generated in htmlcov/index.html")
