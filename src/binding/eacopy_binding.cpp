#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <vector>
#include <filesystem>
#include <stdexcept>
#include <locale>
#include <codecvt>

// Include Windows-specific headers
#ifdef _WIN32
#include <windows.h>
#include <stringapiset.h>
#endif

// Include EACopy headers
#include "EACopyShared.h"
#include "EACopyClient.h"
#include "EACopyServer.h"

namespace py = pybind11;
namespace fs = std::filesystem;
using namespace eacopy; // Use the eacopy namespace

// Helper function to convert string to wide string (UTF-16)
std::wstring utf8_to_wstring(const std::string& str) {
#ifdef _WIN32
    if (str.empty()) return std::wstring();

    // First try to convert assuming it's UTF-8
    int size_needed = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, str.c_str(), (int)str.size(), NULL, 0);

    // If UTF-8 conversion fails, try with the current ANSI code page
    if (size_needed <= 0) {
        UINT codePage = GetACP();  // Get current ANSI code page
        size_needed = MultiByteToWideChar(codePage, 0, str.c_str(), (int)str.size(), NULL, 0);

        if (size_needed <= 0) {
            throw std::runtime_error("Failed to convert string to wide string");
        }

        // Allocate the wide string
        std::wstring wstr(size_needed, 0);

        // Convert using the ANSI code page
        int result = MultiByteToWideChar(codePage, 0, str.c_str(), (int)str.size(), &wstr[0], size_needed);
        if (result <= 0) {
            throw std::runtime_error("Failed to convert string to wide string");
        }

        return wstr;
    }

    // If UTF-8 conversion succeeds, proceed normally
    std::wstring wstr(size_needed, 0);
    int result = MultiByteToWideChar(CP_UTF8, 0, str.c_str(), (int)str.size(), &wstr[0], size_needed);
    if (result <= 0) {
        throw std::runtime_error("Failed to convert UTF-8 string to wide string");
    }

    return wstr;
#else
    // For non-Windows platforms
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
    return converter.from_bytes(str);
#endif
}

// Helper function to handle long paths on Windows
std::string normalize_path(const std::string& path) {
#ifdef _WIN32
    // Add \\?\ prefix for long paths if not already present
    if (path.size() > 2 && path[0] == '\\' && path[1] == '\\' && path[2] == '?' && path[3] == '\\') {
        return path; // Already has the prefix
    }

    // Check if it's a UNC path (\\server\share)
    if (path.size() > 2 && path[0] == '\\' && path[1] == '\\' && path[2] != '?') {
        return "\\\\?\\UNC\\" + path.substr(2); // Convert to \\?\UNC\server\share
    }

    // Regular path
    if (path.size() > 2 && path[1] == ':' && (path[2] == '\\' || path[2] == '/')) {
        return "\\\\?\\" + path; // Add prefix to absolute path
    }

    // Convert relative path to absolute path using wide character version for better Unicode support
    // First convert input path to wide string
    std::wstring wpath = utf8_to_wstring(path);

    // Get full path name using wide character API
    wchar_t wabsolute_path[MAX_PATH] = {0};
    if (GetFullPathNameW(wpath.c_str(), MAX_PATH, wabsolute_path, NULL) == 0) {
        throw std::runtime_error("Failed to get absolute path");
    }

    // Convert back to UTF-8 for consistency
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, wabsolute_path, -1, NULL, 0, NULL, NULL);
    std::string absolute_path(size_needed, 0);
    WideCharToMultiByte(CP_UTF8, 0, wabsolute_path, -1, &absolute_path[0], size_needed, NULL, NULL);

    // Remove null terminator if present
    if (!absolute_path.empty() && absolute_path.back() == '\0') {
        absolute_path.pop_back();
    }

    return "\\\\?\\" + absolute_path;
#else
    return path; // No change for non-Windows platforms
#endif
}

// Helper function to convert wide string (UTF-16) to UTF-8 string
std::string wstring_to_utf8(const std::wstring& wstr) {
#ifdef _WIN32
    if (wstr.empty()) return std::string();

    // Get the required size
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), NULL, 0, NULL, NULL);
    if (size_needed <= 0) {
        throw std::runtime_error("Failed to convert wide string to UTF-8 string");
    }

    // Allocate the UTF-8 string
    std::string str(size_needed, 0);

    // Convert the string
    int result = WideCharToMultiByte(CP_UTF8, 0, wstr.c_str(), (int)wstr.size(), &str[0], size_needed, NULL, NULL);
    if (result <= 0) {
        throw std::runtime_error("Failed to convert wide string to UTF-8 string");
    }

    return str;
#else
    // For non-Windows platforms
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
    return converter.to_bytes(wstr);
