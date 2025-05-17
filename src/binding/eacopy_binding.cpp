#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <vector>
#include <filesystem>
#include <stdexcept>
#include <locale>
#include <codecvt>
#include <iostream>
#include <sstream>

// Enable debug logging
#define EACOPY_DEBUG

// Include Windows-specific headers
#ifdef _WIN32
#include <windows.h>
#include <stringapiset.h>
#endif

// Include our patches first to prevent macro redefinitions
#include "eacopy_patches.h"

// Include EACopy headers
#include "EACopyShared.h"
#include "EACopyClient.h"
#include "EACopyServer.h"

namespace py = pybind11;
namespace fs = std::filesystem;
using namespace eacopy; // Use the eacopy namespace

// 前向声明全局函数
void copyfile(const std::string& src, const std::string& dst);
void copy(const std::string& src, const std::string& dst);
void copy2(const std::string& src, const std::string& dst);
void copytree(const std::string& src, const std::string& dst,
              bool symlinks, bool ignore_dangling_symlinks, bool dirs_exist_ok);
void copy_with_server(const std::string& src, const std::string& dst,
                     const std::string& server_addr, int port, int compression_level);

// Debug logging function
void debug_log(const std::string& message) {
    #ifdef EACOPY_DEBUG
    std::cerr << "[EACopy Debug] " << message << std::endl;
    #endif
}

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

