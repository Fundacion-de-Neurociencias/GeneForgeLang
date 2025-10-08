#!/bin/bash
################################################################################
# Test Runner for GFL Plugin: RAG Engine
################################################################################
# Convenient script to run the test suite with various options.
#
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh -v           # Run with verbose output
#   ./run_tests.sh -c           # Run with coverage
#   ./run_tests.sh -f <file>    # Run specific test file
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "=========================================================================="
echo "🧪 GFL Plugin RAG Engine - Test Suite"
echo "=========================================================================="
echo ""

# Parse arguments
VERBOSE=""
COVERAGE=""
SPECIFIC_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=gfl_plugin_rag_engine --cov-report=html --cov-report=term-missing"
            shift
            ;;
        -f|--file)
            SPECIFIC_FILE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose         Run tests with verbose output"
            echo "  -c, --coverage        Run tests with coverage report"
            echo "  -f, --file <file>     Run specific test file"
            echo "  -h, --help            Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all tests"
            echo "  $0 -v                 # Verbose output"
            echo "  $0 -c                 # With coverage"
            echo "  $0 -f test_plugin_interface.py  # Specific file"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h for help"
            exit 1
            ;;
    esac
done

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-cov
fi

# Run tests
echo "Running tests..."
echo ""

if [ -n "$SPECIFIC_FILE" ]; then
    pytest ${VERBOSE} ${COVERAGE} "tests/${SPECIFIC_FILE}"
else
    pytest ${VERBOSE} ${COVERAGE} tests/
fi

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "=========================================================================="
    echo "✅ All tests passed!"
    echo "=========================================================================="
else
    echo "=========================================================================="
    echo "❌ Some tests failed. Please review the output above."
    echo "=========================================================================="
fi

if [ -n "$COVERAGE" ]; then
    echo ""
    echo "📊 Coverage report generated: htmlcov/index.html"
fi

exit $EXIT_CODE
