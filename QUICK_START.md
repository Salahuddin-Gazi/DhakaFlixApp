# Quick Start - Windows Build Guide

## TL;DR (Just Want to Build?)

1. **Download libmpv-2.dll:**
   - Go to: https://sourceforge.net/projects/mpv-player-windows/files/libmpv/
   - Download latest version, extract and place `libmpv-2.dll` in your project root

2. **Run the build:**

   ```batch
   build_windows.bat
   ```

3. **Find your app:**
   ```
   dist\DhakaFlixStreamer\DhakaFlixStreamer.exe
   ```

Done! ✓

---

## Common Issues & Quick Fixes

### "Missing packages"

```batch
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### "libmpv-2.dll not found"

- Download from: https://sourceforge.net/projects/mpv-player-windows/files/libmpv/
- Place in: project root directory

### "Python not found"

- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Restart terminal after install

### "No dist folder created"

```batch
python build_windows.py --clean --verbose
```

---

## Three Ways to Build

### Method 1: Batch Script (Easiest)

```batch
build_windows.bat
```

### Method 2: Python Script (Better Control)

```batch
python build_windows.py
python build_windows.py --clean        # Clean build
python build_windows.py --verbose      # Debug mode
```

### Method 3: Manual (Step by Step)

Read `BUILD_WINDOWS.md` for detailed instructions

---

## What's Different This Time

✓ **All hidden imports included** - No more "missing package" errors
✓ **Automatic virtual environment setup**
✓ **Better error messages**
✓ **Auto-copy of DLL to dist folder**
✓ **Version-locked dependencies** - Works consistently

---

## Files You'll Need

1. **libmpv-2.dll** - From SourceForge/GitHub (essential!)
2. Everything else is already in the project

## After Building

The executable at `dist\DhakaFlixStreamer\DhakaFlixStreamer.exe` is standalone and ready to:

- Run on other Windows machines
- Be distributed to users
- Be packaged/installed as needed

---

**Need more help?** Check `BUILD_WINDOWS.md` for complete documentation.
