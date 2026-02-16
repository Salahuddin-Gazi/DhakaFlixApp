# Windows Build Troubleshooting Checklist

Use this checklist to diagnose and fix build issues.

## Pre-Build Checklist

- [ ] Python 3.8+ installed
  ```bash
  python --version
  ```
- [ ] Python in PATH
  ```bash
  where python
  ```
- [ ] libmpv-2.dll in project root
  ```bash
  dir libmpv-2.dll
  ```
- [ ] `requirements.txt` exists and has dependencies
  ```bash
  type requirements.txt
  ```

## Build Failure: Missing Packages

**Symptoms:** "ModuleNotFoundError", "No module named", or similar

**Checklist:**

- [ ] Virtual environment activated (you should see `(venv)` in prompt)
  ```bash
  venv\Scripts\activate.bat
  ```
- [ ] All packages installed
  ```bash
  pip install -r requirements.txt
  pip install pyinstaller PyQt6-sip charset-normalizer
  ```
- [ ] Verify packages are installed
  ```bash
  pip list | findstr PyQt6
  pip list | findstr aiohttp
  ```
- [ ] Run with fresh build
  ```bash
  pyinstaller build.spec --clean --noconfirm
  ```

## Build Failure: No dist Folder

**Symptoms:** Build completes but no executable generated

**Checklist:**

- [ ] Check for error in build output (scroll up)
- [ ] Look in `build/` folder for clues
  ```bash
  dir build
  ```
- [ ] Try verbose build
  ```bash
  python build_windows.py --verbose
  ```
- [ ] Try clean build
  ```bash
  pyinstaller --clean build.spec --noconfirm
  rmdir /s /q build dist
  pyinstaller build.spec --clean --noconfirm
  ```
- [ ] Check if PyInstaller corrupted (reinstall it)
  ```bash
  pip uninstall -y pyinstaller
  pip install pyinstaller
  ```

## Runtime Failure: libmpv-2.dll Not Found

**Symptoms:** Application crashes saying "libmpv-2.dll not found"

**Checklist:**

- [ ] DLL exists in project root
  ```bash
  dir libmpv-2.dll
  ```
- [ ] DLL copied to dist folder
  ```bash
  dir dist\DhakaFlixStreamer\libmpv-2.dll
  ```
- [ ] If missing, copy it manually
  ```bash
  copy libmpv-2.dll dist\DhakaFlixStreamer\libmpv-2.dll
  ```
- [ ] DLL is 64-bit (for 64-bit Windows)
  - Use Windows Explorer
  - Right-click `libmpv-2.dll`
  - Check file size is >50MB (indicates 64-bit)

## Runtime Failure: PyQt6 GUI Issues

**Symptoms:** "Could not find Qt plugins" or GUI doesn't render

**Checklist:**

- [ ] Check if Qt plugins exist
  ```bash
  dir dist\DhakaFlixStreamer\PyQt6
  ```
- [ ] Rebuild with latest spec
  ```bash
  pyinstaller build.spec --clean --noconfirm
  ```
- [ ] Manually copy plugins if needed
  ```bash
  xcopy venv\Lib\site-packages\PyQt6\Qt6\plugins dist\DhakaFlixStreamer\PyQt6\Qt6\plugins /Y /E
  ```

## Virtual Environment Issues

**Symptoms:** "venv not recognized", permission errors, etc.

**Checklist:**

- [ ] Create fresh venv
  ```bash
  rmdir /s /q venv
  python -m venv venv
  venv\Scripts\activate.bat
  ```
- [ ] Use python directly if venv fails
  ```bash
  python -m pip install -r requirements.txt
  ```
- [ ] On Windows, use the full path if needed
  ```bash
  C:\Python312\python.exe -m venv venv
  ```

## Terminal/Command Line Issues

**Symptoms:** Commands not found, PATH issues

**Checklist:**

- [ ] Use full path to python
  ```bash
  C:\Python312\python.exe --version
  ```
- [ ] Use python -m for modules
  ```bash
  python -m pip install --upgrade pip
  ```
- [ ] Don't use quotes unless needed
  ```bash
  pyinstaller build.spec --clean --noconfirm
  ```
- [ ] Restart terminal after Python install
  - Close all cmd/PowerShell windows
  - Open fresh terminal
  - Try again

## File Path Issues

**Symptoms:** "File not found", "No such directory"

**Checklist:**

- [ ] Run commands from project root
  ```bash
  cd /path/to/DhakaFlixApp
  dir
  ```
- [ ] Check build.spec references correct files
  ```bash
  type build.spec | findstr main.py
  ```
- [ ] Verify assets folder exists
  ```bash
  dir assets
  ```

## Disk Space / Permissions

**Symptoms:** "Disk full", "Access denied", permission errors

**Checklist:**

- [ ] Check disk space
  ```bash
  wmic logicaldisk get name, size, freespace
  ```
- [ ] Need at least 2GB free space for build
- [ ] Run as Administrator if permission errors
  - Right-click Command Prompt
  - Select "Run as Administrator"
- [ ] Check folder is writable
  ```bash
  echo test > test_write.txt
  del test_write.txt
  ```

## Version Conflicts

**Symptoms:** "Version X conflicts with Y", package incompatibility

**Checklist:**

- [ ] Start with clean requirements
  ```bash
  pip uninstall -y -r requirements.txt
  pip install -r requirements.txt
  ```
- [ ] Update everything
  ```bash
  pip install --upgrade pip setuptools wheel
  pip install --upgrade -r requirements.txt
  ```
- [ ] Check requirements.txt has versions
  ```bash
  type requirements.txt
  ```

## Still Not Working?

**Debug Steps:**

1. [ ] Run with maximum verbosity

   ```bash
   python build_windows.py --verbose
   ```

2. [ ] Check build log
   - Look for error messages
   - Note the exact module/file mentioned

3. [ ] Try Python script builder

   ```bash
   python build_windows.py --clean
   ```

4. [ ] Check documentation
   - Read `BUILD_WINDOWS.md` completely
   - Check `QUICK_START.md` for common solutions

5. [ ] Isolate the problem
   - Test Python import manually
   - Test PyInstaller on simple project
   - Verify each dependency individually

**Last Resort:**

```bash
:: Nuclear option - start completely fresh
rmdir /s /q venv
rmdir /s /q build
rmdir /s /q dist
python -m venv venv
venv\Scripts\activate.bat
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pyinstaller build.spec --clean --noconfirm
```

---

## When Asking for Help

Include:

1. Exact error message (copy/paste)
2. Output of: `python --version`
3. Output of: `pip list`
4. Did you get `libmpv-2.dll` from the correct source?
5. Which build method: batch script, Python script, or manual?

---

**Success Signs:**
✓ `dist\DhakaFlixStreamer\` folder exists
✓ `DhakaFlixStreamer.exe` in that folder
✓ `libmpv-2.dll` in that folder
✓ Application runs without errors
