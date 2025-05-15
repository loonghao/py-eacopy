"""Configuration handling for EACopy."""

class Config:
    """Global configuration options for EACopy.
    
    Attributes:
        thread_count: Default number of threads to use for copy operations.
        compression_level: Default compression level (0-9) for network transfers.
    """

    def __init__(self) -> None:
        """Initialize configuration with default values."""
        # Default thread count
        self.thread_count: int = 4
        
        # Default compression level (0-9)
        self.compression_level: int = 0
