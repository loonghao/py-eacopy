"""Configuration handling for EACopy."""

from enum import Enum
from typing import Callable, Optional, Dict, Any


class ErrorStrategy(str, Enum):
    """Error handling strategies."""
    RAISE = "raise"  # Raise exceptions immediately
    RETRY = "retry"  # Retry the operation
    IGNORE = "ignore"  # Ignore errors and continue


class LogLevel(str, Enum):
    """Log levels for EACopy operations."""
    NONE = "none"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


# Type for progress callback function
ProgressCallback = Callable[[int, int, str], None]


class Config:
    """Global configuration options for EACopy.

    Attributes:
        thread_count: Default number of threads to use for copy operations.
        compression_level: Default compression level (0-9) for network transfers.
        error_strategy: How to handle errors during copy operations.
        retry_count: Number of retries for failed operations when error_strategy is RETRY.
        log_level: Verbosity level for logging.
        buffer_size: Size of the buffer used for copy operations (in bytes).
        preserve_metadata: Whether to preserve file metadata by default.
        follow_symlinks: Whether to follow symbolic links by default.
        progress_callback: Function to call to report progress.
    """

    def __init__(self) -> None:
        """Initialize configuration with default values."""
        # Performance settings
        self.thread_count: int = 4
        self.compression_level: int = 0
        self.buffer_size: int = 8 * 1024 * 1024  # 8MB buffer

        # Error handling
        self.error_strategy: ErrorStrategy = ErrorStrategy.RAISE
        self.retry_count: int = 3
        self.retry_delay: float = 1.0  # seconds

        # Logging
        self.log_level: LogLevel = LogLevel.ERROR

        # Copy behavior
        self.preserve_metadata: bool = True
        self.follow_symlinks: bool = False
        self.dirs_exist_ok: bool = False

        # Callbacks
        self.progress_callback: Optional[ProgressCallback] = None

        # Advanced options
        self.extra_options: Dict[str, Any] = {}
