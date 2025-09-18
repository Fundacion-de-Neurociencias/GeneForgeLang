#!/bin/bash

# Script to run tests in the development container

echo "Running GeneForgeLang tests..."

# Set environment variables
export PYTHONPATH=/workspace
export GFL_ENV=test

# Run different types of tests
echo "Running unit tests..."
python -m pytest tests/unit/ -v

echo "Running integration tests..."
python -m pytest tests/integration/ -v

echo "Running plugin tests..."
python -m pytest tests/test_plugin_interfaces.py -v

echo "Running security checks..."
bandit -r gfl/ -x tests/

echo "Running code quality checks..."
flake8 gfl/
black --check gfl/
mypy gfl/

echo "All tests completed!"
