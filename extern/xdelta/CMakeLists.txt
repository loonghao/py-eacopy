cmake_minimum_required(VERSION 3.15)
project(xdelta C)

# Set C standard
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Define xdelta library
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/xdelta3/xdelta3.c")
    # Using the Git submodule source
    set(XDELTA_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/xdelta3)
else()
    # Fallback to EACopy's version
    set(XDELTA_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../EACopy/external/xdelta/xdelta3)
endif()

# Check if the source file exists
if(NOT EXISTS "${XDELTA_SOURCE_DIR}/xdelta3.c")
    message(FATAL_ERROR "xdelta3.c not found at ${XDELTA_SOURCE_DIR}/xdelta3.c")
endif()

# Define source files explicitly
set(XDELTA_SOURCES "${XDELTA_SOURCE_DIR}/xdelta3.c")
set(XDELTA_HEADERS
    "${XDELTA_SOURCE_DIR}/xdelta3.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-blkcache.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-cfgs.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-decode.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-djw.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-fgk.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-hash.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-internal.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-list.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-lzma.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-main.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-merge.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-second.h"
    "${XDELTA_SOURCE_DIR}/xdelta3-test.h"
)

# Create the xdelta library
add_library(xdelta ${XDELTA_SOURCES} ${XDELTA_HEADERS})

# Add include directories - try both our own xz and EACopy's lzma
target_include_directories(xdelta PUBLIC
    ${XDELTA_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/../EACopy/external/lzma/liblzma/api
    ${CMAKE_CURRENT_SOURCE_DIR}/../xz/src/liblzma/api
)

# Add compile definitions
target_compile_definitions(xdelta PUBLIC
    -DSIZEOF_SIZE_T=8
    -DSIZEOF_UNSIGNED_LONG_LONG=8
    -DXD3_USE_LARGEFILE64=1
    -DSECONDARY_DJW=1
    -DSECONDARY_LZMA=1
    -DSECONDARY_FGK=1
    -DLZMA_API_STATIC
)

if(WIN32)
    target_compile_definitions(xdelta PUBLIC
        -D_WIN32=1
        -DXD3_WIN32=1
    )
endif()
