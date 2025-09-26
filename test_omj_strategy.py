#!/usr/bin/env python3
"""
Quick test script for OMJ (odlišný mateřský jazyk) strategy
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from loguru import logger
from src.smart_playback_system import SmartPlaybackSystem

def test_omj_strategy():
    """Test OMJ strategy selection and configuration"""
    logger.info("🧪 Testing RADIO_OMJ_NE strategy")

    try:
        # Create playback system
        playbook_system = SmartPlaybackSystem()

        # Test page titles that should match
        test_titles = [
            "Navštěvují Vaší školu děti s odlišným mateřským jazykem",
            "Navštěvují Vaši školu děti s odlišným mateřským jazykem (děti s OMJ)?",
            "děti s OMJ potřebují jazykovou podporu"
        ]

        for title in test_titles:
            logger.info(f"\n📄 Testing title: '{title[:60]}...'")

            strategy = playbook_system.get_page_strategy(title)
            logger.info(f"📊 Selected strategy: {strategy.get('pattern', 'UNKNOWN')}")

            if strategy.get('pattern') == 'RADIO_CHOICE':
                answer = strategy.get('selected_answer', '')
                logger.info(f"🎯 Selected answer: '{answer}'")

                if answer == "Ne":
                    logger.success("✅ Correct OMJ strategy selected")
                else:
                    logger.warning(f"⚠️ Wrong answer: '{answer}' (expected: 'Ne')")
            else:
                logger.error(f"❌ Wrong strategy type: {strategy.get('pattern')}")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def main():
    """Main test execution"""
    logger.info("🚀 OMJ STRATEGY TEST")
    logger.info("=" * 30)

    success = test_omj_strategy()

    if success:
        logger.success("🎉 OMJ strategy test PASSED!")
    else:
        logger.error("❌ OMJ strategy test FAILED!")

if __name__ == "__main__":
    main()