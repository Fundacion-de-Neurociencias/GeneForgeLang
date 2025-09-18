#!/bin/bash

# Script to initialize the development environment
echo "Initializing GeneForgeLang development environment..."

# Install project dependencies
echo "Installing project dependencies..."
pip install -e .[full]

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Run initial tests to verify setup
echo "Running initial tests..."
python -m pytest tests/ -x -q

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p tmp
mkdir -p data

# Set up git hooks
echo "Setting up git hooks..."
git config core.hooksPath .git/hooks/

# Verify installation
echo "Verifying installation..."
python -c "import gfl; print('GeneForgeLang imported successfully')"

echo "Development environment initialization complete!"
echo "You can now start developing GeneForgeLang."
