cmake_minimum_required(VERSION 3.15)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

# Set minimum CMake policy version to handle old CMake code in dependencies
set(CMAKE_POLICY_VERSION_MINIMUM 3.5 CACHE STRING "Minimum CMake policy version")

# Simplified CMake configuration focused on using existing static library

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Detect target architecture
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(TARGET_ARCH "x64")
    message(STATUS "Building for 64-bit architecture")
else()
    set(TARGET_ARCH "x86")
    message(STATUS "Building for 32-bit architecture")
endif()

# Find Python
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
message(STATUS "Found Python: ${Python_VERSION}")
message(STATUS "  Python_EXECUTABLE: ${Python_EXECUTABLE}")
message(STATUS "  Python_INCLUDE_DIRS: ${Python_INCLUDE_DIRS}")
message(STATUS "  Python_LIBRARIES: ${Python_LIBRARIES}")

# Force target architecture to match Python architecture
if(WIN32)
    # Get Python architecture
    execute_process(
        COMMAND "${Python_EXECUTABLE}" -c "import sys; print('x64' if sys.maxsize > 2**32 else 'x86')"
        OUTPUT_VARIABLE PYTHON_ARCH
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    message(STATUS "Detected Python architecture: ${PYTHON_ARCH}")

    # Set correct architecture
    if("${PYTHON_ARCH}" STREQUAL "x86")
        set(TARGET_ARCH "x86")
        set(CMAKE_GENERATOR_PLATFORM "Win32" CACHE STRING "Target platform" FORCE)
    else()
        set(TARGET_ARCH "x64")
        set(CMAKE_GENERATOR_PLATFORM "x64" CACHE STRING "Target platform" FORCE)
    endif()
endif()

# Windows-specific configuration
if(WIN32 AND MSVC)
    # Add MSVC-specific flags
    add_compile_options(/MP /bigobj)

    # Set runtime library to match Python's expectations
    # Use Multi-threaded DLL runtime library (/MD) for Release builds
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")
    foreach(flag_var
        CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
        CMAKE_C_FLAGS CMAKE_C_FLAGS_DEBUG CMAKE_C_FLAGS_RELEASE)
        if(${flag_var} MATCHES "/MT")
            string(REGEX REPLACE "/MT" "/MD" ${flag_var} "${${flag_var}}")
        endif()
    endforeach()

    # Disable some warnings
    add_compile_options(/W3 /wd4244 /wd4267 /wd4996 /wd4305)
else()
    # Disable GCC/Clang warnings
    add_compile_options(-Wall -Wno-unused-variable -Wno-sign-compare -Wno-unused-parameter)
endif()

# Find pybind11
find_package(pybind11 CONFIG REQUIRED)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src/binding
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/api
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta/xdelta3
)

# Add global definitions
add_definitions(
    -DSIZEOF_SIZE_T=${CMAKE_SIZEOF_VOID_P}
    -DSIZEOF_UNSIGNED_LONG_LONG=8
    -DXD3_USE_LARGEFILE64=1
    -DSECONDARY_DJW=1
    -DSECONDARY_LZMA=1
    -DSECONDARY_FGK=1
    -DLZMA_API_STATIC
    -DEACOPY_ALLOW_DELTA_COPY
)

if(WIN32)
    add_definitions(-D_WIN32=1 -DXD3_WIN32=1)
endif()

# Build zstd library
set(ZSTD_BUILD_PROGRAMS OFF CACHE BOOL "Build programs" FORCE)
set(ZSTD_BUILD_TESTS OFF CACHE BOOL "Build tests" FORCE)
set(ZSTD_BUILD_SHARED OFF CACHE BOOL "Build shared libraries" FORCE)
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/build/cmake EXCLUDE_FROM_ALL)

# Build lzma library
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma EXCLUDE_FROM_ALL)

# Build xdelta library
add_library(xdelta STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta/xdelta3/xdelta3.c
)
target_include_directories(xdelta PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta/xdelta3
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/api
)
target_compile_definitions(xdelta PRIVATE
    SIZEOF_SIZE_T=${CMAKE_SIZEOF_VOID_P}
    SIZEOF_UNSIGNED_LONG_LONG=8
    XD3_USE_LARGEFILE64=1
    SECONDARY_DJW=1
    SECONDARY_LZMA=1
    SECONDARY_FGK=1
    LZMA_API_STATIC
)
if(WIN32)
    target_compile_definitions(xdelta PRIVATE
        _WIN32=1
        XD3_WIN32=1
    )
endif()

# Create Python module using pybind11
pybind11_add_module(_eacopy_binding MODULE
    src/binding/eacopy_binding.cpp
    src/binding/eacopy_module.cpp
)

# Set target properties
set_target_properties(_eacopy_binding PROPERTIES
    OUTPUT_NAME "_eacopy_binding"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/py_eacopy"
)

# Use existing static library
if(WIN32)
    # Link directly to the existing static library
    target_link_libraries(_eacopy_binding PRIVATE
        "${CMAKE_CURRENT_SOURCE_DIR}/src/binding/EACopyLib.lib"
        libzstd_static lzma xdelta
        ws2_32 advapi32  # Windows-specific libraries
    )
else()
    # For non-Windows platforms, assume static library is in the same location
    target_link_libraries(_eacopy_binding PRIVATE
        "${CMAKE_CURRENT_SOURCE_DIR}/src/binding/EACopyLib.a"
        libzstd_static lzma xdelta
    )
endif()

# Windows-specific DLL handling
if(WIN32 AND MSVC)
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

    # Specify export symbol table file
    set_property(TARGET _eacopy_binding APPEND_STRING PROPERTY LINK_FLAGS
        " /EXPORT:PyInit__eacopy_binding"
    )
endif()

# Install module - Ensure installation to the correct directory
install(TARGETS _eacopy_binding DESTINATION py_eacopy)

# Copy Python files
file(GLOB PYTHON_FILES "${CMAKE_CURRENT_SOURCE_DIR}/src/py_eacopy/*.py")
foreach(PYTHON_FILE ${PYTHON_FILES})
    get_filename_component(FILENAME ${PYTHON_FILE} NAME)
    configure_file(${PYTHON_FILE} "${CMAKE_CURRENT_BINARY_DIR}/py_eacopy/${FILENAME}" COPYONLY)
endforeach()
