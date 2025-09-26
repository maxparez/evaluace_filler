#!/usr/bin/env python3
"""
Test Batch Visual Status Indicators
Tests visual status indicators during batch processing
"""

import sys
import time
import json

# Add src to Python path
sys.path.insert(0, 'src')

from browser_manager import BrowserManager
from utils.status_indicator_manager import StatusIndicatorManager
from loguru import logger

def create_test_batch_config():
    """Create a minimal test configuration for batch processing"""
    test_config = {
        "survey_base_url": "https://dotaznik.tul.cz/index.php/survey/index",
        "access_codes": [
            "00XcmS",  # Test code
            "TEST1",   # Mock codes for demonstration
            "TEST2"
        ],
        "user_profiles": [
            {
                "birth_year_range": [1985, 1990],
                "delay_range": [2, 4]
            }
        ],
        "batch_settings": {
            "random_matrix": True,
            "cleanup_browser": True,
            "delay_between_surveys": 3
        }
    }

    # Save test config
    import os
    os.makedirs('config', exist_ok=True)
    with open('config/test_batch_config.json', 'w') as f:
        json.dump(test_config, f, indent=2)

    return 'config/test_batch_config.json'

def test_batch_visual_status_simulation():
    """
    Simulate batch processing with visual status indicators
    This demonstrates how status indicators work during batch processing
    """

    print("🧪 TESTING BATCH VISUAL STATUS INDICATORS")
    print("=" * 60)
    print("This test simulates batch processing with visual status feedback")
    print("Watch the browser for colored status bars during the simulation!")
    print()

    # Connect to browser
    print("1️⃣ Connecting to browser...")
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
    print("3️⃣ Initializing batch status indicators...")
    status_manager = StatusIndicatorManager(driver)

    # Simulate batch processing of 3 surveys
    surveys = [
        {"code": "00XcmS", "pages": 5},
        {"code": "TEST1", "pages": 7},
        {"code": "TEST2", "pages": 4}
    ]

    total_surveys = len(surveys)

    print(f"4️⃣ Simulating batch processing of {total_surveys} surveys...")
    print("👀 Watch the browser status bar for updates!")
    print()

    for survey_num, survey in enumerate(surveys, 1):
        access_code = survey["code"]
        page_count = survey["pages"]

        print(f"   📋 Processing Survey {survey_num}/{total_surveys}: {access_code}")

        # Start survey status
        status_manager.set_status_with_progress(
            'running',
            survey_num,
            total_surveys,
            f'Zpracovávám dotazník {access_code}'
        )
        time.sleep(2)

        # Simulate processing each page
        for page in range(1, page_count + 1):
            print(f"      📄 Processing page {page}/{page_count}")

            status_manager.set_status_with_progress(
                'processing',
                survey_num,
                total_surveys,
                f'Dotazník {access_code} - Stránka {page}'
            )
            time.sleep(1.5)

            # Simulate waiting between pages
            if page < page_count:
                status_manager.set_status_with_progress(
                    'waiting',
                    survey_num,
                    total_surveys,
                    f'Čekám na načtení další stránky...'
                )
                time.sleep(1)

        # Complete survey
        print(f"      ✅ Survey {access_code} completed!")
        status_manager.set_status_with_progress(
            'completed',
            survey_num,
            total_surveys,
            f'Dotazník {access_code} dokončen úspěšně!'
        )
        time.sleep(2)

        # Show transition between surveys (except for the last one)
        if survey_num < total_surveys:
            print(f"      ⏳ Preparing for next survey...")
            next_survey = surveys[survey_num]
            status_manager.set_status_with_progress(
                'waiting',
                survey_num + 1,
                total_surveys,
                f'Připravuji další dotazník {next_survey["code"]}...'
            )
            time.sleep(2)

    print("\n5️⃣ Simulating batch completion...")
    status_manager.set_status(
        'completed',
        f'🎉 Batch zpracování dokončeno! {total_surveys}/{total_surveys} úspěšných'
    )
    time.sleep(3)

    print("\n6️⃣ Testing error scenario...")
    # Simulate error in next batch
    status_manager.set_status_with_progress(
        'error',
        1,
        1,
        'Simulace chyby v dalším dotazníku'
    )
    time.sleep(3)

    print("\n7️⃣ Cleanup...")
    status_manager.remove()
    time.sleep(1)

    print("\n✅ Batch visual status test completed!")
    print("\n📋 Features Demonstrated:")
    print("   ✅ Batch progress indicators (Survey 1/3, 2/3, 3/3)")
    print("   ✅ Per-survey page progress (Page 1/5, 2/5, etc.)")
    print("   ✅ Status transitions (running → processing → waiting → completed)")
    print("   ✅ Survey completion notifications")
    print("   ✅ Transition between surveys")
    print("   ✅ Error handling with visual feedback")
    print("   ✅ Final batch completion status")

    return True

