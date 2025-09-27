#!/usr/bin/env python3
"""
Test unknown page handling by modifying Ukrainian participants count from 0 → 1
This should create an unknown page that triggers loop detection
"""

import sys
import time

# Add src to Python path
sys.path.insert(0, '.')

from src.smart_playback_system import SmartPlaybackSystem
from batch_processor import BatchSurveyProcessor

def test_unknown_page_scenario():
    print("🧪 UNKNOWN PAGE SCENARIO TEST")
    print("="*60)
    print("🎯 Test Purpose:")
    print("   - Modify Ukrainian participants: 0 → 1")
    print("   - This should create unknown page after demographics")
    print("   - Test loop detection and fallback handling")
    print("   - Verify system recovery on known pages")
    print()

    print("📋 Test Strategy:")
    print("   - Use test_unknown_page_strategy.json")
    print("   - INPUT_UKRAINIAN_PARTICIPANTS_MODIFIED: value '1' (instead of '0')")
    print("   - Should trigger unknown page in Ukrainian demographics")
    print("   - Loop detection should activate after 3 attempts")
    print()

    # Test with SmartPlaybackSystem using test strategy
    try:
        print("🚀 Starting SmartPlaybackSystem with test strategy...")

        playback_system = SmartPlaybackSystem(
            strategy_file="scenarios/test_unknown_page_strategy.json"
        )

        print("✅ Test strategy loaded successfully")
        print(f"📊 Strategy file: {playback_system.strategy_file}")

        # Show the modified strategy
        if hasattr(playback_system, 'strategy_config'):
            config = playback_system.strategy_config
            if 'default_strategies' in config:
                ukrainian_strategy = config['default_strategies'].get('INPUT_UKRAINIAN_PARTICIPANTS_MODIFIED', {})
                print(f"🧪 Test Modification: {ukrainian_strategy.get('description', 'Not found')}")
                print(f"📝 Test Value: '{ukrainian_strategy.get('input_value', 'Not found')}'")

        print()
        print("⚠️  EXPECTED BEHAVIOR:")
        print("   1. Survey processes normally until Ukrainian demographics")
        print("   2. System inputs '1' instead of '0' for Ukrainian count")
        print("   3. Unknown page appears (Ukrainian details form)")
        print("   4. Loop detection triggers after 3 failed attempts")
        print("   5. Manual fallback prompt appears")
        print("   6. User can inspect unknown page manually")
        print("   7. System continues after manual navigation")
        print()

        response = input("🤔 Do you want to run the test with real survey? (y/N): ").strip().lower()

        if response == 'y':
            print("🌐 Starting browser and connecting to survey...")

            # Note: This would require actual survey URL and access code
            print("💡 This test requires:")
            print("   - Valid survey URL and access code")
            print("   - Manual observation of unknown page behavior")
            print("   - Testing loop detection mechanism")
            print()
            print("🔧 To run full test:")
            print("   1. Update batch_config.json with test strategy")
            print("   2. Run: python batch_processor.py")
            print("   3. Monitor for Ukrainian demographics unknown page")

        else:
            print("✅ Test setup completed - strategy file created")
            print("📁 Strategy file: scenarios/test_unknown_page_strategy.json")

        return True

    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

def show_test_instructions():
    """Show manual test instructions"""
    print("\n📝 MANUAL TEST INSTRUCTIONS:")
    print("="*50)
    print("1. 📂 Update batch_config.json:")
    print('   "strategy_file": "scenarios/test_unknown_page_strategy.json"')
    print()
    print("2. 🚀 Run batch processor:")
    print("   python batch_processor.py")
    print()
    print("3. 👀 Observe behavior:")
    print("   - Survey runs normally until Ukrainian demographics")
    print("   - System inputs '1' for Ukrainian participants")
    print("   - Unknown page should appear")
    print("   - Watch for loop detection (3 attempts)")
    print("   - Manual fallback should trigger")
    print()
    print("4. ✅ Expected results:")
    print("   - Loop detection works correctly")
    print("   - Unknown page handling implemented")
    print("   - System recovers on known pages")

if __name__ == "__main__":
    success = test_unknown_page_scenario()

    if success:
        show_test_instructions()
        print("\n🎉 Unknown page test scenario ready!")
    else:
        print("\n❌ Test scenario setup failed")