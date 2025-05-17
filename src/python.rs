// Python bindings for EACopy using PyO3
// This module provides the Python interface to the Rust EACopy implementation

use std::path::PathBuf;
use std::sync::{Arc, Mutex};

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};
use pyo3::exceptions::{PyFileNotFoundError, PyValueError, PyRuntimeError};
use pyo3::PyResult;

use crate::eacopy::{EACopy as RustEACopy};
use crate::config::{Config, ErrorStrategy, LogLevel, global_config};
use crate::error::{Error, Result, to_py_err};

/// Python wrapper for ErrorStrategy enum
#[pyclass]
#[derive(Clone)]
pub enum PyErrorStrategy {
    #[pyo3(name = "RAISE")]
    Raise,
    #[pyo3(name = "RETRY")]
    Retry,
    #[pyo3(name = "IGNORE")]
    Ignore,
}

impl From<PyErrorStrategy> for ErrorStrategy {
    fn from(strategy: PyErrorStrategy) -> Self {
        match strategy {
            PyErrorStrategy::Raise => ErrorStrategy::Raise,
            PyErrorStrategy::Retry => ErrorStrategy::Retry,
            PyErrorStrategy::Ignore => ErrorStrategy::Ignore,
        }
    }
}

impl From<ErrorStrategy> for PyErrorStrategy {
    fn from(strategy: ErrorStrategy) -> Self {
        match strategy {
            ErrorStrategy::Raise => PyErrorStrategy::Raise,
            ErrorStrategy::Retry => PyErrorStrategy::Retry,
            ErrorStrategy::Ignore => PyErrorStrategy::Ignore,
        }
    }
}

/// Python wrapper for LogLevel enum
#[pyclass]
#[derive(Clone)]
pub enum PyLogLevel {
    #[pyo3(name = "NONE")]
    None,
    #[pyo3(name = "ERROR")]
    Error,
    #[pyo3(name = "WARNING")]
    Warning,
    #[pyo3(name = "INFO")]
    Info,
    #[pyo3(name = "DEBUG")]
    Debug,
}

impl From<PyLogLevel> for LogLevel {
    fn from(level: PyLogLevel) -> Self {
        match level {
            PyLogLevel::None => LogLevel::None,
            PyLogLevel::Error => LogLevel::Error,
            PyLogLevel::Warning => LogLevel::Warning,
            PyLogLevel::Info => LogLevel::Info,
            PyLogLevel::Debug => LogLevel::Debug,
        }
    }
}

impl From<LogLevel> for PyLogLevel {
    fn from(level: LogLevel) -> Self {
        match level {
            LogLevel::None => PyLogLevel::None,
            LogLevel::Error => PyLogLevel::Error,
            LogLevel::Warning => PyLogLevel::Warning,
            LogLevel::Info => PyLogLevel::Info,
            LogLevel::Debug => PyLogLevel::Debug,
        }
    }
}

/// Python wrapper for Config struct
#[pyclass]
#[derive(Clone)]
pub struct PyConfig {
    #[pyo3(get, set)]
    pub thread_count: usize,
    #[pyo3(get, set)]
    pub compression_level: u32,
    #[pyo3(get, set)]
    pub buffer_size: usize,
    #[pyo3(get, set)]
    pub error_strategy: PyErrorStrategy,
    #[pyo3(get, set)]
    pub retry_count: u32,
    #[pyo3(get, set)]
    pub retry_delay: f64,
    #[pyo3(get, set)]
    pub log_level: PyLogLevel,
    #[pyo3(get, set)]
    pub preserve_metadata: bool,
    #[pyo3(get, set)]
    pub follow_symlinks: bool,
    #[pyo3(get, set)]
    pub dirs_exist_ok: bool,
    #[pyo3(get, set)]
    pub progress_callback: Option<PyObject>,
}

#[pymethods]
impl PyConfig {
    #[new]
    fn new() -> Self {
        let config = global_config().lock().unwrap();
        PyConfig {
            thread_count: config.thread_count,
            compression_level: config.compression_level,
            buffer_size: config.buffer_size,
            error_strategy: config.error_strategy.into(),
            retry_count: config.retry_count,
            retry_delay: config.retry_delay,
            log_level: config.log_level.into(),
            preserve_metadata: config.preserve_metadata,
            follow_symlinks: config.follow_symlinks,
            dirs_exist_ok: config.dirs_exist_ok,
            progress_callback: None,
        }
    }
}

