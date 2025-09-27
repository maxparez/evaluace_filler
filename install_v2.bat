@echo off
chcp 65001 >nul
cls
title Evaluace Filler - Professional Setup Check
color 0F

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║               EVALUACE FILLER - WINDOWS SETUP CHECK           ║
echo ║                         Professional Edition                    ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Tento nástroj zkontroluje všechny požadavky pro Evaluace Filler
echo a připraví váš systém pro automatizaci dotazníků.
echo.

set ERROR_COUNT=0

echo [1/6] Kontroluji Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python je nainstalován
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo    Verze: %%i
) else (
    echo ❌ CHYBA: Python není nainstalován!
    echo.
    echo Prosím nainstalujte Python 3.8+ z:
    echo https://python.org
    echo.
    echo ⚠️  Při instalaci zaškrtněte "Add Python to PATH"!
    set /a ERROR_COUNT+=1
)
echo.

echo [2/6] Kontroluji Git installation...
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Git je nainstalován
    for /f "tokens=*" %%i in ('git --version 2^>^&1') do echo    Verze: %%i
) else (
    echo ❌ CHYBA: Git není nainstalován!
    echo.
    echo Prosím nainstalujte Git z:
    echo https://git-scm.com/download/win
    echo.
    echo ⚠️  Po instalaci restartujte Command Prompt!
    set /a ERROR_COUNT+=1
)
echo.

echo [3/6] Kontroluji Google Chrome installation...
set "CHROME_PATH="
for /f "tokens=2,*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" /ve 2^>nul') do (
    set "CHROME_PATH=%%b"
)

if defined CHROME_PATH (
    if exist "%CHROME_PATH%" (
        echo ✅ Google Chrome je nainstalován
        echo    Cesta: %CHROME_PATH%
    ) else (
        echo ❌ CHYBA: Chrome je registrován, ale soubor chybí!
        echo    Očekávaná cesta: %CHROME_PATH%
        echo.
        echo Prosím přeinstalujte Chrome z:
        echo https://chrome.google.com
        set /a ERROR_COUNT+=1
    )
) else (
    echo ❌ CHYBA: Google Chrome není nalezen!
    echo.
    echo Prosím nainstalujte Google Chrome z:
    echo https://chrome.google.com
    echo.
    echo ⚠️  Používejte standardní instalaci, ne portable verzi!
    set /a ERROR_COUNT+=1
)
echo.

echo [4/6] Kontroluji pip (Python package manager)...
python -m pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ pip je dostupný
    for /f "tokens=*" %%i in ('python -m pip --version 2^>^&1') do echo    Verze: %%i
) else (
    echo ❌ CHYBA: pip není dostupný!
    echo.
    echo Prosím přeinstalujte Python s pip zahrnutým
    echo nebo aktualizujte pip příkazem:
    echo python -m ensurepip --upgrade
    set /a ERROR_COUNT+=1
)
echo.

echo [5/6] Kontroluji Python virtual environment support...
python -m venv --help >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python venv modul je dostupný
    echo    Podporuje vytváření izolovaných prostředí
) else (
    echo ❌ CHYBA: Python venv modul není dostupný!
    echo.
    echo Instalujte pomocí:
    echo python -m pip install virtualenv
    echo.
    echo ⚠️  Nebo přeinstalujte Python s kompletní sadou modulů!
    set /a ERROR_COUNT+=1
)
echo.

echo [6/6] Kontroluji internetové připojení...
ping -n 1 google.com >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Internetové připojení funguje
    echo    Připraveno pro stahování závislostí
) else (
    echo ⚠️  VAROVÁNÍ: Test internetového připojení selhal!
    echo.
    echo Internetové připojení je vyžadováno pro:
    echo - Stahování Python knihoven
    echo - Automatickou správu ChromeDriver
    echo - Přístup k dotazníkům
    set /a ERROR_COUNT+=1
)
echo.

echo ╔════════════════════════════════════════════════════════════════╗
echo ║                      VÝSLEDKY KONTROLY                        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

if %ERROR_COUNT% equ 0 (
    echo ✅ ÚSPĚCH: VŠECHNY KONTROLY PROŠLY - Systém je připraven!
    echo.
    echo ╔═══════════════════════════════════════════════════════════════╗
    echo ║                        DALŠÍ KROKY                            ║
    echo ╚═══════════════════════════════════════════════════════════════╝
    echo.
    echo 1. Klonování repozitáře:
    echo    git clone https://github.com/maxparez/evaluace_filler.git
    echo.
    echo 2. Přechod do složky:
    echo    cd evaluace_filler
    echo.
    echo 3. Spuštění instalace projektu:
    echo    setup_project_windows.bat
    echo.
    echo 4. Konfigurace přístupových kódů:
    echo    edit_config_windows.bat
    echo.
    echo 5. Spuštění automatizace:
    echo    run_batch_windows.bat
    echo.
    color 0A
) else (
    echo ❌ SELHÁNÍ: NALEZENO %ERROR_COUNT% PROBLÉMŮ!
    echo.
    echo ╔═══════════════════════════════════════════════════════════════╗
    echo ║                    POŽADOVANÝ SOFTWARE                        ║
    echo ╚═══════════════════════════════════════════════════════════════╝
    echo.
    echo • Python 3.8+ (python.org)
    echo   ⚠️  Zaškrtněte "Add Python to PATH" při instalaci!
    echo.
    echo • Git (git-scm.com/download/win)
    echo   ⚠️  Restartujte Command Prompt po instalaci!
    echo.
    echo • Google Chrome (chrome.google.com)
    echo   ⚠️  Používejte standardní instalaci!
    echo.
    echo ℹ️  ChromeDriver bude automaticky spravován webdriver-manager
    echo.
    color 0C
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              Stiskněte libovolnou klávesu pro ukončení         ║
echo ╚════════════════════════════════════════════════════════════════╝
pause >nul

rem Reset color to default before exit
color