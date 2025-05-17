use std::path::PathBuf;
use thiserror::Error;

/// Custom error type for EACopy operations
#[derive(Error, Debug)]
pub enum Error {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("FFI error: {0}")]
    Ffi(String),

    #[error("Path error: {0}")]
    Path(String),

    #[error("File not found: {0}")]
    FileNotFound(PathBuf),

    #[error("Directory not found: {0}")]
    DirectoryNotFound(PathBuf),

    #[error("Permission denied: {0}")]
    PermissionDenied(PathBuf),

    #[error("Destination already exists: {0}")]
    DestinationExists(PathBuf),

    #[error("Invalid argument: {0}")]
    InvalidArgument(String),

    #[error("Network error: {0}")]
    Network(String),

    #[error("Timeout error: {0}")]
    Timeout(String),

    #[error("Encoding error: {0}")]
    Encoding(String),

    #[error("Python error: {0}")]
    Python(String),

    #[error("File too large: {0} ({1} bytes)")]
    FileTooLarge(PathBuf, u64),

    #[error("Disk full: {0} (needed {1} bytes, available {2} bytes)")]
    DiskFull(PathBuf, u64, u64),

    #[error("Read error: {0} (at offset {1})")]
    ReadError(PathBuf, u64),

    #[error("Write error: {0} (at offset {1})")]
    WriteError(PathBuf, u64),

    #[error("Interrupted operation: {0}")]
    Interrupted(String),

    #[error("Server error: {0}")]
    Server(String),

    #[error("Client error: {0}")]
    Client(String),

    #[error("Delta copy error: {0}")]
    DeltaCopy(String),

    #[error("Unsupported operation: {0}")]
    Unsupported(String),

    #[error("Configuration error: {0}")]
    Configuration(String),

    #[error("Unknown error: {0}")]
    Unknown(String),
}

/// Result type for EACopy operations
pub type Result<T> = std::result::Result<T, Error>;

/// Convert a C error code to a Rust Error
pub fn from_error_code(code: i32, path: Option<&PathBuf>) -> Error {
    let unknown_path = PathBuf::from("<unknown>");
    let path = path.unwrap_or(&unknown_path);

    match code {
        // Standard Windows error codes
        2 => Error::FileNotFound(path.clone()),
        3 => Error::DirectoryNotFound(path.clone()),
        5 => Error::PermissionDenied(path.clone()),
        8 => Error::DiskFull(path.clone(), 0, 0),
        13 => Error::InvalidArgument(format!("Invalid data for {}", path.display())),
        32 => Error::Interrupted(format!("Operation on {} was interrupted", path.display())),
        80 => Error::DestinationExists(path.clone()),
        87 => Error::InvalidArgument(format!("Invalid parameter for {}", path.display())),
        112 => Error::DiskFull(path.clone(), 0, 0),
        123 => Error::InvalidArgument(format!("Invalid syntax for {}", path.display())),
        1392 => Error::FileTooLarge(path.clone(), 0),

        // Network-related error codes
        10053 => Error::Network(format!("Connection aborted for {}", path.display())),
        10054 => Error::Network(format!("Connection reset for {}", path.display())),
        10060 => Error::Timeout(format!("Connection timed out for {}", path.display())),
        10061 => Error::Network(format!("Connection refused for {}", path.display())),
        10064 => Error::Network(format!("Host is down for {}", path.display())),
        10065 => Error::Network(format!("No route to host for {}", path.display())),

        // EACopy-specific error codes
        0x1000 => Error::Configuration(format!("Invalid configuration for {}", path.display())),
        0x1001 => Error::Server(format!("Server error for {}", path.display())),
        0x1002 => Error::Client(format!("Client error for {}", path.display())),
        0x1003 => Error::DeltaCopy(format!("Delta copy error for {}", path.display())),
        0x1004 => Error::Unsupported(format!("Unsupported operation for {}", path.display())),

        // Unknown error code
        _ => Error::Unknown(format!("Unknown error code {} for {}", code, path.display())),
    }
}

