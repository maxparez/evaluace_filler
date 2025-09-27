@echo off
title Evaluace Filler - Batch Processor
color 0A

echo.
echo =====================================================
echo   EVALUACE FILLER - BATCH PROCESSOR
echo =====================================================
echo.

echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
) else (
    echo ✗ Virtual environment not found!
    echo Run setup_project_windows.bat first
    goto :error
)
echo.

echo Checking Chrome processes...
tasklist /FI "IMAGENAME eq chrome.exe" 2>NUL | find /I /N "chrome.exe" >NUL
if %errorlevel% equ 0 (
    echo ⚠ Chrome is running - this may cause conflicts
    echo Close Chrome and press any key to continue...
    pause >nul
) else (
    echo ✓ Chrome is not running
)
echo.

echo Starting batch processor...
echo Configuration: config\batch_config.json
echo Window size: 800x600 (configurable in src\config.py)
echo.
echo =====================================================
echo   PROCESSING SURVEYS - DO NOT CLOSE THIS WINDOW
echo =====================================================
echo.

python batch_processor.py

echo.
echo =====================================================
echo   BATCH PROCESSING COMPLETED
echo =====================================================
echo.
echo Check logs\ folder for detailed results
echo Check results\ folder for batch reports
echo.
goto :end

:error
color 0C
echo.
echo Setup required before running batch processor!
echo.

:end
echo Press any key to exit...
pause >nul