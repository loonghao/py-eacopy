# Import built-in modules
import os
import time
from typing import Any, Callable, Optional, TypeVar, cast

# Import third-party modules
import nox

# Constants
THIS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODULE_NAME = "py_eacopy"

# Type variables for better type hints
T = TypeVar("T")


def retry_command(
    session: nox.Session,
    func: Callable[..., T],
    *args: Any,
    max_retries: int = 3,
    retry_delay: float = 2.0,
    **kwargs: Any,
) -> T:
    """Retry a command with exponential backoff.

    Args:
        session: The nox session.
        func: The function to call.
        *args: Arguments to pass to the function.
        max_retries: Maximum number of retries.
        retry_delay: Initial delay between retries in seconds.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The result of the function call.

    Raises:
        Exception: If all retries fail.
    """
    last_exception = None
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            wait_time = retry_delay * (2**attempt)
            session.log(f"Command failed, retrying in {wait_time:.1f}s... ({attempt + 1}/{max_retries})")
            session.log(f"Error: {e}")
            time.sleep(wait_time)
    
    # If we get here, all retries failed
    if last_exception:
        session.log(f"All {max_retries} retries failed!")
        raise last_exception
    
    # This should never happen, but makes the type checker happy
    return cast(T, None)


def build_cpp_extension(session: nox.Session, env: Optional[dict] = None) -> None:
    """Build the C++ extension using scikit-build-core.

    Args:
        session: The nox session.
        env: Optional environment variables to set.
    """
    # Set default environment variables if not provided
    if env is None:
        env = {}
    
    # Set common environment variables
    env.setdefault("CMAKE_BUILD_PARALLEL_LEVEL", str(os.cpu_count() or 4))
    
    # On Windows, set additional environment variables
    if os.name == "nt":
        env.setdefault("CL", "/MP")  # Enable parallel compilation with MSVC
    
    # Build the extension
    session.log("Building C++ extension...")
    session.run("pip", "install", "-e", ".", env=env)
