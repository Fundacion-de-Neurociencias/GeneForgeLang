# Makefile for GFL Genesis Project

# Variables
PYTHON := python3
PIP := pip
PROJECT_NAME := gfl-genesis

# Default target
.PHONY: help
help:
	@echo "GFL Genesis Project Makefile"
	@echo "============================"
	@echo "Available targets:"
	@echo "  setup     - Set up the project environment"
	@echo "  install   - Install all plugins"
	@echo "  test      - Run project tests"
	@echo "  validate  - Validate the GFL workflow"
	@echo "  run       - Execute the GFL workflow"
	@echo "  clean     - Clean up temporary files"

# Set up the project environment
.PHONY: setup
setup:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

# Install all plugins
.PHONY: install
install:
	$(PIP) install -e ./plugins/gfl-plugin-ontarget-scorer
	$(PIP) install -e ./plugins/gfl-plugin-offtarget-scorer
	$(PIP) install -e ./plugins/gfl-crispr-evaluator

# Run project tests
.PHONY: test
test:
	$(PYTHON) -m pytest tests/ -v

# Validate the GFL workflow
.PHONY: validate
validate:
	gfl-validate genesis.gfl

# Execute the GFL workflow
.PHONY: run
run:
	gfl-execute genesis.gfl

# Clean up temporary files
.PHONY: clean
clean:
	rm -rf *.egg-info
	rm -rf build/
	rm -rf dist/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Display project information
.PHONY: info
info:
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python: $(PYTHON)"
	@echo "Pip: $(PIP)"
