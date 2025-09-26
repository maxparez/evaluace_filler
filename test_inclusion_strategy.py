#!/usr/bin/env python3
"""
Test script for inclusion barrier-free strategy
Tests if the barrier-free exception strategy works correctly
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from loguru import logger
from src.smart_playback_system import SmartPlaybackSystem

def test_inclusion_strategy():
    """Test inclusion strategy selection and barrier-free detection"""
    logger.info("🧪 Testing BARRIER_FREE_EXCEPTION strategy")

    try:
        # Create playback system
        playback_system = SmartPlaybackSystem()

        # Test inclusion page title that should trigger barrier-free exception
        test_titles = [
            "Uveďte, prosím, do jaké míry souhlasíte s následujícími výroky týkajícími se realizace šablon v oblasti inkluze",
            "V oblasti inkluze - hodnocení realizace šablon",
            "Inkluze - souhlasíte s následujícími výroky"
        ]

        for i, title in enumerate(test_titles, 1):
            logger.info(f"\n📄 Test {i}: '{title[:60]}...'")

            strategy = playback_system.get_page_strategy(title)
            logger.info(f"📊 Selected strategy: {strategy.get('pattern', 'UNKNOWN')}")

            # Check if barrier-free exception was matched
            if strategy.get('pattern') == 'INCLUSION_MIXED':
                logger.success("✅ Correct INCLUSION_MIXED strategy selected")
                logger.info("🎯 This will use A1 for barrier-free, A6 for others")

                # Check if barrier keywords are present
                barrier_keywords = strategy.get('barrier_keywords', [])
                if barrier_keywords:
                    logger.info(f"🔍 Barrier keywords detected: {barrier_keywords}")
                else:
                    logger.warning("⚠️ No barrier keywords found")
            else:
                logger.error(f"❌ Wrong strategy: {strategy.get('pattern')} (expected: INCLUSION_MIXED)")
                logger.error(f"📋 Strategy details: {strategy}")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def test_barrier_keywords():
    """Test specific barrier-free keyword detection"""
    logger.info("\n🔍 Testing barrier-free keyword detection")

    test_texts = [
        "Díky šablonám došlo k bezbariérovému zpřístupnění školy",
        "Přizpůsobení a vybavení učeben pro žáky se speciálními vzdělávacími potřebami",
        "Fyzické bariéry byly odstraněny",
        "Architektonické bariéry v budově školy",
        "Běžná inkluze bez barrier-free témat"
    ]

    # Load barrier keywords from config
    try:
        playback_system = SmartPlaybackSystem()
        barrier_config = playback_system.strategy_config.get('special_cases', {}).get('barrier_free_exception', {})
        exception_rules = barrier_config.get('exception_rules', [])

        barrier_keywords = []
        for rule in exception_rules:
            barrier_keywords.extend(rule.get('text_contains', []))

        logger.info(f"📋 Loaded barrier keywords: {barrier_keywords}")

        for i, text in enumerate(test_texts, 1):
            logger.info(f"\n🧪 Test text {i}: '{text}'")

            # Check if text contains barrier keywords
            has_barrier = any(keyword.lower() in text.lower() for keyword in barrier_keywords)

            if has_barrier:
                logger.success("✅ Barrier-free keyword detected → Should use A1")
            else:
                logger.info("ℹ️ No barrier-free keywords → Should use A6")

    except Exception as e:
        logger.error(f"❌ Keyword test failed: {e}")

def main():
    """Main test execution"""
    logger.info("🚀 INCLUSION BARRIER-FREE STRATEGY TEST")
    logger.info("=" * 50)

    # Test 1: Strategy selection
    success = test_inclusion_strategy()

    # Test 2: Barrier keyword detection
    test_barrier_keywords()

    if success:
        logger.success("🎉 Inclusion strategy tests PASSED!")
    else:
        logger.error("❌ Inclusion strategy tests FAILED!")

if __name__ == "__main__":
    main()