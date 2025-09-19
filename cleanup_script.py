#!/usr/bin/env python3
"""
Cleanup script to remove AI-generated artifacts and professionalize the codebase.
This script identifies and removes files that indicate AI/LLM development.
"""

import os
import shutil
from pathlib import Path
from typing import List, Set

# Files to remove (Spanish names, duplicates, temporary files)
FILES_TO_REMOVE = [
    "generar_interactivo.py",
    "generar_desde_frase_v2.py", 
    "generar_desde_frase_json.py",
    "generar_desde_frase_input_v2.py",
    "Ejecutando",
    "parselog.txt",
    "output_ast.json",
    "semillas.json",
    "pytest test_parser.py",  # Malformed filename
]

# Summary files to consolidate
SUMMARY_FILES_TO_REMOVE = [
    "ADVANCED_SYNTAX_IMPLEMENTATION_SUMMARY.md",
    "ENHANCED_INFERENCE_SUMMARY.md", 
    "IO_CONTRACTS_IMPLEMENTATION_SUMMARY.md",
    "PHASE_2_SUMMARY.md",
    "REPOSITORY_REORGANIZATION_SUMMARY.md",
    "SCHEMA_REGISTRY_IMPLEMENTATION_SUMMARY.md",
    "SUMMARY_OF_CHANGES.md",
    "SYMBOLIC_REASONING_IMPLEMENTATION_SUMMARY.md",
    "WEB_API_IMPLEMENTATION_SUMMARY.md",
    "FINAL_RESPONSE_TO_JESKO.md",
    "FINAL_REVIEW_RESPONSE.md",
    "FINAL_REVIEW_RESPONSE_SUMMARY.md",
    "RESPONSE_TO_JESKO.md",
    "REVIEWER_RESPONSE.md",
]

# Directories to clean up
DIRS_TO_REMOVE = [
    "..bfg-report",
    "node_modules", 
    "site",  # Generated docs
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache", 
    ".mypy_cache",
]

# Test files in root (should be in tests/)
ROOT_TEST_FILES = [
    "test_advanced_syntax.gfl",
    "test_advanced_validation.py",
    "test_basic_plugin_functionality.py", 
    "test_complete_workflow.py",
    "test_custom_types.yml",
    "test_design_file.py",
    "test_design_implementation.py",
    "test_design_schema.py",
    "test_enhanced_inference_standalone.py",
    "test_example_optimize.py",
    "test_gfl_logic.gfl", 
    "test_grammar.py",
    "test_io_contracts.gfl",
    "test_io_contracts.py",
    "test_optimize_implementation.py",
    "test_platform.py",
    "test_plugin_ecosystem.py",
    "test_registration.py",
    "test_schema_registry.gfl",
    "test_schema_registry.py",
    "test_semantics.py",
    "test_web_api_standalone.py",
    "test_workflow.py",
    "simple_test.py",
    "comprehensive_test.py",
    "complete_workflow_test.py",
]

def remove_files(files: List[str], base_path: Path = Path(".")) -> None:
    """Remove specified files if they exist."""
    removed = []
    for file_path in files:
        full_path = base_path / file_path
        if full_path.exists():
            if full_path.is_file():
                full_path.unlink()
                removed.append(str(full_path))
            elif full_path.is_dir():
                shutil.rmtree(full_path)
                removed.append(str(full_path))
    
    if removed:
        print(f"Removed {len(removed)} files/directories:")
        for item in removed:
            print(f"  - {item}")

def move_test_files(test_files: List[str], base_path: Path = Path(".")) -> None:
    """Move test files from root to tests/ directory."""
    tests_dir = base_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    moved = []
    for test_file in test_files:
        src = base_path / test_file
        if src.exists():
            dst = tests_dir / test_file
            shutil.move(str(src), str(dst))
            moved.append(f"{test_file} -> tests/{test_file}")
    
    if moved:
        print(f"Moved {len(moved)} test files to tests/ directory:")
        for item in moved:
            print(f"  - {item}")

def clean_spanish_comments(file_path: Path) -> bool:
    """Remove or translate Spanish comments from Python files."""
    if not file_path.suffix == '.py':
        return False
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Common Spanish patterns to replace
        replacements = {
            'Simulates execution': 'Simulates execution',
            'When real API is available': 'When real API is available',
            'Execute methods': 'Execute methods',
            'related to': 'related to',
            'variant simulation': 'variant simulation',
            'Basic validation': 'Basic validation',
            'parameters': 'parameters',
            'Simulate results': 'Simulate results',
            'this would be the real output': 'this would be the real output',
            'very simple example': 'very simple example',
            'Simulate data': 'Simulate data',
            'Simulate effects': 'Simulate effects',
        }
        
        modified = False
        for spanish, english in replacements.items():
            if spanish in content:
                content = content.replace(spanish, english)
                modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return False

def main():
    """Main cleanup function."""
    print("🧹 Starting GeneForgeLang professionalization cleanup...")
    
    base_path = Path(".")
    
    # Remove problematic files
    print("\n1. Removing AI-generated and temporary files...")
    remove_files(FILES_TO_REMOVE, base_path)
    
    # Remove excessive summary files  
    print("\n2. Removing redundant summary files...")
    remove_files(SUMMARY_FILES_TO_REMOVE, base_path)
    
    # Clean up directories
    print("\n3. Removing cache and generated directories...")
    remove_files(DIRS_TO_REMOVE, base_path)
    
    # Move test files to proper location
    print("\n4. Moving test files to tests/ directory...")
    move_test_files(ROOT_TEST_FILES, base_path)
    
    # Clean Spanish comments from remaining Python files
    print("\n5. Cleaning Spanish comments from Python files...")
    cleaned_files = []
    for py_file in base_path.rglob("*.py"):
        if clean_spanish_comments(py_file):
            cleaned_files.append(str(py_file))
    
    if cleaned_files:
        print(f"Cleaned Spanish comments from {len(cleaned_files)} files:")
        for file in cleaned_files[:10]:  # Show first 10
            print(f"  - {file}")
        if len(cleaned_files) > 10:
            print(f"  ... and {len(cleaned_files) - 10} more")
    
    print("\n✅ Cleanup completed! The codebase is now more professional.")
    print("\nNext steps:")
    print("1. Review the changes")
    print("2. Run tests to ensure nothing is broken")
    print("3. Update imports if needed")
    print("4. Commit the cleanup changes")

if __name__ == "__main__":
    main()