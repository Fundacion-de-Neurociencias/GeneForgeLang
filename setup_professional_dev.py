#!/usr/bin/env python3
"""
Setup script for professional development environment.
Configures linting, formatting, pre-commit hooks, and CI/CD.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List


def create_pre_commit_config():
    """Create professional pre-commit configuration."""

    config = """# Professional pre-commit configuration for GeneForgeLang
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-toml
      - id: debug-statements
      - id: mixed-line-ending

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-PyYAML, types-requests]
        args: [--strict, --ignore-missing-imports]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-c, pyproject.toml]

  - repo: https://github.com/python-poetry/poetry
    rev: 1.7.1
    hooks:
      - id: poetry-check

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: [--tb=short, -q]
"""

    print("🔧 Creating pre-commit configuration...")
    with open(".pre-commit-config.yaml", "w", encoding="utf-8") as f:
        f.write(config)
    print("  ✓ Created .pre-commit-config.yaml")


def create_github_workflows():
    """Create GitHub Actions workflows for CI/CD."""

    # Create .github/workflows directory
    workflows_dir = Path(".github/workflows")
    workflows_dir.mkdir(parents=True, exist_ok=True)

    # Main CI workflow
    ci_workflow = """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]

    - name: Lint with ruff
      run: |
        ruff check src tests
        ruff format --check src tests

    - name: Type check with mypy
      run: mypy src/geneforgelang

    - name: Security check with bandit
      run: bandit -r src/geneforgelang -c pyproject.toml

    - name: Test with pytest
      run: |
        pytest --cov=src/geneforgelang --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    runs-on: ubuntu-latest
    needs: test

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Check package
      run: twine check dist/*

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/

  docs:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
        pip install mkdocs-material

    - name: Build documentation
      run: mkdocs build --strict

    - name: Upload docs artifacts
      uses: actions/upload-artifact@v3
      with:
        name: docs
        path: site/
"""

    # Release workflow
    release_workflow = """name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*

    - name: Create GitHub Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
"""

    print("🚀 Creating GitHub Actions workflows...")

    with open(workflows_dir / "ci.yml", "w", encoding="utf-8") as f:
        f.write(ci_workflow)
    print("  ✓ Created .github/workflows/ci.yml")

    with open(workflows_dir / "release.yml", "w", encoding="utf-8") as f:
        f.write(release_workflow)
    print("  ✓ Created .github/workflows/release.yml")


def create_vscode_settings():
    """Create VS Code settings for consistent development."""

    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)

    settings = """{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".mypy_cache": true,
        ".ruff_cache": true,
        "*.egg-info": true
    },
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}"""

    extensions = """{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "charliermarsh.ruff",
        "ms-python.mypy-type-checker",
        "ms-python.pytest",
        "redhat.vscode-yaml",
        "ms-vscode.vscode-json"
    ]
}"""

    print("💻 Creating VS Code configuration...")

    with open(vscode_dir / "settings.json", "w", encoding="utf-8") as f:
        f.write(settings)
    print("  ✓ Created .vscode/settings.json")

    with open(vscode_dir / "extensions.json", "w", encoding="utf-8") as f:
        f.write(extensions)
    print("  ✓ Created .vscode/extensions.json")


def create_makefile():
    """Create Makefile for common development tasks."""

    makefile = """# GeneForgeLang Development Makefile

.PHONY: help install dev-install test lint format type-check security clean build docs serve-docs

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

dev-install:  ## Install package in development mode with all dependencies
	pip install -e .[all]
	pre-commit install

test:  ## Run tests
	pytest --cov=src/geneforgelang --cov-report=term-missing --cov-report=html

test-fast:  ## Run tests without coverage
	pytest -x -v

lint:  ## Run linting
	ruff check src tests
	ruff format --check src tests

format:  ## Format code
	ruff format src tests
	ruff check --fix src tests

type-check:  ## Run type checking
	mypy src/geneforgelang

security:  ## Run security checks
	bandit -r src/geneforgelang -c pyproject.toml

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

docs:  ## Build documentation
	mkdocs build

serve-docs:  ## Serve documentation locally
	mkdocs serve

release-check:  ## Check if ready for release
	@echo "Running pre-release checks..."
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security
	$(MAKE) test
	$(MAKE) build
	twine check dist/*
	@echo "✅ All checks passed! Ready for release."

ci:  ## Run all CI checks locally
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security
	$(MAKE) test

# Development shortcuts
dev: dev-install  ## Alias for dev-install
check: ci  ## Alias for ci
fmt: format  ## Alias for format
"""

    print("🔨 Creating Makefile...")
    with open("Makefile", "w", encoding="utf-8") as f:
        f.write(makefile)
    print("  ✓ Created Makefile")


def create_gitignore():
    """Create comprehensive .gitignore file."""

    gitignore = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# poetry
poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
.idea/

# VS Code
.vscode/
!.vscode/settings.json
!.vscode/extensions.json

# Ruff
.ruff_cache/

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
*.gfl.bak
*.yaml.bak
*.json.bak
temp_*
debug_*
test_output/
logs/

# AI/LLM generated artifacts (to prevent)
*_SUMMARY.md
*_summary.md
generar_*.py
*_interactivo.py
*_desde_*.py
"""

    print("🚫 Creating .gitignore...")
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore)
    print("  ✓ Created .gitignore")


def create_editorconfig():
    """Create .editorconfig for consistent formatting."""

    editorconfig = """# EditorConfig is awesome: https://EditorConfig.org

root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.{yml,yaml}]
indent_size = 2

[*.{json,js,ts}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
"""

    print("📝 Creating .editorconfig...")
    with open(".editorconfig", "w", encoding="utf-8") as f:
        f.write(editorconfig)
    print("  ✓ Created .editorconfig")


def create_mkdocs_config():
    """Create MkDocs configuration for documentation."""

    mkdocs_config = """site_name: GeneForgeLang Documentation
site_description: Professional DSL for genomic workflows
site_url: https://geneforgelang.readthedocs.io
repo_url: https://github.com/Fundacion-de-Neurociencias/GeneForgeLang
repo_name: GeneForgeLang

theme:
  name: material
  palette:
    - scheme: default
      primary: blue
      accent: blue
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: blue
      accent: blue
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.highlight
    - search.share
    - content.code.copy

nav:
  - Home: index.md
  - User Guide:
    - Installation: user-guide/installation.md
    - Quick Start: user-guide/quickstart.md
    - Workflow Syntax: user-guide/syntax.md
    - Examples: user-guide/examples.md
  - API Reference:
    - Core API: api/core.md
    - CLI Commands: api/cli.md
    - Plugin System: api/plugins.md
  - Architecture:
    - Overview: architecture/overview.md
    - Design Decisions: architecture/decisions.md
    - Plugin Development: architecture/plugins.md

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            docstring_style: google
            show_source: true

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.tabbed:
      alternate_style: true
  - toc:
      permalink: true

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/Fundacion-de-Neurociencias/GeneForgeLang
    - icon: fontawesome/brands/python
      link: https://pypi.org/project/geneforgelang/
"""

    print("📚 Creating MkDocs configuration...")
    with open("mkdocs.yml", "w", encoding="utf-8") as f:
        f.write(mkdocs_config)
    print("  ✓ Created mkdocs.yml")


def main():
    """Main setup function."""
    print("🔧 Setting up professional development environment for GeneForgeLang...")

    create_pre_commit_config()
    create_github_workflows()
    create_vscode_settings()
    create_makefile()
    create_gitignore()
    create_editorconfig()
    create_mkdocs_config()

    print("\n✅ Professional development environment setup completed!")
    print("\nNext steps:")
    print("1. Install pre-commit hooks: pre-commit install")
    print("2. Install development dependencies: make dev-install")
    print("3. Run initial checks: make ci")
    print("4. Set up your IDE with the provided configurations")
    print("5. Start developing with professional tooling!")

    print("\nAvailable make commands:")
    print("  make help          - Show all available commands")
    print("  make dev-install   - Install development dependencies")
    print("  make test          - Run test suite")
    print("  make lint          - Run linting")
    print("  make format        - Format code")
    print("  make ci            - Run all CI checks")


if __name__ == "__main__":
    main()