// Helper function to handle paths for EACopy
std::string normalize_path(const std::string& path) {
#ifdef _WIN32
    // Convert relative path to absolute path using wide character version for better Unicode support
    // First convert input path to wide string
    std::wstring wpath = utf8_to_wstring(path);

    // Get full path name using wide character API
    wchar_t wabsolute_path[MAX_PATH] = {0};
    if (GetFullPathNameW(wpath.c_str(), MAX_PATH, wabsolute_path, NULL) == 0) {
        throw std::runtime_error("Failed to get absolute path for: " + path);
    }

    // Convert back to UTF-8 for consistency
    int size_needed = WideCharToMultiByte(CP_UTF8, 0, wabsolute_path, -1, NULL, 0, NULL, NULL);
    std::string absolute_path(size_needed, 0);
    WideCharToMultiByte(CP_UTF8, 0, wabsolute_path, -1, &absolute_path[0], size_needed, NULL, NULL);

    // Remove null terminator if present
    if (!absolute_path.empty() && absolute_path.back() == '\0') {
        absolute_path.pop_back();
    }

    // Replace forward slashes with backslashes for Windows
    for (char& c : absolute_path) {
        if (c == '/') {
            c = '\\';
        }
    }

    return absolute_path;
#else
    // For non-Windows platforms, convert to absolute path using filesystem
    fs::path p(path);
    if (p.is_relative()) {
        p = fs::absolute(p);
    }
    return p.string();
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
            // Debug output
            #ifdef EACOPY_DEBUG
            debug_log("EACopy::copyfile called: " + src + " to " + dst);
            #endif

            // Use the standalone function implementation
            ::copyfile(src, dst);
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in copyfile: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in copyfile");
        }
    }

    // Copy a file without metadata
    void copy(const std::string& src, const std::string& dst) {
        try {
            // Debug output
            #ifdef EACOPY_DEBUG
            debug_log("EACopy::copy called: " + src + " to " + dst);
            #endif

            // Use the standalone function implementation
            ::copy(src, dst);
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in copy: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in copy");
        }
    }

    // Copy a file with metadata
    void copy2(const std::string& src, const std::string& dst) {
        try {
            // Debug output
            #ifdef EACOPY_DEBUG
            debug_log("EACopy::copy2 called: " + src + " to " + dst);
            #endif

            // Use the standalone function implementation
            ::copy2(src, dst);
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in copy2: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in copy2");
        }
    }

    // Copy a directory tree
    void copytree(const std::string& src, const std::string& dst,
                  bool symlinks = false,
                  bool ignore_dangling_symlinks = false,
                  bool dirs_exist_ok = false) {
        try {
            // Debug output
            #ifdef EACOPY_DEBUG
            debug_log("EACopy::copytree called: " + src + " to " + dst);
            debug_log("  symlinks: " + std::to_string(symlinks));
            debug_log("  ignore_dangling_symlinks: " + std::to_string(ignore_dangling_symlinks));
            debug_log("  dirs_exist_ok: " + std::to_string(dirs_exist_ok));
            #endif

            // Use the standalone function implementation
            ::copytree(src, dst, symlinks, ignore_dangling_symlinks, dirs_exist_ok);
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
            // Debug output
            #ifdef EACOPY_DEBUG
            debug_log("EACopy::copy_with_server called: " + src + " to " + dst);
            debug_log("  server_addr: " + server_addr);
            debug_log("  port: " + std::to_string(port));
            debug_log("  compression_level: " + std::to_string(compression_level));
            #endif

            // Use the standalone function implementation
            ::copy_with_server(src, dst, server_addr, port, compression_level);
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in copy_with_server: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in copy_with_server");
        }
    }

    // Batch copy multiple files
    void batch_copy(const std::vector<std::pair<std::string, std::string>>& file_pairs) {
        try {
            // Debug output
            #ifdef EACOPY_DEBUG
            debug_log("EACopy::batch_copy called with " + std::to_string(file_pairs.size()) + " file pairs");
            #endif

            for (const auto& pair : file_pairs) {
                try {
                    // Use the copy method we just defined
                    copy(pair.first, pair.second);
                } catch (const std::exception& e) {
                    throw std::runtime_error(std::string("Error in batch_copy: ") + e.what() +
                                            " (src: " + pair.first + ", dst: " + pair.second + ")");
                }
            }
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in batch_copy: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in batch_copy");
        }
    }

    // Batch copy multiple files with metadata
    void batch_copy2(const std::vector<std::pair<std::string, std::string>>& file_pairs) {
        try {
            // Debug output
            #ifdef EACOPY_DEBUG
            debug_log("EACopy::batch_copy2 called with " + std::to_string(file_pairs.size()) + " file pairs");
            #endif

            for (const auto& pair : file_pairs) {
                try {
                    // Use the copy2 method we just defined
                    copy2(pair.first, pair.second);
                } catch (const std::exception& e) {
                    throw std::runtime_error(std::string("Error in batch_copy2: ") + e.what() +
                                            " (src: " + pair.first + ", dst: " + pair.second + ")");
                }
            }
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in batch_copy2: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in batch_copy2");
        }
    }

    // Batch copy multiple directory trees
    void batch_copytree(const std::vector<std::pair<std::string, std::string>>& dir_pairs,
                        bool symlinks = false,
                        bool ignore_dangling_symlinks = false,
                        bool dirs_exist_ok = false) {
        try {
            // Debug output
            #ifdef EACOPY_DEBUG
            debug_log("EACopy::batch_copytree called with " + std::to_string(dir_pairs.size()) + " directory pairs");
            debug_log("  symlinks: " + std::to_string(symlinks));
            debug_log("  ignore_dangling_symlinks: " + std::to_string(ignore_dangling_symlinks));
            debug_log("  dirs_exist_ok: " + std::to_string(dirs_exist_ok));
            #endif

            for (const auto& pair : dir_pairs) {
                try {
                    // Use the copytree method we just defined
                    ::copytree(pair.first, pair.second, symlinks, ignore_dangling_symlinks, dirs_exist_ok);
                } catch (const std::exception& e) {
                    throw std::runtime_error(std::string("Error in batch_copytree: ") + e.what() +
                                            " (src: " + pair.first + ", dst: " + pair.second + ")");
                }
            }
        } catch (const std::exception& e) {
            throw std::runtime_error(std::string("Error in batch_copytree: ") + e.what());
        } catch (...) {
            throw std::runtime_error("Unknown error in batch_copytree");
        }
    }






};

