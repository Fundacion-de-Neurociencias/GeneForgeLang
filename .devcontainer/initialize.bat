@echo off
REM Script to initialize the development environment

echo Initializing GeneForgeLang development environment...

REM Install project dependencies
echo Installing project dependencies...
pip install -e .[full]

REM Install pre-commit hooks
echo Installing pre-commit hooks...
pre-commit install

REM Run initial tests to verify setup
echo Running initial tests...
python -m pytest tests/ -x -q

REM Create necessary directories
echo Creating necessary directories...
mkdir logs
mkdir tmp
mkdir data

REM Set up git hooks
echo Setting up git hooks...
git config core.hooksPath .git/hooks/

REM Verify installation
echo Verifying installation...
python -c "import gfl; print('GeneForgeLang imported successfully')"

echo Development environment initialization complete!
echo You can now start developing GeneForgeLang.

pause
