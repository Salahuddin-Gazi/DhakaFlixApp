#!/usr/bin/env python3
"""
Download libmpv-2.dll for Windows build
This script downloads the required libmpv DLL for the DhakaFlix application.
"""

import os
import sys
import platform
import zipfile
import tempfile
from pathlib import Path

def download_libmpv():
    """Download libmpv DLL from mpv project releases."""

    if platform.system() != "Windows":
        print("This script is for Windows builds only.")
        print(f"Current platform: {platform.system()}")
        return False

    dll_path = Path("libmpv-2.dll")

    # Check if DLL already exists
    if dll_path.exists():
        print(f"✓ libmpv-2.dll already exists at {dll_path.absolute()}")
        return True

    print("=" * 60)
    print("libmpv DLL Download Helper")
    print("=" * 60)
    print()

    print("The DLL file 'libmpv-2.dll' is required but not found.")
    print()
    print("You have two options:")
    print()
    print("Option 1: Manual Download (Recommended)")
    print("-" * 60)
    print("Download from SourceForge:")
    print("  https://sourceforge.net/projects/mpv-player-windows/files/libmpv/")
    print()
    print("Or from GitHub releases:")
    print("  https://github.com/mpv-player/mpv-windows-build/releases/")
    print()
    print("1. Download the latest libmpv build")
    print("2. Extract the DLL file")
    print("3. Place it in the project root directory")
    print("4. Re-run the build script")
    print()

    print("Option 2: Automatic Download Attempt")
    print("-" * 60)
    try:
        import urllib.request
        import shutil

        print("Attempting to download from GitHub...")
        print()

        # Try to download from GitHub releases
        # Note: This is a direct approach, but GitHub releases require specific handling
        url = "https://github.com/mpv-player/mpv-windows-build/releases/download/2024-02-18/mpv-dev-x86_64.7z"

        print(f"URL: {url}")
        print()
        print("Note: This requires 7z extraction which may not be available.")
        print("It's recommended to download manually instead.")
        print()

        if "--auto" in sys.argv:
            print("Automatic mode enabled. Proceeding with download...")
            response = 'y'
        else:
            response = input("Continue with automatic download? (y/n): ").strip().lower()

        if response != 'y':
            return False

        print("Downloading...")
        # This would require additional tools for 7z extraction
        # For now, just provide instructions
        print("Please download manually as described in Option 1.")
        return False

    except Exception as e:
        print(f"Automatic download not available: {e}")
        return False

def create_build_helper():
    """Create a helper batch script for easier building."""
    batch_script = Path("build_with_dll.bat")

    if batch_script.exists():
        return

    content = """@echo off
REM Helper script to download DLL and build

echo Downloading libmpv DLL...
python download_libmpv.py

if errorlevel 1 (
    echo.
    echo DLL download/verification failed.
    echo Please manually place libmpv-2.dll in the project root.
    pause
    exit /b 1
)

echo.
echo DLL ready. Starting build...
call build_windows.bat
"""

    batch_script.write_text(content)
    print(f"✓ Created helper script: {batch_script.name}")

if __name__ == "__main__":
    print()
    success = download_libmpv()

    if success:
        print()
        print("✓ All requirements met. You can now build the application.")
        sys.exit(0)
    else:
        print()
        print("Please obtain libmpv-2.dll before building.")
        print()
        print("After placing the DLL, run: build_windows.bat")
        sys.exit(1)
