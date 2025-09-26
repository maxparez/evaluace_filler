#!/usr/bin/env python3
"""
JavaScript Inclusion Page Filler - Simple & Reliable
Inject JavaScript to fill inclusion page and auto-navigate
"""

import sys
import os
import time

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from loguru import logger
from browser_manager import BrowserManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from utils.page_identifier import PageIdentifier

# Simple JavaScript to fill inclusion page
INCLUSION_FILLER_JS = """
console.log('=== INCLUSION PAGE FILLER STARTING ===');

// Function to fill inclusion page
window.fillInclusionPage = function(ratingLevel = 'A5', autoNavigate = true) {
    console.log('Starting inclusion page fill with rating:', ratingLevel);

    var results = {
        totalRadios: 0,
        filledRadios: 0,
        errors: [],
        success: false
    };

    try {
        // Find all radio buttons with the pattern
        var radios = document.querySelectorAll('input[type="radio"][id*="answer592479X111X4433"][id$="-' + ratingLevel + '"]');
        results.totalRadios = radios.length;

        console.log('Found', radios.length, 'radio buttons for rating', ratingLevel);

        if (radios.length === 0) {
            // Try alternative pattern detection
            var allRadios = document.querySelectorAll('input[type="radio"][id*="answer592479"]');
            console.log('Alternative: found', allRadios.length, 'total radio buttons');

            // Extract pattern and try again
            if (allRadios.length > 0) {
                var sampleId = allRadios[0].id;
                var match = sampleId.match(/(answer\\d+X\\d+X\\d+)SQ\\d+-A\\d+/);
                if (match) {
                    var pattern = match[1];
                    radios = document.querySelectorAll('input[type="radio"][id*="' + pattern + '"][id$="-' + ratingLevel + '"]');
                    results.totalRadios = radios.length;
                    console.log('Using pattern', pattern, '- found', radios.length, 'radios');
                }
            }
        }

        // Fill each radio button
        radios.forEach(function(radio, index) {
            try {
                console.log('Clicking radio', index + 1, ':', radio.id);
                radio.click();
                results.filledRadios++;
            } catch (e) {
                console.error('Failed to click radio', radio.id, ':', e);
                results.errors.push('Radio ' + radio.id + ': ' + e.message);
            }
        });

        results.success = results.filledRadios > 0;

        console.log('Fill complete:', results.filledRadios, '/', results.totalRadios, 'radios filled');

        // Auto navigate if requested
        if (autoNavigate && results.success) {
            console.log('Auto-navigation in 3 seconds...');
            setTimeout(function() {
                var nextButton = document.querySelector('#ls-button-submit');
                if (nextButton) {
                    console.log('Clicking next button...');
                    nextButton.click();
                } else {
                    console.error('Next button not found');
                    results.errors.push('Next button not found');
                }
            }, 3000);
        }

    } catch (e) {
        console.error('Fill inclusion page error:', e);
        results.errors.push('Main error: ' + e.message);
    }

    return results;
};

// Auto-detect and fill if on inclusion page
window.autoFillInclusionIfApplicable = function() {
    var pageText = document.querySelector('.question-text .ls-label-question');
    if (pageText && pageText.textContent.toLowerCase().includes('inkluze')) {
        console.log('Inclusion page detected, auto-filling...');
        return window.fillInclusionPage('A5', true);
    } else {
        console.log('Not an inclusion page, skipping');
        return { success: false, reason: 'Not inclusion page' };
    }
};

console.log('=== INCLUSION FILLER READY ===');
console.log('Use: window.fillInclusionPage("A5", true)');
console.log('Or:  window.autoFillInclusionIfApplicable()');

return {
    fillInclusionPage: window.fillInclusionPage,
    autoFillInclusionIfApplicable: window.autoFillInclusionIfApplicable
};
"""

def js_inclusion_filler():
    """Fill inclusion page using JavaScript injection"""

    print("🚀 JAVASCRIPT INCLUSION PAGE FILLER")
    print("=" * 50)

    # Connect to browser
    manager = BrowserManager()
    if not manager.is_browser_running():
        print("❌ No browser running on port 9222")
        return False

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        current_url = driver.current_url
        print(f"📍 Current page: {current_url}")

        # Check page
        page_id = PageIdentifier.get_page_id(driver)
        print(f"📄 Page: {page_id[:60]}...")

        # Inject JavaScript
        print("💉 Injecting JavaScript filler...")
        result = driver.execute_script(INCLUSION_FILLER_JS)
        print("✅ JavaScript injected successfully")

        # Auto-detect and fill
        print("🎯 Auto-detecting and filling inclusion page...")
        fill_result = driver.execute_script("return window.autoFillInclusionIfApplicable();")

        print(f"\n📊 RESULTS:")
        if fill_result.get('success'):
            print(f"✅ SUCCESS!")
            print(f"  Total radios: {fill_result.get('totalRadios', 0)}")
            print(f"  Filled radios: {fill_result.get('filledRadios', 0)}")

            if fill_result.get('errors'):
                print(f"  ⚠️  Errors: {len(fill_result['errors'])}")
                for error in fill_result['errors'][:3]:  # Show first 3
                    print(f"    - {error}")

            print(f"  🧭 Auto-navigation: Started (3 second delay)")

            # Wait a bit to see the navigation
            print("⏳ Waiting for navigation...")
            time.sleep(5)

            # Check if we moved to next page
            try:
                new_page_id = PageIdentifier.get_page_id(driver)
                if new_page_id != page_id:
                    print(f"🎉 Successfully navigated to: {new_page_id[:60]}...")
                else:
                    print(f"🤔 Still on same page - navigation may have failed")
            except:
                print(f"📍 Navigation status unclear")

        else:
            print(f"❌ FAILED: {fill_result.get('reason', 'Unknown error')}")
            if fill_result.get('errors'):
                print(f"Errors:")
                for error in fill_result['errors']:
                    print(f"  - {error}")

        return fill_result.get('success', False)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def manual_fill_test():
    """Manual test - inject JS and let user trigger"""

    print("🧪 MANUAL JAVASCRIPT TEST")
    print("=" * 50)

    # Connect to browser
    manager = BrowserManager()
    if not manager.is_browser_running():
        print("❌ No browser running")
        return

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("💉 Injecting JavaScript...")
        driver.execute_script(INCLUSION_FILLER_JS)
        print("✅ JavaScript injected")

        print(f"\n🎮 MANUAL CONTROL:")
        print(f"Open browser console (F12) and run:")
        print(f"  window.fillInclusionPage('A5', false)  // Fill without auto-nav")
        print(f"  window.fillInclusionPage('A5', true)   // Fill with auto-nav")
        print(f"  window.autoFillInclusionIfApplicable() // Auto-detect and fill")

        print(f"\n✅ JavaScript functions ready for manual testing")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Auto-fill inclusion page (default)")
    print("2. Manual testing mode")

    try:
        choice = input("Mode [1]: ").strip()
        if choice == '2':
            manual_fill_test()
        else:
            success = js_inclusion_filler()
            print(f"\n🏁 RESULT: {'SUCCESS' if success else 'FAILED'}")
    except (EOFError, KeyboardInterrupt):
        # Run auto mode if no input available
        success = js_inclusion_filler()
        print(f"\n🏁 RESULT: {'SUCCESS' if success else 'FAILED'}")