/// Convert a Python exception to a Rust Error
#[cfg(feature = "python")]
pub fn from_py_err(err: pyo3::PyErr) -> Error {
    Error::Python(format!("{}", err))
}

/// Convert a Rust Error to a Python exception
#[cfg(feature = "python")]
pub fn to_py_err(err: Error) -> pyo3::PyErr {
    use pyo3::exceptions::*;
    use pyo3::PyErr;

    match err {
        Error::FileNotFound(path) => PyFileNotFoundError::new_err(format!("File not found: {}", path.display())),
        Error::DirectoryNotFound(path) => PyFileNotFoundError::new_err(format!("Directory not found: {}", path.display())),
        Error::PermissionDenied(path) => PyPermissionError::new_err(format!("Permission denied: {}", path.display())),
        Error::DestinationExists(path) => PyFileExistsError::new_err(format!("Destination already exists: {}", path.display())),
        Error::InvalidArgument(msg) => PyValueError::new_err(msg),
        Error::Network(msg) => PyConnectionError::new_err(msg),
        Error::Timeout(msg) => PyTimeoutError::new_err(msg),
        Error::Encoding(msg) => PyUnicodeError::new_err(msg),
        Error::Python(msg) => PyRuntimeError::new_err(msg),
        Error::FileTooLarge(path, size) => PyOSError::new_err(format!("File too large: {} ({} bytes)", path.display(), size)),
        Error::DiskFull(path, needed, available) => PyOSError::new_err(format!(
            "Disk full: {} (needed {} bytes, available {} bytes)",
            path.display(), needed, available
        )),
        Error::ReadError(path, offset) => PyOSError::new_err(format!(
            "Read error: {} (at offset {})",
            path.display(), offset
        )),
        Error::WriteError(path, offset) => PyOSError::new_err(format!(
            "Write error: {} (at offset {})",
            path.display(), offset
        )),
        Error::Interrupted(msg) => PyKeyboardInterrupt::new_err(msg),
        Error::Server(msg) => PyConnectionError::new_err(format!("Server error: {}", msg)),
        Error::Client(msg) => PyConnectionError::new_err(format!("Client error: {}", msg)),
        Error::DeltaCopy(msg) => PyRuntimeError::new_err(format!("Delta copy error: {}", msg)),
        Error::Unsupported(msg) => PyNotImplementedError::new_err(format!("Unsupported operation: {}", msg)),
        Error::Configuration(msg) => PyValueError::new_err(format!("Configuration error: {}", msg)),
        Error::Io(err) => {
            let kind = err.kind();
            match kind {
                std::io::ErrorKind::NotFound => PyFileNotFoundError::new_err(format!("IO error: {}", err)),
                std::io::ErrorKind::PermissionDenied => PyPermissionError::new_err(format!("IO error: {}", err)),
                std::io::ErrorKind::ConnectionRefused => PyConnectionError::new_err(format!("IO error: {}", err)),
                std::io::ErrorKind::ConnectionReset => PyConnectionError::new_err(format!("IO error: {}", err)),
                std::io::ErrorKind::ConnectionAborted => PyConnectionError::new_err(format!("IO error: {}", err)),
                std::io::ErrorKind::NotConnected => PyConnectionError::new_err(format!("IO error: {}", err)),
                std::io::ErrorKind::TimedOut => PyTimeoutError::new_err(format!("IO error: {}", err)),
                std::io::ErrorKind::Interrupted => PyKeyboardInterrupt::new_err(format!("IO error: {}", err)),
                std::io::ErrorKind::InvalidInput => PyValueError::new_err(format!("IO error: {}", err)),
                std::io::ErrorKind::InvalidData => PyValueError::new_err(format!("IO error: {}", err)),
                _ => PyOSError::new_err(format!("IO error: {}", err)),
            }
        },
        Error::Ffi(msg) => PyRuntimeError::new_err(format!("FFI error: {}", msg)),
        Error::Path(msg) => PyValueError::new_err(format!("Path error: {}", msg)),
        Error::Unknown(msg) => PyRuntimeError::new_err(format!("Unknown error: {}", msg)),
    }
}
