// FFI bindings to EACopy library
use std::ffi::CString;
use std::fs;
use std::io;
use std::path::Path;
use anyhow::{Result, anyhow};

/// Copy a file from source to destination
pub fn copy_file<P: AsRef<Path>, Q: AsRef<Path>>(source: P, destination: Q) -> Result<bool> {
    // Implementation using Rust's standard library
    let source_path = source.as_ref();
    let dest_path = destination.as_ref();

    // Check if source exists
    if !source_path.exists() {
        return Err(anyhow!("Source file does not exist: {}", source_path.display()));
    }

    // Create parent directory if it doesn't exist
    if let Some(parent) = dest_path.parent() {
        if !parent.exists() {
            fs::create_dir_all(parent)?;
        }
    }

    // Copy the file
    fs::copy(source_path, dest_path)?;

    Ok(true)
}

/// Copy a directory from source to destination
pub fn copy_directory<P: AsRef<Path>, Q: AsRef<Path>>(
    source: P,
    destination: Q,
    recursive: bool
) -> Result<bool> {
    // Implementation using Rust's standard library
    let source_path = source.as_ref();
    let dest_path = destination.as_ref();

    // Check if source exists and is a directory
    if !source_path.exists() {
        return Err(anyhow!("Source directory does not exist: {}", source_path.display()));
    }

    if !source_path.is_dir() {
        return Err(anyhow!("Source is not a directory: {}", source_path.display()));
    }

    // Create destination directory if it doesn't exist
    if !dest_path.exists() {
        fs::create_dir_all(dest_path)?;
    }

    // Copy all entries in the directory
    for entry in fs::read_dir(source_path)? {
        let entry = entry?;
        let entry_path = entry.path();
        let file_name = entry.file_name();
        let dest_entry_path = dest_path.join(file_name);

        if entry_path.is_file() {
            fs::copy(&entry_path, &dest_entry_path)?;
        } else if entry_path.is_dir() && recursive {
            copy_directory(&entry_path, &dest_entry_path, recursive)?;
        }
    }

    Ok(true)
}

/// Get the version of the EACopy library
pub fn get_version() -> Result<String> {
    // Return a fixed version string
    Ok("1.0.0".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::io::Write;
    use tempfile::tempdir;

    #[test]
    fn test_get_version() {
        let version = get_version();
        assert!(version.is_ok());
        let version_str = version.unwrap();
        assert!(!version_str.is_empty());
    }

    #[test]
    fn test_copy_file() -> Result<()> {
        // Create a temporary directory
        let temp_dir = tempdir()?;

        // Create a source file
        let source_path = temp_dir.path().join("source.txt");
        let mut source_file = fs::File::create(&source_path)?;
        writeln!(source_file, "This is a test file.")?;

        // Create a destination path
        let dest_path = temp_dir.path().join("dest.txt");

        // Copy the file
        let result = copy_file(&source_path, &dest_path)?;
        assert!(result);

        // Check if the file was copied
        assert!(dest_path.exists());

        Ok(())
    }

    #[test]
    fn test_copy_directory() -> Result<()> {
        // Create a temporary directory
        let temp_dir = tempdir()?;

        // Create a source directory
        let source_dir = temp_dir.path().join("source");
        fs::create_dir(&source_dir)?;

        // Create a file in the source directory
        let file_path = source_dir.join("test.txt");
        let mut file = fs::File::create(&file_path)?;
        writeln!(file, "This is a test file.")?;

        // Create a destination directory path
        let dest_dir = temp_dir.path().join("dest");

        // Copy the directory
        let result = copy_directory(&source_dir, &dest_dir, true)?;
        assert!(result);

        // Check if the directory was copied
        assert!(dest_dir.exists());
        assert!(dest_dir.join("test.txt").exists());

        Ok(())
    }
}
