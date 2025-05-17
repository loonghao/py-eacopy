// This module contains the raw FFI bindings to the EACopy C++ library
// Generated bindings are included from the build script

// Include the generated bindings
#![allow(non_upper_case_globals)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(dead_code)]
#![allow(clippy::all)]

// Include the generated bindings
include!(concat!(env!("OUT_DIR"), "/bindings.rs"));

// Safe wrappers around the raw FFI bindings
use std::ffi::{c_void, CStr, CString};
use std::path::Path;
use std::ptr;

use crate::error::{Error, Result};
use crate::utils;

// EACopy file flags
pub const EACOPY_COPY_DATA: u32 = 1;
pub const EACOPY_COPY_ATTRIBUTES: u32 = 2;
pub const EACOPY_COPY_TIMESTAMPS: u32 = 4;

// Safe wrapper for copyFile function
pub fn copy_file(source: &Path, dest: &Path, preserve_metadata: bool) -> Result<u64> {
    let source_wide = utils::path_to_wide_string(source);
    let dest_wide = utils::path_to_wide_string(dest);

    let mut bytes_copied: u64 = 0;
    let mut existed: bool = false;
    let mut error_code: u32 = 0;
    let mut io_stats = unsafe { std::mem::zeroed::<eacopy::IOStats>() };

    let flags = if preserve_metadata {
        EACOPY_COPY_DATA | EACOPY_COPY_ATTRIBUTES | EACOPY_COPY_TIMESTAMPS
    } else {
        EACOPY_COPY_DATA
    };

    // Check if source exists and get its size
    let mut file_info = unsafe { std::mem::zeroed::<eacopy::FileInfo>() };
    let mut attributes: u32 = 0;

    unsafe {
        if !eacopy::getFileAttributes(
            source_wide.as_ptr(),
            &mut file_info,
            &mut attributes,
            &mut error_code,
            ptr::null_mut(),
        ) {
            return Err(from_error_code(error_code as i32, Some(&source.to_path_buf())));
        }

        // Optimize buffer size based on file size
        let buffer_size = if file_info.size < 1024 * 1024 {
            // Small files (< 1MB): Use 64KB buffer
            64 * 1024
        } else if file_info.size < 100 * 1024 * 1024 {
            // Medium files (1MB - 100MB): Use 1MB buffer
            1024 * 1024
        } else {
            // Large files (> 100MB): Use 8MB buffer
            8 * 1024 * 1024
        };

        // Use buffered I/O for better performance
        let use_buffered_io = eacopy::UseBufferedIO_Yes;

        // Copy the file
        let result = eacopy::copyFile(
            source_wide.as_ptr(),
            dest_wide.as_ptr(),
            false, // useSystemCopy
            false, // failIfExists
            &mut existed as *mut bool,
            &mut bytes_copied as *mut u64,
            &mut io_stats as *mut eacopy::IOStats,
            use_buffered_io,
        );

        if result {
            Ok(bytes_copied)
        } else {
            let error = std::io::Error::last_os_error();
            Err(Error::Io(error))
        }
    }
}

// Safe wrapper for copyTree function
pub fn copy_tree(
    source: &Path,
    dest: &Path,
    symlinks: bool,
    ignore_dangling_symlinks: bool,
    dirs_exist_ok: bool,
) -> Result<u64> {
    let source_wide = utils::path_to_wide_string(source);
    let dest_wide = utils::path_to_wide_string(dest);

    let mut total_bytes: u64 = 0;
    let mut error_code: u32 = 0;

    unsafe {
        // Create the destination directory if it doesn't exist
        if !dest.exists() {
            if !eacopy::createDirectory(dest_wide.as_ptr(), &mut error_code) {
                return Err(from_error_code(error_code as i32, Some(&dest.to_path_buf())));
            }
        } else if !dirs_exist_ok {
            return Err(Error::DestinationExists(dest.to_path_buf()));
        }

        // Use EACopy's findFiles function to get all files in the source directory
        let mut find_data = std::mem::zeroed::<eacopy::FindData>();
        let source_wildcard = utils::path_to_wide_string(&source.join("*"));

        let find_handle = eacopy::findFirstFile(source_wildcard.as_ptr(), &mut find_data, &mut error_code);
        if find_handle == eacopy::INVALID_HANDLE_VALUE {
            return Err(from_error_code(error_code as i32, Some(&source.to_path_buf())));
        }

        defer! {
            eacopy::findClose(find_handle);
        }

        // Process the first file
        let mut has_more = true;

        while has_more {
            // Get the file name
            let file_name = utils::from_wide_string(find_data.fileName.as_ptr())?;

            // Skip "." and ".." directories
            if file_name != "." && file_name != ".." {
                let source_path = source.join(&file_name);
                let dest_path = dest.join(&file_name);

                // Check if it's a directory
                if find_data.isDirectory() {
                    // Recursively copy the directory
                    let bytes = copy_tree(&source_path, &dest_path, symlinks, ignore_dangling_symlinks, dirs_exist_ok)?;
                    total_bytes += bytes;
                } else if find_data.isSymbolicLink() && symlinks {
                    // Handle symlinks
                    if let Ok(target) = std::fs::read_link(&source_path) {
                        if target.exists() || !ignore_dangling_symlinks {
                            std::os::windows::fs::symlink_file(&target, &dest_path)?;
                        }
                    }
                } else {
                    // Copy the file with metadata
                    let bytes = copy_file(&source_path, &dest_path, true)?;
                    total_bytes += bytes;
                }
            }

            // Find the next file
            has_more = eacopy::findNextFile(find_handle, &mut find_data, &mut error_code);
            if !has_more && error_code != 0 && error_code != 18 { // ERROR_NO_MORE_FILES
                return Err(from_error_code(error_code as i32, Some(&source.to_path_buf())));
            }
        }

        Ok(total_bytes)
    }
}