impl From<PyConfig> for Config {
    fn from(py_config: PyConfig) -> Self {
        let mut config = Config::default();
        config.thread_count = py_config.thread_count;
        config.compression_level = py_config.compression_level;
        config.buffer_size = py_config.buffer_size;
        config.error_strategy = py_config.error_strategy.into();
        config.retry_count = py_config.retry_count;
        config.retry_delay = py_config.retry_delay;
        config.log_level = py_config.log_level.into();
        config.preserve_metadata = py_config.preserve_metadata;
        config.follow_symlinks = py_config.follow_symlinks;
        config.dirs_exist_ok = py_config.dirs_exist_ok;

        // TODO: Handle progress callback

        config
    }
}

/// Python wrapper for EACopyServer class
#[pyclass]
pub struct PyEACopyServer {
    inner: RustEACopy::EACopyServer,
}

#[pymethods]
impl PyEACopyServer {
    #[new]
    #[pyo3(signature = (port=31337, thread_count=4))]
    fn new(port: u16, thread_count: usize) -> PyResult<Self> {
        let server = RustEACopy::create_server(port, thread_count)
            .map_err(to_py_err)?;

        Ok(Self { inner: server })
    }

    /// Start the server
    fn start(&self) -> PyResult<()> {
        self.inner.start().map_err(to_py_err)
    }

    /// Stop the server
    fn stop(&self) -> PyResult<()> {
        self.inner.stop().map_err(to_py_err)
    }

    /// Check if the server is running
    fn is_running(&self) -> bool {
        self.inner.is_running()
    }

    /// Get the server port
    #[getter]
    fn get_port(&self) -> u16 {
        self.inner.get_port()
    }

    /// Get the server thread count
    #[getter]
    fn get_thread_count(&self) -> usize {
        self.inner.get_thread_count()
    }

    /// Get server statistics
    fn get_stats(&self) -> PyResult<PyObject> {
        let stats = self.inner.get_stats();

        Python::with_gil(|py| {
            let dict = PyDict::new(py);
            dict.set_item("connections", stats.connections)?;
            dict.set_item("active_connections", stats.activeConnections)?;
            dict.set_item("bytes_sent", stats.bytesSent)?;
            dict.set_item("bytes_received", stats.bytesReceived)?;
            dict.set_item("files_sent", stats.filesSent)?;
            dict.set_item("files_received", stats.filesReceived)?;

            Ok(dict.into())
        })
    }

    fn __enter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __exit__(
        &self,
        _exc_type: Option<PyObject>,
        _exc_value: Option<PyObject>,
        _traceback: Option<PyObject>,
    ) -> PyResult<bool> {
        if self.is_running() {
            self.stop()?;
        }
        Ok(false) // Don't suppress exceptions
    }
}

/// Python wrapper for EACopy class
#[pyclass]
pub struct PyEACopy {
    inner: RustEACopy,
}

