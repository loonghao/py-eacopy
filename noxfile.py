# Import built-in modules
import os
import sys
import shutil
import glob
from pathlib import Path

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

# Define constants
MODULE_NAME = "py_eacopy"
WHEELHOUSE_DIR = os.path.join(ROOT, "@wheelhouse")

# Helper functions
def get_latest_wheel():
    """Get the latest wheel file from the wheelhouse directory."""
    wheel_files = glob.glob(os.path.join(WHEELHOUSE_DIR, "*.whl"))
    if not wheel_files:
        raise FileNotFoundError(f"No wheel files found in {WHEELHOUSE_DIR}")
    return sorted(wheel_files, key=os.path.getmtime)[-1]

def retry_command(session, func, *args, max_retries=3, **kwargs):
    """Retry a command multiple times."""
    for i in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if i == max_retries - 1:
                raise
            session.log(f"Command failed, retrying ({i+1}/{max_retries}): {e}")

# Build sessions
@nox.session
def build(session):
    """Build the Rust extension."""
    session.install("maturin>=1.4,<2.0")
    session.run("maturin", "build", "--release")

@nox.session
def build_wheel(session):
    """Build the wheel package."""
    session.install("maturin>=1.4,<2.0")
    os.makedirs(WHEELHOUSE_DIR, exist_ok=True)
    session.run("maturin", "build", "--release", "--out", WHEELHOUSE_DIR)

@nox.session
def develop(session):
    """Install the package in development mode."""
    session.install("maturin>=1.4,<2.0")
    session.run("maturin", "develop", "--release")

@nox.session
def clean(session):
    """Clean build artifacts."""
    # Clean Rust build artifacts
    session.run("cargo", "clean", external=True)

    # Clean Python build artifacts
    for path in ["dist", "target", WHEELHOUSE_DIR]:
        if os.path.exists(path):
            session.log(f"Removing {path}")
            shutil.rmtree(path)

# Test sessions
@nox.session
def pytest(session):
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

@nox.session
def test_wheel(session):
    """Test the wheel package."""
    # Install the wheel and test dependencies
    session.install("pytest", "pytest-cov")

    # Find the latest wheel
    try:
        wheel_file = get_latest_wheel()
    except FileNotFoundError:
        session.log("No wheel found, building one...")
        build_wheel(session)
        wheel_file = get_latest_wheel()

    session.log(f"Installing wheel: {wheel_file}")
    session.install(wheel_file)

    # Run tests with simplified test file
    session.run(
        "pytest",
        "tests/test_simplified.py",
        f"--cov={MODULE_NAME}",
        "--cov-report=xml:coverage.xml",
        "--cov-report=term-missing"
    )

@nox.session
def build_test(session):
    """Build and test the package."""
    # Build the wheel
    build_wheel(session)

    # Test the wheel
    test_wheel(session)

# Lint sessions
@nox.session
def lint(session):
    """Run linting checks."""
    session.install("ruff", "black")

    # Lint Python code
    session.run("ruff", "check", "src", "tests")
    session.run("black", "--check", "src", "tests")

    # Lint Rust code
    session.run("cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings", external=True)

@nox.session
def lint_fix(session):
    """Fix linting issues."""
    session.install("ruff", "black")

    # Fix Python code
    session.run("ruff", "check", "--fix", "src", "tests")
    session.run("black", "src", "tests")

    # Fix Rust code
    session.run("cargo", "clippy", "--fix", "--allow-dirty", "--allow-staged", external=True)

# Documentation sessions
@nox.session
def docs(session):
    """Build documentation."""
    session.install("-e", ".[docs]")
    session.run("sphinx-build", "-b", "html", "docs", "docs/_build/html")

@nox.session
def docs_serve(session):
    """Serve documentation with live reloading."""
    session.install("-e", ".[docs]")
    session.run("sphinx-autobuild", "docs", "docs/_build/html")

# Release sessions
@nox.session
def publish(session):
    """Publish the package to PyPI."""
    session.install("maturin>=1.4,<2.0", "twine")

    # Build wheels for all platforms
    session.run("maturin", "build", "--release", "--strip")

    # Upload to PyPI
    session.run("twine", "upload", "target/wheels/*")
