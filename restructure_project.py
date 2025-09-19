#!/usr/bin/env python3
"""
Project restructuring script to create a professional directory layout.
Moves files to appropriate locations following Python packaging best practices.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

def create_professional_structure():
    """Create the new professional directory structure."""
    
    # New directory structure
    directories = [
        "src/geneforgelang",
        "src/geneforgelang/core",
        "src/geneforgelang/plugins", 
        "src/geneforgelang/web",
        "src/geneforgelang/cli",
        "src/geneforgelang/utils",
        "tests/unit",
        "tests/integration", 
        "tests/fixtures",
        "docs/architecture",
        "docs/user-guide",
        "docs/api",
        "examples/basic",
        "examples/advanced",
        "tools/development",
        "scripts/maintenance",
    ]
    
    print("📁 Creating professional directory structure...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {directory}/")

def move_core_files():
    """Move core GFL files to src/geneforgelang/core/."""
    
    core_files = {
        "gfl/__init__.py": "src/geneforgelang/__init__.py",
        "gfl/api.py": "src/geneforgelang/core/api.py", 
        "gfl/parser.py": "src/geneforgelang/core/parser.py",
        "gfl/semantic_validator.py": "src/geneforgelang/core/validator.py",
        "gfl/types.py": "src/geneforgelang/core/types.py",
        "gfl/error_handling.py": "src/geneforgelang/core/errors.py",
        "gfl/inference_engine.py": "src/geneforgelang/core/inference.py",
        "gfl/execution_engine.py": "src/geneforgelang/core/execution.py",
        "gfl/performance.py": "src/geneforgelang/core/performance.py",
    }
    
    print("\n🔧 Moving core files...")
    for src, dst in core_files.items():
        if Path(src).exists():
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  ✓ {src} -> {dst}")

def move_plugin_files():
    """Move plugin-related files to src/geneforgelang/plugins/."""
    
    plugin_files = {
        "gfl/plugins/": "src/geneforgelang/plugins/",
        "alphagenome_plugin.py": "src/geneforgelang/plugins/alphafold.py",
        "variant_simulation_plugin.py": "src/geneforgelang/plugins/variant_sim.py",
    }
    
    print("\n🔌 Moving plugin files...")
    for src, dst in plugin_files.items():
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.exists():
            if src_path.is_dir():
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                print(f"  ✓ {src} -> {dst}")
            else:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
                print(f"  ✓ {src} -> {dst}")

def move_web_files():
    """Move web interface files to src/geneforgelang/web/."""
    
    web_files = {
        "gfl/web_interface.py": "src/geneforgelang/web/interface.py",
        "gfl/api_server.py": "src/geneforgelang/web/server.py", 
        "gfl/server_launcher.py": "src/geneforgelang/web/launcher.py",
        "applications/": "src/geneforgelang/web/apps/",
        "web-interface/": "src/geneforgelang/web/static/",
    }
    
    print("\n🌐 Moving web files...")
    for src, dst in web_files.items():
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            if src_path.is_dir():
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
            print(f"  ✓ {src} -> {dst}")

def move_cli_files():
    """Move CLI files to src/geneforgelang/cli/."""
    
    cli_files = {
        "gfl/cli.py": "src/geneforgelang/cli/main.py",
        "gfl/cli_main.py": "src/geneforgelang/cli/commands.py",
        "gfl/cli_utils.py": "src/geneforgelang/cli/utils.py",
        "gfl/cli_inference.py": "src/geneforgelang/cli/inference.py",
        "gfl/enhanced_cli.py": "src/geneforgelang/cli/enhanced.py",
    }
    
    print("\n💻 Moving CLI files...")
    for src, dst in cli_files.items():
        if Path(src).exists():
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  ✓ {src} -> {dst}")

def move_utility_files():
    """Move utility files to src/geneforgelang/utils/."""
    
    util_files = {
        "gfl/schema_loader.py": "src/geneforgelang/utils/schema.py",
        "gfl/validation_pipeline.py": "src/geneforgelang/utils/validation.py",
        "gfl/client_sdk.py": "src/geneforgelang/utils/client.py",
        "sanitize_identifiers.py": "src/geneforgelang/utils/sanitize.py",
        "bio_data_access.py": "src/geneforgelang/utils/bio_data.py",
    }
    
    print("\n🛠️ Moving utility files...")
    for src, dst in util_files.items():
        if Path(src).exists():
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  ✓ {src} -> {dst}")

def move_documentation():
    """Move and organize documentation files."""
    
    doc_moves = {
        "README.md": "docs/user-guide/README.md",
        "CONTRIBUTING.md": "docs/user-guide/CONTRIBUTING.md", 
        "docs/": "docs/user-guide/",
        "PHASE_4_PLANNING.md": "docs/architecture/phase4-planning.md",
        "REPOSITORY_ORGANIZATION.md": "docs/architecture/organization.md",
        "SECURITY_ADVISORY.md": "docs/architecture/security.md",
        "CHANGELOG.md": "docs/user-guide/CHANGELOG.md",
    }
    
    print("\n📚 Organizing documentation...")
    
    # Keep original README in root, copy to docs
    if Path("README.md").exists():
        shutil.copy2("README.md", "docs/user-guide/README.md")
        print("  ✓ README.md -> docs/user-guide/README.md (copied)")
    
    # Move other docs
    for src, dst in doc_moves.items():
        if src == "README.md":  # Skip README, already handled
            continue
            
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.exists() and src != "docs/":
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            if src_path.is_dir():
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
            print(f"  ✓ {src} -> {dst}")

def move_examples():
    """Move example files to examples/ directory."""
    
    example_files = {
        "example1.gfl": "examples/basic/simple_workflow.gfl",
        "example_crispr_optimization.gfl": "examples/advanced/crispr_optimization.gfl", 
        "example_protein_design.gfl": "examples/advanced/protein_design.gfl",
        "gfl_example.gfl": "examples/basic/basic_syntax.gfl",
        "gfl_examples.gfl": "examples/basic/multiple_examples.gfl",
        "examples/": "examples/",  # Merge existing examples
    }
    
    print("\n📋 Moving example files...")
    for src, dst in example_files.items():
        src_path = Path(src)
        if src_path.exists() and src != "examples/":
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst)
            print(f"  ✓ {src} -> {dst}")

def move_development_tools():
    """Move development tools and scripts."""
    
    tool_moves = {
        "scripts/": "tools/development/",
        "tools/": "tools/",
        "check_plugins.py": "tools/development/check_plugins.py",
        "debug_registration.py": "tools/development/debug_registration.py",
        "export_ast.py": "tools/development/export_ast.py",
        "visualize_ast.py": "tools/development/visualize_ast.py",
        "summarize_ast.py": "tools/development/summarize_ast.py",
    }
    
    print("\n🔧 Moving development tools...")
    for src, dst in tool_moves.items():
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            if src_path.is_dir():
                # Merge directories
                if dst_path.exists():
                    for item in src_path.iterdir():
                        if item.is_file():
                            shutil.copy2(item, dst_path / item.name)
                else:
                    shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
            print(f"  ✓ {src} -> {dst}")

def update_pyproject_toml():
    """Update pyproject.toml for new structure."""
    
    new_pyproject = '''[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "geneforgelang"
version = "1.0.0"
description = "A professional DSL for genomic workflows and bioinformatics"
readme = "README.md"
requires-python = ">=3.9"
license = { text = "MIT" }
authors = [
    { name = "GeneForgeLang Team", email = "team@geneforgelang.org" }
]
maintainers = [
    { name = "GeneForgeLang Team", email = "team@geneforgelang.org" }
]
keywords = ["genomics", "bioinformatics", "dsl", "workflow", "language"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research", 
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Topic :: Software Development :: Languages",
]

dependencies = [
    "PyYAML>=6.0",
    "pydantic>=2.0.0",
    "typing-extensions>=4.0.0",
]

[project.optional-dependencies]
web = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0", 
    "httpx>=0.25.0",
    "slowapi>=0.1.7",
    "starlette>=0.47.2",
    "aiohttp>=3.12.14",
]
cli = [
    "click>=8.0.0",
    "rich>=13.0.0",
    "typer>=0.9.0",
]
ml = [
    "torch>=2.0.0",
    "transformers>=4.30.0",
    "scikit-learn>=1.3.0",
    "numpy>=1.24.0",
]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0", 
    "pytest-mock>=3.10",
    "ruff>=0.1.0",
    "black>=23.0",
    "mypy>=1.5",
    "pre-commit>=3.0",
]
all = [
    "geneforgelang[web,cli,ml,dev]"
]

[project.urls]
Homepage = "https://github.com/Fundacion-de-Neurociencias/GeneForgeLang"
Documentation = "https://geneforgelang.readthedocs.io"
Repository = "https://github.com/Fundacion-de-Neurociencias/GeneForgeLang"
Issues = "https://github.com/Fundacion-de-Neurociencias/GeneForgeLang/issues"

[project.scripts]
gfl = "geneforgelang.cli.main:main"
geneforgelang = "geneforgelang.cli.main:main"

[tool.setuptools.packages.find]
where = ["src"]
include = ["geneforgelang*"]

[tool.setuptools.package-data]
geneforgelang = ["py.typed", "*.json", "*.yaml", "*.yml"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config", 
    "--cov=src/geneforgelang",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]

[tool.coverage.run]
source = ["src/geneforgelang"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
]

[tool.mypy]
python_version = "3.9"
packages = ["src/geneforgelang"]
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true

[tool.ruff]
target-version = "py39"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E", "W",  # pycodestyle
    "F",       # Pyflakes  
    "UP",      # pyupgrade
    "B",       # flake8-bugbear
    "SIM",     # flake8-simplify
    "I",       # isort
    "N",       # pep8-naming
    "D",       # pydocstyle
    "S",       # bandit
    "C4",      # flake8-comprehensions
    "ICN",     # flake8-import-conventions
    "T20",     # flake8-print
]
ignore = [
    "D100", "D101", "D102", "D103", "D104", "D105", "D106", "D107",  # Missing docstrings
    "S101",  # Use of assert
    "S603",  # subprocess call
    "S607",  # Starting a process with a partial executable path
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "D", "T20"]
"tools/**/*.py" = ["T20", "S"]

[tool.black]
line-length = 100
target-version = ['py39']
include = '\\.pyi?$'
'''
    
    print("\n📝 Updating pyproject.toml...")
    with open("pyproject.toml", "w") as f:
        f.write(new_pyproject)
    print("  ✓ Updated pyproject.toml with professional configuration")

def create_init_files():
    """Create __init__.py files for proper Python packages."""
    
    init_files = [
        "src/__init__.py",
        "src/geneforgelang/__init__.py", 
        "src/geneforgelang/core/__init__.py",
        "src/geneforgelang/plugins/__init__.py",
        "src/geneforgelang/web/__init__.py",
        "src/geneforgelang/cli/__init__.py",
        "src/geneforgelang/utils/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
    ]
    
    print("\n📦 Creating package __init__.py files...")
    for init_file in init_files:
        init_path = Path(init_file)
        if not init_path.exists():
            init_path.touch()
            print(f"  ✓ Created {init_file}")

def main():
    """Main restructuring function."""
    print("🏗️ Starting GeneForgeLang project restructuring...")
    print("This will create a professional Python package structure.\n")
    
    create_professional_structure()
    move_core_files()
    move_plugin_files() 
    move_web_files()
    move_cli_files()
    move_utility_files()
    move_documentation()
    move_examples()
    move_development_tools()
    create_init_files()
    update_pyproject_toml()
    
    print("\n✅ Project restructuring completed!")
    print("\nNew structure created:")
    print("  📁 src/geneforgelang/     - Main package")
    print("  📁 tests/                - Test suite") 
    print("  📁 docs/                 - Documentation")
    print("  📁 examples/             - Usage examples")
    print("  📁 tools/                - Development tools")
    print("\nNext steps:")
    print("1. Update import statements in moved files")
    print("2. Run tests to verify everything works")
    print("3. Update CI/CD configuration")
    print("4. Install in development mode: pip install -e .")

if __name__ == "__main__":
    main()