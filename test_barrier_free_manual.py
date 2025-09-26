#!/usr/bin/env python3
"""
Manual Barrier-Free Test Script
Opens browser, logs into survey, and waits for manual navigation to inclusion page
"""

import sys
import os
import time
import json
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.smart_playback_system import SmartPlaybackSystem

class ManualBarrierFreeTest:
    """Test barrier-free exception with manual navigation"""

    def __init__(self, access_code: str = "00XhkO"):
        self.access_code = access_code
        self.driver = None
        self.playback_system = None

        # Load config
        with open('config/batch_config.json', 'r') as f:
            self.config = json.load(f)

    def create_browser(self) -> webdriver.Chrome:
        """Create Chrome browser with GUI"""
        chrome_options = webdriver.ChromeOptions()

        # GUI mode - no headless!
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.maximize_window()

        logger.info("🌐 Browser opened in GUI mode")
        return driver

    def login_to_survey(self) -> bool:
        """Handle survey login"""
        try:
            base_url = self.config['survey_config']['base_url']
            survey_selector = self.config['survey_config']['survey_selector']
            code_input_selector = self.config['survey_config']['code_input_selector']
            access_code_submit_selector = self.config['survey_config']['access_code_submit_selector']

            # Step 1: Navigate to main page
            logger.info(f"🔗 Navigating to {base_url}")
            self.driver.get(base_url)
            time.sleep(3)

            # Step 2: Click survey link
            logger.info("🔍 Looking for survey link...")
            wait = WebDriverWait(self.driver, 10)
            survey_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, survey_selector)))

            logger.info(f"✅ Found survey link: {survey_link.text[:50]}...")
            survey_link.click()
            time.sleep(3)

            # Step 3: Enter access code
            logger.info(f"🔑 Entering access code: {self.access_code}")
            code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, code_input_selector)))
            code_input.clear()
            code_input.send_keys(self.access_code)
            time.sleep(1)

            # Step 4: Submit access code
            logger.info("📤 Submitting access code...")
            submit_button = self.driver.find_element(By.CSS_SELECTOR, access_code_submit_selector)
            submit_button.click()
            time.sleep(3)

            # Verify login
            current_url = self.driver.current_url
            if "592479" in current_url:
                logger.success(f"✅ Successfully logged in to survey with code: {self.access_code}")
                return True
            else:
                logger.error(f"❌ Login failed - unexpected URL: {current_url}")
                return False

        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False

    def wait_for_manual_navigation(self):
        """Wait for user to manually navigate to inclusion page"""
        print("\n" + "="*60)
        print("🎯 MANUAL NAVIGATION REQUIRED")
        print("="*60)
        print("1. Manually navigate through the survey pages")
        print("2. Stop when you reach an INCLUSION page (inkluze)")
        print("3. Look for matrix questions with barrier-free topics")
        print("4. Press ENTER when ready to test barrier-free detection")
        print("="*60)

        input("⏸️  Press ENTER when you're on the inclusion page to test...")

        # Get current page info
        current_url = self.driver.current_url
        page_source = self.driver.page_source[:500] + "..."

        logger.info(f"📍 Current URL: {current_url}")
        logger.info("🧪 Starting barrier-free detection test...")

    def test_barrier_free_detection(self):
        """Test barrier-free exception logic"""
        try:
            # Initialize SmartPlaybackSystem with existing browser
            self.playback_system = SmartPlaybackSystem()
            self.playback_system.driver = self.driver

            # Get page identification
            page_id = self.playback_system.page_identifier.get_page_id(self.driver)
            logger.info(f"📄 Page identified: {page_id}")

            # Test if page matches inclusion pattern
            strategy = self.playback_system.get_page_strategy(page_id)
            logger.info(f"🎯 Strategy selected: {strategy.get('pattern', 'UNKNOWN')}")
            logger.info(f"📝 Description: {strategy.get('description', 'No description')}")

            if strategy.get('pattern') == 'INCLUSION_MIXED_STRATEGY':
                logger.success("🎉 INCLUSION PAGE DETECTED!")

                print("\n" + "="*60)
                print("🧪 TESTING BARRIER-FREE DETECTION")
                print("="*60)
                print("The script will now test barrier-free detection:")
                print("- Barrier-free questions should get A1 (Rozhodně nesouhlasím)")
                print("- Other questions should get A6 (Souhlasím)")
                print("="*60)

                confirm = input("🚀 Execute barrier-free test? (y/N): ").lower()
                if confirm == 'y':
                    # Execute the strategy
                    result = self.playback_system.execute_page_strategy(strategy)

                    if result:
                        logger.success("✅ Barrier-free strategy executed successfully!")
                        print("\n🔍 Check the page to verify:")
                        print("- Questions with 'bezbariérová', 'přístupnost', etc. should have A1 selected")
                        print("- Other questions should have A6 selected")
                    else:
                        logger.error("❌ Barrier-free strategy failed")
                else:
                    logger.info("⏸️  Test cancelled by user")
            else:
                logger.warning("⚠️  This doesn't appear to be an inclusion page")
                logger.info(f"Strategy pattern: {strategy.get('pattern')}")

                # Show what keywords were found
                if hasattr(self.playback_system, 'strategy_config'):
                    special_cases = self.playback_system.strategy_config.get('special_cases', {})
                    barrier_config = special_cases.get('barrier_free_exception', {})
                    patterns = barrier_config.get('page_patterns', [])
                    logger.info(f"Looking for patterns: {patterns}")
                    logger.info(f"In page title: '{page_id[:100]}...'")

        except Exception as e:
            logger.error(f"❌ Test failed: {e}")

    def run_test(self):
        """Run complete manual test"""
        try:
            logger.info("🚀 Starting Manual Barrier-Free Test")

            # Create browser and login
            self.driver = self.create_browser()

            if not self.login_to_survey():
                logger.error("❌ Login failed, aborting test")
                return

            # Wait for manual navigation
            self.wait_for_manual_navigation()

            # Test barrier-free detection
            self.test_barrier_free_detection()

            print("\n" + "="*60)
            print("🔚 TEST COMPLETED")
            print("="*60)
            print("Browser will stay open for manual inspection.")
            print("Close browser window when done.")

            # Keep browser open
            input("Press ENTER to close browser...")

        except KeyboardInterrupt:
            logger.info("⏸️  Test interrupted by user")
        except Exception as e:
            logger.error(f"❌ Test error: {e}")
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    logger.info("🔚 Browser closed")
                except:
                    pass

def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Manual Barrier-Free Test')
    parser.add_argument('--code', default='00XhkO', help='Access code to use')

    args = parser.parse_args()

    test = ManualBarrierFreeTest(access_code=args.code)
    test.run_test()

if __name__ == "__main__":
    main()