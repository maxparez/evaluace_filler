@echo off
chcp 65001 >nul
title Evaluace Filler - Windows Setup Check
color 0A

echo.
echo =====================================================
echo   EVALUACE FILLER - WINDOWS SETUP CHECK
echo =====================================================
echo.

set ERROR_COUNT=0

echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python is installed
    python --version
) else (
    echo [ERROR] Python is not installed or not in PATH
    echo   Download from: https://python.org
    set /a ERROR_COUNT+=1
)
echo.

echo [2/6] Checking Git installation...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Git is installed
    git --version
) else (
    echo [ERROR] Git is not installed or not in PATH
    echo   Download from: https://git-scm.com
    set /a ERROR_COUNT+=1
)
echo.

echo [3/6] Checking Google Chrome installation...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo [OK] Chrome found in Program Files
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo [OK] Chrome found in Program Files (x86)
) else (
    echo [ERROR] Google Chrome not found
    echo   Download from: https://chrome.google.com
    set /a ERROR_COUNT+=1
)
echo.

echo [4/6] Checking pip (Python package manager)...
python -m pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] pip is available
    python -m pip --version
) else (
    echo [ERROR] pip is not available
    echo   Reinstall Python with pip included
    set /a ERROR_COUNT+=1
)
echo.

echo [5/6] Checking virtual environment support...
python -m venv --help >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python venv module is available
) else (
    echo [ERROR] Python venv module is not available
    echo   Install with: python -m pip install virtualenv
    set /a ERROR_COUNT+=1
)
echo.

echo [6/6] Checking internet connectivity...
ping -n 1 google.com >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Internet connection is working
) else (
    echo [WARNING] Internet connection test failed
    echo   Required for downloading dependencies
    set /a ERROR_COUNT+=1
)
echo.

echo =====================================================
echo   SETUP CHECK RESULTS
echo =====================================================

if %ERROR_COUNT% equ 0 (
    echo [SUCCESS] ALL CHECKS PASSED - System is ready!
    echo.
    echo Next steps:
    echo 1. Clone repository: git clone https://github.com/maxparez/evaluace_filler.git
    echo 2. Navigate to folder: cd evaluace_filler
    echo 3. Run setup: setup_project_windows.bat
    color 0A
) else (
    echo [FAILED] %ERROR_COUNT% ISSUES FOUND - Please fix before continuing
    echo.
    echo Required software:
    echo - Python 3.8+ (python.org)
    echo - Git (git-scm.com)
    echo - Google Chrome (chrome.google.com)
    color 0C
)

echo.
echo Press any key to exit...
pause >nul