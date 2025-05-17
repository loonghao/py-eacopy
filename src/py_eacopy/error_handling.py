"""Error handling utilities for py-eacopy."""

import time
import functools
import logging
from typing import Callable, Any, TypeVar, cast

from .config import ErrorStrategy, config

# Set up logging
logger = logging.getLogger("py_eacopy")

# Type variable for function return type
T = TypeVar('T')


def with_error_handling(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to handle errors according to the global error strategy.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        """Wrapper function that implements error handling."""
        # Get the current error strategy from global config
        strategy = config.error_strategy
        retry_count = config.retry_count
        retry_delay = config.retry_delay
        
        # For RAISE strategy, just call the function
        if strategy == ErrorStrategy.RAISE:
            return func(*args, **kwargs)
        
        # For RETRY strategy, try multiple times
        elif strategy == ErrorStrategy.RETRY:
            last_exception = None
            for attempt in range(retry_count + 1):  # +1 for the initial attempt
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < retry_count:
                        logger.warning(
                            f"Error during operation (attempt {attempt+1}/{retry_count+1}): {str(e)}. "
                            f"Retrying in {retry_delay} seconds..."
                        )
                        time.sleep(retry_delay)
                    else:
                        # All retries failed
                        logger.error(
                            f"Operation failed after {retry_count+1} attempts: {str(e)}"
                        )
                        raise
            
            # This should never be reached, but just in case
            assert last_exception is not None
            raise last_exception
        
        # For IGNORE strategy, catch exceptions and log them
        elif strategy == ErrorStrategy.IGNORE:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Error ignored: {str(e)}")
                return cast(T, None)  # Return None for any return type
        
        # Unknown strategy, fall back to RAISE
        else:
            logger.warning(f"Unknown error strategy: {strategy}. Using RAISE instead.")
            return func(*args, **kwargs)
    
    return wrapper
