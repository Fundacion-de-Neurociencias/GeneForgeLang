#!/usr/bin/env python3
"""
Main execution script for GFL Genesis Project
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main entry point for the GFL Genesis project"""
    print("GFL Genesis Project: Optimización de ARN Guía (gRNA) para la Edición Genómica de TP53")
    print("=" * 80)
    
    # Check if GFL is installed
    try:
        import gfl
        print(f"GFL version: {gfl.__version__ if hasattr(gfl, '__version__') else 'unknown'}")
    except ImportError:
        print("Error: GFL is not installed. Please install GeneForgeLang v1.0.0")
        return 1
    
    # Check project structure
    print("\nChecking project structure...")
    from tests.test_project_structure import test_project_structure
    try:
        test_project_structure()
    except AssertionError as e:
        print(f"Error: {e}")
        return 1
    
    # Print next steps
    print("\nNext steps:")
    print("1. Install the plugins:")
    print("   pip install -e ./plugins/gfl-plugin-ontarget-scorer")
    print("   pip install -e ./plugins/gfl-plugin-offtarget-scorer")
    print("   pip install -e ./plugins/gfl-crispr-evaluator")
    print("\n2. Download the required genomic data to the data/ directory")
    print("\n3. Run the GFL workflow:")
    print("   gfl-validate genesis.gfl")
    print("   gfl-execute genesis.gfl")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())