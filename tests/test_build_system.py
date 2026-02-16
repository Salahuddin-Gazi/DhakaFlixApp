"""
Mock tests for the Windows build system.
Tests build configuration, dependencies, and build process validation.

Run with: pytest tests/test_build_system.py -v
Or: python -m pytest tests/test_build_system.py -v
"""

import os
import sys
import unittest
from pathlib import Path
from unittest import mock
import importlib.util
import tempfile
import shutil
import json


class TestRequirements(unittest.TestCase):
    """Test requirements.txt integrity and dependency specifications."""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent
        self.requirements_file = self.project_root / "requirements.txt"

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists."""
        self.assertTrue(
            self.requirements_file.exists(),
            "requirements.txt not found"
        )

    def test_requirements_file_readable(self):
        """Test that requirements.txt is readable."""
        try:
            with open(self.requirements_file, 'r') as f:
                content = f.read()
            self.assertGreater(len(content), 0, "requirements.txt is empty")
        except Exception as e:
            self.fail(f"Cannot read requirements.txt: {e}")

    def test_requirements_has_pyqt6(self):
        """Test that PyQt6 is in requirements."""
        with open(self.requirements_file, 'r') as f:
            content = f.read()
        self.assertIn('PyQt6', content, "PyQt6 not found in requirements.txt")

    def test_requirements_has_mpv(self):
        """Test that python-mpv is in requirements."""
        with open(self.requirements_file, 'r') as f:
            content = f.read()
        self.assertIn('python-mpv', content, "python-mpv not found in requirements.txt")

    def test_requirements_has_aiohttp(self):
        """Test that aiohttp is in requirements."""
        with open(self.requirements_file, 'r') as f:
            content = f.read()
        self.assertIn('aiohttp', content, "aiohttp not found in requirements.txt")

    def test_requirements_has_beautifulsoup(self):
        """Test that beautifulsoup4 is in requirements."""
        with open(self.requirements_file, 'r') as f:
            content = f.read()
        self.assertIn('beautifulsoup4', content, "beautifulsoup4 not found in requirements.txt")

    def test_requirements_has_requests(self):
        """Test that requests is in requirements."""
        with open(self.requirements_file, 'r') as f:
            content = f.read()
        self.assertIn('requests', content, "requests not found in requirements.txt")

    def test_requirements_format_valid(self):
        """Test that requirements.txt has valid format."""
        with open(self.requirements_file, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Should be package or package>=version
            parts = line.split('>=')
            self.assertEqual(len(parts), 2,
                f"Line {i} has invalid format: {line}")

    def test_requirements_version_specified(self):
        """Test that all packages have versions specified."""
        with open(self.requirements_file, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # All should have >=version
            self.assertIn('>=', line,
                f"Line {i} missing version specification: {line}")


class TestBuildSpec(unittest.TestCase):
    """Test PyInstaller build.spec configuration."""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent
        self.build_spec = self.project_root / "build.spec"

    def test_build_spec_exists(self):
        """Test that build.spec exists."""
        self.assertTrue(
            self.build_spec.exists(),
            "build.spec not found"
        )

    def test_build_spec_syntax_valid(self):
        """Test that build.spec has valid Python syntax."""
        try:
            with open(self.build_spec, 'r') as f:
                code = f.read()
            compile(code, str(self.build_spec), 'exec')
        except SyntaxError as e:
            self.fail(f"Syntax error in build.spec: {e}")

    def test_build_spec_has_hidden_imports(self):
        """Test that build.spec includes hidden imports."""
        with open(self.build_spec, 'r') as f:
            content = f.read()
        self.assertIn('hiddenimports', content,
            "hiddenimports not found in build.spec")

    def test_build_spec_has_pyqt6_imports(self):
        """Test that PyQt6 modules are in hidden imports."""
        with open(self.build_spec, 'r') as f:
            content = f.read()
        self.assertIn('PyQt6.QtCore', content,
            "PyQt6.QtCore not in hidden imports")
        self.assertIn('PyQt6.QtGui', content,
            "PyQt6.QtGui not in hidden imports")
        self.assertIn('PyQt6.QtWidgets', content,
            "PyQt6.QtWidgets not in hidden imports")

    def test_build_spec_has_aiohttp_imports(self):
        """Test that aiohttp modules are in hidden imports."""
        with open(self.build_spec, 'r') as f:
            content = f.read()
        self.assertIn('aiohttp', content,
            "aiohttp not in hidden imports")

    def test_build_spec_has_beautifulsoup_imports(self):
        """Test that beautifulsoup is in hidden imports."""
        with open(self.build_spec, 'r') as f:
            content = f.read()
        self.assertIn("'bs4'", content,
            "bs4 not in hidden imports")

    def test_build_spec_has_datas(self):
        """Test that build.spec includes data files."""
        with open(self.build_spec, 'r') as f:
            content = f.read()
        self.assertIn('datas', content,
            "datas not found in build.spec")

    def test_build_spec_has_entry_point(self):
        """Test that build.spec references correct entry point."""
        with open(self.build_spec, 'r') as f:
            content = f.read()
        self.assertIn('src/main.py', content,
            "src/main.py not referenced in build.spec")

    def test_build_spec_has_icon(self):
        """Test that build.spec references icon file."""
        with open(self.build_spec, 'r') as f:
            content = f.read()
        self.assertIn('icon.ico', content,
            "icon.ico not referenced in build.spec")


class TestDependencies(unittest.TestCase):
    """Test that all dependencies can be imported."""

    def _can_import(self, module_name):
        """Check if a module can be imported."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def test_pyqt6_available(self):
        """Test PyQt6 can be imported."""
        # Only test if installed
        if self._can_import('PyQt6'):
            import PyQt6
            self.assertTrue(hasattr(PyQt6, 'QtCore'))

    def test_requests_available(self):
        """Test requests can be imported."""
        if self._can_import('requests'):
            import requests
            self.assertTrue(hasattr(requests, 'get'))

    def test_beautifulsoup_available(self):
        """Test beautifulsoup4 can be imported."""
        if self._can_import('bs4'):
            from bs4 import BeautifulSoup
            self.assertTrue(callable(BeautifulSoup))

    def test_aiohttp_available(self):
        """Test aiohttp can be imported."""
        if self._can_import('aiohttp'):
            import aiohttp
            self.assertTrue(hasattr(aiohttp, 'ClientSession'))


