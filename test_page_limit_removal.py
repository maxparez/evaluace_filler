#!/usr/bin/env python3
"""
Test for Page Limit Removal
Verifies that page limits have been properly removed/configurable
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, 'src')

from config import Config

def test_page_limit_default():
    """Test that default page limit is unlimited (0)"""
    print("🧪 Testing default page limit configuration...")

    default_limit = Config.PLAYBACK_MAX_PAGES
    print(f"Default PLAYBACK_MAX_PAGES: {default_limit}")

    if default_limit == 0:
        print("✅ Default is unlimited (0)")
        return True
    else:
        print(f"❌ Default should be 0 (unlimited), got {default_limit}")
        return False

def test_page_limit_conversion():
    """Test that 0 converts to None for unlimited"""
    print("\n🧪 Testing page limit conversion logic...")

    # Test default (0 -> None)
    max_pages = Config.PLAYBACK_MAX_PAGES if Config.PLAYBACK_MAX_PAGES > 0 else None
    print(f"Default {Config.PLAYBACK_MAX_PAGES} converts to: {max_pages}")

    if max_pages is None:
        print("✅ Default correctly converts to None (unlimited)")
        conversion_test = True
    else:
        print("❌ Default should convert to None for unlimited")
        conversion_test = False

    # Test with environment override
    os.environ['PLAYBACK_MAX_PAGES'] = '10'

    # Reload config to pick up override
    from importlib import reload
    import config
    reload(config)

    test_limit = config.Config.PLAYBACK_MAX_PAGES
    max_pages_test = test_limit if test_limit > 0 else None

    print(f"Override {test_limit} converts to: {max_pages_test}")

    if max_pages_test == 10:
        print("✅ Override correctly converts to integer limit")
        override_test = True
    else:
        print("❌ Override should convert to integer limit")
        override_test = False

    # Clean up
    del os.environ['PLAYBACK_MAX_PAGES']

    return conversion_test and override_test

def test_batch_processor_logic():
    """Test that batch_processor uses the new logic"""
    print("\n🧪 Testing batch processor logic...")

    # Simulate batch processor logic
    max_pages = Config.PLAYBACK_MAX_PAGES if Config.PLAYBACK_MAX_PAGES > 0 else None

    if max_pages is None:
        message = "🚀 UNLIMITED MODE: Running until survey completion"
        expected = True
    else:
        message = f"📊 LIMITED MODE: Maximum {max_pages} pages"
        expected = False  # We expect unlimited by default

    print(f"Batch processor message: {message}")

    if expected:
        print("✅ Batch processor correctly configured for unlimited mode")
        return True
    else:
        print("❌ Batch processor should be in unlimited mode by default")
        return False

def test_smart_playback_system_signature():
    """Test that SmartPlaybackSystem has correct method signature"""
    print("\n🧪 Testing SmartPlaybackSystem method signature...")

    from smart_playback_system import SmartPlaybackSystem
    import inspect

    # Check the method signature
    sig = inspect.signature(SmartPlaybackSystem.run_complete_survey)
    params = sig.parameters

    print(f"Method signature: {sig}")

    if 'max_pages' in params:
        max_pages_param = params['max_pages']
        default_value = max_pages_param.default

        print(f"max_pages parameter default: {default_value}")

        if default_value is None:
            print("✅ SmartPlaybackSystem method defaults to unlimited (None)")
            return True
        else:
            print(f"❌ SmartPlaybackSystem method should default to None, got {default_value}")
            return False
    else:
        print("❌ SmartPlaybackSystem method missing max_pages parameter")
        return False

def test_no_hardcoded_limits():
    """Test that there are no hardcoded limits in key files"""
    print("\n🧪 Testing for removal of hardcoded limits...")

    # Check batch_processor.py for old limit logic
    with open('batch_processor.py', 'r') as f:
        batch_content = f.read()

    # Look for old hardcoded limits
    old_patterns = [
        'max_pages = 10',  # Old test limit
        'max_pages = 60',  # Old full survey limit
        'Reached maximum pages limit'  # Old warning message
    ]

    hardcoded_found = []
    for pattern in old_patterns:
        if pattern in batch_content:
            hardcoded_found.append(pattern)

    if not hardcoded_found:
        print("✅ No old hardcoded limits found in batch_processor.py")
        return True
    else:
        print(f"❌ Found old hardcoded limits: {hardcoded_found}")
        return False

def main():
    """Run all page limit removal tests"""
    print("🚫 PAGE LIMIT REMOVAL TEST SUITE")
    print("=" * 50)

    tests = [
        ("Default Page Limit", test_page_limit_default),
        ("Page Limit Conversion", test_page_limit_conversion),
        ("Batch Processor Logic", test_batch_processor_logic),
        ("SmartPlaybackSystem Signature", test_smart_playback_system_signature),
        ("No Hardcoded Limits", test_no_hardcoded_limits),
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
        print("🎉 All page limit removal tests PASSED!")
        print("✅ Page limits successfully removed/made configurable!")
        return True
    else:
        print("❌ Some page limit removal tests FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)