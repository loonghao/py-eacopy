#include <pybind11/pybind11.h>
#include <string>
#include <iostream>

// Enable debug logging
#define EACOPY_DEBUG

namespace py = pybind11;

// Forward declarations
void init_eacopy_binding(py::module& m);

PYBIND11_MODULE(_eacopy_binding, m) {
    m.doc() = "Python bindings for EACopy, a high-performance file copy tool";

    // Add version information
    m.attr("__eacopy_version__") = "1.0.0"; // Replace with actual EACopy version

    // Initialize bindings
    init_eacopy_binding(m);

}
