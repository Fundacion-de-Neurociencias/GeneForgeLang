#!/bin/bash

# Verification script to check if the development container is set up correctly

echo "Verifying GeneForgeLang development container setup..."

# Check Python installation
echo "Checking Python installation..."
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python is not installed correctly"
    exit 1
fi

# Check pip installation
echo "Checking pip installation..."
pip --version
if [ $? -ne 0 ]; then
    echo "❌ pip is not installed correctly"
    exit 1
fi

# Check project dependencies
echo "Checking project dependencies..."
pip list | grep geneforgelang
if [ $? -ne 0 ]; then
    echo "⚠️  GeneForgeLang package not found (may be installed in development mode)"
fi

# Check required tools
echo "Checking required development tools..."
TOOLS=("black" "flake8" "mypy" "bandit" "pytest" "ruff" "safety")
for tool in "${TOOLS[@]}"; do
    if command -v $tool &> /dev/null; then
        echo "✅ $tool is installed"
    else
        echo "❌ $tool is not installed"
        exit 1
    fi
done

# Check Docker installation
echo "Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    docker --version
else
    echo "❌ Docker is not installed"
    exit 1
fi

# Check Git installation
echo "Checking Git installation..."
if command -v git &> /dev/null; then
    echo "✅ Git is installed"
    git --version
else
    echo "❌ Git is not installed"
    exit 1
fi

# Check project structure
echo "Checking project structure..."
if [ -d "/workspace/gfl" ] && [ -d "/workspace/tests" ]; then
    echo "✅ Project structure is correct"
else
    echo "❌ Project structure is incorrect"
    exit 1
fi

# Check environment variables
echo "Checking environment variables..."
if [ -n "$PYTHONPATH" ]; then
    echo "✅ PYTHONPATH is set: $PYTHONPATH"
else
    echo "⚠️  PYTHONPATH is not set"
fi

# Run a simple import test
echo "Running simple import test..."
python -c "import gfl; print('✅ GeneForgeLang imported successfully')"
if [ $? -ne 0 ]; then
    echo "❌ Failed to import GeneForgeLang"
    exit 1
fi

# Run a simple test
echo "Running simple test..."
python -c "from gfl.plugins.plugin_registry import BaseGFLPlugin; print('✅ BaseGFLPlugin imported successfully')"
if [ $? -ne 0 ]; then
    echo "❌ Failed to import BaseGFLPlugin"
    exit 1
fi

echo "🎉 All verification checks passed!"
echo "Your GeneForgeLang development container is ready to use."
