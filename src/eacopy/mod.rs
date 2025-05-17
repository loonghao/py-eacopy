// Main EACopy implementation module
// This module provides the high-level API for EACopy operations

use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

use crate::bindings;
use crate::config::{Config, ErrorStrategy, global_config};
use crate::error::{Error, Result};

// Re-export types
pub use crate::config::{Config, ErrorStrategy, LogLevel};
pub use crate::bindings::EACopyServer;

/// EACopy class for file copy operations
pub struct EACopy {
    config: Config,
}

impl EACopy {
    /// Create a new EACopy instance with default configuration
    pub fn new() -> Self {
        let config = global_config().lock().unwrap().clone();
        EACopy { config }
    }

    /// Create a new EACopy instance with custom configuration
    pub fn with_config(config: Config) -> Self {
        EACopy { config }
    }

    /// Copy file content from src to dst
    pub fn copyfile<P: AsRef<Path>, Q: AsRef<Path>>(&self, src: P, dst: Q) -> Result<()> {
        let src_path = src.as_ref();
        let dst_path = dst.as_ref();

        // Check if source exists
        if !src_path.exists() {
            return Err(Error::FileNotFound(src_path.to_path_buf()));
        }

        // Check if source is a file
        if !src_path.is_file() {
            return Err(Error::InvalidArgument(format!(
                "Source is not a file: {}",
                src_path.display()
            )));
        }

        // Create parent directory if it doesn't exist
        if let Some(parent) = dst_path.parent() {
            if !parent.exists() {
                std::fs::create_dir_all(parent)?;
            }
        }

        // Copy the file
        bindings::copy_file(src_path, dst_path, false)?;

        Ok(())
    }

    /// Copy a file from src to dst, preserving file content but not metadata
    pub fn copy<P: AsRef<Path>, Q: AsRef<Path>>(&self, src: P, dst: Q) -> Result<()> {
        let src_path = src.as_ref();
        let dst_path = dst.as_ref();

        // Check if source exists
        if !src_path.exists() {
            return Err(Error::FileNotFound(src_path.to_path_buf()));
        }

        // If source is a directory, error
        if src_path.is_dir() {
            return Err(Error::InvalidArgument(format!(
                "Source is a directory, use copytree instead: {}",
                src_path.display()
            )));
        }

        // If destination is a directory, copy to a file inside that directory
        let dst_path = if dst_path.is_dir() {
            if let Some(file_name) = src_path.file_name() {
                dst_path.join(file_name)
            } else {
                return Err(Error::InvalidArgument(format!(
                    "Source has no file name: {}",
                    src_path.display()
                )));
            }
        } else {
            dst_path.to_path_buf()
        };

        // Create parent directory if it doesn't exist
        if let Some(parent) = dst_path.parent() {
            if !parent.exists() {
                std::fs::create_dir_all(parent)?;
            }
        }

        // Copy the file
        bindings::copy_file(src_path, &dst_path, false)?;

        Ok(())
    }

    /// Copy a file from src to dst, preserving file content and metadata
    pub fn copy2<P: AsRef<Path>, Q: AsRef<Path>>(&self, src: P, dst: Q) -> Result<()> {
        let src_path = src.as_ref();
        let dst_path = dst.as_ref();

        // Check if source exists
        if !src_path.exists() {
            return Err(Error::FileNotFound(src_path.to_path_buf()));
        }

        // If source is a directory, error
        if src_path.is_dir() {
            return Err(Error::InvalidArgument(format!(
                "Source is a directory, use copytree instead: {}",
                src_path.display()
            )));
        }

        // If destination is a directory, copy to a file inside that directory
        let dst_path = if dst_path.is_dir() {
            if let Some(file_name) = src_path.file_name() {
                dst_path.join(file_name)
            } else {
                return Err(Error::InvalidArgument(format!(
                    "Source has no file name: {}",
                    src_path.display()
                )));
            }
        } else {
            dst_path.to_path_buf()
        };

        // Create parent directory if it doesn't exist
        if let Some(parent) = dst_path.parent() {
            if !parent.exists() {
                std::fs::create_dir_all(parent)?;
            }
        }

        // Copy the file with metadata
        bindings::copy_file(src_path, &dst_path, true)?;

        Ok(())
    }