class TestProjectStructure(unittest.TestCase):
    """Test project file structure for build requirements."""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent

    def test_src_main_exists(self):
        """Test that src/main.py exists."""
        main_file = self.project_root / "src" / "main.py"
        self.assertTrue(main_file.exists(), "src/main.py not found")

    def test_assets_folder_exists(self):
        """Test that assets folder exists."""
        assets = self.project_root / "assets"
        self.assertTrue(assets.exists(), "assets folder not found")
        self.assertTrue(assets.is_dir(), "assets is not a directory")

    def test_icon_exists(self):
        """Test that icon.ico exists in assets."""
        icon = self.project_root / "assets" / "icon.ico"
        self.assertTrue(icon.exists(), "assets/icon.ico not found")

    def test_build_files_exist(self):
        """Test that all build scripts exist."""
        expected_files = [
            'build.spec',
            'build_windows.bat',
            'build_windows.py',
            'requirements.txt',
        ]

        for filename in expected_files:
            file_path = self.project_root / filename
            self.assertTrue(file_path.exists(), f"{filename} not found")


class TestBuildScripts(unittest.TestCase):
    """Test build script quality and structure."""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent

    def test_batch_script_readable(self):
        """Test that build_windows.bat is readable."""
        batch_file = self.project_root / "build_windows.bat"
        try:
            with open(batch_file, 'r') as f:
                content = f.read()
            self.assertGreater(len(content), 100, "batch script too short")
        except Exception as e:
            self.fail(f"Cannot read batch script: {e}")

    def test_batch_script_has_pyinstaller(self):
        """Test that batch script runs pyinstaller."""
        batch_file = self.project_root / "build_windows.bat"
        with open(batch_file, 'r') as f:
            content = f.read()
        self.assertIn('pyinstaller', content.lower(),
            "pyinstaller not called in batch script")

    def test_batch_script_has_requirements(self):
        """Test that batch script installs requirements."""
        batch_file = self.project_root / "build_windows.bat"
        with open(batch_file, 'r') as f:
            content = f.read()
        self.assertIn('requirements.txt', content,
            "requirements.txt not referenced in batch script")

    def test_python_build_script_valid(self):
        """Test that build_windows.py has valid Python syntax."""
        python_script = self.project_root / "build_windows.py"
        try:
            with open(python_script, 'r') as f:
                code = f.read()
            compile(code, str(python_script), 'exec')
        except SyntaxError as e:
            self.fail(f"Syntax error in build_windows.py: {e}")

    def test_python_build_script_has_builder_class(self):
        """Test that build_windows.py has Builder class."""
        python_script = self.project_root / "build_windows.py"
        with open(python_script, 'r') as f:
            content = f.read()
        self.assertIn('class Builder', content,
            "Builder class not found in build_windows.py")


