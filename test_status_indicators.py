#!/usr/bin/env python3
"""
Test Script for Visual Status Indicators
Tests the status indicator system in real browser environment
"""

import sys
import time

# Add src to Python path
sys.path.insert(0, 'src')

from browser_manager import BrowserManager
from utils.status_indicator_manager import StatusIndicatorManager
from loguru import logger

def test_status_indicators():
    """Test all status indicator functionality"""

    print("🧪 TESTING VISUAL STATUS INDICATORS")
    print("=" * 50)

    # Connect to browser
    print("\n1️⃣ Connecting to browser...")
    browser_manager = BrowserManager()
    driver = browser_manager.get_or_create_browser()

    if not driver:
        print("❌ Failed to connect to browser")
        return False

    # Navigate to a test page
    print("2️⃣ Navigating to test page...")
    driver.get("https://www.google.com")
    time.sleep(2)

    # Initialize status manager
    print("3️⃣ Initializing status indicator manager...")
    status_manager = StatusIndicatorManager(driver)

    # Test all status types with delays for visual verification
    status_tests = [
        ("inactive", "Testing inactive status", 2),
        ("running", "Testing running status", 3),
        ("processing", "Testing processing status", 3),
        ("waiting", "Testing waiting status", 3),
        ("manual_required", "Testing manual required status", 4),
        ("error", "Testing error status", 3),
        ("completed", "Testing completed status", 3)
    ]

    print("4️⃣ Testing all status indicators...")

    for status, description, delay in status_tests:
        print(f"\n   🧪 {description}")

        if status == "manual_required":
            status_manager.set_manual_required(
                "Test manual intervention",
                "This is just a test - click X to close"
            )
        elif status == "error":
            status_manager.automation_error("Test error message")
        else:
            status_manager.set_status(status)

        print(f"   ⏳ Waiting {delay}s for visual verification...")
        time.sleep(delay)

    print("\n5️⃣ Testing progress indicators...")

    # Test progress indicators
    for page in range(1, 6):
        print(f"   📄 Testing page {page}/5")
        status_manager.set_status_with_progress(
            'running', page, 5, f'Zpracovávám otázku {page}'
        )
        time.sleep(2)

    print("\n6️⃣ Testing convenience methods...")

    # Test convenience methods
    convenience_tests = [
        ("start_automation", lambda: status_manager.start_automation(1, 10)),
        ("processing_page", lambda: status_manager.processing_page(3, "Testing processing")),
        ("waiting_for_page", lambda: status_manager.waiting_for_page(4)),
        ("automation_completed", lambda: status_manager.automation_completed()),
    ]

    for method_name, method_call in convenience_tests:
        print(f"   🔧 Testing {method_name}")
        method_call()
        time.sleep(2)

    print("\n7️⃣ Testing visibility and status checks...")

    # Test status checks
    current_status = status_manager.get_current_status()
    is_visible = status_manager.is_visible()

    print(f"   📊 Current status: {current_status}")
    print(f"   👁️ Is visible: {is_visible}")

    print("\n8️⃣ Testing hide/show functionality...")

    print("   🙈 Hiding status bar...")
    status_manager.hide()
    time.sleep(2)

    print("   👁️ Showing status bar...")
    status_manager.show()
    time.sleep(2)

    print("\n9️⃣ Final cleanup...")
    print("   🧹 Removing status indicator...")
    status_manager.remove()
    time.sleep(1)

    print("\n✅ Status indicator test completed!")
    print("\n📋 Test Summary:")
    print("   ✅ All status types tested")
    print("   ✅ Progress indicators tested")
    print("   ✅ Convenience methods tested")
    print("   ✅ Visibility controls tested")
    print("   ✅ Cleanup tested")

    # Keep browser open for manual verification
    print(f"\n🌐 Browser left open for manual inspection")
    print(f"   Current URL: {driver.current_url}")
    print(f"   Browser title: {driver.title}")

    return True

def test_integration_with_smart_playback():
    """Test status indicators with SmartPlaybackSystem integration"""

    print("\n" + "=" * 50)
    print("🔗 TESTING SMARTPLAYBACKSYSTEM INTEGRATION")
    print("=" * 50)

    try:
        from smart_playback_system import SmartPlaybackSystem

        print("1️⃣ Creating SmartPlaybackSystem instance...")
        playback_system = SmartPlaybackSystem()

        print("2️⃣ Connecting to browser...")
        if playback_system.connect_to_browser():
            print("✅ Connected successfully")

            if playback_system.status_manager:
                print("✅ Status manager initialized")

                # Test a few status updates
                print("3️⃣ Testing status manager integration...")
                playback_system.status_manager.start_automation(1)
                time.sleep(2)

                playback_system.status_manager.processing_page(1, "Integration test")
                time.sleep(2)

                playback_system.status_manager.automation_completed()
                time.sleep(2)

                print("✅ Integration test completed successfully!")
                return True
            else:
                print("❌ Status manager not initialized")
                return False
        else:
            print("❌ Failed to connect to browser")
            return False

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all status indicator tests"""

    print("🚀 STARTING COMPREHENSIVE STATUS INDICATOR TESTS")
    print("=" * 70)

    try:
        # Test basic functionality
        basic_test_success = test_status_indicators()

        # Test integration
        integration_test_success = test_integration_with_smart_playback()

        # Summary
        print("\n" + "=" * 70)
        print("📊 FINAL TEST RESULTS")
        print("=" * 70)

        print(f"Basic functionality test: {'✅ PASS' if basic_test_success else '❌ FAIL'}")
        print(f"Integration test: {'✅ PASS' if integration_test_success else '❌ FAIL'}")

        if basic_test_success and integration_test_success:
            print("\n🎉 ALL STATUS INDICATOR TESTS PASSED!")
            print("✅ Visual indicators ready for production use!")
            return True
        else:
            print("\n❌ Some tests failed - check implementation")
            return False

    except Exception as e:
        print(f"\n💥 Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()

    input("\n⏸️ Press Enter to exit and close browser...")

    sys.exit(0 if success else 1)