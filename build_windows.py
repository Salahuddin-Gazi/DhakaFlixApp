#!/usr/bin/env python3
"""
Build script for DhakaFlix Streamer Windows executable.
This script automates the entire build process.

Usage:
    python build_windows.py              # Full build
    python build_windows.py --clean      # Clean build
    python build_windows.py --no-venv    # Build without virtual environment
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

class BuildError(Exception):
    """Build process error."""
    pass

class Builder:
    def __init__(self, venv_enabled=True, clean=False, verbose=False):
        self.venv_enabled = venv_enabled
        self.clean = clean
        self.verbose = verbose
        self.venv_path = Path("venv")
        self.dist_path = Path("dist")
        self.build_path = Path("build")

    def log(self, message, level="INFO"):
        """Log message with level."""
        if level == "INFO":
            prefix = "[✓]"
        elif level == "WARN":
            prefix = "[!]"
        elif level == "ERROR":
            prefix = "[✗]"
        else:
            prefix = "[*]"

        print(f"{prefix} {message}")

    def run_command(self, cmd, description=None, check=True):
        """Run a shell command."""
        if description:
            self.log(description)

        if self.verbose:
            self.log(f"Running: {cmd}", "DEBUG")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=not self.verbose,
                text=True
            )

            if check and result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                raise BuildError(f"Command failed: {cmd}\n{error_msg}")

            return result
        except Exception as e:
            if check:
                raise BuildError(f"Failed to run command: {cmd}\n{str(e)}")
            return None

    def get_python_cmd(self):
        """Get appropriate python command."""
        if self.venv_enabled and self.venv_path.exists():
            if sys.platform == "win32":
                return str(self.venv_path / "Scripts" / "python.exe")
            else:
                return str(self.venv_path / "bin" / "python")
        return sys.executable

    def get_pip_cmd(self):
        """Get appropriate pip command."""
        if self.venv_enabled and self.venv_path.exists():
            if sys.platform == "win32":
                return str(self.venv_path / "Scripts" / "pip.exe")
            else:
                return str(self.venv_path / "bin" / "pip")
        return f"{sys.executable} -m pip"

    def check_python(self):
        """Check Python installation."""
        self.log("Checking Python installation")

        result = self.run_command(
            f"{sys.executable} --version",
            check=False
        )

        if result.returncode != 0:
            raise BuildError("Python is not installed or not in PATH")

        self.log(result.stdout.strip())

    def setup_venv(self):
        """Create and setup virtual environment."""
        if not self.venv_enabled:
            self.log("Virtual environment disabled", "WARN")
            return

        if self.venv_path.exists():
            self.log("Virtual environment already exists")
            return

        self.log("Creating virtual environment")
        self.run_command(f"{sys.executable} -m venv venv")

    def install_dependencies(self):
        """Install all dependencies."""
        self.log("Installing dependencies from requirements.txt")

        pip_cmd = self.get_pip_cmd()

        # Upgrade pip, setuptools, wheel
        self.log("Upgrading pip, setuptools, and wheel")
        self.run_command(f"{pip_cmd} install --upgrade pip setuptools wheel")

        # Install requirements
        self.run_command(f"{pip_cmd} install -r requirements.txt")

        # Install additional build tools
        self.log("Installing additional build tools")
        self.run_command(
            f"{pip_cmd} install pyinstaller PyQt6-sip charset-normalizer urllib3"
        )

    def check_libmpv(self):
        """Check for libmpv DLL."""
        dll_path = Path("libmpv-2.dll")

        if dll_path.exists():
            self.log("libmpv-2.dll found")
            return True

        self.log("libmpv-2.dll not found", "WARN")
        self.log(
            "Please download from: "
            "https://sourceforge.net/projects/mpv-player-windows/files/libmpv/",
            "WARN"
        )

        return False

    def clean_previous_builds(self):
        """Clean previous builds."""
        if self.clean or self.build_path.exists():
            self.log("Cleaning previous builds")

            for path in [self.build_path, self.dist_path]:
                if path.exists():
                    shutil.rmtree(path)

    def build_executable(self):
        """Build executable using PyInstaller."""
        self.log("Building executable with PyInstaller")

        python_cmd = self.get_python_cmd()

        # Build
        cmd = f"{python_cmd} -m PyInstaller build.spec --clean --noconfirm"
        self.run_command(cmd)

        # Check if build was successful
        exe_dir = self.dist_path / "DhakaFlixStreamer"
        if not exe_dir.exists():
            raise BuildError("Build failed: dist folder not created")

        self.log(f"Executable created at {exe_dir}")

    def copy_libmpv(self):
        """Copy libmpv DLL to dist folder."""
        dll_source = Path("libmpv-2.dll")
        exe_dir = self.dist_path / "DhakaFlixStreamer"
        dll_dest = exe_dir / "libmpv-2.dll"

        if dll_source.exists():
            self.log("Copying libmpv-2.dll to dist folder")
            shutil.copy(dll_source, dll_dest)
            self.log(f"Copied to {dll_dest}")
        else:
            self.log("libmpv-2.dll not found, skipping copy", "WARN")

    def build(self):
        """Run complete build process."""
        print()
        print("=" * 60)
        print("DhakaFlix Streamer Windows Build")
        print("=" * 60)
        print()

        try:
            self.check_python()
            print()

            self.setup_venv()
            print()

            self.install_dependencies()
            print()

            self.check_libmpv()
            print()

            self.clean_previous_builds()
            print()

            self.build_executable()
            print()

            self.copy_libmpv()
            print()

            # Success
            print("=" * 60)
            self.log("BUILD SUCCESSFUL!")
            print("=" * 60)
            print()
            print(f"Executable location:")
            print(f"  {self.dist_path / 'DhakaFlixStreamer' / 'DhakaFlixStreamer.exe'}")
            print()

            if not (Path("libmpv-2.dll")).exists():
                print("⚠️  WARNING: libmpv-2.dll is missing!")
                print("   The application won't work without it.")
                print("   Download and place it in the dist folder.")
                print()

            return 0

        except BuildError as e:
            print()
            print("=" * 60)
            self.log("BUILD FAILED!", "ERROR")
            print("=" * 60)
            print()
            print(f"Error: {e}")
            print()
            return 1
        except Exception as e:
            print()
            print("=" * 60)
            self.log("UNEXPECTED ERROR!", "ERROR")
            print("=" * 60)
            print()
            print(f"Error: {e}")
            print()
            return 1

def main():
    parser = argparse.ArgumentParser(
        description="Build DhakaFlix Streamer for Windows"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean previous builds"
    )
    parser.add_argument(
        "--no-venv",
        action="store_true",
        help="Don't use virtual environment"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    builder = Builder(
        venv_enabled=not args.no_venv,
        clean=args.clean,
        verbose=args.verbose
    )

    return builder.build()

if __name__ == "__main__":
    sys.exit(main())
