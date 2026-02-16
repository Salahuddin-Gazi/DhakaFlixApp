# Windows Build Instructions for DhakaFlix Streamer

This guide will help you build DhakaFlix Streamer into a standalone Windows executable.

## Prerequisites

1. **Python 3.8+** - Download from https://www.python.org/downloads/
   - During installation, make sure to check "Add Python to PATH"

2. **libmpv DLL** - Required for video playback

## Quick Build (Windows)

Run the batch script in your project directory:

```batch
build_windows.bat
```

This script will:

1. ✓ Check Python installation
2. ✓ Create a virtual environment (if needed)
3. ✓ Install all dependencies from `requirements.txt`
4. ✓ Download/verify libmpv DLL
5. ✓ Build the executable using PyInstaller

## Step-by-Step Manual Build

### 1. Install Python Dependencies

```batch
:: Create virtual environment
python -m venv venv

:: Activate virtual environment
venv\Scripts\activate.bat

:: Upgrade pip
python -m pip install --upgrade pip setuptools wheel

:: Install dependencies
pip install -r requirements.txt

:: Install additional build tools
pip install pyinstaller PyQt6-sip charset-normalizer
```

### 2. Obtain libmpv-2.dll

The application requires `libmpv-2.dll` for video playback.

#### Option A: Download from SourceForge (Easiest)

1. Visit: https://sourceforge.net/projects/mpv-player-windows/files/libmpv/
2. Download the latest `libmpv` release
3. Extract the archive and find `libmpv-2.dll` (usually in `libmpv/libmpv-2.dll`)
4. Place the DLL in your project root directory

#### Option B: Download from GitHub

1. Visit: https://github.com/mpv-player/mpv-windows-build/releases/
2. Download a recent `mpv-dev-x86_64` release
3. Use 7-Zip to extract the 7z archive
4. Find `libmpv-2.dll` and place it in your project root

### 3. Build with PyInstaller

```batch
:: Run the build (using the spec file)
pyinstaller build.spec --clean --noconfirm

:: Copy the DLL to the dist folder
copy libmpv-2.dll dist\DhakaFlixStreamer\libmpv-2.dll
```

## Troubleshooting

### "Missing packages" Error

**Problem:** Build fails saying packages are missing even though they're installed.

**Solutions:**

1. Ensure you're using the virtual environment:

   ```batch
   venv\Scripts\activate.bat
   ```

2. Verify all packages are installed:

   ```batch
   pip install -r requirements.txt
   pip install pyinstaller PyQt6-sip charset-normalizer
   ```

3. Clear PyInstaller cache:
   ```batch
   pyinstaller --clean build.spec
   ```

### No `dist` Folder Created

**Problem:** Build completes but no executable is generated.

**Solutions:**

1. Check for error messages in the build output
2. Ensure all hidden imports are included (handled in updated `build.spec`)
3. Try building with debug mode:

   ```batch
   pyinstaller build.spec -d
   ```

4. Check `build/` and `DhakaFlixStreamer.spec` for more details

### Missing libmpv-2.dll

**Problem:** Application runs but crashes with "libmpv-2.dll not found"

**Solution:**

1. Download the DLL as described in Section 2
2. Place it in the `dist\DhakaFlixStreamer\` folder
3. Or in the same directory as the executable

### PyQt6 Plugin Issues

**Problem:** "Could not find Qt plugins"

**Solution:** The updated `build.spec` includes PyQt6 plugins automatically. If issues persist:

1. Manually include Qt plugins:
   ```batch
   copy venv\Lib\site-packages\PyQt6\Qt6\plugins dist\DhakaFlixStreamer\PyQt6\Qt6\plugins /Y
   ```

## Build Configuration Details

### build.spec

The `build.spec` file configures PyInstaller with:

- **Hidden Imports:** All required modules including PyQt6, aiohttp, beautifulsoup4, etc.
- **PyQt6 Data:** Automatically includes Qt libraries and plugins
- **Assets:** Includes the `assets/` folder with icons and resources
- **Excludes:** Unnecessary packages (matplotlib, numpy, pandas, etc.)

### requirements.txt

Contains all Python package dependencies with version specifications for reproducibility:

- PyQt6 - GUI framework
- python-mpv - Video player
- aiohttp - Async HTTP client
- beautifulsoup4 - HTML parsing
- requests - HTTP requests
- And supporting libraries

## Running the Built Application

After successful build:

```batch
dist\DhakaFlixStreamer\DhakaFlixStreamer.exe
```

Or double-click the executable from Windows Explorer.

## Distribution

To distribute the application:

1. Ensure `dist\DhakaFlixStreamer\` contains:
   - `DhakaFlixStreamer.exe`
   - `libmpv-2.dll`
   - All other generated files and libraries

2. You can ZIP the entire `DhakaFlixStreamer` folder for distribution

3. Users just need to download and run the executable

## Advanced Build Options

### Optimize Build Size

To reduce executable size:

```batch
:: Remove UPX (already disabled in spec)
:: Disable debug info
pyinstaller build.spec --clean --noconfirm -F
```

### Build with Console Window

For debugging (show console output):

Edit `build.spec` and change:

```python
console=True,  # Instead of console=False
```

## Common Issues and Solutions

| Issue                      | Solution                                         |
| -------------------------- | ------------------------------------------------ |
| "Python not found"         | Ensure Python is added to PATH, restart terminal |
| "pip not found"            | Use `python -m pip` instead of just `pip`        |
| App crashes on startup     | Check console for error messages                 |
| Missing modules at runtime | Add to `hiddenimports` in `build.spec`           |
| DLL not found              | Copy `libmpv-2.dll` to dist folder               |

## Need Help?

1. Check the error messages carefully
2. Ensure Python and all dependencies are installed
3. Verify libmpv-2.dll is present
4. Try building from a fresh terminal window
5. Check PyInstaller documentation: https://pyinstaller.org/

---

**Note:** This build process creates a self-contained Windows executable. The first run may be slower as Windows scans the executable. This is normal.
