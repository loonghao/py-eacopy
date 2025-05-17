use std::ffi::{CString, OsStr, OsString};
use std::os::windows::ffi::{OsStrExt, OsStringExt};
use std::path::{Path, PathBuf};
use std::ptr;

use crate::error::{Error, Result};

/// Convert a Rust string to a wide string (UTF-16) for Windows API
pub fn to_wide_string(s: &str) -> Vec<u16> {
    OsStr::new(s)
        .encode_wide()
        .chain(std::iter::once(0))
        .collect()
}

/// Convert a wide string (UTF-16) to a Rust string
pub fn from_wide_string(wide: &[u16]) -> Result<String> {
    let len = wide.iter().position(|&c| c == 0).unwrap_or(wide.len());
    let os_string = OsString::from_wide(&wide[..len]);
    os_string
        .into_string()
        .map_err(|_| Error::Encoding("Failed to convert wide string to UTF-8".to_string()))
}

/// Convert a Rust string to a C string
pub fn to_c_string(s: &str) -> Result<CString> {
    CString::new(s).map_err(|_| Error::Encoding("Failed to convert string to C string".to_string()))
}

/// Convert a Path to a wide string (UTF-16) for Windows API
pub fn path_to_wide_string(path: &Path) -> Vec<u16> {
    path.as_os_str()
        .encode_wide()
        .chain(std::iter::once(0))
        .collect()
}

/// Convert a wide string (UTF-16) to a Path
pub fn wide_string_to_path(wide: &[u16]) -> Result<PathBuf> {
    let len = wide.iter().position(|&c| c == 0).unwrap_or(wide.len());
    let os_string = OsString::from_wide(&wide[..len]);
    Ok(PathBuf::from(os_string))
}

/// Check if a path exists
pub fn path_exists(path: &Path) -> bool {
    path.exists()
}

/// Check if a path is a file
pub fn is_file(path: &Path) -> bool {
    path.is_file()
}

/// Check if a path is a directory
pub fn is_dir(path: &Path) -> bool {
    path.is_dir()
}

/// Check if a path is absolute
pub fn is_absolute(path: &Path) -> bool {
    path.is_absolute()
}

/// Get the parent directory of a path
pub fn parent_dir(path: &Path) -> Option<&Path> {
    path.parent()
}

/// Get the file name of a path
pub fn file_name(path: &Path) -> Option<&OsStr> {
    path.file_name()
}

/// Join two paths
pub fn join_paths(base: &Path, path: &Path) -> PathBuf {
    base.join(path)
}

/// Create a directory and all parent directories
pub fn create_dir_all(path: &Path) -> Result<()> {
    std::fs::create_dir_all(path).map_err(Error::from)
}

/// Remove a file
pub fn remove_file(path: &Path) -> Result<()> {
    std::fs::remove_file(path).map_err(Error::from)
}

/// Remove a directory and all its contents
pub fn remove_dir_all(path: &Path) -> Result<()> {
    std::fs::remove_dir_all(path).map_err(Error::from)
}

/// Copy a file
pub fn copy_file(from: &Path, to: &Path) -> Result<u64> {
    std::fs::copy(from, to).map_err(Error::from)
}

/// Get the canonical path
pub fn canonicalize(path: &Path) -> Result<PathBuf> {
    path.canonicalize().map_err(Error::from)
}

/// Get the current working directory
pub fn current_dir() -> Result<PathBuf> {
    std::env::current_dir().map_err(Error::from)
}

/// Set the current working directory
pub fn set_current_dir(path: &Path) -> Result<()> {
    std::env::set_current_dir(path).map_err(Error::from)
}
