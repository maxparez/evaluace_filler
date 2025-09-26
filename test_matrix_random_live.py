#!/usr/bin/env python3
"""
Live Test Script for MATRIX_RANDOM_RATING Strategy
Tests the random matrix strategy on actual browser with detailed logging
"""

import sys
import os
import json
import time
import random
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from src.smart_playback_system import SmartPlaybackSystem

class MatrixRandomTester:
    """Test MATRIX_RANDOM_RATING strategy on live browser"""

    def __init__(self):
        self.driver = None
        self.playback_system = None

    def setup_browser(self):
        """Setup Chrome browser for testing"""
        logger.info("🚀 Setting up browser for matrix random testing")

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.success("✅ Browser setup complete")

    def setup_playback_system(self, enable_random=True):
        """Setup SmartPlaybackSystem with random matrix enabled"""
        logger.info(f"🔧 Setting up SmartPlaybackSystem (random_matrix: {enable_random})")

        self.playback_system = SmartPlaybackSystem()
        self.playback_system.driver = self.driver

        # Enable or disable random matrix strategy
        if hasattr(self.playback_system, 'strategy_config') and 'default_strategies' in self.playback_system.strategy_config:
            default_strategies = self.playback_system.strategy_config['default_strategies']

            if 'MATRIX_RANDOM_RATING' in default_strategies:
                default_strategies['MATRIX_RANDOM_RATING']['enabled'] = enable_random
                default_strategies['MATRIX_RANDOM_RATING']['priority'] = 10 if enable_random else 0

                logger.success(f"✅ MATRIX_RANDOM_RATING {'enabled' if enable_random else 'disabled'}")

                # Lower priority of fixed strategies when random is enabled
                if enable_random:
                    for strategy_name in ['MATRIX_RATING_A6', 'MATRIX_RATING_A5']:
                        if strategy_name in default_strategies:
                            default_strategies[strategy_name]['priority'] = 0
                            logger.info(f"🔽 Lowered {strategy_name} priority to 0")
            else:
                logger.error("❌ MATRIX_RANDOM_RATING strategy not found!")
                return False
        else:
            logger.error("❌ Strategy config not found!")
            return False

        return True

    def navigate_to_survey(self):
        """Navigate to survey and enter access code"""
        logger.info("🌐 Navigating to survey...")

        try:
            # Load config
            with open('config/batch_config.json', 'r') as f:
                config = json.load(f)

            base_url = config['survey_config']['base_url']
            survey_selector = config['survey_config']['survey_selector']
            code_input_selector = config['survey_config']['code_input_selector']
            access_code_submit_selector = config['survey_config']['access_code_submit_selector']
            access_code = config['access_codes'][1]  # Use second test code

            # Navigate to main page
            logger.info(f"📍 Opening {base_url}")
            self.driver.get(base_url)
            time.sleep(3)

            # Click survey link
            wait = WebDriverWait(self.driver, 10)
            survey_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, survey_selector)))
            logger.info(f"🔗 Clicking survey link: {survey_link.text[:50]}...")
            survey_link.click()
            time.sleep(3)

            # Enter access code
            logger.info(f"🔑 Entering access code: {access_code}")
            code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, code_input_selector)))
            code_input.clear()
            code_input.send_keys(access_code)
            time.sleep(1)

            # Submit code
            submit_button = self.driver.find_element(By.CSS_SELECTOR, access_code_submit_selector)
            submit_button.click()
            time.sleep(3)

            logger.success("✅ Survey navigation complete")
            return True

        except Exception as e:
            logger.error(f"❌ Survey navigation failed: {e}")
            return False

    def find_matrix_page(self, max_pages=15):
        """Find a matrix question page by advancing through survey"""
        logger.info(f"🔍 Looking for matrix page (max {max_pages} pages)...")

        for page_num in range(1, max_pages + 1):
            try:
                logger.info(f"📄 Checking page {page_num}")

                # Get current page info
                page_source = self.driver.page_source.lower()
                current_url = self.driver.current_url

                # Check if this is a matrix page
                if self.is_matrix_page():
                    logger.success(f"🎯 Found matrix page on page {page_num}!")
                    return True

                # Check for final pages
                if any(keyword in page_source for keyword in ["děkujeme", "dokončeno", "completed", "thank"]):
                    logger.warning("⚠️ Reached end of survey without finding matrix page")
                    return False

                # Navigate to next page
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "#ls-button-submit")
                    if next_button and next_button.is_enabled():
                        logger.info("➡️ Moving to next page...")
                        next_button.click()
                        time.sleep(2)
                    else:
                        logger.warning("⚠️ Next button not available")
                        return False

                except Exception as nav_e:
                    logger.error(f"❌ Navigation failed: {nav_e}")
                    return False

            except Exception as e:
                logger.error(f"❌ Error on page {page_num}: {e}")
                return False

        logger.warning(f"⚠️ No matrix page found in {max_pages} pages")
        return False

    def is_matrix_page(self):
        """Check if current page is a matrix question"""
        try:
            # Look for matrix question indicators
            matrix_indicators = [
                ".question-text .ls-label-question",  # Main question text
                "table.table",  # Matrix table
                "input[type='radio'][id*='answer']",  # Radio buttons
                ".ls-answers"  # Answer container
            ]

            found_indicators = 0
            for selector in matrix_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        found_indicators += 1
                        logger.debug(f"✓ Found indicator: {selector} ({len(elements)} elements)")
                except:
                    pass

            # Also check page text for matrix keywords
            page_source = self.driver.page_source.lower()
            matrix_keywords = [
                "uveďte, prosím, do jaké míry",
                "souhlasíte s následuj",
                "hodnocení",
                "matrix"
            ]

            keyword_matches = sum(1 for keyword in matrix_keywords if keyword in page_source)

            logger.debug(f"🔍 Matrix indicators: {found_indicators}/4, Keywords: {keyword_matches}/4")

            return found_indicators >= 2 or keyword_matches >= 1

        except Exception as e:
            logger.error(f"❌ Error checking matrix page: {e}")
            return False

    def test_random_strategy(self, test_runs=3):
        """Test the MATRIX_RANDOM_RATING strategy multiple times"""
        logger.info(f"🧪 Testing MATRIX_RANDOM_RATING strategy ({test_runs} runs)")

        results = []

        for run in range(1, test_runs + 1):
            logger.info(f"\n--- TEST RUN {run}/{test_runs} ---")

            try:
                # Get current page title for strategy selection
                try:
                    page_title_element = self.driver.find_element(By.CSS_SELECTOR, ".question-text .ls-label-question")
                    page_title = page_title_element.text if page_title_element else ""
                    logger.info(f"📄 Page title: '{page_title[:100]}...'")
                except:
                    page_title = ""
                    logger.warning("⚠️ Could not get page title, using empty string")

                # Get page strategy
                strategy = self.playback_system.get_page_strategy(page_title)
                logger.info(f"📊 Selected strategy: {strategy.get('pattern', 'UNKNOWN')}")

                if strategy.get('pattern') != 'MATRIX_RANDOM_RATING':
                    logger.warning(f"⚠️ Expected MATRIX_RANDOM_RATING, got {strategy.get('pattern')}")
                    results.append({'run': run, 'success': False, 'reason': 'Wrong strategy selected'})
                    continue

                # Execute strategy
                logger.info("🎲 Executing MATRIX_RANDOM_RATING strategy...")
                success = self.playback_system.execute_matrix_random_strategy(strategy)

                if success:
                    logger.success(f"✅ Run {run}: Strategy executed successfully")

                    # Check what was actually selected
                    selected_ratings = self.get_selected_ratings()
                    logger.info(f"📍 Selected ratings: {selected_ratings}")

                    results.append({
                        'run': run,
                        'success': True,
                        'selected_ratings': selected_ratings,
                        'unique_ratings': len(set(selected_ratings)) if selected_ratings else 0
                    })
                else:
                    logger.error(f"❌ Run {run}: Strategy execution failed")
                    results.append({'run': run, 'success': False, 'reason': 'Execution failed'})

                # Wait between runs
                if run < test_runs:
                    time.sleep(2)

            except Exception as e:
                logger.error(f"❌ Run {run} failed with exception: {e}")
                results.append({'run': run, 'success': False, 'reason': str(e)})

        return results

    def get_selected_ratings(self):
        """Get list of currently selected ratings"""
        try:
            selected_radios = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']:checked")
            ratings = []

            for radio in selected_radios:
                radio_id = radio.get_attribute('id') or ''
                # Extract rating from ID (e.g., A5, A6, A7)
                if '-A' in radio_id:
                    rating = radio_id.split('-A')[-1]
                    if rating in ['5', '6', '7']:
                        ratings.append(f'A{rating}')

            return ratings

        except Exception as e:
            logger.error(f"❌ Error getting selected ratings: {e}")
            return []

    def analyze_results(self, results):
        """Analyze test results"""
        logger.info("\n" + "="*50)
        logger.info("📊 MATRIX RANDOM STRATEGY TEST RESULTS")
        logger.info("="*50)

        successful_runs = [r for r in results if r['success']]
        success_rate = len(successful_runs) / len(results) * 100 if results else 0

        logger.info(f"🎯 Success Rate: {success_rate:.1f}% ({len(successful_runs)}/{len(results)})")

        if successful_runs:
            all_ratings = []
            for result in successful_runs:
                if 'selected_ratings' in result:
                    all_ratings.extend(result['selected_ratings'])

            if all_ratings:
                rating_counts = {}
                for rating in all_ratings:
                    rating_counts[rating] = rating_counts.get(rating, 0) + 1

                logger.info(f"📈 Rating Distribution:")
                for rating, count in sorted(rating_counts.items()):
                    percentage = count / len(all_ratings) * 100
                    logger.info(f"   {rating}: {count} times ({percentage:.1f}%)")

                # Check if distribution seems random
                unique_ratings = len(rating_counts)
                if unique_ratings >= 2:
                    logger.success("✅ Good randomness - multiple ratings used")
                else:
                    logger.warning("⚠️ Poor randomness - only one rating type used")

        # Show failed runs
        failed_runs = [r for r in results if not r['success']]
        if failed_runs:
            logger.warning(f"❌ Failed runs: {len(failed_runs)}")
            for result in failed_runs:
                logger.warning(f"   Run {result['run']}: {result.get('reason', 'Unknown error')}")

        return success_rate >= 70  # Consider 70%+ success rate as passing

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🧹 Browser cleanup complete")
            except:
                logger.warning("⚠️ Browser cleanup failed")

