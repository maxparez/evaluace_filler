#!/usr/bin/env python3
"""
Test MATRIX_RANDOM_RATING strategy implementation
"""

import sys
import os
import json
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from loguru import logger
from src.smart_playback_system import SmartPlaybackSystem

def test_random_matrix_config():
    """Test MATRIX_RANDOM_RATING strategy configuration"""
    try:
        # Create SmartPlaybackSystem
        playback_system = SmartPlaybackSystem()

        logger.info("🧪 Testing MATRIX_RANDOM_RATING configuration")

        # Check if strategy exists
        default_strategies = playback_system.strategy_config.get('default_strategies', {})

        if 'MATRIX_RANDOM_RATING' not in default_strategies:
            logger.error("❌ MATRIX_RANDOM_RATING strategy not found in configuration!")
            return False

        random_strategy = default_strategies['MATRIX_RANDOM_RATING']
        logger.success("✅ MATRIX_RANDOM_RATING strategy found")

        # Check configuration
        logger.info(f"📊 Pattern: {random_strategy.get('pattern')}")
        logger.info(f"🎯 Rating options: {random_strategy.get('rating_options')}")
        logger.info(f"⚡ Priority: {random_strategy.get('priority')}")
        logger.info(f"🔧 Enabled: {random_strategy.get('enabled')}")

        # Test batch config
        with open('config/batch_config.json', 'r') as f:
            batch_config = json.load(f)

        random_matrix_enabled = batch_config.get('batch_settings', {}).get('random_matrix', False)
        logger.info(f"🎲 Batch random_matrix setting: {random_matrix_enabled}")

        # Test strategy selection simulation
        test_page_title = "Uveďte, prosím, do jaké míry souhlasíte s následujícími výroky"

        # Test with random disabled
        random_strategy['enabled'] = False
        strategy = playback_system.get_page_strategy(test_page_title)
        logger.info(f"📄 With random disabled, selected: {strategy.get('pattern', 'UNKNOWN')}")

        # Test with random enabled
        random_strategy['enabled'] = True
        random_strategy['priority'] = 10
        strategy = playback_system.get_page_strategy(test_page_title)
        logger.info(f"🎲 With random enabled, selected: {strategy.get('pattern', 'UNKNOWN')}")

        if strategy.get('pattern') == 'MATRIX_RANDOM_RATING':
            logger.success("🎉 MATRIX_RANDOM_RATING strategy selection works!")
            return True
        else:
            logger.warning("⚠️  MATRIX_RANDOM_RATING not selected - check priority/keywords")
            return False

    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def test_batch_config_update():
    """Test updating batch config for random matrix"""
    logger.info("🔧 Testing batch config update")

    # Enable random matrix in config
    with open('config/batch_config.json', 'r') as f:
        config = json.load(f)

    config['batch_settings']['random_matrix'] = True
    logger.info("✅ Set random_matrix = true in batch config")

    # Save updated config
    with open('config/batch_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    logger.success("💾 Batch config updated for MATRIX_RANDOM_RATING testing")

    return True

def reset_batch_config():
    """Reset batch config to default"""
    logger.info("🔄 Resetting batch config")

    with open('config/batch_config.json', 'r') as f:
        config = json.load(f)

    config['batch_settings']['random_matrix'] = False

    with open('config/batch_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    logger.info("✅ Batch config reset to random_matrix = false")

def main():
    """Main test execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Test MATRIX_RANDOM_RATING implementation')
    parser.add_argument('--enable', action='store_true', help='Enable random matrix for testing')
    parser.add_argument('--disable', action='store_true', help='Disable random matrix')

    args = parser.parse_args()

    logger.info("🚀 MATRIX_RANDOM_RATING Implementation Test")
    logger.info("=" * 50)

    try:
        if args.enable:
            success = test_batch_config_update()
            if success:
                logger.info("🎲 Random matrix enabled for next batch run")
                logger.info("Run: python batch_processor.py")
                logger.info("Code 00XcmS will use random A5/A6/A7 on matrix pages")

        elif args.disable:
            reset_batch_config()

        else:
            # Run configuration test
            success = test_random_matrix_config()

            if success:
                logger.success("🎉 MATRIX_RANDOM_RATING implementation test PASSED!")
                logger.info("\nNext steps:")
                logger.info("1. python test_random_matrix.py --enable")
                logger.info("2. python batch_processor.py")
                logger.info("3. Check logs for 'Random matrix rating enabled'")
            else:
                logger.error("❌ MATRIX_RANDOM_RATING implementation test FAILED!")

    except KeyboardInterrupt:
        logger.info("⏸️  Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()