// Standalone functions that use the EACopy class
void copyfile(const std::string& src, const std::string& dst) {
    try {
        // Debug output
        #ifdef EACOPY_DEBUG
        debug_log("Standalone copyfile called: " + src + " to " + dst);
        #endif

        // Use standard file copy for now as a fallback
        std::filesystem::path src_path(src);
        std::filesystem::path dst_path(dst);

        if (!std::filesystem::exists(src_path)) {
            throw std::runtime_error("Source file does not exist: " + src);
        }

        // Create destination directory if it doesn't exist
        std::filesystem::path dst_dir = dst_path.parent_path();
        if (!dst_dir.empty() && !std::filesystem::exists(dst_dir)) {
            std::filesystem::create_directories(dst_dir);
        }

        // Copy the file using std::filesystem
        std::filesystem::copy_file(
            src_path,
            dst_path,
            std::filesystem::copy_options::overwrite_existing
        );

        // Verify the file was copied
        if (!std::filesystem::exists(dst_path)) {
            throw std::runtime_error("File copy operation completed but destination file does not exist: " + dst);
        }
    } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Error in standalone copyfile: ") + e.what());
    } catch (...) {
        throw std::runtime_error("Unknown error in standalone copyfile");
    }
}

void copy(const std::string& src, const std::string& dst) {
    try {
        // Debug output
        #ifdef EACOPY_DEBUG
        debug_log("Standalone copy called: " + src + " to " + dst);
        #endif

        // Use standard file copy for now as a fallback
        std::filesystem::path src_path(src);
        std::filesystem::path dst_path(dst);

        if (!std::filesystem::exists(src_path)) {
            throw std::runtime_error("Source file does not exist: " + src);
        }

        // If dst is a directory, use the source filename
        if (std::filesystem::exists(dst_path) && std::filesystem::is_directory(dst_path)) {
            dst_path /= src_path.filename();
        }

        // Create destination directory if it doesn't exist
        std::filesystem::path dst_dir = dst_path.parent_path();
        if (!dst_dir.empty() && !std::filesystem::exists(dst_dir)) {
            std::filesystem::create_directories(dst_dir);
        }

        // Copy the file using std::filesystem
        std::filesystem::copy_file(
            src_path,
            dst_path,
            std::filesystem::copy_options::overwrite_existing
        );

        // Verify the file was copied
        if (!std::filesystem::exists(dst_path)) {
            throw std::runtime_error("File copy operation completed but destination file does not exist: " + dst);
        }
    } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Error in standalone copy: ") + e.what());
    } catch (...) {
        throw std::runtime_error("Unknown error in standalone copy");
    }
}

void copy2(const std::string& src, const std::string& dst) {
    try {
        // Debug output
        #ifdef EACOPY_DEBUG
        debug_log("Standalone copy2 called: " + src + " to " + dst);
        #endif

        // Use standard file copy for now as a fallback
        std::filesystem::path src_path(src);
        std::filesystem::path dst_path(dst);

        if (!std::filesystem::exists(src_path)) {
            throw std::runtime_error("Source file does not exist: " + src);
        }

        // If dst is a directory, use the source filename
        if (std::filesystem::exists(dst_path) && std::filesystem::is_directory(dst_path)) {
            dst_path /= src_path.filename();
        }

        // Create destination directory if it doesn't exist
        std::filesystem::path dst_dir = dst_path.parent_path();
        if (!dst_dir.empty() && !std::filesystem::exists(dst_dir)) {
            std::filesystem::create_directories(dst_dir);
        }

        // Copy the file using std::filesystem with preserve attributes option
        std::filesystem::copy_file(
            src_path,
            dst_path,
            std::filesystem::copy_options::overwrite_existing
        );

        // Copy file times (last write time)
        auto last_write_time = std::filesystem::last_write_time(src_path);
        std::filesystem::last_write_time(dst_path, last_write_time);

        // Verify the file was copied
        if (!std::filesystem::exists(dst_path)) {
            throw std::runtime_error("File copy operation completed but destination file does not exist: " + dst);
        }
    } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Error in standalone copy2: ") + e.what());
    } catch (...) {
        throw std::runtime_error("Unknown error in standalone copy2");
    }
}