#[pymethods]
impl PyEACopy {
    #[new]
    #[pyo3(signature = (
        thread_count=4,
        compression_level=0,
        buffer_size=8*1024*1024,
        preserve_metadata=true,
        follow_symlinks=false,
        dirs_exist_ok=false,
        progress_callback=None
    ))]
    fn new(
        thread_count: usize,
        compression_level: u32,
        buffer_size: usize,
        preserve_metadata: bool,
        follow_symlinks: bool,
        dirs_exist_ok: bool,
        progress_callback: Option<PyObject>,
    ) -> Self {
        let mut config = Config::default();
        config.thread_count = thread_count;
        config.compression_level = compression_level;
        config.buffer_size = buffer_size;
        config.preserve_metadata = preserve_metadata;
        config.follow_symlinks = follow_symlinks;
        config.dirs_exist_ok = dirs_exist_ok;

        // TODO: Handle progress callback

        PyEACopy {
            inner: RustEACopy::with_config(config),
        }
    }

    /// Copy file content from src to dst
    fn copyfile(&self, src: &str, dst: &str) -> PyResult<()> {
        self.inner.copyfile(src, dst).map_err(to_py_err)
    }

    /// Copy a file from src to dst, preserving file content but not metadata
    fn copy(&self, src: &str, dst: &str) -> PyResult<()> {
        self.inner.copy(src, dst).map_err(to_py_err)
    }

    /// Copy a file from src to dst, preserving file content and metadata
    fn copy2(&self, src: &str, dst: &str) -> PyResult<()> {
        self.inner.copy2(src, dst).map_err(to_py_err)
    }

    /// Recursively copy a directory tree from src to dst
    #[pyo3(signature = (src, dst, symlinks=false, ignore_dangling_symlinks=false, dirs_exist_ok=false))]
    fn copytree(
        &self,
        src: &str,
        dst: &str,
        symlinks: bool,
        ignore_dangling_symlinks: bool,
        dirs_exist_ok: bool,
    ) -> PyResult<()> {
        self.inner
            .copytree(src, dst, symlinks, ignore_dangling_symlinks, dirs_exist_ok)
            .map_err(to_py_err)
    }

    /// Copy file or directory using EACopyService for acceleration
    #[pyo3(signature = (src, dst, server_addr, port=31337, compression_level=0))]
    fn copy_with_server(
        &self,
        src: &str,
        dst: &str,
        server_addr: &str,
        port: u16,
        compression_level: u32,
    ) -> PyResult<()> {
        self.inner
            .copy_with_server(src, dst, server_addr, port, compression_level)
            .map_err(to_py_err)
    }

    /// Copy multiple files in batch
    fn batch_copy(&self, file_pairs: &PyList) -> PyResult<()> {
        let mut pairs = Vec::new();

        for item in file_pairs.iter() {
            let tuple = item.downcast::<PyTuple>()?;
            if tuple.len() != 2 {
                return Err(PyValueError::new_err("Each item must be a (src, dst) tuple"));
            }

            let src = tuple.get_item(0)?.extract::<String>()?;
            let dst = tuple.get_item(1)?.extract::<String>()?;

            pairs.push((src, dst));
        }

        self.inner.batch_copy(&pairs).map_err(to_py_err)
    }

    /// Copy multiple files with metadata in batch
    fn batch_copy2(&self, file_pairs: &PyList) -> PyResult<()> {
        let mut pairs = Vec::new();

        for item in file_pairs.iter() {
            let tuple = item.downcast::<PyTuple>()?;
            if tuple.len() != 2 {
                return Err(PyValueError::new_err("Each item must be a (src, dst) tuple"));
            }

            let src = tuple.get_item(0)?.extract::<String>()?;
            let dst = tuple.get_item(1)?.extract::<String>()?;

            pairs.push((src, dst));
        }

        self.inner.batch_copy2(&pairs).map_err(to_py_err)
    }

    /// Copy multiple directory trees in batch
    #[pyo3(signature = (dir_pairs, symlinks=false, ignore_dangling_symlinks=false, dirs_exist_ok=false))]
    fn batch_copytree(
        &self,
        dir_pairs: &PyList,
        symlinks: bool,
        ignore_dangling_symlinks: bool,
        dirs_exist_ok: bool,
    ) -> PyResult<()> {
        let mut pairs = Vec::new();

        for item in dir_pairs.iter() {
            let tuple = item.downcast::<PyTuple>()?;
            if tuple.len() != 2 {
                return Err(PyValueError::new_err("Each item must be a (src, dst) tuple"));
            }

            let src = tuple.get_item(0)?.extract::<String>()?;
            let dst = tuple.get_item(1)?.extract::<String>()?;

            pairs.push((src, dst));
        }

        self.inner
            .batch_copytree(&pairs, symlinks, ignore_dangling_symlinks, dirs_exist_ok)
            .map_err(to_py_err)
    }

    /// Set the progress callback function
    fn set_progress_callback(&mut self, callback: PyObject) -> PyResult<()> {
        let py = callback.py();

        // Create a Rust callback that calls the Python function
        let rust_callback = move |copied_bytes: u64, total_bytes: u64, filename: &str| {
            Python::with_gil(|py| {
                let _ = callback.call1(
                    py,
                    (copied_bytes, total_bytes, filename),
                );
            });
        };

        // Set the callback in the Rust EACopy instance
        self.inner.set_progress_callback(rust_callback);

        Ok(())
    }

    /// Get the current thread count
    #[getter]
    fn get_thread_count(&self) -> PyResult<usize> {
        Ok(self.inner.get_config().thread_count)
    }

    /// Set the thread count
    #[setter]
    fn set_thread_count(&mut self, value: usize) -> PyResult<()> {
        let mut config = self.inner.get_config().clone();
        config.thread_count = value;
        self.inner.set_config(config);
        Ok(())
    }

    /// Get the current compression level
    #[getter]
    fn get_compression_level(&self) -> PyResult<u32> {
        Ok(self.inner.get_config().compression_level)
    }

    /// Set the compression level
    #[setter]
    fn set_compression_level(&mut self, value: u32) -> PyResult<()> {
        let mut config = self.inner.get_config().clone();
        config.compression_level = value;
        self.inner.set_config(config);
        Ok(())
    }

    /// Create a new EACopy server
    #[pyo3(signature = (port=31337))]
    fn create_server(&self, port: u16) -> PyResult<PyEACopyServer> {
        let server = self.inner.create_server(port)
            .map_err(to_py_err)?;

        Ok(PyEACopyServer { inner: server })
    }

    /// Perform delta copy using a reference file
    fn delta_copy(&self, src: &str, dst: &str, reference: &str) -> PyResult<()> {
        self.inner.delta_copy(src, dst, reference).map_err(to_py_err)
    }

    fn __enter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __exit__(
        &self,
        _exc_type: Option<PyObject>,
        _exc_value: Option<PyObject>,
        _traceback: Option<PyObject>,
    ) -> PyResult<bool> {
        // No cleanup needed
        Ok(false) // Don't suppress exceptions
    }
}

