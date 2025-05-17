# Import built-in modules

# Import third-party modules
import nox

# Import local modules
from nox_actions.utils import retry_command


def docs(session: nox.Session) -> None:
    """Build documentation."""
    # Install dependencies
    retry_command(session, session.install, "-e", ".[docs]", max_retries=3)
    
    # Change to docs directory
    session.chdir("docs")
    
    # Build documentation
    session.run("make", "html", external=True)
    
    session.log("Documentation built successfully in docs/_build/html/")


def docs_serve(session: nox.Session) -> None:
    """Build and serve documentation with live reloading."""
    # Install dependencies
    retry_command(session, session.install, "-e", ".[docs]", max_retries=3)
    retry_command(session, session.install, "sphinx-autobuild", max_retries=3)
    
    # Serve documentation with live reloading
    session.run("sphinx-autobuild", "docs", "docs/_build/html", "--open-browser")
