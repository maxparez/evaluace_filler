# Evaluace Filler - PowerShell Installer
# Quick installation script for Windows
# Usage: irm https://raw.githubusercontent.com/maxparez/evaluace_filler/main/install.ps1 | iex

param(
    [string]$InstallPath = "$env:LOCALAPPDATA\EvaluaceFiller"
)

# Color functions
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "→ $Message" -ForegroundColor Cyan
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Banner {
    Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   EVALUACE FILLER - AUTOMATICKÁ INSTALACE   ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Green
}

# Check Python
function Test-Python {
    Write-Info "Kontroluji Python..."

    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]

            if ($major -ge 3 -and $minor -ge 10) {
                Write-Success "Python $major.$minor nalezen"
                return $true
            } else {
                Write-Error "Python $major.$minor je příliš starý. Potřebujete Python 3.10+"
                Write-Info "Stáhněte z: https://www.python.org/downloads/"
                return $false
            }
        }
    } catch {
        Write-Error "Python není nainstalován nebo není v PATH"
        Write-Info "Stáhněte z: https://www.python.org/downloads/"
        Write-Info "DŮLEŽITÉ: Při instalaci zaškrtněte 'Add Python to PATH'"
        return $false
    }
}

# Check Git
function Test-Git {
    Write-Info "Kontroluji Git..."

    try {
        $gitVersion = git --version 2>&1
        if ($gitVersion -match "git version") {
            Write-Success "Git nalezen"
            return $true
        }
    } catch {
        Write-Error "Git není nainstalován nebo není v PATH"
        Write-Info "Stáhněte z: https://git-scm.com/download/win"
        return $false
    }
}

# Main installation
function Install-EvaluaceFiller {
    Write-Banner

    # Check prerequisites
    Write-Info "Kontrola prerekvizit..."
    $pythonOk = Test-Python
    $gitOk = Test-Git

    if (-not ($pythonOk -and $gitOk)) {
        Write-Error "`nInstalace přerušena - chybí prerekvizity!"
        Write-Info "Nainstalujte chybějící software a spusťte instalaci znovu."
        exit 1
    }

    Write-Success "`nVšechny prerekvizity splněny!`n"

    # Create installation directory
    Write-Info "Vytvářím instalační složku: $InstallPath"
    New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
    Write-Success "Složka vytvořena"

    # Clone repository
    Write-Info "Stahuji aplikaci z GitHubu..."
    try {
        git clone --quiet https://github.com/maxparez/evaluace_filler.git $InstallPath 2>&1 | Out-Null
        Write-Success "Aplikace stažena"
    } catch {
        Write-Error "Chyba při stahování z GitHubu"
        Write-Error $_.Exception.Message
        exit 1
    }

    # Change to install directory
    Set-Location $InstallPath

    # Create virtual environment
    Write-Info "Vytvářím Python virtuální prostředí..."
    try {
        python -m venv venv
        Write-Success "Virtuální prostředí vytvořeno"
    } catch {
        Write-Error "Chyba při vytváření virtuálního prostředí"
        Write-Error $_.Exception.Message
        exit 1
    }

    # Activate venv and install dependencies
    Write-Info "Instaluji závislosti (může trvat 1-2 minuty)..."
    try {
        & "$InstallPath\venv\Scripts\Activate.ps1"
        pip install --quiet -r requirements.txt
        Write-Success "Závislosti nainstalovány"
    } catch {
        Write-Error "Chyba při instalaci závislostí"
        Write-Error $_.Exception.Message
        exit 1
    }

    # Create config from example
    Write-Info "Vytvářím konfigurační soubor..."
    if (Test-Path "config\batch_config.example.json") {
        Copy-Item "config\batch_config.example.json" "config\batch_config.json"
        Write-Success "Konfigurační soubor vytvořen"
    }

    # Create desktop shortcuts
    Write-Info "Vytvářím zástupce na ploše..."
    try {
        $WshShell = New-Object -comObject WScript.Shell
        $DesktopPath = [System.Environment]::GetFolderPath('Desktop')

        # Shortcut 1: Config editor
        $ShortcutPath = Join-Path $DesktopPath "Evaluace Filler - Konfigurace.lnk"
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = "notepad.exe"
        $Shortcut.Arguments = "`"$InstallPath\config\batch_config.json`""
        $Shortcut.WorkingDirectory = "$InstallPath\config"
        $Shortcut.Description = "Otevřít konfiguraci Evaluace Filler"
        $Shortcut.IconLocation = "shell32.dll,70"  # Document icon
        $Shortcut.Save()

        # Shortcut 2: Run application
        $ShortcutPath2 = Join-Path $DesktopPath "Evaluace Filler - Spustit.lnk"
        $Shortcut2 = $WshShell.CreateShortcut($ShortcutPath2)
        $Shortcut2.TargetPath = "$InstallPath\run_batch_windows.bat"
        $Shortcut2.WorkingDirectory = "$InstallPath"
        $Shortcut2.Description = "Spustit Evaluace Filler"
        $Shortcut2.IconLocation = "shell32.dll,25"  # Play/Run icon
        $Shortcut2.Save()

        Write-Success "Zástupce vytvořeny na ploše"
    } catch {
        Write-Info "Nepodařilo se vytvořit zástupce (není kritické)"
    }

    # Success message
    Write-Host "`n╔════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║         INSTALACE DOKONČENA!                ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════╝`n" -ForegroundColor Green

    Write-Success "Aplikace nainstalována v: $InstallPath"
    Write-Info "`nDALŠÍ KROKY:"
    Write-Host "  1. Upravte konfiguraci - použijte zástupce na ploše nebo otevřete:" -ForegroundColor Yellow
    Write-Host "     $InstallPath\config\batch_config.json" -ForegroundColor Cyan
    Write-Host "  2. Vložte své hash kódy místo příkladů (ABCD12, EFGH34)" -ForegroundColor Yellow
    Write-Host "  3. Uložte soubor (Ctrl+S)" -ForegroundColor Yellow
    Write-Host "  4. Spusťte aplikaci pomocí:" -ForegroundColor Yellow
    Write-Host "     $InstallPath\run_batch_windows.bat" -ForegroundColor Cyan
    Write-Host "`nPodrobný návod najdete v: $InstallPath\INSTALACE_NAVOD.html`n" -ForegroundColor Cyan
}

# Run installation
Install-EvaluaceFiller
