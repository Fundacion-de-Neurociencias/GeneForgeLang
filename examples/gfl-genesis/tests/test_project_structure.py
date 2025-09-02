"""
Test script to validate GFL Genesis project structure
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_project_structure():
    """Test that all required directories and files exist"""

    # Required directories
    required_dirs = [
        "schemas",
        "plugins",
        "data",
        "results",
        "docs",
        "tests"
    ]

    # Required files
    required_files = [
        "README.md",
        "genesis.gfl",
        "requirements.txt",
        "schemas/crispr_types.yml",
        "docs/project_plan.md"
    ]

    # Check directories
    for directory in required_dirs:
        dir_path = project_root / directory
        assert dir_path.exists(), f"Directory {directory} does not exist"
        assert dir_path.is_dir(), f"{directory} is not a directory"

    # Check files
    for file in required_files:
        file_path = project_root / file
        assert file_path.exists(), f"File {file} does not exist"
        assert file_path.is_file(), f"{file} is not a file"

    print("All project structure tests passed!")

if __name__ == "__main__":
    test_project_structure()