    /// Recursively copy a directory tree from src to dst
    pub fn copytree<P: AsRef<Path>, Q: AsRef<Path>>(
        &self,
        src: P,
        dst: Q,
        symlinks: bool,
        ignore_dangling_symlinks: bool,
        dirs_exist_ok: bool,
    ) -> Result<()> {
        let src_path = src.as_ref();
        let dst_path = dst.as_ref();

        // Check if source exists
        if !src_path.exists() {
            return Err(Error::DirectoryNotFound(src_path.to_path_buf()));
        }

        // Check if source is a directory
        if !src_path.is_dir() {
            return Err(Error::InvalidArgument(format!(
                "Source is not a directory: {}",
                src_path.display()
            )));
        }

        // Copy the directory tree
        bindings::copy_tree(
            src_path,
            dst_path,
            symlinks,
            ignore_dangling_symlinks,
            dirs_exist_ok,
        )?;

        Ok(())
    }

    /// Copy file or directory using EACopyService for acceleration
    pub fn copy_with_server<P: AsRef<Path>, Q: AsRef<Path>>(
        &self,
        src: P,
        dst: Q,
        server_addr: &str,
        port: u16,
        compression_level: u32,
    ) -> Result<()> {
        let src_path = src.as_ref();
        let dst_path = dst.as_ref();

        // Check if source exists
        if !src_path.exists() {
            return Err(Error::FileNotFound(src_path.to_path_buf()));
        }

        // Copy with server
        bindings::copy_with_server(
            src_path,
            dst_path,
            server_addr,
            port,
            compression_level,
        )?;

        Ok(())
    }

    /// Copy multiple files in batch
    pub fn batch_copy<P: AsRef<Path>, Q: AsRef<Path>>(
        &self,
        file_pairs: &[(P, Q)],
    ) -> Result<()> {
        // Convert to references
        let pairs: Vec<(&Path, &Path)> = file_pairs
            .iter()
            .map(|(src, dst)| (src.as_ref(), dst.as_ref()))
            .collect();

        // Use the bindings function
        bindings::batch_copy(&pairs, false)?;

        Ok(())
    }

    /// Copy multiple files with metadata in batch
    pub fn batch_copy2<P: AsRef<Path>, Q: AsRef<Path>>(
        &self,
        file_pairs: &[(P, Q)],
    ) -> Result<()> {
        // Convert to references
        let pairs: Vec<(&Path, &Path)> = file_pairs
            .iter()
            .map(|(src, dst)| (src.as_ref(), dst.as_ref()))
            .collect();

        // Use the bindings function
        bindings::batch_copy(&pairs, true)?;

        Ok(())
    }

    /// Copy multiple directory trees in batch
    pub fn batch_copytree<P: AsRef<Path>, Q: AsRef<Path>>(
        &self,
        dir_pairs: &[(P, Q)],
        symlinks: bool,
        ignore_dangling_symlinks: bool,
        dirs_exist_ok: bool,
    ) -> Result<()> {
        // Convert to references
        let pairs: Vec<(&Path, &Path)> = dir_pairs
            .iter()
            .map(|(src, dst)| (src.as_ref(), dst.as_ref()))
            .collect();

        // Use the bindings function
        bindings::batch_copy_tree(&pairs, symlinks, ignore_dangling_symlinks, dirs_exist_ok)?;

        Ok(())
    }

    /// Set the progress callback function
    pub fn set_progress_callback<F>(&mut self, callback: F)
    where
        F: Fn(u64, u64, &str) + Send + Sync + 'static,
    {
        self.config.progress_callback = Some(Arc::new(callback));
    }

    /// Get the current configuration
    pub fn get_config(&self) -> &Config {
        &self.config
    }

    /// Update the configuration
    pub fn set_config(&mut self, config: Config) {
        self.config = config;
    }

    /// Create a new EACopy server
    pub fn create_server(&self, port: u16) -> Result<EACopyServer> {
        bindings::EACopyServer::new(port, self.config.thread_count)
    }

