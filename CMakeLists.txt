cmake_minimum_required(VERSION 3.15)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX C)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Detect target architecture
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(TARGET_ARCH "x64")
    message(STATUS "Building for 64-bit architecture")
else()
    set(TARGET_ARCH "x86")
    message(STATUS "Building for 32-bit architecture")
endif()

# Force target architecture to match Python architecture
if(WIN32)
    # Get Python architecture
    execute_process(
        COMMAND "${Python_EXECUTABLE}" -c "import sys; print('x64' if sys.maxsize > 2**32 else 'x86')"
        OUTPUT_VARIABLE PYTHON_ARCH
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )

    message(STATUS "Detected Python architecture: ${PYTHON_ARCH}")

    # Force target architecture to match Python architecture
    if("${PYTHON_ARCH}" STREQUAL "x86")
        set(TARGET_ARCH "x86")
        set(CMAKE_GENERATOR_PLATFORM "Win32" CACHE STRING "Target platform" FORCE)
        message(STATUS "Building for 32-bit architecture")
        # Set SIZEOF_SIZE_T for 32-bit architecture
        set(SIZEOF_SIZE_T 4)
        # Ensure Visual Studio knows this is a Win32 build
        set(CMAKE_VS_PLATFORM_NAME "Win32" CACHE STRING "Visual Studio platform name" FORCE)
    else()
        set(TARGET_ARCH "x64")
        set(CMAKE_GENERATOR_PLATFORM "x64" CACHE STRING "Target platform" FORCE)
        message(STATUS "Building for 64-bit architecture")
        # Set SIZEOF_SIZE_T for 64-bit architecture
        set(SIZEOF_SIZE_T 8)
        # Ensure Visual Studio knows this is an x64 build
        set(CMAKE_VS_PLATFORM_NAME "x64" CACHE STRING "Visual Studio platform name" FORCE)
    endif()

    # Set MSVC runtime library for all configurations
    if(MSVC)
        # Use dynamic linking runtime library (MD/MDd) to match Python's expectations
        set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL" CACHE STRING "MSVC runtime library" FORCE)

        # Force MD runtime for all configurations
        foreach(flag_var
            CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
            CMAKE_C_FLAGS CMAKE_C_FLAGS_DEBUG CMAKE_C_FLAGS_RELEASE)
            if(${flag_var} MATCHES "/MT")
                string(REGEX REPLACE "/MT" "/MD" ${flag_var} "${${flag_var}}")
            endif()
        endforeach()
    endif()

    # Set platform-specific flags
    if(MSVC)
        if("${PYTHON_ARCH}" STREQUAL "x86")
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /DWIN32")
            set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /DWIN32")
        else()
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /DWIN64")
            set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /DWIN64")
        endif()
    endif()

    # Set platform-specific configuration
    # Set configuration type to Release for both architectures
    set(CMAKE_CONFIGURATION_TYPES "Debug;Release" CACHE STRING "Configuration types" FORCE)
    # Use CMAKE_BUILD_TYPE instead of CMAKE_DEFAULT_CONFIGS which is not supported by VS2022
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Default configuration" FORCE)
endif()

# Enable faster builds
if(MSVC)
    # Enable multi-processor compilation for MSVC
    add_compile_options(/MP)
    # Enable faster linking
    add_link_options(/INCREMENTAL:NO)
    # Optimize for speed
    add_compile_options(/O2)
endif()

# Set build parallelism if not already set
if(NOT DEFINED CMAKE_BUILD_PARALLEL_LEVEL)
    include(ProcessorCount)
    ProcessorCount(CPU_COUNT)
    if(CPU_COUNT EQUAL 0)
        set(CPU_COUNT 4)
    endif()
    set(CMAKE_BUILD_PARALLEL_LEVEL ${CPU_COUNT} CACHE STRING "Number of parallel build jobs" FORCE)
endif()

