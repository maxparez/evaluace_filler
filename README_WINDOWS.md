# Evaluace Filler - Windows Installation Guide

## 🚀 Quick Start (3 simple steps)

### Step 1: Check System Requirements
Double-click: **`setup_check_windows.bat`**

This will verify you have:
- ✅ Python 3.8+ installed
- ✅ Git installed
- ✅ Google Chrome installed
- ✅ Internet connection

### Step 2: Setup Project
```cmd
git clone https://github.com/maxparez/evaluace_filler.git
cd evaluace_filler
setup_project_windows.bat
```

### Step 3: Run Batch Processing
Double-click: **`run_batch_windows.bat`**

## 📋 What Each File Does

| File | Purpose |
|------|---------|
| `setup_check_windows.bat` | Check system requirements |
| `setup_project_windows.bat` | Install project dependencies |
| `run_batch_windows.bat` | Start survey automation |

## ⚙️ Configuration

### Access Codes
Edit `config/batch_config.json`:
```json
{
  "access_codes": [
    "00XhkO",
    "00XcmS",
    "YOUR_CODE_HERE"
  ]
}
```

### Browser Window Settings
Edit `src/config.py` or set environment variables:
```cmd
set BROWSER_WINDOW_SIZE=1024,768
set BROWSER_WINDOW_POSITION=100,50
```

### Birth Year
Edit `config/batch_config.json`:
```json
{
  "user_profile": {
    "birth_year": 1972
  }
}
```

## 🔧 System Requirements

- **Windows 10/11**
- **Python 3.8+** - Download from [python.org](https://python.org)
- **Git** - Download from [git-scm.com](https://git-scm.com)
- **Google Chrome** - Download from [chrome.google.com](https://chrome.google.com)
- **Internet connection** - For downloading dependencies

## 📁 Project Structure

```
evaluace_filler/
├── setup_check_windows.bat      ← Check requirements
├── setup_project_windows.bat    ← Install project
├── run_batch_windows.bat        ← Run automation
├── batch_processor.py           ← Main automation script
├── config/
│   └── batch_config.json        ← Survey configuration
├── src/
│   └── config.py                ← System configuration
├── logs/                        ← Application logs
├── results/                     ← Batch reports
└── venv/                        ← Python virtual environment
```

## 🆘 Troubleshooting

### "Python is not recognized"
- Install Python from [python.org](https://python.org)
- ✅ Check "Add Python to PATH" during installation

### "Git is not recognized"
- Install Git from [git-scm.com](https://git-scm.com)
- Restart Command Prompt after installation

### "Chrome not found"
- Install Chrome from [chrome.google.com](https://chrome.google.com)
- System automatically detects standard installation paths

### Browser conflicts
- Close all Chrome windows before running
- System creates clean browser sessions automatically

## 📊 Features

- ✅ **Fully automated survey completion**
- ✅ **Multiple survey batch processing**
- ✅ **Windows native compatibility**
- ✅ **Configurable browser window size/position**
- ✅ **Automatic Chrome driver management**
- ✅ **Comprehensive logging and reporting**
- ✅ **No manual intervention required**

## 📞 Support

If you encounter issues:
1. Run `setup_check_windows.bat` to verify system requirements
2. Check `logs/` folder for error details
3. Ensure Chrome is completely closed before running
4. Try running Command Prompt as Administrator if needed

---

**Evaluace Filler** - Automated survey completion system for Windows