#endif
}

// Define EACopy flags
#define EACOPY_COPY_DATA eacopy::FileFlags_Data
#define EACOPY_COPY_ATTRIBUTES eacopy::FileFlags_Attributes
#define EACOPY_COPY_TIMESTAMPS eacopy::FileFlags_Timestamps

// Wrapper class for EACopy functionality
class EACopy {
private:
    // Configuration options
    int thread_count = 4;
    int compression_level = 0;
    int buffer_size = 8 * 1024 * 1024;  // 8MB buffer
    bool preserve_metadata = true;
    bool follow_symlinks = false;
    bool dirs_exist_ok = false;

public:
    EACopy() {}

    // Constructor with configuration options
    EACopy(int thread_count, int compression_level, int buffer_size,
           bool preserve_metadata, bool follow_symlinks, bool dirs_exist_ok)
        : thread_count(thread_count),
          compression_level(compression_level),
          buffer_size(buffer_size),
          preserve_metadata(preserve_metadata),
          follow_symlinks(follow_symlinks),
          dirs_exist_ok(dirs_exist_ok) {}

    // Copy a file
    void copyfile(const std::string& src, const std::string& dst) {
        try {
            // Normalize paths for long path support
            std::string normalized_src = normalize_path(src);
            std::string normalized_dst = normalize_path(dst);

            // Convert to wide strings for better Unicode support
            std::wstring wsrc_path = utf8_to_wstring(normalized_src);
            std::wstring wdst_path = utf8_to_wstring(normalized_dst);

            // Use std::filesystem with wide strings for better Unicode support
            #ifdef _WIN32
            std::filesystem::path src_path(wsrc_path);
            std::filesystem::path dst_path(wdst_path);
            #else
            std::filesystem::path src_path(normalized_src);
            std::filesystem::path dst_path(normalized_dst);
            #endif

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

            settings.sourceDirectory = wsrc_path;
            settings.destDirectory = wdst_path;
            settings.dirCopyFlags = EACOPY_COPY_DATA;

            eacopy::Client client(settings);
            eacopy::ClientStats stats;
            eacopy::Log log;

            if (client.process(log, stats) != 0) {
                throw std::runtime_error("Failed to copy file: " + src + " to " + dst);
            }
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in copyfile: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in copyfile");
        }
    }

    // Copy a file with metadata
    void copy2(const std::string& src, const std::string& dst) {
        try {
            // Normalize paths for long path support
            std::string normalized_src = normalize_path(src);
            std::string normalized_dst = normalize_path(dst);

            // Convert to wide strings for better Unicode support
            std::wstring wsrc_path = utf8_to_wstring(normalized_src);
            std::wstring wdst_path = utf8_to_wstring(normalized_dst);

            // Use std::filesystem with wide strings for better Unicode support
            #ifdef _WIN32
            std::filesystem::path src_path(wsrc_path);
            std::filesystem::path dst_path(wdst_path);
            #else
            std::filesystem::path src_path(normalized_src);
            std::filesystem::path dst_path(normalized_dst);
            #endif

            if (!fs::exists(src_path)) {
                throw std::runtime_error("Source file does not exist: " + src);
            }

            if (fs::is_directory(src_path)) {
                throw std::runtime_error("Source is a directory, not a file: " + src);
            }

            // If dst is a directory, use the source filename
            if (fs::exists(dst_path) && fs::is_directory(dst_path)) {
                #ifdef _WIN32
                dst_path /= src_path.filename();
                // Update wdst_path with the new path including filename
                wdst_path = dst_path.wstring();
                #else
                dst_path /= src_path.filename();
                // Update normalized_dst with the new path including filename
                normalized_dst = dst_path.string();
                wdst_path = utf8_to_wstring(normalized_dst);
                #endif
            }

            // Create destination directory if it doesn't exist
            fs::path dst_dir = dst_path.parent_path();
            if (!dst_dir.empty() && !fs::exists(dst_dir)) {
                fs::create_directories(dst_dir);
            }

            // Use EACopy to copy the file with metadata
            eacopy::ClientSettings settings;

            settings.sourceDirectory = wsrc_path;
            settings.destDirectory = wdst_path;
            settings.dirCopyFlags = EACOPY_COPY_DATA | EACOPY_COPY_ATTRIBUTES | EACOPY_COPY_TIMESTAMPS;

            eacopy::Client client(settings);
            eacopy::ClientStats stats;
            eacopy::Log log;

            if (client.process(log, stats) != 0) {
                throw std::runtime_error("Failed to copy file with metadata: " + src + " to " + dst);
            }
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in copy2: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in copy2");
        }
    }