# Use ccache if available for faster rebuilds
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    set(CMAKE_C_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
    set(CMAKE_CXX_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
    message(STATUS "Using ccache: ${CCACHE_PROGRAM}")
endif()

# Handle PYTHON_LIMITED_API variable from scikit-build-core
if(DEFINED PYTHON_LIMITED_API AND PYTHON_LIMITED_API)
    message(STATUS "Python limited API requested, but not supported by this project")
    # We acknowledge the variable but don't use it
endif()

# Handle SKBUILD_SOABI variable from scikit-build-core
if(DEFINED SKBUILD_SOABI AND SKBUILD_SOABI)
    message(STATUS "SKBUILD_SOABI set to: ${SKBUILD_SOABI}")
    # We acknowledge the variable but don't use it
endif()

# Find Python with all required components
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# Architecture compatibility is now handled at the beginning of the file

# Output Python version information
message(STATUS "Found Python: ${Python_VERSION}")
message(STATUS "  Python_EXECUTABLE: ${Python_EXECUTABLE}")
message(STATUS "  Python_INCLUDE_DIRS: ${Python_INCLUDE_DIRS}")
message(STATUS "  Python_LIBRARIES: ${Python_LIBRARIES}")

# Windows-specific configuration
if(WIN32)
    # Set Windows platform-specific configuration for MSVC
    if(MSVC)
        # Add MSVC-specific flags
        add_compile_options(/MP /bigobj)

        # Enable multi-threaded compilation
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /MP")

        # Set runtime library to match Python's expectations
        # Use Multi-threaded DLL runtime library (/MD) for all targets
        # This is critical for compatibility with Python extensions
        set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")

        # Force MD runtime for all configurations
        foreach(flag_var
            CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
            CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO
            CMAKE_C_FLAGS CMAKE_C_FLAGS_DEBUG CMAKE_C_FLAGS_RELEASE
            CMAKE_C_FLAGS_MINSIZEREL CMAKE_C_FLAGS_RELWITHDEBINFO)
            if(${flag_var} MATCHES "/MT")
                string(REGEX REPLACE "/MT" "/MD" ${flag_var} "${${flag_var}}")
            endif()
        endforeach()

        # Use export symbol table file
        set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS OFF)

        # Use dynamic linking to Python library
        set(PYTHON_LINK_STATIC OFF)
    endif()
endif()

# Disable some warnings
if(MSVC)
    # Disable warnings for MSVC
    add_compile_options(/W3 /wd4244 /wd4267 /wd4996 /wd4305)
endif()

# Print debug information
message(STATUS "Python_EXECUTABLE: ${Python_EXECUTABLE}")
message(STATUS "Python_LIBRARIES: ${Python_LIBRARIES}")
message(STATUS "Python_INCLUDE_DIRS: ${Python_INCLUDE_DIRS}")
message(STATUS "CMAKE_GENERATOR_PLATFORM: ${CMAKE_GENERATOR_PLATFORM}")
message(STATUS "CMAKE_VS_PLATFORM_NAME: ${CMAKE_VS_PLATFORM_NAME}")
message(STATUS "TARGET_ARCH: ${TARGET_ARCH}")
message(STATUS "SIZEOF_SIZE_T: ${SIZEOF_SIZE_T}")

# Use pybind11 from scikit-build-core
find_package(pybind11 CONFIG REQUIRED)

# Print information about using the forked EACopy
message(STATUS "Using forked EACopy from: https://github.com/loonghao/EACopy")

# Configure EACopy options
set(EACOPY_BUILD_TESTS OFF CACHE BOOL "Build EACopy tests")
set(EACOPY_BUILD_SERVICE OFF CACHE BOOL "Build EACopy service")

# Configure EACopy to use its own dependencies
# Configure EACopy to use our own dependencies instead of its internal ones
set(EACOPY_USE_SYSTEM_ZSTD ON CACHE BOOL "Use system zstd library" FORCE)
set(EACOPY_USE_SYSTEM_LZMA ON CACHE BOOL "Use system lzma library" FORCE)
set(EACOPY_USE_SYSTEM_XDELTA ON CACHE BOOL "Use system xdelta library" FORCE)

# Set CMake policy version minimum to handle older CMake code in dependencies
set(CMAKE_POLICY_VERSION_MINIMUM 3.5 CACHE STRING "Minimum CMake policy version")

# Add our own dependencies as subdirectories
message(STATUS "Using external dependencies from Git submodules")

# Add zstd
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/extern/zstd/CMakeLists.txt")
    message(STATUS "Using zstd from Git submodule")
    set(ZSTD_BUILD_PROGRAMS OFF CACHE BOOL "Build programs" FORCE)
    set(ZSTD_BUILD_TESTS OFF CACHE BOOL "Build tests" FORCE)
    set(ZSTD_BUILD_SHARED OFF CACHE BOOL "Build shared libraries" FORCE)
    add_subdirectory(extern/zstd/build/cmake EXCLUDE_FROM_ALL)
    set(ZSTD_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/extern/zstd/lib)
else()
    message(STATUS "zstd Git submodule not found, using EACopy's version")
    set(ZSTD_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib)
endif()

# Add xz (lzma)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/extern/xz/CMakeLists.txt")
    message(STATUS "Using xz (lzma) from Git submodule")
    set(BUILD_SHARED_LIBS OFF CACHE BOOL "Build shared libraries" FORCE)
    set(ENABLE_TESTS OFF CACHE BOOL "Enable tests" FORCE)
    add_subdirectory(extern/xz EXCLUDE_FROM_ALL)
    set(LZMA_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/extern/xz/src/liblzma/api)
else()
    message(STATUS "xz Git submodule not found, using EACopy's version")
    set(LZMA_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/api)
endif()

# Add xdelta
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/extern/xdelta/xdelta3/xdelta3.c")
    message(STATUS "Using xdelta from Git submodule")
    set(XDELTA_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/extern/xdelta/xdelta3)
    add_subdirectory(extern/xdelta EXCLUDE_FROM_ALL)
else()
    message(STATUS "xdelta Git submodule not found, using EACopy's version")
    set(XDELTA_INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta/xdelta3)
    add_subdirectory(extern/xdelta EXCLUDE_FROM_ALL)
endif()

# Ensure Visual Studio project configuration is correct
if(MSVC)
    # Set the correct platform for Visual Studio projects
    set_property(GLOBAL PROPERTY USE_FOLDERS ON)

    # Set configuration type to Release for all platforms
    set(CMAKE_CONFIGURATION_TYPES "Release" CACHE STRING "Configuration types" FORCE)

    # Set build type to Release
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type" FORCE)

    # Add platform-specific definitions
    if("${PYTHON_ARCH}" STREQUAL "x86")
        add_definitions(-DWIN32 -D_WIN32)
    else()
        add_definitions(-DWIN64 -D_WIN64)
    endif()

    # Disable specific warnings that might cause issues
    add_compile_options(
        /W3     # Warning level 3
        /MP     # Multi-processor compilation
        /wd4244 # Disable warning C4244: conversion from 'double' to 'float'
        /wd4267 # Disable warning C4267: conversion from 'size_t' to 'int'
        /wd4305 # Disable warning C4305: truncation from 'double' to 'float'
        /bigobj # Support for large object files
    )
endif()

# Add EACopy as a subdirectory
add_subdirectory(extern/EACopy EXCLUDE_FROM_ALL)

# Set global definitions for all targets
add_definitions(
    -DSIZEOF_UNSIGNED_LONG_LONG=8
    -DXD3_USE_LARGEFILE64=1
    -DSECONDARY_DJW=1
    -DSECONDARY_LZMA=1
    -DSECONDARY_FGK=1
    -DLZMA_API_STATIC
    -DEACOPY_USE_SYSTEM_ZSTD
    -DEACOPY_USE_SYSTEM_LZMA
    -DEACOPY_USE_SYSTEM_XDELTA
)

# Set SIZEOF_SIZE_T based on Python architecture
add_definitions(-DSIZEOF_SIZE_T=${SIZEOF_SIZE_T})
message(STATUS "Setting SIZEOF_SIZE_T=${SIZEOF_SIZE_T} based on Python architecture")

if(WIN32)
    add_definitions(-D_WIN32=1 -DXD3_WIN32=1)
endif()

# Create our own library for the Python binding
add_library(EACopyLib STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include/EACopyClient.h
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyClient.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include/EACopyNetwork.h
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyNetwork.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include/EACopyShared.h
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyShared.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include/EACopyDelta.h
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyDelta.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyDeltaZstd.h
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyDeltaXDelta.h
)

# Force dynamic runtime library for EACopyLib
if(MSVC)
    # Use dynamic libraries (MD) to match Python's runtime
    # This is critical for compatibility with Python extensions
    foreach(flag_var
        CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
        CMAKE_C_FLAGS CMAKE_C_FLAGS_DEBUG CMAKE_C_FLAGS_RELEASE)
        if(${flag_var} MATCHES "/MT")
            string(REGEX REPLACE "/MT" "/MD" ${flag_var} "${${flag_var}}")
        endif()
    endforeach()

    # Explicitly set MD/MDd for the library
    target_compile_options(EACopyLib PRIVATE
        $<$<CONFIG:Debug>:/MDd>
        $<$<CONFIG:Release>:/MD>
    )
endif()

# Add the necessary include directories
target_include_directories(EACopyLib PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include
    ${ZSTD_INCLUDE_DIR}
    ${LZMA_INCLUDE_DIR}
    ${XDELTA_INCLUDE_DIR}
)

# Add the necessary definitions
target_compile_definitions(EACopyLib PUBLIC
    -DEACOPY_ALLOW_DELTA_COPY
)

# Link EACopyLib against our own dependencies
target_link_libraries(EACopyLib PRIVATE libzstd_static lzma xdelta)

# Include directories for our binding
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src/binding
)

