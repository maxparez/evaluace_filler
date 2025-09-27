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
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo   Version: %PYTHON_VERSION%

    REM Check if Python version is 3.8+
    for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
        if %%a geq 3 if %%b geq 8 (
            echo ✓ Python version is compatible (3.8+ required)
        ) else (
            echo ✗ Python version %PYTHON_VERSION% is too old (3.8+ required)
            set /a ERROR_COUNT+=1
        )
    )
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
    for /f "tokens=3" %%i in ('git --version') do set GIT_VERSION=%%i
    echo   Version: %GIT_VERSION%
) else (
    echo ✗ Git is not installed or not in PATH
    echo   Download from: https://git-scm.com
    set /a ERROR_COUNT+=1
)
echo.

echo [3/6] Checking Google Chrome installation...
set "CHROME_FOUND=0"
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo ✓ Chrome found at: C:\Program Files\Google\Chrome\Application\chrome.exe
    set "CHROME_FOUND=1"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo ✓ Chrome found at: C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
    set "CHROME_FOUND=1"
) else (
    echo ✗ Google Chrome not found in standard locations
    echo   Download from: https://chrome.google.com
    set /a ERROR_COUNT+=1
)
echo.

echo [4/6] Checking pip (Python package manager)...
python -m pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ pip is available
    for /f "tokens=2" %%i in ('python -m pip --version') do set PIP_VERSION=%%i
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