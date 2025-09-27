#!/usr/bin/env python3
"""
Centralized Configuration for Evaluace Filler
"""

import os
import tempfile
from typing import Dict, Any
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

class Config:
    """Centralized configuration class for all Evaluace Filler components"""

    # Browser Configuration
    CHROME_DEBUG_PORT: int = int(os.getenv('CHROME_DEBUG_PORT', '9222'))
    CHROME_USER_DATA_DIR: str = os.getenv('CHROME_USER_DATA_DIR', str(Path(tempfile.gettempdir()) / "chrome_evaluace"))
    # CHROMEDRIVER_PATH: Removed - now using webdriver-manager for automatic chromedriver management

    # Browser Options
    BROWSER_WINDOW_SIZE: str = os.getenv('BROWSER_WINDOW_SIZE', '1200,800')
    BROWSER_HEADLESS: bool = os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true'
    BROWSER_TIMEOUT: int = int(os.getenv('BROWSER_TIMEOUT', '30'))

    # Survey Configuration
    SURVEY_BASE_URL: str = os.getenv('SURVEY_BASE_URL', '')
    SURVEY_ACCESS_CODE: str = os.getenv('SURVEY_ACCESS_CODE', '')

    # Timing Configuration
    PAGE_LOAD_TIMEOUT: int = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
    ELEMENT_WAIT_TIMEOUT: int = int(os.getenv('ELEMENT_WAIT_TIMEOUT', '10'))
    NAVIGATION_DELAY: float = float(os.getenv('NAVIGATION_DELAY', '3.0'))
    FORM_FILL_DELAY: float = float(os.getenv('FORM_FILL_DELAY', '1.0'))

    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', str(PROJECT_ROOT / 'logs' / 'evaluace_filler.log'))
    ENABLE_DEBUG_LOGS: bool = os.getenv('ENABLE_DEBUG_LOGS', 'false').lower() == 'true'

    # Paths Configuration
    SCENARIOS_DIR: Path = PROJECT_ROOT / 'scenarios'
    CONFIG_DIR: Path = PROJECT_ROOT / 'config'
    LOGS_DIR: Path = PROJECT_ROOT / 'logs'
    JS_SCRIPTS_DIR: Path = PROJECT_ROOT / 'src' / 'js_scripts'

    # JavaScript Configuration
    JS_EXECUTION_TIMEOUT: int = int(os.getenv('JS_EXECUTION_TIMEOUT', '30'))
    JS_CACHE_ENABLED: bool = os.getenv('JS_CACHE_ENABLED', 'true').lower() == 'true'

    # Batch Processing Configuration
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '50'))
    BATCH_PARALLEL_WORKERS: int = int(os.getenv('BATCH_PARALLEL_WORKERS', '1'))
    BATCH_RETRY_COUNT: int = int(os.getenv('BATCH_RETRY_COUNT', '3'))

    # Playback Configuration
    PLAYBACK_RANDOM_MATRIX: bool = os.getenv('PLAYBACK_RANDOM_MATRIX', 'true').lower() == 'true'
    PLAYBACK_ENABLE_SCREENSHOTS: bool = os.getenv('PLAYBACK_ENABLE_SCREENSHOTS', 'false').lower() == 'true'
    PLAYBACK_SCREENSHOT_DIR: str = os.getenv('PLAYBACK_SCREENSHOT_DIR', str(PROJECT_ROOT / 'screenshots'))
    PLAYBACK_MAX_PAGES: int = int(os.getenv('PLAYBACK_MAX_PAGES', '0'))  # 0 = unlimited

    @classmethod
    def get_chrome_options(cls) -> Dict[str, Any]:
        """Get Chrome browser options dictionary"""
        return {
            'debug_port': cls.CHROME_DEBUG_PORT,
            'user_data_dir': cls.CHROME_USER_DATA_DIR,
            'window_size': cls.BROWSER_WINDOW_SIZE,
            'headless': cls.BROWSER_HEADLESS,
            'timeout': cls.BROWSER_TIMEOUT
        }

    @classmethod
    def get_timing_config(cls) -> Dict[str, float]:
        """Get timing configuration dictionary"""
        return {
            'page_load_timeout': cls.PAGE_LOAD_TIMEOUT,
            'element_wait_timeout': cls.ELEMENT_WAIT_TIMEOUT,
            'navigation_delay': cls.NAVIGATION_DELAY,
            'form_fill_delay': cls.FORM_FILL_DELAY
        }

    @classmethod
    def get_paths_config(cls) -> Dict[str, Path]:
        """Get paths configuration dictionary"""
        return {
            'scenarios_dir': cls.SCENARIOS_DIR,
            'config_dir': cls.CONFIG_DIR,
            'logs_dir': cls.LOGS_DIR,
            'js_scripts_dir': cls.JS_SCRIPTS_DIR,
            'project_root': PROJECT_ROOT
        }

    @classmethod
    def validate_paths(cls) -> bool:
        """Validate that all required paths exist or create them"""
        paths_to_create = [
            cls.LOGS_DIR,
            cls.SCENARIOS_DIR / 'recorded_sessions',
            Path(cls.PLAYBACK_SCREENSHOT_DIR) if cls.PLAYBACK_ENABLE_SCREENSHOTS else None
        ]

        for path in paths_to_create:
            if path and not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    print(f"Failed to create directory {path}: {e}")
                    return False

        return True

    @classmethod
    def load_from_env_file(cls, env_file: str = None) -> bool:
        """Load configuration from .env file"""
        if not env_file:
            env_file = PROJECT_ROOT / '.env'

        if not Path(env_file).exists():
            return False

        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"\'')
            return True
        except Exception as e:
            print(f"Failed to load .env file: {e}")
            return False

    @classmethod
    def print_config(cls):
        """Print current configuration for debugging"""
        print("🔧 EVALUACE FILLER CONFIGURATION")
        print("=" * 50)
        print(f"Chrome Debug Port: {cls.CHROME_DEBUG_PORT}")
        print(f"Chrome User Data Dir: {cls.CHROME_USER_DATA_DIR}")
        print("ChromeDriver: Auto-managed via webdriver-manager")
        print(f"Browser Window Size: {cls.BROWSER_WINDOW_SIZE}")
        print(f"Browser Headless: {cls.BROWSER_HEADLESS}")
        print(f"Page Load Timeout: {cls.PAGE_LOAD_TIMEOUT}s")
        print(f"Navigation Delay: {cls.NAVIGATION_DELAY}s")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print(f"Random Matrix: {cls.PLAYBACK_RANDOM_MATRIX}")
        print(f"JS Cache Enabled: {cls.JS_CACHE_ENABLED}")
        print(f"Project Root: {PROJECT_ROOT}")
        print("=" * 50)


