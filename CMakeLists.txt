cmake_minimum_required(VERSION 3.15...3.30)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX C)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

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

# Configure EACopy options
set(EACOPY_BUILD_TESTS OFF CACHE BOOL "Build EACopy tests")
set(EACOPY_BUILD_SERVICE OFF CACHE BOOL "Build EACopy service")
# Set CMake policy version minimum to handle older CMake code in dependencies
set(CMAKE_POLICY_VERSION_MINIMUM 3.5 CACHE STRING "Minimum CMake policy version")

# Update EACopy's CMake minimum version to be compatible with our project
file(READ ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/CMakeLists.txt EACOPY_CMAKE_CONTENT)
string(REPLACE "cmake_minimum_required(VERSION 3.1)" "cmake_minimum_required(VERSION 3.15)" EACOPY_CMAKE_CONTENT "${EACOPY_CMAKE_CONTENT}")
file(WRITE ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/CMakeLists.txt "${EACOPY_CMAKE_CONTENT}")

# Set global definitions for all targets
add_definitions(
    -DSIZEOF_UNSIGNED_LONG_LONG=8
    -DXD3_USE_LARGEFILE64=1
    -DSECONDARY_DJW=1
    -DSECONDARY_LZMA=1
    -DSECONDARY_FGK=1
    -DLZMA_API_STATIC
)

if(WIN32)
    add_definitions(-D_WIN32=1 -DXD3_WIN32=1)
endif()

# Apply patch to xdelta3.h to disable static_assert
execute_process(
    COMMAND ${CMAKE_COMMAND} -E copy
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta/xdelta3/xdelta3.h
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta/xdelta3/xdelta3.h.orig
)

execute_process(
    COMMAND ${CMAKE_COMMAND} -E copy
    ${CMAKE_CURRENT_SOURCE_DIR}/xdelta3.h.patch
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta/xdelta3/
)

execute_process(
    COMMAND git apply xdelta3.h.patch
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta/xdelta3/
)

# Add EACopy as a subdirectory
# This will build the EACopy library and its dependencies (zstd, lzma, xdelta)
add_subdirectory(extern/EACopy EXCLUDE_FROM_ALL)

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

# Add the necessary include directories
target_include_directories(EACopyLib PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/zstd/lib
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/lzma/liblzma/api
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/external/xdelta/xdelta3
)

# Add the necessary definitions
target_compile_definitions(EACopyLib PUBLIC
    -DEACOPY_ALLOW_DELTA_COPY
)

# Link EACopyLib against the EACopy dependencies
target_link_libraries(EACopyLib PRIVATE libzstd_static lzma xdelta)

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

# Link against our library
target_link_libraries(_eacopy_binding PRIVATE EACopyLib)

# Install the binding module
install(TARGETS _eacopy_binding DESTINATION eacopy)
