@echo off
REM Setup script for Windows development environment

echo Setting up development container scripts...

REM This script doesn't need to do much on Windows since batch files are directly executable

echo Creating convenient batch files for easy access...

REM Copy batch files to a location in PATH for easy access
copy initialize.bat C:\Users\Public\Documents\gfl-init.bat
copy run-tests.bat C:\Users\Public\Documents\gfl-test.bat

echo Created convenient batch files:
echo   gfl-init.bat  - initialize the development environment
echo   gfl-test.bat  - run all tests

echo Setup complete!

pause
