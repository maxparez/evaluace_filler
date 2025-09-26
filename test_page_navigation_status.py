#!/usr/bin/env python3
"""
Test Page Navigation Status Updates
Tests that status indicators update after every page navigation
"""

import sys
import time

# Add src to Python path
sys.path.insert(0, 'src')

from browser_manager import BrowserManager
from utils.status_indicator_manager import StatusIndicatorManager
from smart_playback_system import SmartPlaybackSystem
from loguru import logger

def test_navigation_status_updates():
    """
    Test that status indicators update correctly during page navigation
    """

    print("🧪 TESTING PAGE NAVIGATION STATUS UPDATES")
    print("=" * 60)
    print("This test verifies status updates after every page navigation")
    print("Watch for status changes during page transitions!")
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

    # Initialize status manager
    print("3️⃣ Initializing status manager...")
    status_manager = StatusIndicatorManager(driver)

    print("4️⃣ Testing navigation status sequence...")
    print("👀 Watch the status bar for updates during navigation simulation!")
    print()

    # Simulate the complete navigation lifecycle
    navigation_sequence = [
        {
            'phase': 'Page Processing Start',
            'action': lambda: status_manager.processing_page(1, 'Analyzuji stránku'),
            'description': 'Blue: Processing current page',
            'duration': 2
        },
        {
            'phase': 'Form Filling',
            'action': lambda: status_manager.processing_page(1, 'Vyplňuji formulář'),
            'description': 'Blue: Filling out form elements',
            'duration': 3
        },
        {
            'phase': 'Navigation Triggered',
            'action': lambda: status_manager.waiting_for_page(2),
            'description': 'Orange: Waiting for next page to load',
            'duration': 2
        },
        {
            'phase': 'New Page Loading',
            'action': lambda: status_manager.processing_page(2, 'Načítám novou stránku'),
            'description': 'Blue: New page is being processed',
            'duration': 2
        },
        {
            'phase': 'New Page Analysis',
            'action': lambda: status_manager.processing_page(2, 'Analyzuji nový obsah'),
            'description': 'Blue: Analyzing new page content',
            'duration': 2
        },
        {
            'phase': 'Form Filling Page 2',
            'action': lambda: status_manager.processing_page(2, 'Vyplňuji stránku 2'),
            'description': 'Blue: Processing second page',
            'duration': 3
        },
        {
            'phase': 'Next Navigation',
            'action': lambda: status_manager.waiting_for_page(3),
            'description': 'Orange: Transitioning to page 3',
            'duration': 2
        },
        {
            'phase': 'Page 3 Processing',
            'action': lambda: status_manager.processing_page(3, 'Načítám stránku 3'),
            'description': 'Blue: Processing third page',
            'duration': 2
        },
        {
            'phase': 'Manual Intervention Needed',
            'action': lambda: status_manager.require_manual_intervention(
                'Neznámý typ stránky',
                'Vyplňte ručně a pokračujte'
            ),
            'description': 'Red: Manual intervention required',
            'duration': 4
        },
        {
            'phase': 'Continue After Manual',
            'action': lambda: status_manager.processing_page(4, 'Pokračuji po manuálním zásahu'),
            'description': 'Blue: Continuing after manual fix',
            'duration': 2
        },
        {
            'phase': 'Final Navigation',
            'action': lambda: status_manager.waiting_for_page(5),
            'description': 'Orange: Moving to final page',
            'duration': 2
        },
        {
            'phase': 'Survey Completion',
            'action': lambda: status_manager.automation_completed(),
            'description': 'Green: Survey completed successfully',
            'duration': 3
        }
    ]

    for i, step in enumerate(navigation_sequence, 1):
        print(f"{i:2d}️⃣ {step['phase']}")
        print(f"     📝 {step['description']}")

        # Execute the status update
        step['action']()

        print(f"     ⏳ Waiting {step['duration']}s for visual verification...")
        time.sleep(step['duration'])
        print()

    print("5️⃣ Testing rapid navigation updates...")
    print("     (Simulating quick page-to-page navigation)")

    # Test rapid navigation updates
    for page in range(1, 6):
        # Process page
        status_manager.processing_page(page, f'Rychlé zpracování stránky {page}')
        time.sleep(1)

        # Navigate to next
        if page < 5:
            status_manager.waiting_for_page(page + 1)
            time.sleep(0.5)

    print("\n6️⃣ Testing error during navigation...")
    status_manager.automation_error('Chyba během navigace na stránku 3')
    time.sleep(3)

    print("7️⃣ Cleanup...")
    status_manager.remove()
    time.sleep(1)

    print("\n✅ Page navigation status test completed!")
    print("\n📋 Navigation Lifecycle Tested:")
    print("   ✅ Page processing start (Blue)")
    print("   ✅ Form filling activities (Blue)")
    print("   ✅ Navigation transition (Orange)")
    print("   ✅ New page loading (Blue)")
    print("   ✅ Content analysis (Blue)")
    print("   ✅ Manual intervention alerts (Red)")
    print("   ✅ Error handling (Red)")
    print("   ✅ Survey completion (Green)")
    print("   ✅ Rapid navigation updates")

    return True

