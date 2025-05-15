#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <vector>
#include <filesystem>
#include <stdexcept>

// Include EACopy headers
#include "EACopyShared.h"
#include "EACopyClient.h"
#include "EACopyServer.h"

namespace py = pybind11;
namespace fs = std::filesystem;
using namespace eacopy; // Use the eacopy namespace

// Define EACopy flags
#define EACOPY_COPY_DATA eacopy::FileFlags_Data
#define EACOPY_COPY_ATTRIBUTES eacopy::FileFlags_Attributes
#define EACOPY_COPY_TIMESTAMPS eacopy::FileFlags_Timestamps

// Wrapper class for EACopy functionality
class EACopy {
public:
    EACopy() {}

    // Copy a file
    void copyfile(const std::string& src, const std::string& dst) {
        fs::path src_path(src);
        fs::path dst_path(dst);

        if (!fs::exists(src_path)) {
            throw std::runtime_error("Source file does not exist: " + src);
        }

        if (fs::is_directory(src_path)) {
            throw std::runtime_error("Source is a directory, not a file: " + src);
        }

        // Create destination directory if it doesn't exist
        fs::path dst_dir = dst_path.parent_path();
        if (!dst_dir.empty() && !fs::exists(dst_dir)) {
            fs::create_directories(dst_dir);
        }

        // Use EACopy to copy the file
        eacopy::ClientSettings settings;
        // Convert std::string to std::wstring for paths
        std::wstring wsrc_path(src_path.string().begin(), src_path.string().end());
        std::wstring wdst_path(dst_path.string().begin(), dst_path.string().end());
        settings.sourceDirectory = wsrc_path;
        settings.destDirectory = wdst_path;
        settings.dirCopyFlags = EACOPY_COPY_DATA;

        eacopy::Client client(settings);
        eacopy::ClientStats stats;
        eacopy::Log log;

        if (client.process(log, stats) != 0) {
            throw std::runtime_error("Failed to copy file: " + src + " to " + dst);
        }
    }

    // Copy a file with metadata
    void copy2(const std::string& src, const std::string& dst) {
        fs::path src_path(src);
        fs::path dst_path(dst);

        if (!fs::exists(src_path)) {
            throw std::runtime_error("Source file does not exist: " + src);
        }

        if (fs::is_directory(src_path)) {
            throw std::runtime_error("Source is a directory, not a file: " + src);
        }

        // If dst is a directory, use the source filename
        if (fs::exists(dst_path) && fs::is_directory(dst_path)) {
            dst_path /= src_path.filename();
        }

        // Create destination directory if it doesn't exist
        fs::path dst_dir = dst_path.parent_path();
        if (!dst_dir.empty() && !fs::exists(dst_dir)) {
            fs::create_directories(dst_dir);
        }

        // Use EACopy to copy the file with metadata
        eacopy::ClientSettings settings;
        // Convert std::string to std::wstring for paths
        std::wstring wsrc_path(src_path.string().begin(), src_path.string().end());
        std::wstring wdst_path(dst_path.string().begin(), dst_path.string().end());
        settings.sourceDirectory = wsrc_path;
        settings.destDirectory = wdst_path;
        settings.dirCopyFlags = EACOPY_COPY_DATA | EACOPY_COPY_ATTRIBUTES | EACOPY_COPY_TIMESTAMPS;

        eacopy::Client client(settings);
        eacopy::ClientStats stats;
        eacopy::Log log;

        if (client.process(log, stats) != 0) {
            throw std::runtime_error("Failed to copy file with metadata: " + src + " to " + dst);
        }
    }

