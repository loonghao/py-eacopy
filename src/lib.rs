// Rust library for EACopy bindings
// This is the main entry point for the Rust library

mod ffi;

use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;

/// Python module implementation
#[pymodule]
fn _eacopy_binding(_py: Python, m: &PyModule) -> PyResult<()> {
    // Add functions
    m.add_function(wrap_pyfunction!(copy_file, m)?)?;
    m.add_function(wrap_pyfunction!(copy_directory, m)?)?;
    m.add_function(wrap_pyfunction!(version, m)?)?;

    // Add version information
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    // Try to add EACopy version
    match ffi::get_version() {
        Ok(version) => m.add("__eacopy_version__", version)?,
        Err(_) => m.add("__eacopy_version__", "unknown")?
    };

    Ok(())
}

/// Copy a file from source to destination
#[pyfunction]
fn copy_file(source: &str, destination: &str) -> PyResult<bool> {
    ffi::copy_file(source, destination)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to copy file: {}", e)))
}

/// Copy a directory from source to destination
#[pyfunction]
fn copy_directory(source: &str, destination: &str, recursive: bool) -> PyResult<bool> {
    ffi::copy_directory(source, destination, recursive)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to copy directory: {}", e)))
}

/// Get the version of the EACopy library
#[pyfunction]
fn version() -> PyResult<String> {
    match ffi::get_version() {
        Ok(version) => Ok(version),
        Err(_) => Ok(format!("py-eacopy {}", env!("CARGO_PKG_VERSION")))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        let version = version().unwrap();
        assert!(!version.is_empty());
    }
}
