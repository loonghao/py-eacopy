# Import built-in modules

# Import third-party modules
import nox

# Import local modules
from nox_actions.utils import retry_command


def lint(session: nox.Session) -> None:
    """Run linting checks."""
    # Install dependencies
    retry_command(session, session.install, "ruff", "mypy", "isort", max_retries=3)
    
    # Run linting checks
    session.run("mypy", "--install-types", "--non-interactive")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")
    session.run("isort", "--check-only", ".")
    session.run("mypy", "src/eacopy", "--strict")


def lint_fix(session: nox.Session) -> None:
    """Fix linting issues."""
    # Install dependencies
    retry_command(session, session.install, "ruff", "mypy", "isort", max_retries=3)
    
    # Fix linting issues
    session.run("ruff", "check", "--fix", ".")
    session.run("ruff", "format", ".")
    session.run("isort", ".")
