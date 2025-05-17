#!/usr/bin/env python
"""
Build wheel packages for py-eacopy on Unix-like systems (Linux, macOS).

This script is designed to build wheel packages for py-eacopy on Unix-like systems,
where cibuildwheel may encounter issues. It tries multiple build methods
and uses the first one that succeeds.
"""

# Import built-in modules
import os
import platform
import subprocess
import sys


def run_command(cmd, cwd=None, env=None):
    """Run a command and return whether it succeeded and its output."""
    print(f"Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        print(result.stdout)
        return result.returncode == 0, result.stdout
    except Exception as e:
        print(f"Error running command: {e}")
        return False, str(e)


def install_dependencies():
    """Install build dependencies."""
    print("Installing build dependencies...")
    
    # Install basic dependencies
    success, _ = run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools"]
    )
    if not success:
        return False
    
    # Install build dependencies
    success, _ = run_command(
        [
            sys.executable, "-m", "pip", "install",
            "scikit-build-core>=0.5.0",
            "pybind11>=2.10.0",
            "cmake>=3.15.0",
            "ninja",
        ]
    )
    
    return success


def build_wheels():
    """Build wheel packages using multiple methods."""
    print("Building wheels...")
    
    # Create wheelhouse directory if it doesn't exist
    os.makedirs("wheelhouse", exist_ok=True)
    
    # Determine platform
    system = platform.system().lower()
    if system == "linux":
        platform_name = "linux"
    elif system == "darwin":
        platform_name = "macos"
    else:
        print(f"Unsupported platform: {system}")
        return False
    
    # Try different build methods
    build_methods = [
        {
            "name": "cibuildwheel",
            "install": [
                sys.executable, "-m", "pip", "install",
                "cibuildwheel", "wheel", "setuptools>=42.0.0",
                "setuptools_scm>=8.0.0", "scikit-build-core>=0.5.0",
                "pybind11>=2.10.0", "cmake>=3.15.0", "ninja"
            ],
            "build": [
                sys.executable, "-m", "cibuildwheel",
                "--platform", platform_name,
                "--output-dir", "wheelhouse"
            ],
            "env_additions": {
                "CIBW_BUILD_VERBOSITY": "3",
                "CIBW_BUILD": f"cp{sys.version_info.major}{sys.version_info.minor}-*"
            }
        },
        {
            "name": "build",
            "install": [
                sys.executable, "-m", "pip", "install",
                "build", "wheel", "setuptools>=42.0.0",
                "scikit-build-core>=0.5.0", "pybind11>=2.10.0",
                "cmake>=3.15.0", "ninja"
            ],
            "build": [
                sys.executable, "-m", "build",
                "--wheel",
                "--outdir", "dist/"
            ],
            "env_additions": {}
        },
        {
            "name": "pip wheel",
            "install": [
                sys.executable, "-m", "pip", "install",
                "wheel", "setuptools>=42.0.0",
                "scikit-build-core>=0.5.0", "pybind11>=2.10.0",
                "cmake>=3.15.0", "ninja"
            ],
            "build": [
                sys.executable, "-m", "pip", "wheel",
                ".",
                "-w", "wheelhouse",
                "--no-deps"
            ],
            "env_additions": {}
        }
    ]
    
    for method in build_methods:
        print(f"\nTrying build method: {method['name']}")
        
        # Install dependencies for this method
        success, _ = run_command(method["install"])
        if not success:
            print(f"Failed to install dependencies for {method['name']}")
            continue
        
        # Set environment variables
        env = os.environ.copy()
        for key, value in method["env_additions"].items():
            env[key] = value
        
        # Run build command
        success, _ = run_command(method["build"], env=env)
        if success:
            print(f"Successfully built wheels using {method['name']}")
            
            # If using build, move wheels from dist to wheelhouse
            if method["name"] == "build" and os.path.exists("dist"):
                os.makedirs("wheelhouse", exist_ok=True)
                for wheel in os.listdir("dist"):
                    if wheel.endswith(".whl"):
                        src = os.path.join("dist", wheel)
                        dst = os.path.join("wheelhouse", wheel)
                        print(f"Moving {src} to {dst}")
                        os.rename(src, dst)
            
            return True
        
        print(f"Failed to build wheels using {method['name']}")
    
    return False


def verify_wheels():
    """Verify the built wheels."""
    print("\nVerifying wheels...")
    
    # Check if wheelhouse directory exists
    if not os.path.exists("wheelhouse"):
        print("No wheelhouse directory found.")
        return False
    
    # List wheels
    wheels = [f for f in os.listdir("wheelhouse") if f.endswith(".whl")]
    if not wheels:
        print("No wheels found in wheelhouse directory.")
        return False
    
    print(f"Found {len(wheels)} wheels:")
    for wheel in wheels:
        print(f"  - {wheel}")
    
    return True


def main():
    """Main function."""
    print("=" * 80)
    print("Building wheels for py-eacopy")
    print("=" * 80)
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies.")
        return 1
    
    # Build wheels
    if not build_wheels():
        print("Failed to build wheels.")
        return 1
    
    # Verify wheels
    if not verify_wheels():
        print("Failed to verify wheels.")
        return 1
    
    print("=" * 80)
    print("Wheel build completed successfully!")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
