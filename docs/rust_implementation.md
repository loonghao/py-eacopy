# Rust Implementation

This document describes the Rust implementation of py-eacopy, which provides Python bindings to the EACopy C++ library using Rust's FFI capabilities and PyO3.

## Architecture

The Rust implementation of py-eacopy follows a layered architecture:

1. **FFI Layer**: Rust bindings to the EACopy C++ library using FFI.
2. **Rust API Layer**: Safe Rust wrappers around the FFI bindings.
3. **Python Bindings Layer**: PyO3 bindings that expose the Rust API to Python.
4. **Python API Layer**: Python modules that provide a user-friendly API.

```
┌───────────────────┐
│   Python API      │ <- User-facing API (py_eacopy module)
├───────────────────┤
│  Python Bindings  │ <- PyO3 bindings (_eacopy_binding module)
├───────────────────┤
│    Rust API       │ <- Safe Rust wrappers (eacopy module)
├───────────────────┤
│      FFI          │ <- Raw FFI bindings (bindings module)
├───────────────────┤
│    EACopy C++     │ <- EACopy C++ library
└───────────────────┘
```

## Building from Source

### Prerequisites

- Rust toolchain (rustc, cargo)
- Python 3.8 or later
- CMake 3.15 or later
- C++ compiler (MSVC on Windows, GCC on Linux, Clang on macOS)

### Build Steps

1. Clone the repository:

```bash
git clone https://github.com/loonghao/py-eacopy.git
cd py-eacopy
```

2. Build the package using maturin:

```bash
# Install maturin
pip install maturin

# Build in development mode
maturin develop

# Or build a wheel
maturin build --release
```

3. Or build using nox:

```bash
# Install nox
pip install nox

# Build in development mode
nox -s develop

# Or build a wheel
nox -s build-wheel
```

## API Reference

### Python API

The Python API is designed to be compatible with the original py-eacopy API, providing a familiar interface for users.

#### Basic File Operations

- `copy(src, dst)`: Copy a file from src to dst, preserving file content but not metadata.
- `copy2(src, dst)`: Copy a file from src to dst, preserving file content and metadata.
- `copyfile(src, dst)`: Copy file content from src to dst.
- `copytree(src, dst, symlinks=False, ignore_dangling_symlinks=False, dirs_exist_ok=False)`: Recursively copy a directory tree from src to dst.

#### Network Operations

- `copy_with_server(src, dst, server_addr, port=31337, compression_level=0)`: Copy file or directory using EACopyService for acceleration.
- `create_server(port=31337, thread_count=4)`: Create a new EACopy server for network file transfers.

#### Delta Copy Operations

- `delta_copy(src, dst, reference)`: Perform delta copy using a reference file.

#### Batch Operations

- `batch_copy(file_pairs)`: Copy multiple files in batch.
- `batch_copy2(file_pairs)`: Copy multiple files with metadata in batch.
- `batch_copytree(dir_pairs, symlinks=False, ignore_dangling_symlinks=False, dirs_exist_ok=False)`: Copy multiple directory trees in batch.

#### Asynchronous Functions

- `async_copy(src, dst)`: Asynchronous version of copy function.
- `async_copy2(src, dst)`: Asynchronous version of copy2 function.
- `async_copyfile(src, dst)`: Asynchronous version of copyfile function.
- `async_copytree(src, dst, symlinks=False, ignore_dangling_symlinks=False, dirs_exist_ok=False)`: Asynchronous version of copytree function.
- `async_copy_with_server(src, dst, server_addr, port=31337, compression_level=0)`: Asynchronous version of copy_with_server function.
- `async_delta_copy(src, dst, reference)`: Asynchronous version of delta_copy function.

#### Classes

##### EACopy

Wrapper class for EACopy functionality.

- `__init__(thread_count=4, compression_level=0, buffer_size=8*1024*1024, preserve_metadata=True, follow_symlinks=False, dirs_exist_ok=False, progress_callback=None)`: Initialize EACopy with custom configuration.
- `copyfile(src, dst)`: Copy file content from src to dst.
- `copy(src, dst)`: Copy a file from src to dst, preserving file content but not metadata.
- `copy2(src, dst)`: Copy a file from src to dst, preserving file content and metadata.
- `copytree(src, dst, symlinks=False, ignore_dangling_symlinks=False, dirs_exist_ok=False)`: Recursively copy a directory tree from src to dst.
- `copy_with_server(src, dst, server_addr, port=31337, compression_level=0)`: Copy file or directory using EACopyService for acceleration.
- `create_server(port=31337)`: Create a new EACopy server.
- `delta_copy(src, dst, reference)`: Perform delta copy using a reference file.
- `batch_copy(file_pairs)`: Copy multiple files in batch.
- `batch_copy2(file_pairs)`: Copy multiple files with metadata in batch.
- `batch_copytree(dir_pairs, symlinks=False, ignore_dangling_symlinks=False, dirs_exist_ok=False)`: Copy multiple directory trees in batch.
- `set_progress_callback(callback)`: Set the progress callback function.