    // Copy a file without metadata
    void copy(const std::string& src, const std::string& dst) {
        try {
            // Normalize paths for long path support
            std::string normalized_src = normalize_path(src);
            std::string normalized_dst = normalize_path(dst);

            // Convert to wide strings for better Unicode support
            std::wstring wsrc_path = utf8_to_wstring(normalized_src);
            std::wstring wdst_path = utf8_to_wstring(normalized_dst);

            // Use std::filesystem with wide strings for better Unicode support
            #ifdef _WIN32
            std::filesystem::path src_path(wsrc_path);
            std::filesystem::path dst_path(wdst_path);
            #else
            std::filesystem::path src_path(normalized_src);
            std::filesystem::path dst_path(normalized_dst);
            #endif

            if (!fs::exists(src_path)) {
                throw std::runtime_error("Source file does not exist: " + src);
            }

            if (fs::is_directory(src_path)) {
                throw std::runtime_error("Source is a directory, not a file: " + src);
            }

            // If dst is a directory, use the source filename
            if (fs::exists(dst_path) && fs::is_directory(dst_path)) {
                #ifdef _WIN32
                dst_path /= src_path.filename();
                // Update wdst_path with the new path including filename
                wdst_path = dst_path.wstring();
                #else
                dst_path /= src_path.filename();
                // Update normalized_dst with the new path including filename
                normalized_dst = dst_path.string();
                wdst_path = utf8_to_wstring(normalized_dst);
                #endif
            }

            // Create destination directory if it doesn't exist
            fs::path dst_dir = dst_path.parent_path();
            if (!dst_dir.empty() && !fs::exists(dst_dir)) {
                fs::create_directories(dst_dir);
            }

            // Use EACopy to copy the file
            eacopy::ClientSettings settings;

            settings.sourceDirectory = wsrc_path;
            settings.destDirectory = wdst_path;
            settings.dirCopyFlags = EACOPY_COPY_DATA;

            eacopy::Client client(settings);
            eacopy::ClientStats stats;
            eacopy::Log log;

            if (client.process(log, stats) != 0) {
                throw std::runtime_error("Failed to copy file: " + src + " to " + dst);
            }
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in copy: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in copy");
        }
    }

    // Copy a directory tree
    void copytree(const std::string& src, const std::string& dst,
                  bool symlinks = false,
                  bool ignore_dangling_symlinks = false,
                  bool dirs_exist_ok = false) {
        try {
            // Normalize paths for long path support
            std::string normalized_src = normalize_path(src);
            std::string normalized_dst = normalize_path(dst);

            // Convert to wide strings for better Unicode support
            std::wstring wsrc_path = utf8_to_wstring(normalized_src);
            std::wstring wdst_path = utf8_to_wstring(normalized_dst);

            // Use std::filesystem with wide strings for better Unicode support
            #ifdef _WIN32
            std::filesystem::path src_path(wsrc_path);
            std::filesystem::path dst_path(wdst_path);
            #else
            std::filesystem::path src_path(normalized_src);
            std::filesystem::path dst_path(normalized_dst);
            #endif

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

            settings.sourceDirectory = wsrc_path;
            settings.destDirectory = wdst_path;
            settings.dirCopyFlags = EACOPY_COPY_DATA | EACOPY_COPY_ATTRIBUTES | EACOPY_COPY_TIMESTAMPS;
            settings.copySubdirDepth = -1; // -1 means unlimited depth

            // Handle symlinks option
            if (symlinks) {
                // EACopy doesn't have a specific flag for symbolic links
                // Instead, we can use the replaceSymLinksAtDestination setting
                settings.replaceSymLinksAtDestination = !symlinks;
            }

            eacopy::Client client(settings);
            eacopy::ClientStats stats;
            eacopy::Log log;

            if (client.process(log, stats) != 0) {
                throw std::runtime_error("Failed to copy directory tree: " + src + " to " + dst);
            }
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in copytree: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in copytree");
        }
    }

    // Copy with server
    void copy_with_server(const std::string& src, const std::string& dst,
                         const std::string& server_addr,
                         int port = 31337,
                         int compression_level = 0) {
        try {
            // Normalize paths for long path support
            std::string normalized_src = normalize_path(src);
            std::string normalized_dst = normalize_path(dst);

            // Convert to wide strings for better Unicode support
            std::wstring wsrc_path = utf8_to_wstring(normalized_src);
            std::wstring wdst_path = utf8_to_wstring(normalized_dst);

            // Use std::filesystem with wide strings for better Unicode support
            #ifdef _WIN32
            std::filesystem::path src_path(wsrc_path);
            std::filesystem::path dst_path(wdst_path);
            #else
            std::filesystem::path src_path(normalized_src);
            std::filesystem::path dst_path(normalized_dst);
            #endif

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

            // Convert server address to wide string
            std::wstring wserver_addr = utf8_to_wstring(server_addr);

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
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in copy_with_server: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in copy_with_server");
        }
    }

