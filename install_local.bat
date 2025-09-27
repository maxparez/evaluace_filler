@echo off
set SCRIPT_VERSION=11.1
rem "Lokalni" verze instalujici do aktualniho adresare

chcp 1250 > nul

echo +------------------------------------------------------------------+
echo ^|         Instalace - Evaluace Filler (Lokalni verze %SCRIPT_VERSION%)        ^|
echo +------------------------------------------------------------------+
echo.
echo Tento skript provede kompletni kontrolu a instalaci aplikace.
echo Cilovy adresar: %CD%
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
echo --- KROK 2: Instalace aplikace do aktualniho adresare ---
echo.

set "INSTALL_DIR=%CD%"
echo [1/4] Instalacni adresar: %INSTALL_DIR%

rem Kontrola, zda adresar neni prazdny (kromě install_local.bat)
set FILE_COUNT=0
for %%f in (*) do (
    if not "%%f"=="install_local.bat" (
        set /a FILE_COUNT+=1
    )
)

if %FILE_COUNT% gtr 0 (
    echo.
    echo UPOZORNENI: Adresar neni prazdny!
    echo Pokracovanim prepisete existujici soubory.
    echo.
    echo Stisknete Y pro pokracovani nebo N pro zruseni:
    choice /c YN /n
    if errorlevel 2 (
        echo Instalace zrusena uzivatelem.
        pause
        exit /b 0
    )
    echo.
    echo Odstranuji existujici soubory (kromě install_local.bat)...
    for %%f in (*) do (
        if not "%%f"=="install_local.bat" (
            if exist "%%f\*" (
                rmdir /s /q "%%f"
            ) else (
                del /q "%%f"
            )
        )
    )
)
echo [OK] Adresar pripraven pro instalaci
echo.

echo [2/4] Stahuji aplikaci z GitHubu...

git clone -b windows-installer https://github.com/maxparez/evaluace_filler.git temp_clone
if errorlevel 1 (
    echo [CHYBA] Stazeni aplikace selhalo! Zkontrolujte pripojeni k internetu.
    pause
    exit /b 1
)

rem Presune VŠECHNY soubory a adresáře z docasneho adresare do aktualniho
echo       Presouvam soubory a adresáře...
xcopy temp_clone\* "%CD%" /E /H /Y
if errorlevel 1 (
    echo [CHYBA] Nepodarilo se presunout soubory aplikace!
    pause
    exit /b 1
)
rem Odstrani docasny adresar
rmdir /s /q temp_clone

echo [OK] Aplikace stazena a pripravena v aktualnim adresari.
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
echo --- KROK 3: Vytvoreni spoustecich skriptu ---
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

echo Vytvarim konfiguraci editoru edit_config.bat...
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo echo Oteviram konfiguraci v Notepadu...
    echo notepad.exe config\batch_config.json
    echo pause
) > edit_config.bat

echo.
echo +------------------------------------------------------------------+
echo ^|                    INSTALACE DOKONCENA!                        ^|
echo +------------------------------------------------------------------+
echo.
echo Aplikace je nainstalovana v: %INSTALL_DIR%
echo.
echo Aplikaci spustite:
echo   1. Spustenim run.bat z tohoto adresare
echo   2. Pro editaci konfigurace: edit_config.bat
echo.
echo Soubory v adresari:
echo   - run.bat (spusti aplikaci)
echo   - edit_config.bat (upravi konfiguraci)
echo   - config\ (konfiguracni soubory)
echo   - src\ (zdrojove kody)
echo   - scenarios\ (automatizacni strategie)
echo   - venv\ (Python virtualni prostredi)
echo.
pause