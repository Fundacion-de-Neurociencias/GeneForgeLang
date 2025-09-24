# GeneForgeLang Development Makefile

.PHONY: help install dev-install test lint format type-check security clean build docs serve-docs setup-genesis-data

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

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

setup-genesis-data:  ## Setup data environment for GFL Genesis project
	@echo "-> Configurando el entorno de datos para el proyecto GFL Genesis..."
	@/bin/bash examples/gfl-genesis/scripts/fetch_data.sh
	@/bin/bash examples/gfl-genesis/scripts/preprocess_data.sh
	@echo "✅ Entorno de datos de Genesis configurado."

# Development shortcuts
dev: dev-install  ## Alias for dev-install
check: ci  ## Alias for ci
fmt: format  ## Alias for format