def main():
    """Main test execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Live MATRIX_RANDOM_RATING Strategy Tester')
    parser.add_argument('--runs', type=int, default=3, help='Number of test runs (default: 3)')
    parser.add_argument('--max-search', type=int, default=15, help='Max pages to search for matrix (default: 15)')
    parser.add_argument('--no-random', action='store_true', help='Test without random strategy (control test)')

    args = parser.parse_args()

    tester = MatrixRandomTester()

    try:
        logger.info("🚀 MATRIX RANDOM STRATEGY LIVE TEST")
        logger.info("=" * 50)

        # Setup
        logger.info("1️⃣ Setting up browser...")
        tester.setup_browser()

        logger.info("2️⃣ Setting up playback system...")
        if not tester.setup_playback_system(enable_random=not args.no_random):
            logger.error("❌ Playback system setup failed")
            return

        logger.info("3️⃣ Navigating to survey...")
        if not tester.navigate_to_survey():
            logger.error("❌ Survey navigation failed")
            return

        logger.info("4️⃣ Finding matrix page...")
        if not tester.find_matrix_page(args.max_search):
            logger.error("❌ Could not find matrix page")
            return

        logger.info("5️⃣ Testing strategy...")
        results = tester.test_random_strategy(args.runs)

        logger.info("6️⃣ Analyzing results...")
        success = tester.analyze_results(results)

        if success:
            logger.success("🎉 MATRIX RANDOM STRATEGY TEST PASSED!")
        else:
            logger.error("❌ MATRIX RANDOM STRATEGY TEST FAILED!")

    except KeyboardInterrupt:
        logger.info("⏸️ Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()