cmake_minimum_required(VERSION 3.15...3.30)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Use scikit-build-core's FindPython support
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# Output Python version information
message(STATUS "Found Python: ${Python_VERSION}")
message(STATUS "  Python_EXECUTABLE: ${Python_EXECUTABLE}")
message(STATUS "  Python_INCLUDE_DIRS: ${Python_INCLUDE_DIRS}")
message(STATUS "  Python_LIBRARIES: ${Python_LIBRARIES}")

# Find pybind11
find_package(pybind11 CONFIG REQUIRED)
message(STATUS "Found pybind11 v${pybind11_VERSION}")

# Add EACopy
set(EACOPY_BUILD_TESTS OFF CACHE BOOL "Build EACopy tests")
set(EACOPY_BUILD_SERVICE OFF CACHE BOOL "Build EACopy service")
# Set CMake policy version minimum to handle older CMake code in dependencies
set(CMAKE_POLICY_VERSION_MINIMUM 3.5 CACHE STRING "Minimum CMake policy version")

# Instead of using EACopy directly, we'll create our own library with the necessary files
# Define the EACopy shared files we need
set(EACOPY_SHARED_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include/EACopyNetwork.h
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyNetwork.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include/EACopyShared.h
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyShared.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include/EACopyDelta.h
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyDelta.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyDeltaZstd.h
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyDeltaXDelta.h
)

# Add zstd library
add_library(zstd STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/common/debug.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/common/entropy_common.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/common/error_private.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/common/fse_decompress.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/common/pool.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/common/threading.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/common/xxhash.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/common/zstd_common.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/compress/fse_compress.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/compress/hist.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/compress/huf_compress.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/compress/zstd_compress.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/compress/zstd_double_fast.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/compress/zstd_fast.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/compress/zstd_lazy.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/compress/zstd_ldm.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/compress/zstd_opt.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/decompress/huf_decompress.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/decompress/zstd_decompress.c
)

target_include_directories(zstd PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib/common
)

# Add lzma library
add_library(lzma STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/common.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/block_util.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/easy_preset.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/filter_common.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/hardware_physmem.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/index.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/stream_flags_common.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/vli_size.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/alone_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/block_buffer_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/block_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/block_header_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/easy_buffer_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/easy_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/easy_encoder_memusage.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/filter_buffer_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/filter_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/filter_flags_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/index_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/stream_buffer_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/stream_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/stream_flags_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/vli_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/alone_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/auto_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/block_buffer_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/block_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/block_header_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/easy_decoder_memusage.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/filter_buffer_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/filter_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/filter_flags_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/index_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/index_hash.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/stream_buffer_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/stream_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/stream_flags_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common/vli_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/lzma/lzma_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/lzma/lzma_encoder_presets.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/lzma/lzma_encoder_optimum_fast.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/lzma/lzma_encoder_optimum_normal.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/lzma/fastpos_table.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/lzma/lzma_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/lzma/lzma2_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/lzma/lzma2_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/check/check.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/check/crc32_table.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/check/crc32_fast.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/check/crc64_table.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/check/crc64_fast.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/check/sha256.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/delta/delta_common.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/delta/delta_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/delta/delta_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/simple/simple_coder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/simple/simple_encoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/simple/simple_decoder.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/simple/x86.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/simple/powerpc.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/simple/ia64.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/simple/arm.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/simple/armthumb.c
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/simple/sparc.c
)

target_include_directories(lzma PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/api
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/common
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/check
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/delta
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/lz
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/lzma
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/rangecoder
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/simple
)

# Add xdelta library
add_library(xdelta STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta/xdelta3/xdelta3.c
)

target_include_directories(xdelta PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta/xdelta3
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/api
)

# Create our own library
add_library(EACopyLib STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include/EACopyClient.h
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/source/EACopyClient.cpp
    ${EACOPY_SHARED_FILES}
)

# Add the necessary include directories
target_include_directories(EACopyLib PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/api
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta
)

# Add the necessary definitions
target_compile_definitions(EACopyLib PUBLIC
    -DEACOPY_ALLOW_DELTA_COPY
    -DSIZEOF_SIZE_T=8
    -DSIZEOF_UNSIGNED_LONG_LONG=8
    -D_WIN32=1
    -DXD3_USE_LARGEFILE64=1
    -DSECONDARY_DJW=1
    -DSECONDARY_LZMA=1
    -DSECONDARY_FGK=1
    -DXD3_WIN32=1
    -DLZMA_API_STATIC
)

# Include directories for our binding
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src/binding
)

# Add the pybind11 module
pybind11_add_module(_eacopy_binding
    src/binding/eacopy_binding.cpp
    src/binding/eacopy_module.cpp
)

# Link EACopyLib against the dependency libraries
target_link_libraries(EACopyLib PRIVATE zstd lzma xdelta)

# Link against our library
target_link_libraries(_eacopy_binding PRIVATE EACopyLib)

# Install the binding module
install(TARGETS _eacopy_binding DESTINATION eacopy)
