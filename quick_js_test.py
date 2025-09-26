#!/usr/bin/env python3
"""
Quick JavaScript Object Availability Test
Identifies why AutomationStatusIndicator becomes undefined
"""

import sys
import time

# Add src to Python path
sys.path.insert(0, 'src')

from browser_manager import BrowserManager
from utils.status_indicator_manager import StatusIndicatorManager

def test_javascript_availability():
    """Test JavaScript object availability without user interaction"""

    print("🧪 JAVASCRIPT AVAILABILITY TEST")
    print("=" * 50)

    # Connect to browser
    print("1. Connecting to browser...")
    browser_manager = BrowserManager()
    driver = browser_manager.get_or_create_browser()

    if not driver:
        print("❌ Failed to connect to browser")
        return False

    # Navigate to test page
    print("2. Navigating to test page...")
    driver.get("https://www.google.com")
    time.sleep(2)

    # Test StatusIndicatorManager
    print("3. Testing StatusIndicatorManager...")
    status_manager = StatusIndicatorManager(driver)

    # Test 1: Initial loading
    print("\n   Test 1: Initial JavaScript loading")
    load_result = status_manager._ensure_status_js_loaded()
    print(f"   Load result: {load_result}")

    if load_result:
        # Check object availability
        obj_check = driver.execute_script("return typeof window.AutomationStatusIndicator;")
        print(f"   Object type: {obj_check}")

        # Check method availability
        method_check = driver.execute_script(
            "return typeof window.AutomationStatusIndicator.setStatusWithProgress === 'function';"
        )
        print(f"   Method available: {method_check}")

        # Test method call
        if method_check:
            try:
                result = status_manager.set_status_with_progress('running', 1, 5, 'Test message')
                print(f"   Method call result: {result}")
            except Exception as e:
                print(f"   Method call failed: {e}")

        # Test 2: Page navigation effect
        print("\n   Test 2: Page navigation effect")
        print("   Navigating to different page...")
        driver.get("https://example.com")
        time.sleep(2)

        # Check object after navigation
        after_nav = driver.execute_script("return typeof window.AutomationStatusIndicator;")
        print(f"   After navigation: {after_nav}")

        if after_nav == 'undefined':
            print("   ❗ JavaScript object lost during navigation")
            print("   ❗ Testing automatic reload...")

            # Test reload
            reload_result = status_manager._ensure_status_js_loaded()
            print(f"   Reload result: {reload_result}")

            if reload_result:
                recheck = driver.execute_script("return typeof window.AutomationStatusIndicator;")
                print(f"   After reload: {recheck}")

                # Test method after reload
                try:
                    result = status_manager.set_status_with_progress('processing', 2, 5, 'After reload')
                    print(f"   Method after reload: {result}")
                except Exception as e:
                    print(f"   Method after reload failed: {e}")

    # Cleanup
    print("\n4. Cleanup...")
    try:
        status_manager.remove()
        print("   ✅ Cleanup completed")
    except:
        pass

    print("\n✅ JavaScript availability test completed!")
    return True

if __name__ == "__main__":
    try:
        from browser_manager import BrowserManager
        manager = BrowserManager()
        if not manager.is_browser_running():
            print("⚠️ No browser detected. Starting new browser...")

        success = test_javascript_availability()
        print(f"\n🔍 Test {'completed' if success else 'failed'}")

    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback
        traceback.print_exc()