    // Batch copy multiple files
    void batch_copy(const std::vector<std::pair<std::string, std::string>>& file_pairs) {
        for (const auto& pair : file_pairs) {
            try {
                copy(pair.first, pair.second);
            } catch (const std::exception& e) {
                throw std::runtime_error(std::string("Error in batch_copy: ") + e.what() +
                                        " (src: " + pair.first + ", dst: " + pair.second + ")");
            }
        }
    }

    // Batch copy multiple files with metadata
    void batch_copy2(const std::vector<std::pair<std::string, std::string>>& file_pairs) {
        for (const auto& pair : file_pairs) {
            try {
                copy2(pair.first, pair.second);
            } catch (const std::exception& e) {
                throw std::runtime_error(std::string("Error in batch_copy2: ") + e.what() +
                                        " (src: " + pair.first + ", dst: " + pair.second + ")");
            }
        }
    }

    // Batch copy multiple directory trees
    void batch_copytree(const std::vector<std::pair<std::string, std::string>>& dir_pairs,
                        bool symlinks = false,
                        bool ignore_dangling_symlinks = false,
                        bool dirs_exist_ok = false) {
        for (const auto& pair : dir_pairs) {
            try {
                copytree(pair.first, pair.second, symlinks, ignore_dangling_symlinks, dirs_exist_ok);
            } catch (const std::exception& e) {
                throw std::runtime_error(std::string("Error in batch_copytree: ") + e.what() +
                                        " (src: " + pair.first + ", dst: " + pair.second + ")");
            }
        }
    }
};

// Standalone functions that use the EACopy class
void copyfile(const std::string& src, const std::string& dst) {
    try {
        EACopy eacopy;
        eacopy.copyfile(src, dst);
    } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Error in standalone copyfile: ") + e.what());
    }
}

void copy(const std::string& src, const std::string& dst) {
    try {
        EACopy eacopy;
        eacopy.copy(src, dst);
    } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Error in standalone copy: ") + e.what());
    }
}

void copy2(const std::string& src, const std::string& dst) {
    try {
        EACopy eacopy;
        eacopy.copy2(src, dst);
    } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Error in standalone copy2: ") + e.what());
    }
}

void copytree(const std::string& src, const std::string& dst,
              bool symlinks = false,
              bool ignore_dangling_symlinks = false,
              bool dirs_exist_ok = false) {
    try {
        EACopy eacopy;
        eacopy.copytree(src, dst, symlinks, ignore_dangling_symlinks, dirs_exist_ok);
    } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Error in standalone copytree: ") + e.what());
    }
}

void copy_with_server(const std::string& src, const std::string& dst,
                     const std::string& server_addr,
                     int port = 31337,
                     int compression_level = 0) {
    try {
        EACopy eacopy;
        eacopy.copy_with_server(src, dst, server_addr, port, compression_level);
    } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Error in standalone copy_with_server: ") + e.what());
    }
}

// Initialize the bindings
void init_eacopy_binding(py::module& m) {
    // Bind the EACopy class
    py::class_<EACopy>(m, "EACopy")
        .def(py::init<>())
        .def(py::init<int, int, int, bool, bool, bool>(),
             py::arg("thread_count") = 4,
             py::arg("compression_level") = 0,
             py::arg("buffer_size") = 8 * 1024 * 1024,
             py::arg("preserve_metadata") = true,
             py::arg("follow_symlinks") = false,
             py::arg("dirs_exist_ok") = false,
             "Initialize EACopy with custom configuration")
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
             "Copy file or directory using EACopyService for acceleration")
        .def("batch_copy", &EACopy::batch_copy,
             py::arg("file_pairs"),
             "Copy multiple files in batch")
        .def("batch_copy2", &EACopy::batch_copy2,
             py::arg("file_pairs"),
             "Copy multiple files with metadata in batch")
        .def("batch_copytree", &EACopy::batch_copytree,
             py::arg("dir_pairs"),
             py::arg("symlinks") = false,
             py::arg("ignore_dangling_symlinks") = false,
             py::arg("dirs_exist_ok") = false,
             "Copy multiple directory trees in batch")
        .def("__enter__", [](EACopy& self) { return &self; })
        .def("__exit__", [](EACopy& self, py::object exc_type, py::object exc_value, py::object traceback) {
            // No cleanup needed, just a context manager for convenience
            return false;  // Don't suppress exceptions
        });

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