# Use pybind11 to create the Python module
pybind11_add_module(_eacopy_binding MODULE
    src/binding/eacopy_binding.cpp
    src/binding/eacopy_module.cpp
)

# Link against our library
target_link_libraries(_eacopy_binding PRIVATE EACopyLib)

# Windows-specific DLL handling
if(WIN32 AND MSVC)
    # Add additional Windows-specific libraries that might be needed
    target_link_libraries(_eacopy_binding PRIVATE ws2_32 advapi32)

    # Add Windows-specific compile definitions
    target_compile_definitions(_eacopy_binding PRIVATE
        NOMINMAX  # Avoid min/max macro conflicts with STL
        WIN32_LEAN_AND_MEAN  # Reduce Windows header includes
    )

    # Disable automatic export of all symbols
    set_property(TARGET _eacopy_binding PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS OFF)

    # Specify macro definition for exported symbols
    target_compile_definitions(_eacopy_binding PRIVATE
        "PYBIND11_EXPORT=__declspec(dllexport)"
    )

    # Explicitly export the PyInit function
    set_property(TARGET _eacopy_binding APPEND_STRING PROPERTY LINK_FLAGS
        " /EXPORT:PyInit__eacopy_binding"
    )
endif()

# Install the binding module
install(TARGETS _eacopy_binding DESTINATION eacopy)