##### EACopyServer

Wrapper class for EACopy server functionality.

- `__init__(port=31337, thread_count=4)`: Initialize a new EACopy server.
- `start()`: Start the server.
- `stop()`: Stop the server.
- `is_running()`: Check if the server is running.
- `get_stats()`: Get server statistics.
- `port`: The port the server is listening on.
- `thread_count`: The number of threads the server is using.

##### Config

Global configuration options for EACopy.

- `thread_count`: Default number of threads to use for copy operations.
- `compression_level`: Default compression level (0-9) for network transfers.
- `buffer_size`: Size of the buffer used for copy operations (in bytes).
- `error_strategy`: How to handle errors during copy operations.
- `retry_count`: Number of retries for failed operations when error_strategy is RETRY.
- `retry_delay`: Delay between retries in seconds.
- `log_level`: Verbosity level for logging.
- `preserve_metadata`: Whether to preserve file metadata by default.
- `follow_symlinks`: Whether to follow symbolic links by default.
- `dirs_exist_ok`: Whether to allow existing directories by default.
- `progress_callback`: Function to call to report progress.

#### Enums

##### ErrorStrategy

Error handling strategies.

- `RAISE`: Raise exceptions immediately.
- `RETRY`: Retry the operation.
- `IGNORE`: Ignore errors and continue.

##### LogLevel

Log levels for EACopy operations.

- `NONE`: No logging.
- `ERROR`: Error level logging.
- `WARNING`: Warning level logging.
- `INFO`: Info level logging.
- `DEBUG`: Debug level logging.

#### Callback Types

- `ProgressCallback`: Type for progress callback function. Signature: `(copied_bytes: int, total_bytes: int, filename: str) -> None`

### Rust API

The Rust API provides a safe interface to the EACopy C++ library.

#### Modules

- `eacopy`: Main EACopy implementation module.
- `bindings`: Raw FFI bindings to the EACopy C++ library.
- `error`: Error handling module.
- `config`: Configuration module.
- `utils`: Utility functions.

#### Core Structs

##### EACopy

Main EACopy class for file copy operations.

- `new()`: Create a new EACopy instance with default configuration.
- `with_config(config: Config)`: Create a new EACopy instance with custom configuration.
- `copyfile(src: impl AsRef<Path>, dst: impl AsRef<Path>) -> Result<()>`: Copy file content from src to dst.
- `copy(src: impl AsRef<Path>, dst: impl AsRef<Path>) -> Result<()>`: Copy a file from src to dst, preserving file content but not metadata.
- `copy2(src: impl AsRef<Path>, dst: impl AsRef<Path>) -> Result<()>`: Copy a file from src to dst, preserving file content and metadata.
- `copytree(src: impl AsRef<Path>, dst: impl AsRef<Path>, symlinks: bool, ignore_dangling_symlinks: bool, dirs_exist_ok: bool) -> Result<()>`: Recursively copy a directory tree from src to dst.
- `copy_with_server(src: impl AsRef<Path>, dst: impl AsRef<Path>, server_addr: &str, port: u16, compression_level: u32) -> Result<()>`: Copy file or directory using EACopyService for acceleration.
- `create_server(port: u16) -> Result<EACopyServer>`: Create a new EACopy server.
- `delta_copy(src: impl AsRef<Path>, dst: impl AsRef<Path>, reference: impl AsRef<Path>) -> Result<()>`: Perform delta copy using a reference file.
- `batch_copy(file_pairs: &[(impl AsRef<Path>, impl AsRef<Path>)]) -> Result<()>`: Copy multiple files in batch.
- `batch_copy2(file_pairs: &[(impl AsRef<Path>, impl AsRef<Path>)]) -> Result<()>`: Copy multiple files with metadata in batch.
- `batch_copytree(dir_pairs: &[(impl AsRef<Path>, impl AsRef<Path>)], symlinks: bool, ignore_dangling_symlinks: bool, dirs_exist_ok: bool) -> Result<()>`: Copy multiple directory trees in batch.
- `set_progress_callback<F>(callback: F) where F: Fn(u64, u64, &str) + Send + Sync + 'static`: Set the progress callback function.
- `get_config() -> &Config`: Get the current configuration.
- `set_config(config: Config)`: Update the configuration.