// Safe wrapper for copyWithServer function
pub fn copy_with_server(
    source: &Path,
    dest: &Path,
    server_addr: &str,
    port: u16,
    compression_level: u32,
) -> Result<u64> {
    let source_wide = utils::path_to_wide_string(source);
    let dest_wide = utils::path_to_wide_string(dest);

    // Convert server address to wide string
    let server_addr_wide = utils::to_wide_string(server_addr);

    // Create client settings
    let mut settings = unsafe { std::mem::zeroed::<eacopy::ClientSettings>() };
    settings.port = port as u32;
    settings.compressionLevel = compression_level;
    settings.maxThreads = 8; // Default to 8 threads
    settings.bufferSize = 8 * 1024 * 1024; // Default to 8MB buffer
    settings.retryCount = 3; // Default to 3 retries
    settings.retryDelay = 1000; // Default to 1 second delay
    settings.timeout = 30000; // Default to 30 seconds timeout

    // Create client stats
    let mut stats = unsafe { std::mem::zeroed::<eacopy::ClientStats>() };

    // Create client
    let mut client = unsafe { std::mem::zeroed::<eacopy::Client>() };

    unsafe {
        // Initialize client
        if !eacopy::createClient(&mut client, &settings, &mut stats) {
            return Err(Error::Network(format!(
                "Failed to create client connection to server {}:{}",
                server_addr, port
            )));
        }

        // Ensure client is destroyed when we're done
        defer! {
            eacopy::destroyClient(&mut client);
        }

        // Copy file or directory
        let mut total_bytes: u64 = 0;

        if source.is_file() {
            // Copy file
            let mut file_info = std::mem::zeroed::<eacopy::FileInfo>();
            let mut attributes: u32 = 0;
            let mut error_code: u32 = 0;

            // Get file info
            if !eacopy::getFileAttributes(
                source_wide.as_ptr(),
                &mut file_info,
                &mut attributes,
                &mut error_code,
                std::ptr::null_mut()
            ) {
                return Err(Error::from_error_code(error_code as i32, Some(&source.to_path_buf())));
            }

            // Copy file
            let mut processed_by_server = false;
            let mut out_size: u64 = 0;
            let mut out_read: u64 = 0;
            let mut copy_context = std::mem::zeroed::<eacopy::NetworkCopyContext>();

            let result = eacopy::sendReadFileCommand(
                &mut client,
                source_wide.as_ptr(),
                dest_wide.as_ptr(),
                &file_info,
                attributes,
                &mut out_size,
                &mut out_read,
                &mut copy_context,
                &mut processed_by_server,
            );

            match result {
                eacopy::ReadFileResult_ReadFileResult_Success => {
                    total_bytes = out_read;
                    Ok(total_bytes)
                },
                eacopy::ReadFileResult_ReadFileResult_ServerBusy => {
                    Err(Error::Network(format!(
                        "Server {}:{} is busy, try again later",
                        server_addr, port
                    )))
                },
                _ => {
                    let error = std::io::Error::last_os_error();
                    Err(Error::Network(format!(
                        "Failed to copy file {} to {} via server {}:{}: {}",
                        source.display(), dest.display(), server_addr, port, error
                    )))
                },
            }
        } else if source.is_dir() {
            // Copy directory
            // First, create destination directory
            let mut created_dirs = std::mem::zeroed::<eacopy::FilesSet>();

            if !eacopy::sendCreateDirectoryCommand(&mut client, dest_wide.as_ptr(), &mut created_dirs) {
                let error = std::io::Error::last_os_error();
                return Err(Error::Network(format!(
                    "Failed to create directory {} on server {}:{}: {}",
                    dest.display(), server_addr, port, error
                )));
            }

            // Then, find all files in source directory
            let mut files = std::mem::zeroed::<eacopy::Vector<eacopy::NameAndFileInfo>>();
            let mut copy_context = std::mem::zeroed::<eacopy::CopyContext>();

            let source_wildcard = utils::path_to_wide_string(&source.join("*"));

            if !eacopy::sendFindFiles(&mut client, source_wildcard.as_ptr(), &mut files, &mut copy_context) {
                let error = std::io::Error::last_os_error();
                return Err(Error::Network(format!(
                    "Failed to list files in directory {} on server {}:{}: {}",
                    source.display(), server_addr, port, error
                )));
            }

            // Copy each file
            for i in 0..files.size {
                let file = files.data.offset(i as isize);
                let file_name = utils::from_wide_string((*file).name.as_ptr())?;
                let source_file = source.join(&file_name);
                let dest_file = dest.join(&file_name);

                // Check if it's a directory
                if (*file).info.isDirectory() {
                    // Create directory on server
                    let dest_file_wide = utils::path_to_wide_string(&dest_file);
                    if !eacopy::sendCreateDirectoryCommand(&mut client, dest_file_wide.as_ptr(), &mut created_dirs) {
                        let error = std::io::Error::last_os_error();
                        return Err(Error::Network(format!(
                            "Failed to create directory {} on server {}:{}: {}",
                            dest_file.display(), server_addr, port, error
                        )));
                    }

                    // Recursively copy directory
                    let bytes = copy_with_server(&source_file, &dest_file, server_addr, port, compression_level)?;
                    total_bytes += bytes;
                } else {
                    // Copy file
                    let bytes = copy_with_server(&source_file, &dest_file, server_addr, port, compression_level)?;
                    total_bytes += bytes;
                }
            }

            Ok(total_bytes)
        } else {
            Err(Error::InvalidArgument(format!(
                "Source is neither a file nor a directory: {}",
                source.display()
            )))
        }
    }
}

