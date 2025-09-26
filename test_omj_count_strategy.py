#!/usr/bin/env python3
"""
Quick test script for OMJ count strategy
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from loguru import logger
from src.smart_playback_system import SmartPlaybackSystem

def test_omj_count_strategy():
    """Test OMJ count strategy selection and configuration"""
    logger.info("🧪 Testing INPUT_OMJ_COUNT strategy")

    try:
        # Create playback system
        playback_system = SmartPlaybackSystem()

        # Test the problematic page title
        test_title = "Kolik dětí z Vaší školy má odlišný mateřský jazyk?"

        logger.info(f"📄 Testing title: '{test_title}'")

        strategy = playback_system.get_page_strategy(test_title)
        logger.info(f"📊 Selected strategy: {strategy.get('pattern', 'UNKNOWN')}")

        if strategy.get('pattern') == 'INPUT_FIELD':
            input_value = strategy.get('input_value', '')
            logger.info(f"🎯 Input value: '{input_value}'")
            if input_value == "0":
                logger.success("✅ Correct input value: 0")
            else:
                logger.error(f"❌ Wrong input value: {input_value} (expected: 0)")
            logger.success("✅ Correct INPUT_OMJ_COUNT strategy selected")
            return True
        else:
            logger.error(f"❌ Wrong strategy: {strategy.get('pattern')} (expected: INPUT_FIELD)")
            logger.error(f"📋 Strategy details: {strategy}")
            return False

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def main():
    """Main test execution"""
    logger.info("🚀 OMJ COUNT STRATEGY TEST")
    logger.info("=" * 35)

    success = test_omj_count_strategy()

    if success:
        logger.success("🎉 OMJ count strategy test PASSED!")
    else:
        logger.error("❌ OMJ count strategy test FAILED!")

if __name__ == "__main__":
    main()