    /// Perform delta copy using a reference file
    pub fn delta_copy<P: AsRef<Path>, Q: AsRef<Path>, R: AsRef<Path>>(
        &self,
        src: P,
        dst: Q,
        reference: R,
    ) -> Result<()> {
        let src_path = src.as_ref();
        let dst_path = dst.as_ref();
        let reference_path = reference.as_ref();

        // Check if source exists
        if !src_path.exists() {
            return Err(Error::FileNotFound(src_path.to_path_buf()));
        }

        // Check if reference exists
        if !reference_path.exists() {
            return Err(Error::FileNotFound(reference_path.to_path_buf()));
        }

        // Check if source and reference are files
        if !src_path.is_file() || !reference_path.is_file() {
            return Err(Error::InvalidArgument(format!(
                "Source and reference must be files: {} and {}",
                src_path.display(),
                reference_path.display()
            )));
        }

        // Create parent directory if it doesn't exist
        if let Some(parent) = dst_path.parent() {
            if !parent.exists() {
                std::fs::create_dir_all(parent)?;
            }
        }

        // Perform delta copy
        bindings::delta_copy(
            src_path,
            dst_path,
            reference_path,
            self.config.compression_level,
        )?;

        Ok(())
    }
}

impl Default for EACopy {
    fn default() -> Self {
        Self::new()
    }
}

// Standalone functions that use the global configuration

/// Copy file content from src to dst
pub fn copyfile<P: AsRef<Path>, Q: AsRef<Path>>(src: P, dst: Q) -> Result<()> {
    let eacopy = EACopy::new();
    eacopy.copyfile(src, dst)
}

/// Copy a file from src to dst, preserving file content but not metadata
pub fn copy<P: AsRef<Path>, Q: AsRef<Path>>(src: P, dst: Q) -> Result<()> {
    let eacopy = EACopy::new();
    eacopy.copy(src, dst)
}

/// Copy a file from src to dst, preserving file content and metadata
pub fn copy2<P: AsRef<Path>, Q: AsRef<Path>>(src: P, dst: Q) -> Result<()> {
    let eacopy = EACopy::new();
    eacopy.copy2(src, dst)
}

/// Recursively copy a directory tree from src to dst
pub fn copytree<P: AsRef<Path>, Q: AsRef<Path>>(
    src: P,
    dst: Q,
    symlinks: bool,
    ignore_dangling_symlinks: bool,
    dirs_exist_ok: bool,
) -> Result<()> {
    let eacopy = EACopy::new();
    eacopy.copytree(src, dst, symlinks, ignore_dangling_symlinks, dirs_exist_ok)
}

/// Copy file or directory using EACopyService for acceleration
pub fn copy_with_server<P: AsRef<Path>, Q: AsRef<Path>>(
    src: P,
    dst: Q,
    server_addr: &str,
    port: u16,
    compression_level: u32,
) -> Result<()> {
    let eacopy = EACopy::new();
    eacopy.copy_with_server(src, dst, server_addr, port, compression_level)
}

/// Copy multiple files in batch
pub fn batch_copy<P: AsRef<Path>, Q: AsRef<Path>>(file_pairs: &[(P, Q)]) -> Result<()> {
    let eacopy = EACopy::new();
    eacopy.batch_copy(file_pairs)
}

/// Copy multiple files with metadata in batch
pub fn batch_copy2<P: AsRef<Path>, Q: AsRef<Path>>(file_pairs: &[(P, Q)]) -> Result<()> {
    let eacopy = EACopy::new();
    eacopy.batch_copy2(file_pairs)
}

/// Copy multiple directory trees in batch
pub fn batch_copytree<P: AsRef<Path>, Q: AsRef<Path>>(
    dir_pairs: &[(P, Q)],
    symlinks: bool,
    ignore_dangling_symlinks: bool,
    dirs_exist_ok: bool,
) -> Result<()> {
    let eacopy = EACopy::new();
    eacopy.batch_copytree(dir_pairs, symlinks, ignore_dangling_symlinks, dirs_exist_ok)
}

/// Create a new EACopy server
pub fn create_server(port: u16, thread_count: usize) -> Result<EACopyServer> {
    EACopyServer::new(port, thread_count)
}

/// Perform delta copy using a reference file
pub fn delta_copy<P: AsRef<Path>, Q: AsRef<Path>, R: AsRef<Path>>(
    src: P,
    dst: Q,
    reference: R,
) -> Result<()> {
    let eacopy = EACopy::new();
    eacopy.delta_copy(src, dst, reference)
}