    // Copy a file without metadata
    void copy(const std::string& src, const std::string& dst) {
        fs::path src_path(src);
        fs::path dst_path(dst);

        if (!fs::exists(src_path)) {
            throw std::runtime_error("Source file does not exist: " + src);
        }

        if (fs::is_directory(src_path)) {
            throw std::runtime_error("Source is a directory, not a file: " + src);
        }

        // If dst is a directory, use the source filename
        if (fs::exists(dst_path) && fs::is_directory(dst_path)) {
            dst_path /= src_path.filename();
        }

        // Create destination directory if it doesn't exist
        fs::path dst_dir = dst_path.parent_path();
        if (!dst_dir.empty() && !fs::exists(dst_dir)) {
            fs::create_directories(dst_dir);
        }

        // Use EACopy to copy the file
        eacopy::ClientSettings settings;
        // Convert std::string to std::wstring for paths
        std::wstring wsrc_path(src_path.string().begin(), src_path.string().end());
        std::wstring wdst_path(dst_path.string().begin(), dst_path.string().end());
        settings.sourceDirectory = wsrc_path;
        settings.destDirectory = wdst_path;
        settings.dirCopyFlags = EACOPY_COPY_DATA;

        eacopy::Client client(settings);
        eacopy::ClientStats stats;
        eacopy::Log log;

        if (client.process(log, stats) != 0) {
            throw std::runtime_error("Failed to copy file: " + src + " to " + dst);
        }
    }

    // Copy a directory tree
    void copytree(const std::string& src, const std::string& dst,
                  bool symlinks = false,
                  bool ignore_dangling_symlinks = false,
                  bool dirs_exist_ok = false) {
        fs::path src_path(src);
        fs::path dst_path(dst);

        if (!fs::exists(src_path)) {
            throw std::runtime_error("Source directory does not exist: " + src);
        }

        if (!fs::is_directory(src_path)) {
            throw std::runtime_error("Source is not a directory: " + src);
        }

        // Check if destination exists and is not a directory
        if (fs::exists(dst_path) && !fs::is_directory(dst_path)) {
            throw std::runtime_error("Destination exists and is not a directory: " + dst);
        }

        // Check if destination directory exists and dirs_exist_ok is false
        if (fs::exists(dst_path) && fs::is_directory(dst_path) && !dirs_exist_ok) {
            throw std::runtime_error("Destination directory already exists: " + dst);
        }

        // Create destination directory if it doesn't exist
        if (!fs::exists(dst_path)) {
            fs::create_directories(dst_path);
        }

        // Use EACopy to copy the directory tree
        eacopy::ClientSettings settings;
        // Convert std::string to std::wstring for paths
        std::wstring wsrc_path(src_path.string().begin(), src_path.string().end());
        std::wstring wdst_path(dst_path.string().begin(), dst_path.string().end());
        settings.sourceDirectory = wsrc_path;
        settings.destDirectory = wdst_path;
        settings.dirCopyFlags = EACOPY_COPY_DATA | EACOPY_COPY_ATTRIBUTES | EACOPY_COPY_TIMESTAMPS;
        settings.copySubdirDepth = -1; // -1 means unlimited depth

        eacopy::Client client(settings);
        eacopy::ClientStats stats;
        eacopy::Log log;

        if (client.process(log, stats) != 0) {
            throw std::runtime_error("Failed to copy directory tree: " + src + " to " + dst);
        }
    }

    // Copy with server
    void copy_with_server(const std::string& src, const std::string& dst,
                         const std::string& server_addr,
                         int port = 31337,
                         int compression_level = 0) {
        fs::path src_path(src);
        fs::path dst_path(dst);

        if (!fs::exists(src_path)) {
            throw std::runtime_error("Source does not exist: " + src);
        }

        // Create destination directory if it doesn't exist
        fs::path dst_dir = dst_path;
        if (!fs::is_directory(src_path)) {
            dst_dir = dst_path.parent_path();
        }

        if (!dst_dir.empty() && !fs::exists(dst_dir)) {
            fs::create_directories(dst_dir);
        }

        // Use EACopy with server to copy
        eacopy::ClientSettings settings;
        // Convert std::string to std::wstring for paths and server address
        std::wstring wsrc_path(src_path.string().begin(), src_path.string().end());
        std::wstring wdst_path(dst_path.string().begin(), dst_path.string().end());
        std::wstring wserver_addr(server_addr.begin(), server_addr.end());
        settings.sourceDirectory = wsrc_path;
        settings.destDirectory = wdst_path;
        settings.dirCopyFlags = EACOPY_COPY_DATA | EACOPY_COPY_ATTRIBUTES | EACOPY_COPY_TIMESTAMPS;
        settings.copySubdirDepth = fs::is_directory(src_path) ? -1 : 0;
        settings.serverAddress = wserver_addr;
        settings.serverPort = port;
        settings.compressionLevel = compression_level;
        settings.useServer = eacopy::UseServer_Required;

        eacopy::Client client(settings);
        eacopy::ClientStats stats;
        eacopy::Log log;

        if (client.process(log, stats) != 0) {
            throw std::runtime_error("Failed to copy with server: " + src + " to " + dst);
        }
    }
};

