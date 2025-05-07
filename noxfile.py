# Import third-party modules
import nox


@nox.session
def lint(session):
    """Run linting checks."""
    session.install("ruff", "mypy", "isort")
    session.run("mypy", "--install-types", "--non-interactive")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")
    session.run("isort", "--check-only", ".")
    session.run("mypy", "src/eacopy", "--strict")


@nox.session
def lint_fix(session):
    """Fix linting issues."""
    session.install("ruff", "mypy", "isort")
    session.run("ruff", "check", "--fix", ".")
    session.run("ruff", "format", ".")
    session.run("isort", ".")


@nox.session
def pytest(session):
    """Run tests."""
    session.install("pytest", "pytest-cov")
    session.install("-e", ".")
    session.run("pytest", "tests/", "--cov=eacopy", "--cov-report=xml:coverage.xml", "--cov-report=term-missing")


@nox.session
def docs(session):
    """Build documentation."""
    session.install("-e", ".[docs]")
    session.chdir("docs")
    session.run("make", "html", external=True)


@nox.session
def docs_serve(session):
    """Build and serve documentation with live reloading."""
    session.install("-e", ".[docs]")
    session.install("sphinx-autobuild")
    session.run("sphinx-autobuild", "docs", "docs/_build/html", "--open-browser")