##### EACopyServer

Server for accelerated network file transfers.

- `new(port: u16, thread_count: usize) -> Result<Self>`: Create a new EACopy server.
- `start() -> Result<()>`: Start the server.
- `stop() -> Result<()>`: Stop the server.
- `is_running() -> bool`: Check if the server is running.
- `get_stats() -> eacopy::ServerStats`: Get server statistics.
- `get_port() -> u16`: Get the server port.
- `get_thread_count() -> usize`: Get the server thread count.

##### Config

Configuration options for EACopy.

- `new() -> Self`: Create a new configuration with default values.
- `with_thread_count(thread_count: usize) -> Self`: Set the number of threads to use for copy operations.
- `with_compression_level(compression_level: u32) -> Self`: Set the compression level (0-9) for network transfers.
- `with_buffer_size(buffer_size: usize) -> Self`: Set the buffer size for copy operations.
- `with_error_strategy(error_strategy: ErrorStrategy) -> Self`: Set the error handling strategy.
- `with_retry_count(retry_count: u32) -> Self`: Set the number of retries for failed operations.
- `with_retry_delay(retry_delay: f64) -> Self`: Set the delay between retries in seconds.
- `with_log_level(log_level: LogLevel) -> Self`: Set the verbosity level for logging.
- `with_preserve_metadata(preserve_metadata: bool) -> Self`: Set whether to preserve file metadata.
- `with_follow_symlinks(follow_symlinks: bool) -> Self`: Set whether to follow symbolic links.
- `with_dirs_exist_ok(dirs_exist_ok: bool) -> Self`: Set whether to allow existing directories.
- `with_progress_callback<F>(callback: F) -> Self where F: Fn(u64, u64, &str) + Send + Sync + 'static`: Set the progress callback function.

#### Enums

##### ErrorStrategy

Error handling strategies.

- `Raise`: Raise exceptions immediately.
- `Retry`: Retry the operation.
- `Ignore`: Ignore errors and continue.

##### LogLevel

Log levels for EACopy operations.

- `None`: No logging.
- `Error`: Error level logging.
- `Warning`: Warning level logging.
- `Info`: Info level logging.
- `Debug`: Debug level logging.

##### Error

Custom error type for EACopy operations.

- `Io(std::io::Error)`: IO error.
- `Ffi(String)`: FFI error.
- `Path(String)`: Path error.
- `FileNotFound(PathBuf)`: File not found error.
- `DirectoryNotFound(PathBuf)`: Directory not found error.
- `PermissionDenied(PathBuf)`: Permission denied error.
- `DestinationExists(PathBuf)`: Destination already exists error.
- `InvalidArgument(String)`: Invalid argument error.
- `Network(String)`: Network error.
- `Timeout(String)`: Timeout error.
- `Encoding(String)`: Encoding error.
- `Python(String)`: Python error.
- `FileTooLarge(PathBuf, u64)`: File too large error.
- `DiskFull(PathBuf, u64, u64)`: Disk full error.
- `ReadError(PathBuf, u64)`: Read error.
- `WriteError(PathBuf, u64)`: Write error.
- `Interrupted(String)`: Interrupted operation error.
- `Server(String)`: Server error.
- `Client(String)`: Client error.
- `DeltaCopy(String)`: Delta copy error.
- `Unsupported(String)`: Unsupported operation error.
- `Configuration(String)`: Configuration error.
- `Unknown(String)`: Unknown error.

#### Type Aliases

- `Result<T>`: Result type for EACopy operations.
- `ProgressCallback`: Type for progress callback function.

#### Global Functions

- `copy(src: impl AsRef<Path>, dst: impl AsRef<Path>) -> Result<()>`: Copy a file from src to dst, preserving file content but not metadata.
- `copy2(src: impl AsRef<Path>, dst: impl AsRef<Path>) -> Result<()>`: Copy a file from src to dst, preserving file content and metadata.
- `copyfile(src: impl AsRef<Path>, dst: impl AsRef<Path>) -> Result<()>`: Copy file content from src to dst.
- `copytree(src: impl AsRef<Path>, dst: impl AsRef<Path>, symlinks: bool, ignore_dangling_symlinks: bool, dirs_exist_ok: bool) -> Result<()>`: Recursively copy a directory tree from src to dst.
- `copy_with_server(src: impl AsRef<Path>, dst: impl AsRef<Path>, server_addr: &str, port: u16, compression_level: u32) -> Result<()>`: Copy file or directory using EACopyService for acceleration.
- `create_server(port: u16, thread_count: usize) -> Result<EACopyServer>`: Create a new EACopy server.
- `delta_copy(src: impl AsRef<Path>, dst: impl AsRef<Path>, reference: impl AsRef<Path>) -> Result<()>`: Perform delta copy using a reference file.
- `batch_copy(file_pairs: &[(impl AsRef<Path>, impl AsRef<Path>)]) -> Result<()>`: Copy multiple files in batch.
- `batch_copy2(file_pairs: &[(impl AsRef<Path>, impl AsRef<Path>)]) -> Result<()>`: Copy multiple files with metadata in batch.
- `batch_copytree(dir_pairs: &[(impl AsRef<Path>, impl AsRef<Path>)], symlinks: bool, ignore_dangling_symlinks: bool, dirs_exist_ok: bool) -> Result<()>`: Copy multiple directory trees in batch.

