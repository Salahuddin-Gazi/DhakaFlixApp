#!/usr/bin/env python3
"""
Build Test Runner - Run all build system tests with reporting.

Usage:
    python3 run_build_tests.py              # Run all tests
    python3 run_build_tests.py unit         # Run unit tests only
    python3 run_build_tests.py integration  # Run integration tests only
    python3 run_build_tests.py verbose      # Run with verbose output
    python3 run_build_tests.py report       # Show test report
"""

import sys
import os
import unittest
import argparse
from pathlib import Path
from io import StringIO


def discover_tests(test_type='all'):
    """Discover and load tests."""
    project_root = Path(__file__).parent
    tests_dir = project_root / 'tests'

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    if test_type in ('all', 'unit'):
        try:
            unit_tests = loader.discover(
                str(tests_dir),
                pattern='test_build_system.py'
            )
            suite.addTests(unit_tests)
        except Exception as e:
            print(f"Error loading unit tests: {e}")

    if test_type in ('all', 'integration'):
        try:
            integration_tests = loader.discover(
                str(tests_dir),
                pattern='test_build_integration.py'
            )
            suite.addTests(integration_tests)
        except Exception as e:
            print(f"Error loading integration tests: {e}")

    return suite


def run_tests(suite, verbose=False):
    """Run test suite and return results."""
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result


def print_summary(result):
    """Print test summary."""
    print("\n" + "="*70)
    print(" "*20 + "TEST EXECUTION SUMMARY")
    print("="*70)

    total = result.testsRun
    failed = len(result.failures) + len(result.errors)
    passed = total - failed

    print(f"\nTotal Tests Run: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} {'✅' if failed == 0 else '❌'}")

    if total > 0:
        success_rate = (passed / total) * 100
        print(f"Success Rate: {success_rate:.1f}%")

    if result.failures:
        print("\n" + "-"*70)
        print("FAILURES:")
        print("-"*70)
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)

    if result.errors:
        print("\n" + "-"*70)
        print("ERRORS:")
        print("-"*70)
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)

    print("\n" + "="*70)

    if failed == 0:
        print("✅ ALL TESTS PASSED - BUILD SYSTEM IS VALID")
    else:
        print(f"❌ {failed} TEST(S) FAILED - REVIEW ABOVE")

    print("="*70 + "\n")

    return 0 if failed == 0 else 1


def show_test_report():
    """Show test report from file."""
    report_file = Path(__file__).parent / "MOCK_TEST_RESULTS.md"

    if report_file.exists():
        with open(report_file, 'r') as f:
            print(f.read())
    else:
        print("Test report not found. Run tests first.")


def show_configuration():
    """Show build configuration summary."""
    project_root = Path(__file__).parent

    print("\n" + "="*70)
    print(" "*15 + "BUILD SYSTEM CONFIGURATION")
    print("="*70)

    # Check files
    files = {
        'build.spec': project_root / 'build.spec',
        'build_windows.bat': project_root / 'build_windows.bat',
        'build_windows.py': project_root / 'build_windows.py',
        'requirements.txt': project_root / 'requirements.txt',
        'download_libmpv.py': project_root / 'download_libmpv.py',
        'src/main.py': project_root / 'src' / 'main.py',
        'assets/icon.ico': project_root / 'assets' / 'icon.ico',
    }

    print("\nBuild Files:")
    for name, path in files.items():
        status = "✓" if path.exists() else "✗"
        print(f"  {status} {name}")

    # Show dependencies
    req_file = project_root / 'requirements.txt'
    if req_file.exists():
        with open(req_file, 'r') as f:
            deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        print(f"\nDependencies ({len(deps)} packages):")
        for dep in deps:
            print(f"  • {dep}")

    print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Run build system tests'
    )
    parser.add_argument(
        'test_type',
        nargs='?',
        choices=['all', 'unit', 'integration', 'verbose', 'report', 'config'],
        default='all',
        help='Type of tests to run (default: all)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Handle special commands
    if args.test_type == 'report':
        show_test_report()
        return 0

    if args.test_type == 'config':
        show_configuration()
        return 0

    # Determine test type and verbose
    test_type = 'all' if args.test_type == 'verbose' else args.test_type
    verbose = args.verbose or args.test_type == 'verbose'

    # Print header
    print("\n" + "="*70)
    print(" "*20 + "BUILD SYSTEM TEST RUNNER")
    print("="*70)
    print(f"\nTest Type: {test_type.upper()}")
    print(f"Verbose: {'Yes' if verbose else 'No'}")
    print("\n" + "="*70 + "\n")

    # Discover and run tests
    suite = discover_tests(test_type)

    if suite.countTestCases() == 0:
        print("❌ No tests found!")
        return 1

    print(f"Discovered {suite.countTestCases()} test(s)\n")

    result = run_tests(suite, verbose=verbose)

    # Print summary
    return print_summary(result)


if __name__ == '__main__':
    sys.exit(main())
