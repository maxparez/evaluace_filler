@echo off
title Evaluace Filler - Windows Setup Check
color 0A

echo.
echo =====================================================
echo   EVALUACE FILLER - WINDOWS SETUP CHECK
echo =====================================================
echo.

REM Function to check if command exists
set "ERROR_COUNT=0"

echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python is installed
    python --version > temp_version.txt 2>&1
    set /p PYTHON_VERSION=<temp_version.txt
    del temp_version.txt
    echo   Version: %PYTHON_VERSION%
    echo ✓ Python version check passed
) else (
    echo ✗ Python is not installed or not in PATH
    echo   Download from: https://python.org
    set /a ERROR_COUNT+=1
)
echo.

echo [2/6] Checking Git installation...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Git is installed
    git --version > temp_git.txt 2>&1
    set /p GIT_VERSION=<temp_git.txt
    del temp_git.txt
    echo   Version: %GIT_VERSION%
) else (
    echo ✗ Git is not installed or not in PATH
    echo   Download from: https://git-scm.com
    set /a ERROR_COUNT+=1
)
echo.

echo [3/6] Checking Google Chrome installation...
set "CHROME_FOUND=0"
set "CHROME_PATH1=C:\Program Files\Google\Chrome\Application\chrome.exe"
set "CHROME_PATH2=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if exist "%CHROME_PATH1%" (
    echo ✓ Chrome found at: %CHROME_PATH1%
    set "CHROME_FOUND=1"
) else (
    if exist "%CHROME_PATH2%" (
        echo ✓ Chrome found at: %CHROME_PATH2%
        set "CHROME_FOUND=1"
    ) else (
        echo ✗ Google Chrome not found in standard locations
        echo   Download from: https://chrome.google.com
        set /a ERROR_COUNT+=1
    )
)
echo.

echo [4/6] Checking pip (Python package manager)...
python -m pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ pip is available
    python -m pip --version > temp_pip.txt 2>&1
    set /p PIP_VERSION=<temp_pip.txt
    del temp_pip.txt
    echo   Version: %PIP_VERSION%
) else (
    echo ✗ pip is not available
    echo   Reinstall Python with pip included
    set /a ERROR_COUNT+=1
)
echo.

echo [5/6] Checking virtual environment support...
python -m venv --help >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python venv module is available
) else (
    echo ✗ Python venv module is not available
    echo   Install with: python -m pip install virtualenv
    set /a ERROR_COUNT+=1
)
echo.

echo [6/6] Checking internet connectivity...
ping -n 1 google.com >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Internet connection is working
) else (
    echo ⚠ Internet connection test failed
    echo   Required for downloading dependencies
    set /a ERROR_COUNT+=1
)
echo.

echo =====================================================
echo   SETUP CHECK RESULTS
echo =====================================================

if %ERROR_COUNT% equ 0 (
    echo ✓ ALL CHECKS PASSED - System is ready!
    echo.
    echo Next steps:
    echo 1. Clone repository: git clone https://github.com/maxparez/evaluace_filler.git
    echo 2. Navigate to folder: cd evaluace_filler
    echo 3. Run setup: setup_project_windows.bat
    echo.
    color 0A
) else (
    echo ✗ %ERROR_COUNT% ISSUES FOUND - Please fix before continuing
    echo.
    echo Required software:
    echo - Python 3.8+ (python.org)
    echo - Git (git-scm.com)
    echo - Google Chrome (chrome.google.com)
    echo.
    color 0C
)

echo =====================================================
echo Press any key to exit...
pause >nul