// Standalone functions that use the EACopy class
void copyfile(const std::string& src, const std::string& dst) {
    EACopy eacopy;
    eacopy.copyfile(src, dst);
}

void copy(const std::string& src, const std::string& dst) {
    EACopy eacopy;
    eacopy.copy(src, dst);
}

void copy2(const std::string& src, const std::string& dst) {
    EACopy eacopy;
    eacopy.copy2(src, dst);
}

void copytree(const std::string& src, const std::string& dst,
              bool symlinks = false,
              bool ignore_dangling_symlinks = false,
              bool dirs_exist_ok = false) {
    EACopy eacopy;
    eacopy.copytree(src, dst, symlinks, ignore_dangling_symlinks, dirs_exist_ok);
}

void copy_with_server(const std::string& src, const std::string& dst,
                     const std::string& server_addr,
                     int port = 31337,
                     int compression_level = 0) {
    EACopy eacopy;
    eacopy.copy_with_server(src, dst, server_addr, port, compression_level);
}

// Initialize the bindings
void init_eacopy_binding(py::module& m) {
    // Bind the EACopy class
    py::class_<EACopy>(m, "EACopy")
        .def(py::init<>())
        .def("copyfile", &EACopy::copyfile,
             py::arg("src"), py::arg("dst"),
             "Copy file content from src to dst")
        .def("copy", &EACopy::copy,
             py::arg("src"), py::arg("dst"),
             "Copy file from src to dst, preserving file content but not metadata")
        .def("copy2", &EACopy::copy2,
             py::arg("src"), py::arg("dst"),
             "Copy file from src to dst, preserving file content and metadata")
        .def("copytree", &EACopy::copytree,
             py::arg("src"), py::arg("dst"),
             py::arg("symlinks") = false,
             py::arg("ignore_dangling_symlinks") = false,
             py::arg("dirs_exist_ok") = false,
             "Recursively copy a directory tree from src to dst")
        .def("copy_with_server", &EACopy::copy_with_server,
             py::arg("src"), py::arg("dst"),
             py::arg("server_addr"),
             py::arg("port") = 31337,
             py::arg("compression_level") = 0,
             "Copy file or directory using EACopyService for acceleration");

    // Bind standalone functions
    m.def("copyfile", &copyfile,
          py::arg("src"), py::arg("dst"),
          "Copy file content from src to dst");
    m.def("copy", &copy,
          py::arg("src"), py::arg("dst"),
          "Copy file from src to dst, preserving file content but not metadata");
    m.def("copy2", &copy2,
          py::arg("src"), py::arg("dst"),
          "Copy file from src to dst, preserving file content and metadata");
    m.def("copytree", &copytree,
          py::arg("src"), py::arg("dst"),
          py::arg("symlinks") = false,
          py::arg("ignore_dangling_symlinks") = false,
          py::arg("dirs_exist_ok") = false,
          "Recursively copy a directory tree from src to dst");
    m.def("copy_with_server", &copy_with_server,
          py::arg("src"), py::arg("dst"),
          py::arg("server_addr"),
          py::arg("port") = 31337,
          py::arg("compression_level") = 0,
          "Copy file or directory using EACopyService for acceleration");
}
