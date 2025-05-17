# EACopy Server Examples

This document provides examples of using the EACopy server functionality in py-eacopy.

## Starting and Using an EACopy Server

The EACopy server allows for accelerated network file transfers. Here's how to use it:

```python
import py_eacopy
import time

# Create and start a server
with py_eacopy.create_server(port=31337, thread_count=4) as server:
    print(f"Server started on port {server.port}")
    
    # Get server statistics
    stats = server.get_stats()
    print(f"Server statistics: {stats}")
    
    # Copy a file using the server
    py_eacopy.copy_with_server(
        "source_file.txt",
        "destination_file.txt",
        "localhost",  # Server address
        port=31337,   # Server port
        compression_level=5  # Compression level (0-9)
    )
    
    # Copy a directory using the server
    py_eacopy.copy_with_server(
        "source_directory",
        "destination_directory",
        "localhost",
        port=31337,
        compression_level=5
    )
    
    # Server is automatically stopped when exiting the context
```

## Manual Server Management

If you need more control over the server lifecycle:

```python
import py_eacopy
import time

# Create a server
server = py_eacopy.create_server(port=31337, thread_count=4)

try:
    # Start the server
    server.start()
    print(f"Server started on port {server.port}")
    
    # Check if the server is running
    if server.is_running():
        print("Server is running")
    
    # Perform operations with the server
    # ...
    
    # Get server statistics
    stats = server.get_stats()
    print(f"Server statistics: {stats}")
    
    # Keep the server running for a while
    time.sleep(60)
finally:
    # Stop the server
    if server.is_running():
        server.stop()
        print("Server stopped")
```

## Using EACopy Class with Server

You can also create a server using the EACopy class:

```python
import py_eacopy

# Create an EACopy instance
eac = py_eacopy.EACopy(
    thread_count=8,
    compression_level=5,
    buffer_size=16 * 1024 * 1024
)

# Create a server
server = eac.create_server(port=31337)

# Start the server
server.start()

try:
    # Copy a file using the server
    eac.copy_with_server(
        "source_file.txt",
        "destination_file.txt",
        "localhost",
        port=31337
    )
finally:
    # Stop the server
    if server.is_running():
        server.stop()
```

## Asynchronous Server Operations

You can use the server with asynchronous operations:

```python
import asyncio
import py_eacopy

async def copy_with_server_async():
    # Create and start a server
    server = py_eacopy.create_server(port=31337)
    server.start()
    
    try:
        # Copy a file asynchronously
        await py_eacopy.async_copy_with_server(
            "source_file.txt",
            "destination_file.txt",
            "localhost",
            port=31337
        )
        
        # Copy a directory asynchronously
        await py_eacopy.async_copy_with_server(
            "source_directory",
            "destination_directory",
            "localhost",
            port=31337
        )
    finally:
        # Stop the server
        if server.is_running():
            server.stop()

# Run the async function
asyncio.run(copy_with_server_async())
```

## Performance Considerations

- **Thread Count**: Adjust the `thread_count` parameter based on your system's CPU core count. For most systems, setting it to the number of CPU cores or slightly higher works well.
- **Compression Level**: The `compression_level` parameter (0-9) controls the compression level for network transfers. Higher values provide better compression but use more CPU. For high-speed networks, lower values (0-3) are often more efficient.
- **Buffer Size**: The `buffer_size` parameter controls the size of the buffer used for copy operations. Larger buffers can improve performance for large files but use more memory.
- **Network Bandwidth**: The server automatically adjusts to the available network bandwidth, but you can fine-tune performance by adjusting the compression level and buffer size.

## Troubleshooting

- **Connection Refused**: Make sure the server is running and the port is not blocked by a firewall.
- **Server Busy**: The server may be busy processing other requests. Try again later or increase the thread count.
- **Timeout**: The network connection may be slow or unstable. Try increasing the timeout or reducing the compression level.
- **Permission Denied**: Make sure the user running the server has permission to access the files being copied.
- **Port Already in Use**: Choose a different port if the specified port is already in use by another application.
