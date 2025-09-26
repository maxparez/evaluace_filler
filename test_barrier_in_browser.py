#!/usr/bin/env python3
"""
Test barrier-free detection in currently open browser
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Connect to existing Chrome browser session
def test_barrier_free():
    try:
        # Connect to existing Chrome on debugging port
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Connected to existing browser")

        # Test barrier-free JavaScript
        js_code = """
        console.log('Testing barrier-free detection');
        var barrierKeywords = ["bezbariérová", "zpřístupnění školy", "přizpůsobení a vybavení učeben", "bezbariérové", "přístupnost", "fyzické bariéry", "architektonické bariéry"];
        var barrierCount = 0;
        var regularCount = 0;
        var totalProcessed = 0;
        var results = [];

        // Find all radio button groups (rows in matrix)
        var rows = document.querySelectorAll('tr, .answer-item, .answers-list > li');

        rows.forEach(function(row) {
            var rowText = row.textContent.toLowerCase();
            var hasBarrierKeyword = barrierKeywords.some(function(keyword) {
                return rowText.includes(keyword.toLowerCase());
            });

            var radioA1 = row.querySelector('input[type="radio"][id$="-A1"]');
            var radioA6 = row.querySelector('input[type="radio"][id$="-A6"]');

            if (hasBarrierKeyword && radioA1) {
                // Barrier-free question: select A1 (Rozhodně nesouhlasím)
                if (!radioA1.checked) {
                    radioA1.click();
                    barrierCount++;
                    totalProcessed++;
                    results.push({
                        type: 'BARRIER_A1',
                        text: rowText.substring(0, 80) + '...',
                        id: radioA1.id
                    });
                }
            } else if (radioA6) {
                // Regular question: select A6 (Souhlasím)
                if (!radioA6.checked) {
                    radioA6.click();
                    regularCount++;
                    totalProcessed++;
                    results.push({
                        type: 'REGULAR_A6',
                        text: rowText.substring(0, 80) + '...',
                        id: radioA6.id
                    });
                }
            }
        });

        return {
            barrier_free_a1: barrierCount,
            regular_a6: regularCount,
            total_processed: totalProcessed,
            details: results
        };
        """

        print("🧪 Executing barrier-free test JavaScript...")
        result = driver.execute_script(js_code)

        print("\n" + "="*60)
        print("🎯 BARRIER-FREE TEST RESULTS")
        print("="*60)
        print(f"✅ A1 (Barrier-free): {result['barrier_free_a1']}")
        print(f"✅ A6 (Regular): {result['regular_a6']}")
        print(f"📊 Total processed: {result['total_processed']}")
        print()

        if result['details']:
            print("📝 DETAILS:")
            for detail in result['details']:
                type_emoji = "🚫" if detail['type'] == 'BARRIER_A1' else "✅"
                print(f"{type_emoji} {detail['type']}: {detail['text']}")
                print(f"   ID: {detail['id']}")
            print()

        if result['barrier_free_a1'] > 0:
            print("🎉 SUCCESS! Barrier-free questions detected and marked A1")
        else:
            print("⚠️  No barrier-free questions found on this page")

        print("="*60)

        # Don't close browser - leave it for user inspection

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTry running Chrome with remote debugging:")
        print("google-chrome --remote-debugging-port=9222")

if __name__ == "__main__":
    test_barrier_free()