cmake_minimum_required(VERSION 3.15)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

# Set up module path for our own cmake modules
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules")

# Set minimum CMake policy version to handle old CMake code in dependencies
set(CMAKE_POLICY_VERSION_MINIMUM 3.5 CACHE STRING "Minimum CMake policy version")

# Enable ccache if available
include(UseCCache)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Include CPM.cmake for dependency management
include(cmake/CPM.cmake)

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

# Add dependencies using CPM.cmake
CPMAddPackage(
  NAME pybind11
  GITHUB_REPOSITORY pybind/pybind11
  VERSION 2.11.1
  OPTIONS
    "PYBIND11_TEST OFF"
)

CPMAddPackage(
  NAME utf8cpp
  GITHUB_REPOSITORY nemtrif/utfcpp
  VERSION 3.2.5
)

CPMAddPackage(
  NAME Boost
  VERSION 1.84.0
  URL https://github.com/boostorg/boost/releases/download/boost-1.84.0/boost-1.84.0.tar.xz
  URL_HASH SHA256=2e64e5d79a738d0fa6fb546c6e5c2bd28f88d268a2a080546f74e5ff98f29d0e
  OPTIONS "BOOST_ENABLE_CMAKE ON"
)

# Add more dependencies using CPM.cmake
CPMAddPackage(
  NAME zstd
  GITHUB_REPOSITORY facebook/zstd
  VERSION 1.5.5
  OPTIONS
    "ZSTD_BUILD_PROGRAMS OFF"
    "ZSTD_BUILD_TESTS OFF"
    "ZSTD_BUILD_SHARED OFF"
    "ZSTD_STATIC_LINKING_ONLY ON"
)

# Build zstd library from source
add_library(libzstd_static STATIC
    ${zstd_SOURCE_DIR}/lib/common/debug.c
    ${zstd_SOURCE_DIR}/lib/common/entropy_common.c
    ${zstd_SOURCE_DIR}/lib/common/error_private.c
    ${zstd_SOURCE_DIR}/lib/common/fse_decompress.c
    ${zstd_SOURCE_DIR}/lib/common/pool.c
    ${zstd_SOURCE_DIR}/lib/common/threading.c
    ${zstd_SOURCE_DIR}/lib/common/xxhash.c
    ${zstd_SOURCE_DIR}/lib/common/zstd_common.c
    ${zstd_SOURCE_DIR}/lib/compress/fse_compress.c
    ${zstd_SOURCE_DIR}/lib/compress/hist.c
    ${zstd_SOURCE_DIR}/lib/compress/huf_compress.c
    ${zstd_SOURCE_DIR}/lib/compress/zstd_compress.c
    ${zstd_SOURCE_DIR}/lib/compress/zstd_compress_literals.c
    ${zstd_SOURCE_DIR}/lib/compress/zstd_compress_sequences.c
    ${zstd_SOURCE_DIR}/lib/compress/zstd_compress_superblock.c
    ${zstd_SOURCE_DIR}/lib/compress/zstd_double_fast.c
    ${zstd_SOURCE_DIR}/lib/compress/zstd_fast.c
    ${zstd_SOURCE_DIR}/lib/compress/zstd_lazy.c
    ${zstd_SOURCE_DIR}/lib/compress/zstd_ldm.c
    ${zstd_SOURCE_DIR}/lib/compress/zstd_opt.c
    ${zstd_SOURCE_DIR}/lib/decompress/huf_decompress.c
    ${zstd_SOURCE_DIR}/lib/decompress/zstd_ddict.c
    ${zstd_SOURCE_DIR}/lib/decompress/zstd_decompress.c
    ${zstd_SOURCE_DIR}/lib/decompress/zstd_decompress_block.c
)

target_include_directories(libzstd_static PRIVATE
    ${zstd_SOURCE_DIR}/lib
    ${zstd_SOURCE_DIR}/lib/common
    ${zstd_SOURCE_DIR}/lib/compress
    ${zstd_SOURCE_DIR}/lib/decompress
)

target_compile_definitions(libzstd_static PRIVATE
    ZSTD_STATIC_LINKING_ONLY
)

CPMAddPackage(
  NAME xz
  GITHUB_REPOSITORY tukaani-project/xz
  VERSION 5.4.5
  DOWNLOAD_ONLY YES
)

