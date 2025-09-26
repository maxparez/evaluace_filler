# Centralized Configuration System

## Overview

The Evaluace Filler now uses a centralized configuration system that eliminates hardcoded values and provides flexible configuration management.

## Configuration File: `src/config.py`

### Key Features:
- **Environment Variable Support**: Override any setting via environment variables
- **Type Safety**: All configuration values have proper type validation
- **Path Management**: Automatic creation and validation of required directories
- **Convenient Accessors**: Dictionary methods for grouped configuration options
- **Default Values**: Sensible defaults for all settings

## Configuration Options

### Browser Configuration
```python
CHROME_DEBUG_PORT = 9222                    # Chrome remote debugging port
CHROME_USER_DATA_DIR = '/tmp/chrome_evaluace'  # Browser user data directory
CHROMEDRIVER_PATH = '/usr/bin/chromedriver' # Path to ChromeDriver executable
BROWSER_WINDOW_SIZE = '1200,800'            # Browser window dimensions
BROWSER_HEADLESS = False                    # Run browser in headless mode
BROWSER_TIMEOUT = 30                        # Browser operation timeout (seconds)
```

### Timing Configuration
```python
PAGE_LOAD_TIMEOUT = 30      # Page load timeout (seconds)
ELEMENT_WAIT_TIMEOUT = 10   # Element wait timeout (seconds)
NAVIGATION_DELAY = 3.0      # Delay between page navigations (seconds)
FORM_FILL_DELAY = 1.0       # Delay between form fills (seconds)
```

### JavaScript Configuration
```python
JS_EXECUTION_TIMEOUT = 30   # JavaScript execution timeout (seconds)
JS_CACHE_ENABLED = True     # Enable JavaScript file caching
```

### Playback Configuration
```python
PLAYBACK_RANDOM_MATRIX = True           # Use random matrix selection
PLAYBACK_ENABLE_SCREENSHOTS = False     # Enable screenshot capture
PLAYBACK_SCREENSHOT_DIR = 'screenshots' # Screenshot storage directory
PLAYBACK_MAX_PAGES = 0                  # Maximum pages per survey (0 = unlimited)
```

### Batch Processing Configuration
```python
BATCH_SIZE = 50              # Maximum surveys per batch
BATCH_PARALLEL_WORKERS = 1   # Number of parallel workers
BATCH_RETRY_COUNT = 3        # Retry attempts for failed surveys
```

## Environment Variable Override

### Using .env File
1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` with your values:
```bash
# Browser Configuration
CHROME_DEBUG_PORT=9223
CHROME_USER_DATA_DIR=/custom/chrome/data
BROWSER_HEADLESS=true

# Timing Configuration
NAVIGATION_DELAY=5.0
FORM_FILL_DELAY=2.0
```

### Using Environment Variables
```bash
# Override debug port for this run
CHROME_DEBUG_PORT=9999 python src/smart_playback_system.py

# Run in headless mode
BROWSER_HEADLESS=true python batch_processor.py

# Set page limit for testing (e.g., only process 5 pages)
PLAYBACK_MAX_PAGES=5 python batch_processor.py

# Run with unlimited pages (default)
PLAYBACK_MAX_PAGES=0 python batch_processor.py
```

## Usage Examples

### Basic Usage
```python
from src.config import Config

# Access configuration values
debug_port = Config.CHROME_DEBUG_PORT
navigation_delay = Config.NAVIGATION_DELAY

# Use dictionary accessors
chrome_opts = Config.get_chrome_options()
timing_opts = Config.get_timing_config()
```

### Browser Manager Integration
```python
from src.browser_manager import BrowserManager
from src.config import Config

# BrowserManager automatically uses config values
manager = BrowserManager()
print(f"Using port: {manager.debug_port}")  # Uses Config.CHROME_DEBUG_PORT

# Or override specific values
custom_manager = BrowserManager(debug_port=8888)
```

### Smart Playback System Integration
```python
from src.smart_playback_system import SmartPlaybackSystem
from src.config import Config

# System automatically uses config timing values
system = SmartPlaybackSystem()
# Uses Config.NAVIGATION_DELAY, Config.FORM_FILL_DELAY, etc.
```

## Configuration Testing

Run the comprehensive configuration test suite:
```bash
python test_configuration.py
```

Test results include:
- ✅ Config Import
- ✅ Config Values
- ✅ Environment Override
- ✅ BrowserManager Integration
- ✅ Path Validation
- ✅ Config Dictionaries

## Benefits

### Before Centralization ❌
- Hardcoded values scattered across files:
  - `debug_port: int = 9222` in browser_manager.py
  - `time.sleep(3)` in smart_playback_system.py
  - `"/tmp/chrome_evaluace"` in multiple files
- Difficult to change configuration
- No environment variable support
- Inconsistent values across components

### After Centralization ✅
- Single source of truth for all configuration
- Environment variable support for all settings
- Type-safe configuration values
- Easy testing with different configurations
- Consistent behavior across all components
- Path validation and auto-creation
- Convenient dictionary accessors

## Migration Guide

### For Developers
All hardcoded values have been replaced with `Config.*` references:
- `9222` → `Config.CHROME_DEBUG_PORT`
- `"/tmp/chrome_evaluace"` → `Config.CHROME_USER_DATA_DIR`
- `time.sleep(3)` → `time.sleep(Config.NAVIGATION_DELAY)`
- `"/usr/bin/chromedriver"` → `Config.CHROMEDRIVER_PATH`

### For Users
No changes required for basic usage. For customization:
1. Create `.env` file from `.env.example`
2. Customize values as needed
3. Run normally - configuration is loaded automatically

## Path Management

The configuration system automatically creates required directories:
- `logs/` - Application logs
- `scenarios/recorded_sessions/` - Recorded survey sessions
- `screenshots/` - Screenshot storage (if enabled)

## Debug and Monitoring

Print current configuration:
```python
from src.config import Config
Config.print_config()
```

Validate paths:
```python
from src.config import Config
if Config.validate_paths():
    print("All paths ready!")
```

## Best Practices

1. **Use Config class**: Always import and use `Config.*` instead of hardcoded values
2. **Test with overrides**: Use environment variables to test different configurations
3. **Document changes**: Update CONFIG_README.md when adding new configuration options
4. **Validate paths**: Use `Config.validate_paths()` before file operations
5. **Use dictionary accessors**: Use `get_*_config()` methods for grouped options

## Future Enhancements

- Configuration file validation
- Configuration profiles (development, production, testing)
- Dynamic configuration updates
- Configuration UI/CLI interface