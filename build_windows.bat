@echo off
setlocal enabledelayedexpansion
echo.
echo =====================================
echo DhakaFlix Streamer Windows Builder
echo =====================================
echo.

:: Set Python executable
set PYTHON=python
set PIP=pip

:: Check Python installation
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python and add it to your PATH.
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
%PYTHON% --version

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo.
    echo [2/5] Creating virtual environment...
    %PYTHON% -m venv venv
) else (
    echo.
    echo [2/5] Virtual environment already exists...
)

:: Activate virtual environment
echo [3/5] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat

:: Upgrade pip, setuptools, wheel
echo.
echo Installing build tools...
%PIP% install --upgrade pip setuptools wheel

:: Install all requirements
echo Installing project dependencies...
%PIP% install -r requirements.txt

:: Install additional dependencies that might be missing
echo Installing additional PyInstaller and dependencies...
%PIP% install pyinstaller PyQt6-sip charset-normalizer urllib3

echo.
echo [4/5] Downloading libmpv DLL for Windows...
:: Check if DLL already exists
if exist libmpv-2.dll (
    echo libmpv-2.dll already exists, skipping download...
) else (
    echo Downloading libmpv-2.dll...
    :: Download libmpv DLL from GitHub releases (mpv project)
    powershell -Command "^
        try {^
            $url = 'https://github.com/mpv-player/mpv-windows-build/releases/download/2024-02-18/mpv-dev-x86_64.7z';^
            Write-Host 'Note: For a simpler approach, you can download libmpv manually from:';^
            Write-Host 'https://sourceforge.net/projects/mpv-player-windows/files/libmpv/';^
            Write-Host '';^
            Write-Host 'Or use: https://github.com/mpv-player/mpv-windows-build/releases/';^
            Write-Host '';^
            Write-Host 'For now, creating a placeholder. You can manually add libmpv-2.dll';^
        } catch {^
            Write-Host 'Download setup completed. Please manually add libmpv-2.dll';^
        }^
    " || (
        echo.
        echo NOTE: Automatic DLL download requires additional tools.
        echo Please download libmpv-2.dll manually from:
        echo https://sourceforge.net/projects/mpv-player-windows/files/libmpv/
        echo Or from: https://github.com/mpv-player/mpv-windows-build/releases/
        echo.
        echo Once downloaded, place it in the project root directory.
    )
)

echo.
echo [5/5] Building executable with PyInstaller...
echo.

:: Clean previous builds
if exist build (
    echo Cleaning previous build...
    rmdir /s /q build
)

:: Run PyInstaller
pyinstaller build.spec --clean --noconfirm

echo.
if exist dist\DhakaFlixStreamer (
    echo =====================================
    echo BUILD SUCCESSFUL!
    echo =====================================
    echo.
    echo The executable is located at:
    echo   dist\DhakaFlixStreamer\DhakaFlixStreamer.exe
    echo.

    :: Copy libmpv DLL if it exists
    if exist libmpv-2.dll (
        echo Copying libmpv-2.dll to dist folder...
        copy libmpv-2.dll dist\DhakaFlixStreamer\libmpv-2.dll >nul
        echo Done!
    ) else (
        echo.
        echo WARNING: libmpv-2.dll not found!
        echo.
        echo The application won't work without this DLL.
        echo Download it from:
        echo   https://sourceforge.net/projects/mpv-player-windows/files/libmpv/
        echo.
        echo Or use mpv Windows builds:
        echo   https://github.com/mpv-player/mpv-windows-build/releases/
        echo.
        echo Extract the DLL and place it in:
        echo   dist\DhakaFlixStreamer\libmpv-2.dll
    )
    echo.
    echo You can now run:
    echo   dist\DhakaFlixStreamer\DhakaFlixStreamer.exe
) else (
    echo.
    echo BUILD FAILED!
    echo Please check the error messages above.
)

echo.
pause