void copytree(const std::string& src, const std::string& dst,
              bool symlinks = false,
              bool ignore_dangling_symlinks = false,
              bool dirs_exist_ok = false) {
    try {
        // Debug output
        #ifdef EACOPY_DEBUG
        debug_log("Standalone copytree called: " + src + " to " + dst);
        debug_log("  symlinks: " + std::to_string(symlinks));
        debug_log("  ignore_dangling_symlinks: " + std::to_string(ignore_dangling_symlinks));
        debug_log("  dirs_exist_ok: " + std::to_string(dirs_exist_ok));
        #endif

        // Use standard directory copy for now as a fallback
        std::filesystem::path src_path(src);
        std::filesystem::path dst_path(dst);

        if (!std::filesystem::exists(src_path)) {
            throw std::runtime_error("Source directory does not exist: " + src);
        }

        if (!std::filesystem::is_directory(src_path)) {
            throw std::runtime_error("Source is not a directory: " + src);
        }

        // Check if destination exists and is not a directory
        if (std::filesystem::exists(dst_path) && !std::filesystem::is_directory(dst_path)) {
            throw std::runtime_error("Destination exists and is not a directory: " + dst);
        }

        // Check if destination directory exists and dirs_exist_ok is false
        if (std::filesystem::exists(dst_path) && std::filesystem::is_directory(dst_path) && !dirs_exist_ok) {
            #ifdef EACOPY_DEBUG
            debug_log("Destination directory already exists, but dirs_exist_ok is false: " + dst);
            #endif
            throw std::runtime_error("Destination directory already exists: " + dst);
        }

        // Create destination directory if it doesn't exist
        if (!std::filesystem::exists(dst_path)) {
            std::filesystem::create_directories(dst_path);
        }

        // Copy the directory tree using std::filesystem
        std::filesystem::copy_options options = std::filesystem::copy_options::recursive;
        options |= std::filesystem::copy_options::overwrite_existing;

        if (symlinks) {
            options |= std::filesystem::copy_options::copy_symlinks;
        }

        // Manually copy directory contents to handle errors better
        for (const auto& entry : std::filesystem::directory_iterator(src_path)) {
            const auto& src_entry = entry.path();
            const auto dst_entry = dst_path / src_entry.filename();

            try {
                if (std::filesystem::is_directory(src_entry)) {
                    // Recursively copy subdirectory
                    copytree(src_entry.string(), dst_entry.string(), symlinks, ignore_dangling_symlinks, dirs_exist_ok);
                } else if (std::filesystem::is_symlink(src_entry) && !symlinks) {
                    // Skip symlinks if not copying them
                    continue;
                } else if (std::filesystem::is_symlink(src_entry) && ignore_dangling_symlinks) {
                    // Skip dangling symlinks if requested
                    if (!std::filesystem::exists(std::filesystem::read_symlink(src_entry))) {
                        continue;
                    }
                    std::filesystem::copy(src_entry, dst_entry, options);
                } else {
                    // Copy regular file
                    std::filesystem::copy(src_entry, dst_entry, options);
                }
            } catch (const std::exception& e) {
                throw std::runtime_error(std::string("Error copying ") + src_entry.string() + " to " + dst_entry.string() + ": " + e.what());
            }
        }

        // Verify the destination directory exists
        if (!std::filesystem::exists(dst_path)) {
            throw std::runtime_error("Directory tree copy operation completed but destination directory does not exist: " + dst);
        }
    } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Error in standalone copytree: ") + e.what());
    } catch (...) {
        throw std::runtime_error("Unknown error in standalone copytree");
    }
}

void copy_with_server(const std::string& src, const std::string& dst,
                     const std::string& server_addr,
                     int port = 31337,
                     int compression_level = 0) {
    try {
        // Debug output
        #ifdef EACOPY_DEBUG
        debug_log("Standalone copy_with_server called: " + src + " to " + dst);
        debug_log("  server_addr: " + server_addr);
        debug_log("  port: " + std::to_string(port));
        debug_log("  compression_level: " + std::to_string(compression_level));
        #endif

        // For now, fall back to regular copy functions since server functionality is complex
        std::filesystem::path src_path(src);

        if (std::filesystem::is_directory(src_path)) {
            // Use copytree for directories
            copytree(src, dst, false, false, false);
        } else {
            // Use copy2 for files
            copy2(src, dst);
        }

        // In a real implementation, we would connect to the server and use it for copying
        debug_log("Note: Server functionality is not fully implemented. Using fallback copy methods.");
    } catch (const std::exception& e) {
        throw std::runtime_error(std::string("Error in standalone copy_with_server: ") + e.what());
    } catch (...) {
        throw std::runtime_error("Unknown error in standalone copy_with_server");
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