// Safe wrapper for batch operations
pub fn batch_copy(file_pairs: &[(&Path, &Path)], preserve_metadata: bool) -> Result<u64> {
    let mut total_bytes: u64 = 0;

    for (src, dst) in file_pairs {
        let bytes = copy_file(src, dst, preserve_metadata)?;
        total_bytes += bytes;
    }

    Ok(total_bytes)
}

// Safe wrapper for batch directory operations
pub fn batch_copy_tree(
    dir_pairs: &[(&Path, &Path)],
    symlinks: bool,
    ignore_dangling_symlinks: bool,
    dirs_exist_ok: bool,
) -> Result<u64> {
    let mut total_bytes: u64 = 0;

    for (src, dst) in dir_pairs {
        let bytes = copy_tree(src, dst, symlinks, ignore_dangling_symlinks, dirs_exist_ok)?;
        total_bytes += bytes;
    }

    Ok(total_bytes)
}

// Safe wrapper for server management
pub struct EACopyServer {
    server: *mut eacopy::Server,
    settings: eacopy::ServerSettings,
    stats: eacopy::ServerStats,
}

impl EACopyServer {
    pub fn new(port: u16, thread_count: usize) -> Result<Self> {
        unsafe {
            let mut server = std::mem::zeroed::<eacopy::Server>();
            let mut settings = std::mem::zeroed::<eacopy::ServerSettings>();
            let mut stats = std::mem::zeroed::<eacopy::ServerStats>();

            // Configure server settings
            settings.port = port as u32;
            settings.maxThreads = thread_count as u32;
            settings.bufferSize = 8 * 1024 * 1024; // 8MB buffer

            // Create server
            if !eacopy::createServer(&mut server, &settings, &mut stats) {
                let error = std::io::Error::last_os_error();
                return Err(Error::Network(format!(
                    "Failed to create EACopy server on port {}: {}",
                    port, error
                )));
            }

            Ok(Self {
                server: &mut server as *mut _,
                settings,
                stats,
            })
        }
    }

    pub fn start(&self) -> Result<()> {
        unsafe {
            if !eacopy::startServer(self.server) {
                let error = std::io::Error::last_os_error();
                return Err(Error::Network(format!(
                    "Failed to start EACopy server on port {}: {}",
                    self.settings.port, error
                )));
            }

            Ok(())
        }
    }