CPMAddPackage(
  NAME xdelta
  URL https://github.com/jmacd/xdelta/archive/refs/heads/master.zip
  DOWNLOAD_ONLY YES
)

# Add EACopy as a dependency
CPMAddPackage(
  NAME EACopy
  URL https://github.com/electronicarts/EACopy/archive/refs/heads/master.zip
  DOWNLOAD_ONLY YES
)

# Include directories
include_directories(
    ${EACopy_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src/binding
    ${zstd_SOURCE_DIR}/lib
    ${xz_SOURCE_DIR}/src/liblzma/api
    ${xdelta_SOURCE_DIR}/xdelta3
    ${Boost_INCLUDE_DIR}
    ${utf8cpp_SOURCE_DIR}/source
)

# Add utf8cpp include directory
include_directories(SYSTEM ${utf8cpp_SOURCE_DIR})

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

# Build lzma library from source
add_library(lzma STATIC
    ${xz_SOURCE_DIR}/src/liblzma/common/common.c
    ${xz_SOURCE_DIR}/src/liblzma/common/block_util.c
    ${xz_SOURCE_DIR}/src/liblzma/common/easy_preset.c
    ${xz_SOURCE_DIR}/src/liblzma/common/filter_common.c
    ${xz_SOURCE_DIR}/src/liblzma/common/hardware_physmem.c
    ${xz_SOURCE_DIR}/src/liblzma/common/index.c
    ${xz_SOURCE_DIR}/src/liblzma/common/stream_flags_common.c
    ${xz_SOURCE_DIR}/src/liblzma/common/string_conversion.c
    ${xz_SOURCE_DIR}/src/liblzma/common/vli_size.c
    ${xz_SOURCE_DIR}/src/liblzma/check/check.c
    ${xz_SOURCE_DIR}/src/liblzma/check/crc32_table.c
    ${xz_SOURCE_DIR}/src/liblzma/check/crc32_fast.c
    ${xz_SOURCE_DIR}/src/liblzma/check/crc64_table.c
    ${xz_SOURCE_DIR}/src/liblzma/check/crc64_fast.c
    ${xz_SOURCE_DIR}/src/liblzma/check/sha256.c
    ${xz_SOURCE_DIR}/src/liblzma/lz/lz_decoder.c
    ${xz_SOURCE_DIR}/src/liblzma/lz/lz_encoder.c
    ${xz_SOURCE_DIR}/src/liblzma/lz/lz_encoder_mf.c
    ${xz_SOURCE_DIR}/src/liblzma/lzma/lzma_decoder.c
    ${xz_SOURCE_DIR}/src/liblzma/lzma/lzma_encoder.c
    ${xz_SOURCE_DIR}/src/liblzma/lzma/lzma_encoder_presets.c
    ${xz_SOURCE_DIR}/src/liblzma/lzma/lzma2_decoder.c
    ${xz_SOURCE_DIR}/src/liblzma/lzma/lzma2_encoder.c
    ${xz_SOURCE_DIR}/src/liblzma/rangecoder/price_table.c
    ${xz_SOURCE_DIR}/src/liblzma/delta/delta_common.c
    ${xz_SOURCE_DIR}/src/liblzma/delta/delta_decoder.c
    ${xz_SOURCE_DIR}/src/liblzma/delta/delta_encoder.c
    ${xz_SOURCE_DIR}/src/liblzma/simple/simple_coder.c
    ${xz_SOURCE_DIR}/src/liblzma/simple/simple_decoder.c
    ${xz_SOURCE_DIR}/src/liblzma/simple/simple_encoder.c
    ${xz_SOURCE_DIR}/src/liblzma/simple/arm.c
    ${xz_SOURCE_DIR}/src/liblzma/simple/armthumb.c
    ${xz_SOURCE_DIR}/src/liblzma/simple/ia64.c
    ${xz_SOURCE_DIR}/src/liblzma/simple/powerpc.c
    ${xz_SOURCE_DIR}/src/liblzma/simple/sparc.c
    ${xz_SOURCE_DIR}/src/liblzma/simple/x86.c
)

# Create config.h for lzma
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/config.h "
#define HAVE_STDBOOL_H 1
#define HAVE_STDINT_H 1
#define HAVE_MEMORY_H 1
#define HAVE_STRING_H 1
#define HAVE_STRINGS_H 1
#define HAVE_INTTYPES_H 1
#define HAVE_LIMITS_H 1
#define HAVE_STDLIB_H 1
#define HAVE_VISIBILITY 1
#define HAVE_PTHREAD 1
#define HAVE_PTHREAD_PRIO_INHERIT 1
#define HAVE_CLOCK_GETTIME 1
#define HAVE_UTIME 1
#define HAVE_FUTIMENS 1
#define HAVE_FCNTL_H 1
#define HAVE_GETOPT_H 1
#define HAVE_GETOPT_LONG 1
#define HAVE_IMMINTRIN_H 1
#define HAVE_MBRTOWC 1
#define HAVE_WCWIDTH 1
#define HAVE_UTIME_H 1
#define HAVE_SYS_TIME_H 1
#define HAVE_SYS_STAT_H 1
#define HAVE_DECODER_ARM 1
#define HAVE_DECODER_ARMTHUMB 1
#define HAVE_DECODER_DELTA 1
#define HAVE_DECODER_IA64 1
#define HAVE_DECODER_LZMA1 1
#define HAVE_DECODER_LZMA2 1
#define HAVE_DECODER_POWERPC 1
#define HAVE_DECODER_SPARC 1
#define HAVE_DECODER_X86 1
#define HAVE_ENCODER_ARM 1
#define HAVE_ENCODER_ARMTHUMB 1
#define HAVE_ENCODER_DELTA 1
#define HAVE_ENCODER_IA64 1
#define HAVE_ENCODER_LZMA1 1
#define HAVE_ENCODER_LZMA2 1
#define HAVE_ENCODER_POWERPC 1
#define HAVE_ENCODER_SPARC 1
#define HAVE_ENCODER_X86 1
#define HAVE_MF_BT2 1
#define HAVE_MF_BT3 1
#define HAVE_MF_BT4 1
#define HAVE_MF_HC3 1
#define HAVE_MF_HC4 1
#define HAVE_CHECK_CRC32 1
#define HAVE_CHECK_CRC64 1
#define HAVE_CHECK_SHA256 1
#define SIZEOF_SIZE_T 8
#define ASSUME_RAM 128
#define ENABLE_NLS 1
#define MYTHREAD_POSIX 1
#define PACKAGE_NAME \"XZ Utils\"
#define PACKAGE_VERSION \"5.4.5\"
")

target_include_directories(lzma PRIVATE
    ${xz_SOURCE_DIR}/src/liblzma/api
    ${xz_SOURCE_DIR}/src/liblzma/common
    ${xz_SOURCE_DIR}/src/liblzma/check
    ${xz_SOURCE_DIR}/src/liblzma/lz
    ${xz_SOURCE_DIR}/src/liblzma/rangecoder
    ${xz_SOURCE_DIR}/src/liblzma/lzma
    ${xz_SOURCE_DIR}/src/liblzma/delta
    ${xz_SOURCE_DIR}/src/liblzma/simple
    ${xz_SOURCE_DIR}/src/common
    ${CMAKE_CURRENT_BINARY_DIR}
)

target_compile_definitions(lzma PRIVATE
    HAVE_CONFIG_H
    LZMA_API_STATIC
)

# zstd is now handled by CPM.cmake

# Build xdelta library
add_library(xdelta STATIC
    ${xdelta_SOURCE_DIR}/xdelta3/xdelta3.c
)
target_include_directories(xdelta PRIVATE
    ${xdelta_SOURCE_DIR}/xdelta3
    ${xz_SOURCE_DIR}/src/liblzma/api
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
        utf8cpp
        Boost::filesystem
        Boost::signals2
        ws2_32 advapi32  # Windows-specific libraries
    )
else()
    # For non-Windows platforms, assume static library is in the same location
    target_link_libraries(_eacopy_binding PRIVATE
        "${CMAKE_CURRENT_SOURCE_DIR}/src/binding/EACopyLib.a"
        libzstd_static lzma xdelta
        utf8cpp
        Boost::filesystem
        Boost::signals2
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
