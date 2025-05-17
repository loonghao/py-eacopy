#include <string>
#include <cstdint>

// Define the exported functions
extern "C" {
    __declspec(dllexport) int EACopy_CopyFile(const wchar_t* source, const wchar_t* destination) {
        // Placeholder implementation
        return 0; // Success
    }

    __declspec(dllexport) int EACopy_CopyDirectory(const wchar_t* source, const wchar_t* destination, int recursive) {
        // Placeholder implementation
        return 0; // Success
    }

    __declspec(dllexport) const wchar_t* EACopy_GetVersion() {
        // Placeholder implementation
        static const wchar_t version[] = L"1.0.0";
        return version;
    }
}
