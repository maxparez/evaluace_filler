@echo off
title Evaluace Filler - Edit Configuration
color 0B

echo.
echo =====================================================
echo   EVALUACE FILLER - CONFIGURATION EDITOR
echo =====================================================
echo.

echo Opening configuration file in Notepad...
echo File: config\batch_config.json
echo.

if exist "config\batch_config.json" (
    echo ✓ Configuration file found
    echo Opening in Notepad...
    notepad.exe "config\batch_config.json"

    echo.
    echo Configuration editing completed.
    echo.
    echo ✏️ What you can edit:
    echo - access_codes: Add your survey access codes
    echo - birth_year: Change birth year (currently 1972)
    echo - delay_between_surveys: Adjust timing (seconds)
    echo - log_level: Change to INFO, DEBUG, or ERROR
    echo - random_matrix: Enable/disable random A5/A6/A7 answers
    echo.
    echo 💡 Tips:
    echo - Keep JSON syntax valid (quotes, commas, brackets)
    echo - Save file (Ctrl+S) before closing Notepad
    echo - Run setup_project_windows.bat if you change structure
    echo.
) else (
    echo ✗ Configuration file not found!
    echo.
    echo Expected location: config\batch_config.json
    echo.
    echo Make sure you are in the evaluace_filler directory.
    echo Run setup_project_windows.bat to create default config.
    echo.
    color 0C
)

echo =====================================================
echo Configuration paths:
echo - Main config: config\batch_config.json (survey settings)
echo - System config: src\config.py (browser window, etc.)
echo - Strategy config: scenarios\optimized_survey_strategy.json
echo =====================================================
echo.
echo Press any key to exit...
pause >nul