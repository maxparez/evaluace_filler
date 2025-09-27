#!/usr/bin/env python3
"""
Configuration System Test
Tests centralized configuration functionality
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, 'src')

def test_config_import():
    """Test that config can be imported without errors"""
    try:
        from config import Config
        print("✅ Config import successful")
        return True
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

def test_config_values():
    """Test that config values are accessible and have expected types"""
    from config import Config

    tests = [
        ("CHROME_DEBUG_PORT", int, Config.CHROME_DEBUG_PORT),
        ("CHROME_USER_DATA_DIR", str, Config.CHROME_USER_DATA_DIR),
        # CHROMEDRIVER_PATH removed - now using webdriver-manager
        ("NAVIGATION_DELAY", float, Config.NAVIGATION_DELAY),
        ("JS_CACHE_ENABLED", bool, Config.JS_CACHE_ENABLED),
    ]

    all_passed = True
    for name, expected_type, value in tests:
        if isinstance(value, expected_type):
            print(f"✅ {name}: {value} (type: {type(value).__name__})")
        else:
            print(f"❌ {name}: Expected {expected_type.__name__}, got {type(value).__name__}")
            all_passed = False

    return all_passed

def test_environment_override():
    """Test that environment variables override default values"""
    from config import Config

    # Test override
    original_port = Config.CHROME_DEBUG_PORT
    os.environ['CHROME_DEBUG_PORT'] = '8888'

    # Create new config instance to pick up override
    from importlib import reload
    import config
    reload(config)

    new_port = config.Config.CHROME_DEBUG_PORT

    if new_port == 8888:
        print(f"✅ Environment override working: {original_port} → {new_port}")
        success = True
    else:
        print(f"❌ Environment override failed: expected 8888, got {new_port}")
        success = False

    # Clean up
    del os.environ['CHROME_DEBUG_PORT']
    return success

def test_browser_manager_integration():
    """Test that BrowserManager uses config values"""
    try:
        import sys
        sys.path.insert(0, 'src')
        from browser_manager import BrowserManager
        from config import Config

        manager = BrowserManager()

        # Check that manager uses config values
        if manager.debug_port == Config.CHROME_DEBUG_PORT:
            print(f"✅ BrowserManager uses config debug port: {manager.debug_port}")
            port_success = True
        else:
            print(f"❌ BrowserManager debug port mismatch: config={Config.CHROME_DEBUG_PORT}, manager={manager.debug_port}")
            port_success = False

        if manager.user_data_dir == Config.CHROME_USER_DATA_DIR:
            print(f"✅ BrowserManager uses config user data dir: {manager.user_data_dir}")
            dir_success = True
        else:
            print(f"❌ BrowserManager user data dir mismatch: config={Config.CHROME_USER_DATA_DIR}, manager={manager.user_data_dir}")
            dir_success = False

        return port_success and dir_success

    except Exception as e:
        print(f"❌ BrowserManager integration test failed: {e}")
        return False

def test_path_validation():
    """Test that path validation works"""
    from config import Config

    paths_valid = Config.validate_paths()
    if paths_valid:
        print("✅ Path validation successful")

        # Check that required directories exist
        required_paths = [
            Config.LOGS_DIR,
            Config.SCENARIOS_DIR / 'recorded_sessions'
        ]

        all_exist = True
        for path in required_paths:
            if path.exists():
                print(f"✅ Path exists: {path}")
            else:
                print(f"❌ Path missing: {path}")
                all_exist = False

        return all_exist
    else:
        print("❌ Path validation failed")
        return False

def test_config_dictionaries():
    """Test that config provides convenient dictionary accessors"""
    from config import Config

    chrome_opts = Config.get_chrome_options()
    timing_opts = Config.get_timing_config()
    paths_opts = Config.get_paths_config()

    # Check chrome options
    required_chrome_keys = ['debug_port', 'user_data_dir', 'window_size', 'headless', 'timeout']
    chrome_success = all(key in chrome_opts for key in required_chrome_keys)
    print(f"{'✅' if chrome_success else '❌'} Chrome options dict: {list(chrome_opts.keys())}")

    # Check timing options
    required_timing_keys = ['page_load_timeout', 'element_wait_timeout', 'navigation_delay', 'form_fill_delay']
    timing_success = all(key in timing_opts for key in required_timing_keys)
    print(f"{'✅' if timing_success else '❌'} Timing options dict: {list(timing_opts.keys())}")

    # Check paths options
    required_paths_keys = ['scenarios_dir', 'config_dir', 'logs_dir', 'js_scripts_dir', 'project_root']
    paths_success = all(key in paths_opts for key in required_paths_keys)
    print(f"{'✅' if paths_success else '❌'} Paths options dict: {list(paths_opts.keys())}")

    return chrome_success and timing_success and paths_success

def main():
    """Run all configuration tests"""
    print("🔧 CONFIGURATION SYSTEM TEST SUITE")
    print("=" * 50)

    tests = [
        ("Config Import", test_config_import),
        ("Config Values", test_config_values),
        ("Environment Override", test_environment_override),
        ("BrowserManager Integration", test_browser_manager_integration),
        ("Path Validation", test_path_validation),
        ("Config Dictionaries", test_config_dictionaries),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 30)

        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n🎯 FINAL SCORE: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All configuration tests PASSED!")
        return True
    else:
        print("❌ Some configuration tests FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)