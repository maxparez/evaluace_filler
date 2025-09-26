#!/usr/bin/env python3
"""
Debug Login Process
Test specific access code login to identify issues
"""

import sys
import time
import json

# Add src to Python path
sys.path.insert(0, 'src')

from browser_manager import BrowserManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger

def test_login_process(access_code="00XhkO"):
    """Test login process with specific access code"""

    print(f"🧪 TESTING LOGIN PROCESS FOR CODE: {access_code}")
    print("=" * 60)

    try:
        # Load config
        with open('config/batch_config.json', 'r') as f:
            config = json.load(f)

        base_url = config['survey_config']['base_url']
        survey_selector = config['survey_config']['survey_selector']
        code_input_selector = config['survey_config']['code_input_selector']
        access_code_submit_selector = config['survey_config']['access_code_submit_selector']

        print(f"Base URL: {base_url}")
        print(f"Survey selector: {survey_selector}")
        print(f"Code input selector: {code_input_selector}")
        print(f"Submit selector: {access_code_submit_selector}")
        print()

        # Connect to browser
        print("1️⃣ Connecting to browser...")
        browser_manager = BrowserManager()
        driver = browser_manager.get_or_create_browser()

        if not driver:
            print("❌ Failed to connect to browser")
            return False

        print("✅ Browser connected")

        # Step 1: Navigate to main page
        print(f"2️⃣ Navigating to {base_url}")
        driver.get(base_url)
        time.sleep(3)

        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")

        # Step 2: Look for survey link
        print("3️⃣ Looking for survey link...")
        wait = WebDriverWait(driver, 10)

        try:
            survey_links = driver.find_elements(By.CSS_SELECTOR, survey_selector)
            print(f"Found {len(survey_links)} elements with survey selector")

            if survey_links:
                survey_link = survey_links[0]
                print(f"Survey link text: '{survey_link.text}'")
                print(f"Survey link href: {survey_link.get_attribute('href')}")

                # Wait for clickable and click
                survey_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, survey_selector)))
                survey_link.click()
                time.sleep(3)

                print(f"After click - URL: {driver.current_url}")
                print(f"After click - Title: {driver.title}")
            else:
                print("❌ No survey links found!")
                return False

        except Exception as e:
            print(f"❌ Error finding survey link: {e}")
            return False

        # Step 3: Look for access code input
        print("4️⃣ Looking for access code input...")

        try:
            code_inputs = driver.find_elements(By.CSS_SELECTOR, code_input_selector)
            print(f"Found {len(code_inputs)} access code input fields")

            if code_inputs:
                code_input = code_inputs[0]
                print(f"Input field type: {code_input.get_attribute('type')}")
                print(f"Input field placeholder: {code_input.get_attribute('placeholder')}")
                print(f"Input field name: {code_input.get_attribute('name')}")

                # Wait for input to be present and enter code
                code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, code_input_selector)))
                code_input.clear()
                code_input.send_keys(access_code)
                print(f"✅ Entered access code: {access_code}")

                # Verify the value was entered
                entered_value = code_input.get_attribute('value')
                print(f"Value in field: '{entered_value}'")

                time.sleep(1)
            else:
                print("❌ No access code input fields found!")
                return False

        except Exception as e:
            print(f"❌ Error with access code input: {e}")
            return False

        # Step 4: Look for submit button
        print("5️⃣ Looking for submit button...")

        try:
            submit_buttons = driver.find_elements(By.CSS_SELECTOR, access_code_submit_selector)
            print(f"Found {len(submit_buttons)} submit buttons")

            if submit_buttons:
                submit_button = submit_buttons[0]
                print(f"Submit button text: '{submit_button.text}'")
                print(f"Submit button type: {submit_button.get_attribute('type')}")
                print(f"Submit button enabled: {submit_button.is_enabled()}")

                print("Clicking submit button...")
                submit_button.click()
                time.sleep(5)  # Wait longer for redirect

                print(f"After submit - URL: {driver.current_url}")
                print(f"After submit - Title: {driver.title}")

            else:
                print("❌ No submit buttons found!")
                return False

        except Exception as e:
            print(f"❌ Error with submit button: {e}")
            return False

        # Step 5: Check result
        print("6️⃣ Checking login result...")

        current_url = driver.current_url
        page_source = driver.page_source

        print(f"Final URL: {current_url}")

        # Check for success indicators
        if "592479" in current_url:
            print("✅ LOGIN SUCCESSFUL - Found survey ID in URL")
            return True
        elif "index.php" in current_url and len(current_url) > len(base_url) + 20:
            print("✅ LOGIN SUCCESSFUL - Redirected to survey page")
            return True
        else:
            print("❌ LOGIN FAILED - No survey redirect detected")

            # Look for error messages
            error_selectors = [".alert", ".error", ".warning", "[class*='error']", "[class*='warning']", ".message"]
            for selector in error_selectors:
                try:
                    error_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in error_elements:
                        if elem.is_displayed() and elem.text.strip():
                            print(f"Error message: {elem.text}")
                except:
                    pass

            return False

    except Exception as e:
        print(f"💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_login_process()
    print(f"\n🔍 Login test {'PASSED' if success else 'FAILED'}")