use std::env;

fn main() {
    println!("cargo:rerun-if-changed=build.rs");
    println!("cargo:rerun-if-changed=src/ffi.rs");

    // Get target
    let target = env::var("TARGET").unwrap_or_default();

    // Check if we're building for Windows
    let is_windows = target.contains("windows");

    if is_windows {
        // Link to Windows dependencies if needed
        println!("cargo:rustc-link-lib=dylib=ws2_32");
        println!("cargo:rustc-link-lib=dylib=userenv");
    } else {
        // For non-Windows platforms, we would need a different approach
        println!("cargo:warning=Building on non-Windows platforms is not fully supported yet");
    }
}
