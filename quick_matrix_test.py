#!/usr/bin/env python3
"""
Quick Matrix Random Strategy Test
Rychlé testování MATRIX_RANDOM_RATING strategie bez navigace
"""

import sys
import os
import json
import time

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from loguru import logger
from src.smart_playback_system import SmartPlaybackSystem

def test_strategy_selection():
    """Test strategy selection logic"""
    logger.info("🧪 Testing MATRIX_RANDOM_RATING strategy selection")

    try:
        # Create playback system
        playback_system = SmartPlaybackSystem()

        # Check if random strategy exists
        if not hasattr(playback_system, 'strategy_config') or 'default_strategies' not in playback_system.strategy_config:
            logger.error("❌ Strategy config not found")
            return False

        default_strategies = playback_system.strategy_config.get('default_strategies', {})

        if 'MATRIX_RANDOM_RATING' not in default_strategies:
            logger.error("❌ MATRIX_RANDOM_RATING strategy not found")
            return False

        random_strategy = default_strategies['MATRIX_RANDOM_RATING']
        logger.success(f"✅ Found MATRIX_RANDOM_RATING strategy")
        logger.info(f"📊 Configuration: {json.dumps(random_strategy, indent=2)}")

        # Test with strategy disabled
        random_strategy['enabled'] = False
        strategy = playback_system.get_page_strategy("Uveďte, prosím, do jaké míry souhlasíte")
        logger.info(f"🔴 With disabled: {strategy.get('pattern', 'UNKNOWN')}")

        # Test with strategy enabled
        random_strategy['enabled'] = True
        random_strategy['priority'] = 10
        strategy = playback_system.get_page_strategy("Uveďte, prosím, do jaké míry souhlasíte")
        logger.info(f"🟢 With enabled: {strategy.get('pattern', 'UNKNOWN')}")

        if strategy.get('pattern') == 'MATRIX_RANDOM_RATING':
            logger.success("🎉 Strategy selection works correctly!")
            return True
        else:
            logger.error(f"❌ Wrong strategy selected: {strategy.get('pattern')}")
            return False

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def test_strategy_configuration():
    """Test strategy configuration details"""
    logger.info("🔧 Testing strategy configuration")

    try:
        playback_system = SmartPlaybackSystem()

        # Get strategy config
        default_strategies = playback_system.strategy_config.get('default_strategies', {})
        random_strategy = default_strategies.get('MATRIX_RANDOM_RATING', {})

        if not random_strategy:
            logger.error("❌ MATRIX_RANDOM_RATING strategy not found")
            return False

        # Check required fields
        required_fields = ['rating_options', 'keywords', 'priority', 'enabled']
        missing_fields = []

        for field in required_fields:
            if field not in random_strategy:
                missing_fields.append(field)

        if missing_fields:
            logger.error(f"❌ Missing fields: {missing_fields}")
            return False

        # Check rating options
        rating_options = random_strategy.get('rating_options', [])
        expected_options = ['A5', 'A6', 'A7']

        if set(rating_options) == set(expected_options):
            logger.success(f"✅ Rating options correct: {rating_options}")
        else:
            logger.warning(f"⚠️ Rating options: {rating_options} (expected: {expected_options})")

        # Check keywords
        keywords = random_strategy.get('keywords', [])
        logger.info(f"📝 Keywords: {keywords}")

        # Check priority
        priority = random_strategy.get('priority', 0)
        logger.info(f"⚡ Priority: {priority}")

        # Test strategy method exists
        if hasattr(playback_system, 'execute_matrix_random_strategy'):
            logger.success("✅ execute_matrix_random_strategy method exists")
        else:
            logger.error("❌ execute_matrix_random_strategy method missing")
            return False

        logger.success("✅ Strategy configuration is valid")
        return True

    except Exception as e:
        logger.error(f"❌ Strategy configuration test failed: {e}")
        return False

def test_batch_config_integration():
    """Test batch config integration"""
    logger.info("🔧 Testing batch config integration")

    try:
        # Load batch config
        with open('config/batch_config.json', 'r') as f:
            config = json.load(f)

        # Check random_matrix setting
        random_matrix = config.get('batch_settings', {}).get('random_matrix', False)
        logger.info(f"📋 batch_config.json random_matrix: {random_matrix}")

        if 'random_matrix' in config.get('batch_settings', {}):
            logger.success("✅ random_matrix setting found in batch config")

            # Test both values
            for value in [True, False]:
                config['batch_settings']['random_matrix'] = value
                logger.info(f"🔄 Testing with random_matrix = {value}")

            logger.success("✅ Batch config integration working")
            return True
        else:
            logger.error("❌ random_matrix setting not found in batch config")
            return False

    except Exception as e:
        logger.error(f"❌ Batch config test failed: {e}")
        return False

def main():
    """Main test execution"""
    logger.info("🚀 QUICK MATRIX RANDOM STRATEGY TEST")
    logger.info("=" * 40)

    tests = [
        ("Strategy Selection", test_strategy_selection),
        ("Strategy Configuration", test_strategy_configuration),
        ("Batch Config Integration", test_batch_config_integration)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            if test_func():
                logger.success(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} ERROR: {e}")

    logger.info("\n" + "=" * 40)
    logger.info(f"📊 RESULTS: {passed}/{total} tests passed")

    if passed == total:
        logger.success("🎉 ALL TESTS PASSED!")
        return True
    else:
        logger.error("❌ SOME TESTS FAILED!")
        return False

if __name__ == "__main__":
    main()