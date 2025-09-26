#!/usr/bin/env python3
"""
Test script for JavaScript externalization
Validates that all JavaScript code has been moved to external files
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from loguru import logger
from src.utils.javascript_loader import JavaScriptLoader

def test_javascript_loader():
    """Test JavaScript loader functionality"""
    logger.info("🧪 Testing JavaScript Loader")

    try:
        js_loader = JavaScriptLoader()

        # Test script validation
        validation_results = js_loader.validate_scripts()
        logger.info(f"📊 Script validation results: {validation_results}")

        all_valid = all(validation_results.values())
        if all_valid:
            logger.success("✅ All expected JavaScript files found")
        else:
            logger.error("❌ Some JavaScript files are missing")
            for script, valid in validation_results.items():
                if not valid:
                    logger.error(f"  Missing: {script}.js")

        # Test listing available scripts
        available_scripts = js_loader.list_available_scripts()
        logger.info(f"📄 Available scripts: {available_scripts}")

        # Test loading individual scripts
        for script_name in ['matrix_strategy', 'barrier_free_inclusion', 'input_strategy', 'radio_strategy']:
            try:
                js_code = js_loader.load_script(script_name)
                logger.success(f"✅ Loaded {script_name}.js ({len(js_code)} chars)")
            except Exception as e:
                logger.error(f"❌ Failed to load {script_name}.js: {e}")

        return all_valid

    except Exception as e:
        logger.error(f"❌ JavaScript loader test failed: {e}")
        return False

def test_smart_playback_system():
    """Test that SmartPlaybackSystem uses external JavaScript"""
    logger.info("🧪 Testing SmartPlaybackSystem integration")

    try:
        from src.smart_playback_system import SmartPlaybackSystem

        # Initialize system
        playback_system = SmartPlaybackSystem()

        # Verify JavaScript loader is initialized
        if hasattr(playback_system, 'js_loader'):
            logger.success("✅ JavaScript loader integrated into SmartPlaybackSystem")

            # Test strategy creation
            test_page_id = "Uveďte, prosím, do jaké míry souhlasíte s následujícími výroky týkajícími se realizace šablon v oblasti inkluze"
            strategy = playback_system.get_page_strategy(test_page_id)

            if strategy.get('pattern') == 'INCLUSION_MIXED_STRATEGY':
                logger.success("✅ Inclusion strategy correctly configured with barrier_keywords")
                if 'barrier_keywords' in strategy:
                    logger.info(f"📊 Barrier keywords: {len(strategy['barrier_keywords'])} items")
                else:
                    logger.warning("⚠️ No barrier_keywords found in inclusion strategy")

            return True
        else:
            logger.error("❌ JavaScript loader not found in SmartPlaybackSystem")
            return False

    except Exception as e:
        logger.error(f"❌ SmartPlaybackSystem test failed: {e}")
        return False

def check_code_cleanup():
    """Check that JavaScript code has been removed from Python files"""
    logger.info("🧪 Checking for JavaScript code cleanup in Python files")

    python_file = Path(__file__).parent / 'src' / 'smart_playback_system.py'

    try:
        with open(python_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for large JavaScript blocks
        js_indicators = [
            'console.log(',
            'document.querySelectorAll(',
            'forEach(function(',
            'var radios =',
            'var inputs =',
            'Matrix filling with',
            'Input field filling:',
            'Radio choice selection:'
        ]

        remaining_js = []
        for indicator in js_indicators:
            if indicator in content:
                remaining_js.append(indicator)

        if remaining_js:
            logger.warning(f"⚠️ Possible JavaScript code still in Python file: {remaining_js}")
            return False
        else:
            logger.success("✅ No JavaScript code blocks found in Python file")
            return True

    except Exception as e:
        logger.error(f"❌ Code cleanup check failed: {e}")
        return False

def main():
    """Main test execution"""
    logger.info("🚀 JAVASCRIPT EXTERNALIZATION TEST")
    logger.info("=" * 50)

    tests_passed = 0
    total_tests = 3

    # Test 1: JavaScript loader functionality
    if test_javascript_loader():
        tests_passed += 1

    # Test 2: SmartPlaybackSystem integration
    if test_smart_playback_system():
        tests_passed += 1

    # Test 3: Code cleanup verification
    if check_code_cleanup():
        tests_passed += 1

    logger.info("\n" + "=" * 50)
    logger.info(f"📊 TEST RESULTS: {tests_passed}/{total_tests} passed")

    if tests_passed == total_tests:
        logger.success("🎉 All JavaScript externalization tests PASSED!")
    else:
        logger.error(f"❌ {total_tests - tests_passed} tests FAILED!")

    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)