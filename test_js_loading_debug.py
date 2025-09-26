#!/usr/bin/env python3
"""
Debug JavaScript Loading Issues
Diagnoses JavaScript object availability problems
"""

import sys
import time

# Add src to Python path
sys.path.insert(0, 'src')

from browser_manager import BrowserManager
from utils.status_indicator_manager import StatusIndicatorManager
from loguru import logger

def debug_javascript_loading():
    """
    Debug JavaScript loading and availability issues
    """

    print("🐛 DEBUGGING JAVASCRIPT LOADING ISSUES")
    print("=" * 60)
    print("This test diagnoses JavaScript object availability problems")
    print()

    # Connect to browser
    print("1️⃣ Connecting to browser...")
    browser_manager = BrowserManager()
    driver = browser_manager.get_or_create_browser()

    if not driver:
        print("❌ Failed to connect to browser")
        return False

    # Navigate to test page
    print("2️⃣ Navigating to test page...")
    driver.get("https://www.google.com")
    time.sleep(2)

    print("3️⃣ Testing JavaScript object availability...")

    # Test 1: Manual JavaScript loading
    print("\n   🧪 Test 1: Manual JavaScript loading")

    try:
        # Check initial state
        initial_check = driver.execute_script("return typeof window.AutomationStatusIndicator;")
        print(f"      Initial AutomationStatusIndicator type: {initial_check}")

        # Load JavaScript manually
        import os
        from pathlib import Path

        js_path = Path('src/js_scripts/status_indicator.js')
        print(f"      Loading JavaScript from: {js_path}")
        print(f"      File exists: {js_path.exists()}")

        if js_path.exists():
            with open(js_path, 'r', encoding='utf-8') as f:
                status_js = f.read()

            print(f"      JavaScript file size: {len(status_js)} characters")

            # Execute JavaScript
            driver.execute_script(status_js)
            print("      ✅ JavaScript executed successfully")

            # Check if object is now available
            after_load_check = driver.execute_script("return typeof window.AutomationStatusIndicator;")
            print(f"      After load AutomationStatusIndicator type: {after_load_check}")

            if after_load_check == 'object':
                # Check available methods
                methods = driver.execute_script(
                    "return Object.getOwnPropertyNames(window.AutomationStatusIndicator);"
                )
                print(f"      Available methods: {methods}")

                # Test init method
                init_result = driver.execute_script("return window.AutomationStatusIndicator.init();")
                print(f"      Init result: {init_result}")

                # Test setStatusWithProgress availability
                has_method = driver.execute_script(
                    "return typeof window.AutomationStatusIndicator.setStatusWithProgress === 'function';"
                )
                print(f"      Has setStatusWithProgress method: {has_method}")

                if has_method:
                    # Test the actual method
                    test_result = driver.execute_script(
                        "return window.AutomationStatusIndicator.setStatusWithProgress('running', 1, 5, 'Test message');"
                    )
                    print(f"      setStatusWithProgress test result: {test_result}")
                    time.sleep(2)

                    print("      ✅ Manual JavaScript loading successful!")
                else:
                    print("      ❌ setStatusWithProgress method not available")
            else:
                print("      ❌ AutomationStatusIndicator object not created")

        else:
            print("      ❌ JavaScript file not found")

    except Exception as e:
        print(f"      ❌ Manual loading test failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: StatusIndicatorManager
    print("\n   🧪 Test 2: StatusIndicatorManager initialization")

    try:
        status_manager = StatusIndicatorManager(driver)
        print("      ✅ StatusIndicatorManager created")

        # Test initialization
        print("      Testing _ensure_status_js_loaded...")
        load_result = status_manager._ensure_status_js_loaded()
        print(f"      Load result: {load_result}")

        if load_result:
            # Test status setting
            print("      Testing set_status...")
            status_result = status_manager.set_status('running', 'Test status message')
            print(f"      Set status result: {status_result}")
            time.sleep(2)

            # Test status with progress
            print("      Testing set_status_with_progress...")
            progress_result = status_manager.set_status_with_progress('processing', 2, 5, 'Test progress')
            print(f"      Set progress result: {progress_result}")
            time.sleep(2)

            if progress_result:
                print("      ✅ StatusIndicatorManager working correctly!")
            else:
                print("      ❌ set_status_with_progress failed")
        else:
            print("      ❌ JavaScript loading failed")

    except Exception as e:
        print(f"      ❌ StatusIndicatorManager test failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 3: Page navigation effect
    print("\n   🧪 Test 3: Page navigation effect on JavaScript objects")

    try:
        print("      Checking object before navigation...")
        before_nav = driver.execute_script("return typeof window.AutomationStatusIndicator;")
        print(f"      Before navigation: {before_nav}")

        # Navigate to another page
        print("      Navigating to different page...")
        driver.get("https://example.com")
        time.sleep(2)

        print("      Checking object after navigation...")
        after_nav = driver.execute_script("return typeof window.AutomationStatusIndicator;")
        print(f"      After navigation: {after_nav}")

        if after_nav == 'undefined':
            print("      ❗ JavaScript object lost during navigation (this is expected)")
            print("      ❗ This explains why status indicators fail after page changes")

            # Test reloading
            print("      Testing StatusIndicatorManager reload...")
            reload_result = status_manager._ensure_status_js_loaded()
            print(f"      Reload result: {reload_result}")

            if reload_result:
                recheck = driver.execute_script("return typeof window.AutomationStatusIndicator;")
                print(f"      After reload: {recheck}")

        # Navigate back
        print("      Navigating back to Google...")
        driver.get("https://www.google.com")
        time.sleep(2)

        final_check = driver.execute_script("return typeof window.AutomationStatusIndicator;")
        print(f"      After return navigation: {final_check}")

    except Exception as e:
        print(f"      ❌ Navigation test failed: {e}")

    # Clean up
    print("\n4️⃣ Cleanup...")
    try:
        driver.execute_script("if (window.AutomationStatusIndicator) window.AutomationStatusIndicator.remove();")
        print("      ✅ Cleanup completed")
    except:
        pass

    print("\n✅ JavaScript debugging completed!")
    print("\n📋 Key Findings:")
    print("   - Check if JavaScript file loads correctly")
    print("   - Check if object is created after loading")
    print("   - Check if methods are available")
    print("   - Check if navigation resets JavaScript context")
    print("   - Check if StatusIndicatorManager handles reloading")

    return True

def main():
    """Run JavaScript loading debug tests"""

    print("🐛 JAVASCRIPT LOADING DEBUG SUITE")
    print("=" * 70)
    print("Debugging JavaScript object availability issues")
    print()

    try:
        # Check browser availability
        from browser_manager import BrowserManager
        manager = BrowserManager()
        if not manager.is_browser_running():
            print("⚠️ Browser not detected. Please start browser first:")
            print("💡 Run: python src/browser_manager.py")
            print()
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                return False

        # Run debug test
        success = debug_javascript_loading()

        if success:
            print("\n🎉 DEBUG TEST COMPLETED!")
            print("✅ Check the output above for specific issues")
            return True
        else:
            print("\n❌ Debug test failed")
            return False

    except Exception as e:
        print(f"\n💥 Debug test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🐛 Starting JavaScript Loading Debug...")
    print("📋 This will help identify why status indicators fail!")
    print()

    input("Press Enter when ready to start debugging...")
    print()

    success = main()

    print(f"\n🔍 Debug test {'completed successfully' if success else 'failed'}!")
    input("Press Enter to exit...")

    sys.exit(0 if success else 1)