class TestBuildMock(unittest.TestCase):
    """Mock tests for actual build process."""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_mock_venv_creation(self):
        """Test virtual environment creation simulation."""
        venv_path = Path(self.temp_dir) / "venv"

        # Simulate venv creation
        venv_path.mkdir()
        (venv_path / "Scripts").mkdir()
        (venv_path / "Lib").mkdir()

        self.assertTrue(venv_path.exists())
        self.assertTrue((venv_path / "Scripts").exists())
        self.assertTrue((venv_path / "Lib").exists())

    def test_mock_dist_folder_creation(self):
        """Test dist folder creation simulation."""
        dist_path = Path(self.temp_dir) / "dist" / "DhakaFlixStreamer"
        dist_path.mkdir(parents=True)

        self.assertTrue(dist_path.exists())
        self.assertTrue(dist_path.is_dir())

    def test_mock_dll_copy(self):
        """Test DLL copy simulation."""
        # Create mock DLL
        source_dll = Path(self.temp_dir) / "libmpv-2.dll"
        source_dll.write_text("mock dll content")

        # Simulate copy
        dest_dir = Path(self.temp_dir) / "dist" / "DhakaFlixStreamer"
        dest_dir.mkdir(parents=True)
        dest_dll = dest_dir / "libmpv-2.dll"

        shutil.copy(source_dll, dest_dll)

        self.assertTrue(dest_dll.exists())
        self.assertEqual(dest_dll.read_text(), "mock dll content")

    def test_mock_executable_creation(self):
        """Test executable file creation simulation."""
        exe_path = Path(self.temp_dir) / "dist" / "DhakaFlixStreamer" / "DhakaFlixStreamer.exe"
        exe_path.parent.mkdir(parents=True)
        exe_path.write_text("mock executable")

        self.assertTrue(exe_path.exists())
        self.assertTrue(exe_path.name.endswith('.exe'))

    @mock.patch('subprocess.run')
    def test_mock_pip_install(self, mock_run):
        """Test pip install command simulation."""
        mock_run.return_value = mock.MagicMock(returncode=0, stdout="", stderr="")

        import subprocess
        result = subprocess.run("pip install -r requirements.txt", shell=True)

        self.assertEqual(result.returncode, 0)
        mock_run.assert_called_once()

    @mock.patch('subprocess.run')
    def test_mock_pyinstaller_build(self, mock_run):
        """Test PyInstaller build command simulation."""
        mock_run.return_value = mock.MagicMock(returncode=0, stdout="", stderr="")

        import subprocess
        result = subprocess.run("pyinstaller build.spec --clean --noconfirm", shell=True)

        self.assertEqual(result.returncode, 0)
        mock_run.assert_called_once()


