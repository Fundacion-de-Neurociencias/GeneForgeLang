@echo off
REM Verification script to check if the development container is set up correctly

echo Verifying GeneForgeLang development container setup...

REM Check Python installation
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python is not installed correctly
    exit /b 1
)

REM Check pip installation
echo Checking pip installation...
pip --version
if %errorlevel% neq 0 (
    echo ❌ pip is not installed correctly
    exit /b 1
)

REM Check project dependencies
echo Checking project dependencies...
pip list | findstr geneforgelang
if %errorlevel% neq 0 (
    echo ⚠️  GeneForgeLang package not found (may be installed in development mode)
)

REM Check required tools
echo Checking required development tools...
for %%t in (black flake8 mypy bandit pytest ruff safety) do (
    where %%t >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ %%t is installed
    ) else (
        echo ❌ %%t is not installed
        exit /b 1
    )
)

REM Check Docker installation
echo Checking Docker installation...
where docker >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker is installed
    docker --version
) else (
    echo ❌ Docker is not installed
    exit /b 1
)

REM Check Git installation
echo Checking Git installation...
where git >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git is installed
    git --version
) else (
    echo ❌ Git is not installed
    exit /b 1
)

REM Check project structure
echo Checking project structure...
if exist "\workspace\gfl" if exist "\workspace\tests" (
    echo ✅ Project structure is correct
) else (
    echo ❌ Project structure is incorrect
    exit /b 1
)

REM Check environment variables
echo Checking environment variables...
if defined PYTHONPATH (
    echo ✅ PYTHONPATH is set: %PYTHONPATH%
) else (
    echo ⚠️  PYTHONPATH is not set
)

REM Run a simple import test
echo Running simple import test...
python -c "import gfl; print('✅ GeneForgeLang imported successfully')"
if %errorlevel% neq 0 (
    echo ❌ Failed to import GeneForgeLang
    exit /b 1
)

REM Run a simple test
echo Running simple test...
python -c "from gfl.plugins.plugin_registry import BaseGFLPlugin; print('✅ BaseGFLPlugin imported successfully')"
if %errorlevel% neq 0 (
    echo ❌ Failed to import BaseGFLPlugin
    exit /b 1
)

echo 🎉 All verification checks passed!
echo Your GeneForgeLang development container is ready to use.

pause
