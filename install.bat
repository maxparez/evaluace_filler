@echo off
set SCRIPT_VERSION=11.0
rem "Neprustrelna" verze pouzivajici GOTO misto problematickych IF bloku.

chcp 1250 > nul

echo +------------------------------------------------------------------+
echo ^|         Instalace - Evaluace Filler (Verze %SCRIPT_VERSION%)             ^|
echo +------------------------------------------------------------------+
echo.
echo Tento skript provede kompletní kontrolu a instalaci aplikace.
echo Cilovy adresar: %LOCALAPPDATA%\evaluace_filler_app
echo.

REM --- KROK 1: KONTROLA SYSTEMU ---
echo --- KROK 1: Kontrola systemu ---
echo.
set "ERROR_MSG="

rem -- Kontrola 1: Python --
echo [1/4] Kontroluji Python...
python --version >nul 2>&1
if errorlevel 1 (
    set "ERROR_MSG=Python neni nainstalovan nebo neni v PATH! Nainstalujte jej z https://www.python.org"
    goto :KONTROLA_SELHALA
)
echo [OK] Python nalezen
echo.

rem -- Kontrola 2: Git --
echo [2/4] Kontroluji Git...
git --version >nul 2>&1
if errorlevel 1 (
    set "ERROR_MSG=Git neni nainstalovan nebo neni v PATH! Nainstalujte jej z https://git-scm.com/download/win"
    goto :KONTROLA_SELHALA
)
echo [OK] Git nalezen
echo.

rem -- Kontrola 3: Google Chrome --
echo [3/4] Kontroluji Google Chrome...
set "CHROME_PATH="
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" /ve >nul 2>nul
if errorlevel 1 (
    set "ERROR_MSG=Google Chrome nenalezen! Nainstalujte jej z https://chrome.google.com"
    goto :KONTROLA_SELHALA
)
echo [OK] Chrome nalezen
echo.

rem -- Kontrola 4: Internet --
echo [4/4] Kontroluji pripojeni k internetu...
ping -n 1 google.com >nul 2>&1
if errorlevel 1 (
    set "ERROR_MSG=Pripojeni k internetu se nezdarilo! Aplikace vyzaduje pripojeni pro stazeni souboru."
    goto :KONTROLA_SELHALA
)
echo [OK] Pripojeni k internetu funguje
echo.


echo [OK] Vsechny kontroly probehly uspesne.
echo.
goto :INSTALACE

:KONTROLA_SELHALA
echo [CHYBA] %ERROR_MSG%
echo.
echo -----------------------------------------------------------------
echo [CHYBA] V systemu byl nalezen problem. Instalace nemuze pokracovat.
echo Prosim, opravte problem uvedeny vyse a spuste skript znovu.
echo.
pause
exit /b 1


:INSTALACE
REM --- KROK 2: INSTALACE ---
echo --- KROK 2: Instalace aplikace ---
echo.

set "INSTALL_DIR=%LOCALAPPDATA%\evaluace_filler_app"
echo [1/4] Pripravuji instalacni adresar...
if exist "%INSTALL_DIR%" (
    echo       Odstranuji starou verzi...
    rmdir /s /q "%INSTALL_DIR%"
)
mkdir "%INSTALL_DIR%"
echo [OK] Adresar pripraven: %INSTALL_DIR%
echo.

echo [2/4] Stahuji aplikaci z GitHubu...
cd /d "%INSTALL_DIR%"

git clone -b windows-installer https://github.com/maxparez/evaluace_filler.git temp_clone
if errorlevel 1 (
    echo [CHYBA] Stazeni aplikace selhalo! Zkontrolujte pripojeni k internetu.
    pause
    exit /b 1
)

rem Presune obsah z docasneho adresare do aktualniho.
move temp_clone\* "%CD%"
rem Odstrani prazdny docasny adresar
rmdir temp_clone

echo [OK] Aplikace stazena a pripravena v instalacnim adresari.
echo.

echo [3/4] Vytvarim a aktivuji virtualni prostredi pro Python...
python -m venv venv
if errorlevel 1 (
    echo [CHYBA] Nepodarilo se vytvorit virtualni prostredi!
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
echo [OK] Virtualni prostredi aktivovano.
echo.

echo [4/4] Instaluji potrebne Python knihovny...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
    echo [CHYBA] Instalace knihoven selhala! Zkontrolujte vypis chyb vyse.
    pause
    exit /b 1
)
echo [OK] Knihovny uspesne nainstalovany.
echo.

REM --- KROK 3: DOKONCENI ---
echo --- KROK 3: Vytvoreni zastupce ---
echo.

echo Vytvarim spousteci skript run.bat...
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo echo Aktivuji virtualni prostredi a spoustim aplikaci...
    echo call venv\Scripts\activate
    echo python batch_processor.py
    echo pause
) > run.bat

echo Vytvarim zastupce na plose...
powershell -ExecutionPolicy Bypass -Command "$WshShell = New-Object -comObject WScript.Shell; $Desktop = [System.Environment]::GetFolderPath('Desktop'); $ShortcutPath = \"$Desktop\Evaluace Filler.lnk\"; $Shortcut = $WshShell.CreateShortcut($ShortcutPath); $Shortcut.TargetPath = '%INSTALL_DIR%\run.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Spusti aplikaci Evaluace Filler'; $Shortcut.Save()"

echo.
echo +------------------------------------------------------------------+
echo ^|                    INSTALACE DOKONCENA!                        ^|
echo +------------------------------------------------------------------+
echo.
echo Aplikace je nainstalovana v: %INSTALL_DIR%
echo.
echo Aplikaci spustite:
echo   1. Dvojklikem na zastupce "Evaluace Filler" na plose
echo   2. Nebo spustenim run.bat ze slozky aplikace
echo.
pause