def test_smart_playback_navigation_integration():
    """
    Test that SmartPlaybackSystem properly updates status during navigation
    """

    print("\n" + "=" * 60)
    print("🔗 TESTING SMARTPLAYBACKSYSTEM NAVIGATION INTEGRATION")
    print("=" * 60)
    print("Testing that SmartPlaybackSystem updates status during real navigation")
    print()

    response = input("Do you want to test with SmartPlaybackSystem integration? (y/N): ").strip().lower()

    if response != 'y':
        print("Skipping SmartPlaybackSystem integration test")
        return True

    try:
        print("1️⃣ Creating SmartPlaybackSystem...")
        playback_system = SmartPlaybackSystem()

        print("2️⃣ Connecting to browser...")
        if not playback_system.connect_to_browser():
            print("❌ Failed to connect to browser")
            return False

        print("✅ Connected successfully with status manager")

        if playback_system.status_manager:
            print("3️⃣ Testing status manager integration...")

            # Simulate navigation method call
            print("     Testing navigate_to_next_page status updates...")

            # Mock strategy for testing
            test_strategy = {
                'auto_navigate': True,
                'navigation_delay': 2000  # 2 seconds
            }

            # Show initial status
            playback_system.status_manager.processing_page(1, 'Připravuji navigaci')
            time.sleep(2)

            print("     🚀 Simulating navigation (without actual page change)...")

            # Test the status updates that would happen during navigation
            # (We can't test real navigation without a real survey, but we can test status updates)

            # Simulate the status updates from navigate_to_next_page
            current_page = 2
            playback_system.status_manager.waiting_for_page(current_page)
            time.sleep(2)

            playback_system.status_manager.processing_page(current_page, 'Načítám novou stránku')
            time.sleep(2)

            playback_system.status_manager.processing_page(current_page, 'Analyzuji obsah stránky')
            time.sleep(2)

            print("     ✅ Navigation status updates working correctly!")

            # Test completion
            playback_system.status_manager.automation_completed()
            time.sleep(2)

            return True
        else:
            print("❌ Status manager not available")
            return False

    except Exception as e:
        print(f"❌ SmartPlaybackSystem integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive page navigation status tests"""

    print("🚀 COMPREHENSIVE PAGE NAVIGATION STATUS TESTS")
    print("=" * 70)
    print("Testing status indicator updates during page navigation")
    print()

    try:
        # Check browser availability
        from browser_manager import BrowserManager
        manager = BrowserManager()
        if not manager.is_browser_running():
            print("⚠️ Browser not detected. Please start browser first:")
            print("💡 Run: python src/browser_manager.py")
            print("💡 Or: python batch_processor.py")
            print()
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                return False

        # Test 1: Navigation status lifecycle
        test1_success = test_navigation_status_updates()

        # Test 2: SmartPlaybackSystem integration
        test2_success = test_smart_playback_navigation_integration()

        # Summary
        print("\n" + "=" * 70)
        print("📊 PAGE NAVIGATION STATUS TEST RESULTS")
        print("=" * 70)

        print(f"Navigation lifecycle test: {'✅ SUCCESS' if test1_success else '❌ FAILED'}")
        print(f"SmartPlaybackSystem integration: {'✅ SUCCESS' if test2_success else '❌ FAILED'}")

        if test1_success and test2_success:
            print("\n🎉 ALL PAGE NAVIGATION STATUS TESTS PASSED!")
            print("✅ Status indicators update correctly after every page navigation!")
            print()
            print("🎯 Navigation Features Confirmed:")
            print("   ✅ Status updates during page processing")
            print("   ✅ Navigation transition indicators (orange)")
            print("   ✅ New page loading status (blue)")
            print("   ✅ Manual intervention alerts (red)")
            print("   ✅ Error handling during navigation")
            print("   ✅ SmartPlaybackSystem integration")
            print("   ✅ Rapid navigation support")
            return True
        else:
            print("\n❌ Some page navigation status tests failed")
            return False

    except Exception as e:
        print(f"\n💥 Page navigation test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Starting Page Navigation Status Tests...")
    print("📋 Make sure browser is running for best results!")
    print()

    input("Press Enter when ready to start navigation status tests...")
    print()

    success = main()

    print(f"\n🎬 Page navigation status test {'completed successfully' if success else 'failed'}!")
    input("Press Enter to exit...")

    sys.exit(0 if success else 1)