    pub fn stop(&self) -> Result<()> {
        unsafe {
            if !eacopy::stopServer(self.server) {
                let error = std::io::Error::last_os_error();
                return Err(Error::Network(format!(
                    "Failed to stop EACopy server on port {}: {}",
                    self.settings.port, error
                )));
            }

            Ok(())
        }
    }

    pub fn is_running(&self) -> bool {
        unsafe {
            eacopy::isServerRunning(self.server)
        }
    }

    pub fn get_stats(&self) -> eacopy::ServerStats {
        unsafe {
            let mut stats = std::mem::zeroed::<eacopy::ServerStats>();
            eacopy::getServerStats(self.server, &mut stats);
            stats
        }
    }

    pub fn get_port(&self) -> u16 {
        self.settings.port as u16
    }

    pub fn get_thread_count(&self) -> usize {
        self.settings.maxThreads as usize
    }
}

impl Drop for EACopyServer {
    fn drop(&mut self) {
        unsafe {
            if self.is_running() {
                let _ = self.stop();
            }
            eacopy::destroyServer(self.server);
        }
    }
}

// Safe wrapper for delta copy operations
pub fn delta_copy(
    source: &Path,
    dest: &Path,
    reference: &Path,
    compression_level: u32,
) -> Result<u64> {
    let source_wide = utils::path_to_wide_string(source);
    let dest_wide = utils::path_to_wide_string(dest);
    let reference_wide = utils::path_to_wide_string(reference);

    unsafe {
        // Open files
        let source_file = eacopy::openFile(
            source_wide.as_ptr(),
            eacopy::FileOpenMode_FileOpenMode_Read,
            0,
            std::ptr::null_mut(),
        );
        if source_file == eacopy::INVALID_FILE_HANDLE {
            return Err(Error::Io(std::io::Error::last_os_error()));
        }

        defer! {
            eacopy::closeFile(source_file);
        }

        let dest_file = eacopy::openFile(
            dest_wide.as_ptr(),
            eacopy::FileOpenMode_FileOpenMode_Write,
            0,
            std::ptr::null_mut(),
        );
        if dest_file == eacopy::INVALID_FILE_HANDLE {
            return Err(Error::Io(std::io::Error::last_os_error()));
        }

        defer! {
            eacopy::closeFile(dest_file);
        }

        let reference_file = eacopy::openFile(
            reference_wide.as_ptr(),
            eacopy::FileOpenMode_FileOpenMode_Read,
            0,
            std::ptr::null_mut(),
        );
        if reference_file == eacopy::INVALID_FILE_HANDLE {
            return Err(Error::Io(std::io::Error::last_os_error()));
        }

        defer! {
            eacopy::closeFile(reference_file);
        }

        // Get file sizes
        let mut source_size: u64 = 0;
        let mut reference_size: u64 = 0;

        if !eacopy::getFileSize(source_file, &mut source_size, std::ptr::null_mut()) {
            return Err(Error::Io(std::io::Error::last_os_error()));
        }

        if !eacopy::getFileSize(reference_file, &mut reference_size, std::ptr::null_mut()) {
            return Err(Error::Io(std::io::Error::last_os_error()));
        }

        // Perform delta copy
        let mut copy_context = std::mem::zeroed::<eacopy::NetworkCopyContext>();
        let mut io_stats = std::mem::zeroed::<eacopy::IOStats>();
        let mut socket_time: u64 = 0;
        let mut socket_size: u64 = 0;
        let mut code_time: u64 = 0;

        let result = eacopy::deltaCopy(
            true, // encode
            std::ptr::null_mut(), // socket
            reference_wide.as_ptr(),
            reference_file,
            reference_size,
            source_wide.as_ptr(),
            source_file,
            source_size,
            &mut copy_context,
            &mut io_stats,
            &mut socket_time,
            &mut socket_size,
            &mut code_time,
        );

        if !result {
            return Err(Error::Io(std::io::Error::last_os_error()));
        }

        Ok(source_size)
    }
}

// Macro for resource cleanup
macro_rules! defer {
    ($($body:tt)*) => {
        let _guard = {
            struct Guard<F: FnOnce()>(Option<F>);
            impl<F: FnOnce()> Drop for Guard<F> {
                fn drop(&mut self) {
                    if let Some(f) = self.0.take() {
                        f()
                    }
                }
            }
            Guard(Some(|| { $($body)* }))
        };
    };
}