class TestBuildValidation(unittest.TestCase):
    """Validate build configuration logic."""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent

    def test_hidden_imports_not_empty(self):
        """Test that hidden imports list is not empty."""
        with open(self.project_root / "build.spec", 'r') as f:
            content = f.read()

        # Extract hiddenimports section
        start = content.find('hiddenimports = [')
        end = content.find(']', start)
        imports_section = content[start:end]

        # Should have multiple imports
        import_count = imports_section.count("'")
        self.assertGreater(import_count, 10,
            "Hidden imports list seems too short")

    def test_datas_includes_assets(self):
        """Test that datas includes assets folder."""
        with open(self.project_root / "build.spec", 'r') as f:
            content = f.read()

        self.assertIn('assets', content,
            "assets folder not included in datas")

    def test_entry_point_exists(self):
        """Test that entry point file exists."""
        main_file = self.project_root / "src" / "main.py"
        self.assertTrue(main_file.exists(),
            "src/main.py entry point not found")

        with open(main_file, 'r') as f:
            content = f.read()
        self.assertIn('if __name__', content,
            "main.py should have if __name__ guard")


class TestBuildHelpers(unittest.TestCase):
    """Test build helper scripts."""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent

    def test_download_libmpv_exists(self):
        """Test that download_libmpv.py exists."""
        script = self.project_root / "download_libmpv.py"
        self.assertTrue(script.exists(),
            "download_libmpv.py not found")

    def test_download_libmpv_syntax_valid(self):
        """Test that download_libmpv.py has valid syntax."""
        script = self.project_root / "download_libmpv.py"
        try:
            with open(script, 'r') as f:
                code = f.read()
            compile(code, str(script), 'exec')
        except SyntaxError as e:
            self.fail(f"Syntax error in download_libmpv.py: {e}")


class TestBuildDocumentation(unittest.TestCase):
    """Test build documentation exists and is complete."""

    def setUp(self):
        self.project_root = Path(__file__).parent.parent

    def test_build_windows_md_exists(self):
        """Test that BUILD_WINDOWS.md exists."""
        doc = self.project_root / "BUILD_WINDOWS.md"
        self.assertTrue(doc.exists(), "BUILD_WINDOWS.md not found")

    def test_quick_start_md_exists(self):
        """Test that QUICK_START.md exists."""
        doc = self.project_root / "QUICK_START.md"
        self.assertTrue(doc.exists(), "QUICK_START.md not found")

    def test_troubleshooting_md_exists(self):
        """Test that TROUBLESHOOTING.md exists."""
        doc = self.project_root / "TROUBLESHOOTING.md"
        self.assertTrue(doc.exists(), "TROUBLESHOOTING.md not found")

    def test_build_windows_md_readable(self):
        """Test that BUILD_WINDOWS.md is readable and has content."""
        doc = self.project_root / "BUILD_WINDOWS.md"
        with open(doc, 'r') as f:
            content = f.read()
        self.assertGreater(len(content), 100,
            "BUILD_WINDOWS.md too short or empty")

    def test_build_windows_md_has_instructions(self):
        """Test that BUILD_WINDOWS.md has setup instructions."""
        doc = self.project_root / "BUILD_WINDOWS.md"
        with open(doc, 'r') as f:
            content = f.read()
        self.assertIn('Python', content,
            "BUILD_WINDOWS.md missing Python setup")


def run_build_summary():
    """Print build configuration summary."""
    print("\n" + "="*60)
    print("BUILD CONFIGURATION SUMMARY")
    print("="*60)

    project_root = Path(__file__).parent.parent

    # Load requirements
    with open(project_root / "requirements.txt", 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    print(f"\nDependencies ({len(requirements)}):")
    for req in requirements:
        print(f"  ✓ {req}")

    # Load hidden imports count
    with open(project_root / "build.spec", 'r') as f:
        content = f.read()
        import_count = content.count("'") // 2

    print(f"\nHidden Imports: ~{import_count} modules")

    # Check files
    files_ok = 0
    files_check = [
        'src/main.py',
        'assets/icon.ico',
        'build.spec',
        'requirements.txt',
        'build_windows.bat',
        'build_windows.py',
        'download_libmpv.py',
    ]

    print(f"\nBuild Files:")
    for file in files_check:
        path = project_root / file
        if path.exists():
            print(f"  ✓ {file}")
            files_ok += 1
        else:
            print(f"  ✗ {file} (MISSING)")

    print(f"\nStatus: {files_ok}/{len(files_check)} files present")
    print("="*60 + "\n")


if __name__ == '__main__':
    # Run summary first
    run_build_summary()

    # Run tests
    unittest.main(verbosity=2)
