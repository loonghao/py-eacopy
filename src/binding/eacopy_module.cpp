#define PYBIND11_PYTHON_VERSION 0x03080000  // Python 3.8
// Removed PYBIND11_STATIC_LIBRARY to use dynamic linking with Python

#include <pybind11/pybind11.h>
#include <string>
#include <iostream>

namespace py = pybind11;

// Forward declarations
void init_eacopy_binding(py::module& m);

PYBIND11_MODULE(_eacopy_binding, m) {
    m.doc() = "Python bindings for EACopy, a high-performance file copy tool";

    // Add version information
    m.attr("__eacopy_version__") = "1.0.0"; // Replace with actual EACopy version

    // Initialize bindings
    init_eacopy_binding(m);

    // Print Python version information for debugging
    std::cout << "Using Python " << PY_VERSION << std::endl;
}
