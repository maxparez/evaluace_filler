@echo off
title Evaluace Filler - Project Setup
color 0A

echo.
echo =====================================================
echo   EVALUACE FILLER - PROJECT SETUP
echo =====================================================
echo.

echo [1/5] Creating virtual environment...
if exist venv (
    echo ✓ Virtual environment already exists
) else (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% equ 0 (
        echo ✓ Virtual environment created successfully
    ) else (
        echo ✗ Failed to create virtual environment
        goto :error
    )
)
echo.

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% equ 0 (
    echo ✓ Virtual environment activated
) else (
    echo ✗ Failed to activate virtual environment
    goto :error
)
echo.

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% equ 0 (
    echo ✓ pip upgraded successfully
) else (
    echo ⚠ pip upgrade failed (continuing anyway)
)
echo.

echo [4/5] Installing project dependencies...
echo Installing packages from requirements.txt...
python -m pip install -r requirements.txt
if %errorlevel% equ 0 (
    echo ✓ All dependencies installed successfully
) else (
    echo ✗ Failed to install dependencies
    goto :error
)
echo.

echo [5/5] Testing configuration...
echo Testing configuration system...
python src\config.py
if %errorlevel% equ 0 (
    echo ✓ Configuration system working
) else (
    echo ⚠ Configuration test failed (may still work)
)
echo.

echo =====================================================
echo   SETUP COMPLETE!
echo =====================================================
echo.
echo Your Evaluace Filler is ready to use!
echo.
echo Quick start:
echo 1. Make sure Chrome is closed
echo 2. Run: python batch_processor.py
echo.
echo Advanced options:
echo - Edit config: config\batch_config.json
echo - View logs: logs\ folder
echo - Test single survey: python run_smart_playback.py
echo.
echo Window settings (configurable in src\config.py):
echo - Default size: 800x600 pixels
echo - Default position: Top-left corner (0,0)
echo.
color 0A
goto :end

:error
echo.
echo =====================================================
echo   SETUP FAILED!
echo =====================================================
echo.
echo Please check the error messages above and try again.
echo Make sure you have:
echo - Python 3.8+ installed
echo - Internet connection
echo - Administrator rights (if needed)
echo.
color 0C

:end
echo Press any key to exit...
pause >nul