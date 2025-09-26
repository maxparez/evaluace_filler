#!/usr/bin/env python3
"""
Inclusion Page Handler - Specialized handling for inclusion pages with barrier-free exceptions
Handles the specific case where barrier-free questions need A1 (Rozhodně nesouhlasím)
"""

from typing import List, Optional
from loguru import logger

class InclusionPageHandler:
    """Specialized handler for inclusion pages with mixed rating strategies"""

    def __init__(self):
        self.barrier_free_keywords = [
            "bezbariérová",
            "bezbariérovost",
            "zpřístupnění školy",
            "přizpůsobení a vybavení učeben",
            "zcela bezbariérová"
        ]

    def get_inclusion_filling_strategy(self, page_title: str) -> dict:
        """
        Get comprehensive filling strategy for inclusion pages

        Returns JavaScript that:
        1. Fills barrier-free questions with A1 (Rozhodně nesouhlasím)
        2. Fills all other inclusion questions with A6 (Souhlasím)
        3. Auto-navigates after completion
        """

        if not self.is_inclusion_page(page_title):
            return None

        strategy = {
            "pattern": "INCLUSION_MIXED_STRATEGY",
            "description": "Mixed strategy for inclusion pages",
            "javascript_strategy": self.generate_inclusion_javascript(),
            "auto_navigate": True,
            "navigation_delay": 4000,  # Extra delay for complex processing
            "expected_actions": [
                "Fill barrier-free questions with A1",
                "Fill other inclusion questions with A6",
                "Auto-navigate to next page"
            ]
        }

        return strategy

    def is_inclusion_page(self, page_title: str) -> bool:
        """Check if this is an inclusion page"""
        inclusion_indicators = [
            "v oblasti inkluze",
            "inkluze",
            "inkluzívní"
        ]

        page_lower = page_title.lower()
        return any(indicator in page_lower for indicator in inclusion_indicators)

    def generate_inclusion_javascript(self) -> str:
        """
        Generate JavaScript for mixed inclusion page filling

        Algorithm:
        1. Find all matrix rows
        2. For each row with barrier-free keywords -> click A1
        3. For all other rows -> click A6
        4. Auto-navigate after delay
        """

        js_template = """
console.log('=== INCLUSION PAGE MIXED STRATEGY ===');

var results = {
    total_rows: 0,
    barrier_free_a1: 0,
    regular_a6: 0,
    errors: []
};

try {
    // Find all question rows in the matrix
    var questionRows = document.querySelectorAll('tr, .answer-item, .question-row');
    results.total_rows = questionRows.length;

    console.log('Found', questionRows.length, 'question rows');

    questionRows.forEach(function(row, index) {
        try {
            var rowText = row.textContent || '';
            var isBarrierFree = false;

            // Check if this row is about barrier-free accessibility
            var barrierKeywords = ['bezbariérová', 'zpřístupnění školy', 'přizpůsobení a vybavení učeben'];
            for (var keyword of barrierKeywords) {
                if (rowText.toLowerCase().includes(keyword)) {
                    isBarrierFree = true;
                    break;
                }
            }

            if (isBarrierFree) {
                // This is barrier-free row -> click A1 (Rozhodně nesouhlasím)
                var a1Radio = row.querySelector('input[type="radio"][id$="-A1"]');
                if (a1Radio) {
                    console.log('Clicking A1 for barrier-free:', rowText.substring(0, 50) + '...');
                    a1Radio.click();
                    results.barrier_free_a1++;
                } else {
                    console.warn('A1 radio not found for barrier-free row');
                    results.errors.push('A1 not found for barrier-free row');
                }
            } else {
                // Regular inclusion row -> click A6 (Souhlasím)
                var a6Radio = row.querySelector('input[type="radio"][id$="-A6"]');
                if (a6Radio) {
                    console.log('Clicking A6 for regular inclusion:', rowText.substring(0, 50) + '...');
                    a6Radio.click();
                    results.regular_a6++;
                } else {
                    // Try A5 as fallback
                    var a5Radio = row.querySelector('input[type="radio"][id$="-A5"]');
                    if (a5Radio) {
                        console.log('Clicking A5 as fallback:', rowText.substring(0, 50) + '...');
                        a5Radio.click();
                        results.regular_a6++; // Count as regular
                    }
                }
            }

        } catch (e) {
            console.error('Error processing row', index, ':', e);
            results.errors.push('Row ' + index + ': ' + e.message);
        }
    });

    console.log('Inclusion filling results:', results);

    // Auto-navigate after delay
    if (results.barrier_free_a1 > 0 || results.regular_a6 > 0) {
        console.log('Auto-navigation in 4 seconds...');
        setTimeout(function() {
            var nextButton = document.querySelector('#ls-button-submit');
            if (nextButton) {
                console.log('Clicking next button...');
                nextButton.click();
            } else {
                console.error('Next button not found');
                results.errors.push('Next button not found');
            }
        }, 4000);
    }

    return results;

} catch (e) {
    console.error('Inclusion page filling error:', e);
    results.errors.push('Main error: ' + e.message);
    return results;
}
"""

        return js_template.strip()

    def create_test_javascript(self, specific_id: Optional[str] = None) -> str:
        """Create test JavaScript for specific inclusion page"""

        if specific_id:
            # Test specific ID that was found
            test_js = f"""
console.log('=== TESTING SPECIFIC BARRIER-FREE ID ===');

// Test the specific barrier-free radio button
var specificRadio = document.querySelector('#{specific_id}');
console.log('Specific radio found:', !!specificRadio);

if (specificRadio) {{
    console.log('ID:', specificRadio.id);
    console.log('Before click - checked:', specificRadio.checked);

    // Click it
    specificRadio.click();

    console.log('After click - checked:', specificRadio.checked);
    console.log('✅ Specific barrier-free A1 clicked successfully!');
}} else {{
    console.log('❌ Specific radio button not found');
}}
"""
        else:
            # Generic test
            test_js = self.generate_inclusion_javascript()

        return test_js

# Usage example and testing
if __name__ == "__main__":
    handler = InclusionPageHandler()

    # Test inclusion page detection
    test_titles = [
        "Uveďte, prosím, do jaké míry souhlasíte s následujícími výroky vztahujícími se k Vaší škole v oblasti inkluze.",
        "Uveďte, prosím, do jaké míry souhlasíte s následujícími výroky vztahujícími se k Vaší škole v oblasti čtenářské gramotnosti.",
        "Nějaká jiná stránka"
    ]

    print("=== INCLUSION PAGE HANDLER TEST ===")
    for title in test_titles:
        is_inclusion = handler.is_inclusion_page(title)
        print(f"'{title[:50]}...' -> Inclusion: {is_inclusion}")

        if is_inclusion:
            strategy = handler.get_inclusion_filling_strategy(title)
            print(f"  Strategy: {strategy['pattern']}")
            print(f"  Description: {strategy['description']}")
            print()

    # Generate test JavaScript
    print("\n=== GENERATED JAVASCRIPT (first 500 chars) ===")
    js_code = handler.generate_inclusion_javascript()
    print(js_code[:500] + "...")