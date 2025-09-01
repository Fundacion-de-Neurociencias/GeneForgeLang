#!/usr/bin/env python3
"""
Pre-release validation script for GeneForgeLang v1.0.0

This script runs all essential tests to ensure the release is ready.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return True if successful, False otherwise."""
    print(f"🏃 Running {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Run all pre-release checks."""
    print("🔍 GeneForgeLang v1.0.0 Pre-release Validation")
    print("=" * 50)
    
    # Change to the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # List of tests to run
    tests = [
        ("python -m pytest tests/test_semantics.py -v", "Semantic validation tests"),
        ("python -m pytest tests/test_advanced_validation.py -v", "Advanced validation tests"),
        ("python -m pytest tests/test_io_contracts.py -v", "IO Contracts tests"),
        ("python -m pytest tests/test_schema_registry.py -v", "Schema Registry tests"),
        ("python -m pytest tests/test_design_implementation.py -v", "Design block tests"),
        ("python -m pytest tests/test_optimize_implementation.py -v", "Optimize block tests"),
        ("python -m pytest tests/test_plugin_ecosystem.py -v", "Plugin ecosystem tests"),
        ("python comprehensive_test.py", "Comprehensive feature test"),
        ("gfl-validate test_advanced_syntax.gfl", "Advanced syntax validation"),
        ("gfl-validate test_io_contracts.gfl", "IO Contracts validation"),
        ("gfl-validate test_schema_registry.gfl", "Schema Registry validation"),
    ]
    
    # Run all tests
    all_passed = True
    for cmd, description in tests:
        if not run_command(cmd, description):
            all_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All pre-release checks passed!")
        print("✅ Ready for GeneForgeLang v1.0.0 release")
        return 0
    else:
        print("❌ Some pre-release checks failed!")
        print("⚠️  Please fix the issues before releasing")
        return 1

if __name__ == "__main__":
    sys.exit(main())