## Examples

### Basic Usage

```python
import py_eacopy

# Copy a file
py_eacopy.copy("source.txt", "destination.txt")

# Copy a file with metadata
py_eacopy.copy2("source.txt", "destination.txt")

# Copy a directory tree
py_eacopy.copytree("source_dir", "destination_dir")

# Use EACopyService for accelerated network transfers
py_eacopy.copy_with_server("source_dir", "destination_dir", "server_address", port=31337)
```

### Using the EACopy Class

```python
from py_eacopy import EACopy

# Create an EACopy instance with custom configuration
eac = EACopy(
    thread_count=8,
    compression_level=5,
    buffer_size=16 * 1024 * 1024,  # 16MB buffer
    preserve_metadata=True,
    follow_symlinks=True,
    dirs_exist_ok=True
)

# Use the instance for copying
eac.copy("source.txt", "destination.txt")
eac.copytree("source_dir", "destination_dir")
```

### Batch Operations

```python
# Batch copy multiple files
py_eacopy.batch_copy([
    ("source1.txt", "destination1.txt"),
    ("source2.txt", "destination2.txt"),
    ("source3.txt", "destination3.txt"),
])

# Batch copy multiple directories
py_eacopy.batch_copytree([
    ("source_dir1", "destination_dir1"),
    ("source_dir2", "destination_dir2"),
])
```

### Asynchronous Operations

```python
import asyncio

async def copy_files():
    # Copy files asynchronously
    await py_eacopy.async_copy("source.txt", "destination.txt")
    await py_eacopy.async_copytree("source_dir", "destination_dir")

# Run the async function
asyncio.run(copy_files())
```

### Progress Tracking

```python
def progress_callback(copied_bytes, total_bytes, filename):
    percent = (copied_bytes / total_bytes) * 100 if total_bytes > 0 else 0
    print(f"Copying {filename}: {percent:.1f}% ({copied_bytes}/{total_bytes} bytes)")

# Set the global progress callback
py_eacopy.config.progress_callback = progress_callback
```

## Performance Considerations

The Rust implementation of py-eacopy is designed to be as performant as the original C++ implementation, with the added benefits of memory safety and improved error handling. Here are some performance considerations:

- **Thread Count**: Adjust the `thread_count` parameter to match your system's CPU core count for optimal performance.
- **Buffer Size**: Increase the `buffer_size` parameter for large files to improve throughput.
- **Compression Level**: For network transfers, adjust the `compression_level` parameter based on your network bandwidth and CPU capabilities.
- **Batch Operations**: Use batch operations for copying multiple files or directories to reduce overhead.
- **Asynchronous Operations**: Use asynchronous operations for I/O-bound tasks to improve responsiveness.

## Troubleshooting

### Common Issues

- **ImportError**: Make sure the package is installed correctly and the Python version is compatible.
- **FileNotFoundError**: Check that the source file or directory exists.
- **PermissionError**: Ensure you have the necessary permissions to read the source and write to the destination.
- **UnicodeError**: Make sure file paths are properly encoded.
- **NetworkError**: Check network connectivity and server availability for `copy_with_server` operations.

### Debugging

- Set the log level to `DEBUG` for more detailed logging:
  ```python
  py_eacopy.config.log_level = py_eacopy.LogLevel.DEBUG
  ```

- Use the progress callback to monitor copy operations:
  ```python
  py_eacopy.config.progress_callback = lambda copied, total, filename: print(f"Copying {filename}: {copied}/{total} bytes")
  ```

## Contributing

Contributions to the Rust implementation of py-eacopy are welcome! Here are some ways you can contribute:

- Report bugs and request features on the [issue tracker](https://github.com/loonghao/py-eacopy/issues).
- Submit pull requests with bug fixes or new features.
- Improve documentation and examples.
- Write tests to increase code coverage.
- Optimize performance for specific use cases.

Please follow the project's coding style and guidelines when contributing.