/// Copy file content from src to dst
#[pyfunction]
fn copyfile(src: &str, dst: &str) -> PyResult<()> {
    crate::eacopy::copyfile(src, dst).map_err(to_py_err)
}

/// Copy a file from src to dst, preserving file content but not metadata
#[pyfunction]
fn copy(src: &str, dst: &str) -> PyResult<()> {
    crate::eacopy::copy(src, dst).map_err(to_py_err)
}

/// Copy a file from src to dst, preserving file content and metadata
#[pyfunction]
fn copy2(src: &str, dst: &str) -> PyResult<()> {
    crate::eacopy::copy2(src, dst).map_err(to_py_err)
}

/// Recursively copy a directory tree from src to dst
#[pyfunction]
#[pyo3(signature = (src, dst, symlinks=false, ignore_dangling_symlinks=false, dirs_exist_ok=false))]
fn copytree(
    src: &str,
    dst: &str,
    symlinks: bool,
    ignore_dangling_symlinks: bool,
    dirs_exist_ok: bool,
) -> PyResult<()> {
    crate::eacopy::copytree(src, dst, symlinks, ignore_dangling_symlinks, dirs_exist_ok)
        .map_err(to_py_err)
}

/// Copy file or directory using EACopyService for acceleration
#[pyfunction]
#[pyo3(signature = (src, dst, server_addr, port=31337, compression_level=0))]
fn copy_with_server(
    src: &str,
    dst: &str,
    server_addr: &str,
    port: u16,
    compression_level: u32,
) -> PyResult<()> {
    crate::eacopy::copy_with_server(src, dst, server_addr, port, compression_level)
        .map_err(to_py_err)
}

/// Create a new EACopy server
#[pyfunction]
#[pyo3(signature = (port=31337, thread_count=4))]
fn create_server(port: u16, thread_count: usize) -> PyResult<PyEACopyServer> {
    let server = RustEACopy::create_server(port, thread_count)
        .map_err(to_py_err)?;

    Ok(PyEACopyServer { inner: server })
}

/// Perform delta copy using a reference file
#[pyfunction]
fn delta_copy(src: &str, dst: &str, reference: &str) -> PyResult<()> {
    RustEACopy::delta_copy(src, dst, reference).map_err(to_py_err)
}

/// Initialize the Python module
pub fn init_module(_py: Python, m: &PyModule) -> PyResult<()> {
    // Add classes
    m.add_class::<PyEACopy>()?;
    m.add_class::<PyEACopyServer>()?;
    m.add_class::<PyConfig>()?;
    m.add_class::<PyErrorStrategy>()?;
    m.add_class::<PyLogLevel>()?;

    // Add functions
    m.add_function(wrap_pyfunction!(copyfile, m)?)?;
    m.add_function(wrap_pyfunction!(copy, m)?)?;
    m.add_function(wrap_pyfunction!(copy2, m)?)?;
    m.add_function(wrap_pyfunction!(copytree, m)?)?;
    m.add_function(wrap_pyfunction!(copy_with_server, m)?)?;
    m.add_function(wrap_pyfunction!(create_server, m)?)?;
    m.add_function(wrap_pyfunction!(delta_copy, m)?)?;

    Ok(())
}
