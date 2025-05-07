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
add_subdirectory(extern/EACopy EXCLUDE_FROM_ALL)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/extern/EACopy/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src/binding
)

# Add the pybind11 module
pybind11_add_module(_eacopy_binding
    src/binding/eacopy_binding.cpp
    src/binding/eacopy_module.cpp
)

# Link against EACopy
target_link_libraries(_eacopy_binding PRIVATE EACopy)

# Install the binding module
install(TARGETS _eacopy_binding DESTINATION eacopy)