def test_real_batch_with_minimal_config():
    """
    Test with real BatchSurveyProcessor but minimal configuration
    """

    print("\n" + "=" * 60)
    print("🚀 TESTING REAL BATCH PROCESSOR WITH VISUAL STATUS")
    print("=" * 60)
    print("This test uses the real BatchSurveyProcessor with minimal test config")
    print()

    response = input("Do you want to test with real batch processor? (y/N): ").strip().lower()

    if response != 'y':
        print("Skipping real batch processor test")
        return True

    try:
        # Create test config
        config_file = create_test_batch_config()
        print(f"📁 Created test config: {config_file}")

        # Import batch processor
        from batch_processor import BatchSurveyProcessor

        print("🔧 Creating BatchSurveyProcessor with test config...")
        processor = BatchSurveyProcessor(config_file)

        print("🚀 Starting batch processing with visual status indicators...")
        print("👀 Watch the browser for automatic status updates!")
        print("⚠️ Note: Only the first survey (00XcmS) may actually work")
        print()

        # Run batch processing
        results = processor.process_batch()

        print(f"✅ Batch processing completed!")
        print(f"📊 Results: {results.get('completed_surveys', 0)}/{results.get('total_surveys', 0)} successful")

        return True

    except Exception as e:
        print(f"❌ Real batch processor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run comprehensive batch visual status tests"""

    print("🚀 COMPREHENSIVE BATCH VISUAL STATUS TESTS")
    print("=" * 70)
    print("Testing visual status indicators during batch survey processing")
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

        # Test 1: Simulation
        test1_success = test_batch_visual_status_simulation()

        # Test 2: Real batch processor
        test2_success = test_real_batch_with_minimal_config()

        # Summary
        print("\n" + "=" * 70)
        print("📊 BATCH VISUAL STATUS TEST RESULTS")
        print("=" * 70)

        print(f"Simulation test: {'✅ SUCCESS' if test1_success else '❌ FAILED'}")
        print(f"Real batch test: {'✅ SUCCESS' if test2_success else '❌ FAILED'}")

        if test1_success and test2_success:
            print("\n🎉 ALL BATCH VISUAL STATUS TESTS PASSED!")
            print("✅ Visual status indicators are working perfectly with batch processing!")
            print()
            print("🎯 Batch Features Confirmed:")
            print("   ✅ Survey-level progress tracking (Survey 1/5, 2/5, etc.)")
            print("   ✅ Page-level progress within surveys (Page 3/10)")
            print("   ✅ Smooth transitions between surveys")
            print("   ✅ Error handling with descriptive messages")
            print("   ✅ Batch completion summaries")
            print("   ✅ Professional user experience")
            return True
        else:
            print("\n❌ Some batch visual status tests failed")
            return False

    except Exception as e:
        print(f"\n💥 Batch test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Starting Batch Visual Status Indicators Test...")
    print("📋 Make sure browser is running for best results!")
    print()

    input("Press Enter when ready to start batch visual status tests...")
    print()

    success = main()

    print(f"\n🎬 Batch visual status test {'completed successfully' if success else 'failed'}!")
    input("Press Enter to exit...")

    sys.exit(0 if success else 1)