# Default configuration instance
config = Config()

# Auto-load .env file if exists
config.load_from_env_file()

# Validate paths on import
config.validate_paths()


def main():
    """Configuration testing and display"""
    print("Testing configuration system...")

    # Print current config
    Config.print_config()

    # Test environment variable override
    print("\n🧪 Testing environment variable override...")
    original_port = Config.CHROME_DEBUG_PORT
    os.environ['CHROME_DEBUG_PORT'] = '9999'

    # Create new config instance to test override
    test_config = Config()
    print(f"Original port: {original_port}")
    print(f"Override port: {test_config.CHROME_DEBUG_PORT}")

    # Test path validation
    print("\n📁 Testing path validation...")
    paths_valid = Config.validate_paths()
    print(f"Paths validation: {'✅ PASS' if paths_valid else '❌ FAIL'}")

    # Test configuration dictionaries
    print("\n📋 Testing configuration dictionaries...")
    chrome_opts = Config.get_chrome_options()
    timing_opts = Config.get_timing_config()
    paths_opts = Config.get_paths_config()

    print(f"Chrome options keys: {list(chrome_opts.keys())}")
    print(f"Timing options keys: {list(timing_opts.keys())}")
    print(f"Paths options keys: {list(paths_opts.keys())}")

    print("\n✅ Configuration system test completed!")


if __name__ == "__main__":
    main()