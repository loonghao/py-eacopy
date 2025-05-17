use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// Error handling strategies
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ErrorStrategy {
    /// Raise exceptions immediately
    Raise,
    /// Retry the operation
    Retry,
    /// Ignore errors and continue
    Ignore,
}

impl Default for ErrorStrategy {
    fn default() -> Self {
        ErrorStrategy::Raise
    }
}

/// Log levels for EACopy operations
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LogLevel {
    None,
    Error,
    Warning,
    Info,
    Debug,
}

impl Default for LogLevel {
    fn default() -> Self {
        LogLevel::Error
    }
}

/// Type for progress callback function
pub type ProgressCallback = Option<Arc<dyn Fn(u64, u64, &str) + Send + Sync>>;

/// Configuration options for EACopy
#[derive(Debug, Clone)]
pub struct Config {
    /// Default number of threads to use for copy operations
    pub thread_count: usize,
    /// Default compression level (0-9) for network transfers
    pub compression_level: u32,
    /// Size of the buffer used for copy operations (in bytes)
    pub buffer_size: usize,
    /// How to handle errors during copy operations
    pub error_strategy: ErrorStrategy,
    /// Number of retries for failed operations when error_strategy is Retry
    pub retry_count: u32,
    /// Delay between retries in seconds
    pub retry_delay: f64,
    /// Verbosity level for logging
    pub log_level: LogLevel,
    /// Whether to preserve file metadata by default
    pub preserve_metadata: bool,
    /// Whether to follow symbolic links by default
    pub follow_symlinks: bool,
    /// Whether to allow existing directories by default
    pub dirs_exist_ok: bool,
    /// Function to call to report progress
    pub progress_callback: ProgressCallback,
    /// Advanced options
    pub extra_options: HashMap<String, String>,
}

impl Default for Config {
    fn default() -> Self {
        Config {
            thread_count: num_cpus::get(),
            compression_level: 0,
            buffer_size: 8 * 1024 * 1024, // 8MB buffer
            error_strategy: ErrorStrategy::default(),
            retry_count: 3,
            retry_delay: 1.0,
            log_level: LogLevel::default(),
            preserve_metadata: true,
            follow_symlinks: false,
            dirs_exist_ok: false,
            progress_callback: None,
            extra_options: HashMap::new(),
        }
    }
}

impl Config {
    /// Create a new configuration with default values
    pub fn new() -> Self {
        Config::default()
    }

    /// Set the number of threads to use for copy operations
    pub fn with_thread_count(mut self, thread_count: usize) -> Self {
        self.thread_count = thread_count;
        self
    }

    /// Set the compression level (0-9) for network transfers
    pub fn with_compression_level(mut self, compression_level: u32) -> Self {
        self.compression_level = compression_level;
        self
    }

    /// Set the buffer size for copy operations
    pub fn with_buffer_size(mut self, buffer_size: usize) -> Self {
        self.buffer_size = buffer_size;
        self
    }

    /// Set the error handling strategy
    pub fn with_error_strategy(mut self, error_strategy: ErrorStrategy) -> Self {
        self.error_strategy = error_strategy;
        self
    }

    /// Set the number of retries for failed operations
    pub fn with_retry_count(mut self, retry_count: u32) -> Self {
        self.retry_count = retry_count;
        self
    }

    /// Set the delay between retries in seconds
    pub fn with_retry_delay(mut self, retry_delay: f64) -> Self {
        self.retry_delay = retry_delay;
        self
    }

    /// Set the verbosity level for logging
    pub fn with_log_level(mut self, log_level: LogLevel) -> Self {
        self.log_level = log_level;
        self
    }

    /// Set whether to preserve file metadata
    pub fn with_preserve_metadata(mut self, preserve_metadata: bool) -> Self {
        self.preserve_metadata = preserve_metadata;
        self
    }

    /// Set whether to follow symbolic links
    pub fn with_follow_symlinks(mut self, follow_symlinks: bool) -> Self {
        self.follow_symlinks = follow_symlinks;
        self
    }

    /// Set whether to allow existing directories
    pub fn with_dirs_exist_ok(mut self, dirs_exist_ok: bool) -> Self {
        self.dirs_exist_ok = dirs_exist_ok;
        self
    }

    /// Set the progress callback function
    pub fn with_progress_callback<F>(mut self, callback: F) -> Self
    where
        F: Fn(u64, u64, &str) + Send + Sync + 'static,
    {
        self.progress_callback = Some(Arc::new(callback));
        self
    }
}

/// Global configuration instance
lazy_static::lazy_static! {
    pub static ref GLOBAL_CONFIG: Arc<Mutex<Config>> = Arc::new(Mutex::new(Config::default()));
}

/// Get a reference to the global configuration
pub fn global_config() -> Arc<Mutex<Config>> {
    GLOBAL_CONFIG.clone()
}

/// Set the global configuration
pub fn set_global_config(config: Config) {
    let mut global = GLOBAL_CONFIG.lock().unwrap();
    *global = config;
}

/// Reset the global configuration to defaults
pub fn reset_global_config() {
    let mut global = GLOBAL_CONFIG.lock().unwrap();
    *global = Config::default();
}
