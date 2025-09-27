#!/usr/bin/env python3
"""
Batch Survey Processor - Process multiple surveys with clean browser sessions
Handles login, code entry, and complete survey automation for multiple access codes
"""
import sys
import os

# --- OPRAVA: TOTO MUSÍ BÝT NA SAMOTNÉM ZAČÁTKU ---
# Tento blok přidá adresář 'src' do cesty, kde Python hledá moduly.
# Je to jediná potřebná úprava systémové cesty.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
# --- KONEC OPRAVY ---

# Nyní všechny ostatní importy
import json
import time
import random
import tempfile
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Importy z našeho adresáře 'src', které nyní budou fungovat
from config import Config
from smart_playback_system import SmartPlaybackSystem
from utils.status_indicator_manager import StatusIndicatorManager

class BatchSurveyProcessor:
    """
    Batch processor for multiple surveys with clean browser sessions

    Features:
    - Clean browser startup/shutdown for each survey
    - Automatic login and code entry
    - Complete survey automation
    - Progress tracking and error handling
    - Configurable user profiles and delays
    """

    def __init__(self, config_file: str = "config/batch_config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()

        # Setup logging
        self.setup_logging()

        # Batch tracking
        self.batch_stats = {
            "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": None,
            "end_time": None,
            "total_surveys": 0,
            "completed_surveys": 0,
            "failed_surveys": 0,
            "survey_results": []
        }

        logger.info(f"BatchSurveyProcessor initialized - Batch ID: {self.batch_stats['batch_id']}")

    def load_config(self):
        """Load batch configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logger.info(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def setup_logging(self):
        """Configure logging for batch processing"""
        log_level = self.config.get('batch_settings', {}).get('log_level', 'INFO')

        # Create logs directory
        os.makedirs('logs', exist_ok=True)

        # Add batch-specific log file
        batch_log_file = f"logs/batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logger.add(batch_log_file, level=log_level, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

        logger.info(f"Batch logging setup complete - Level: {log_level}")

    def create_clean_browser(self) -> webdriver.Chrome:
        """Create a fresh Chrome browser instance"""
        chrome_options = webdriver.ChromeOptions()

        # Use cross-platform temporary user data directory for clean session
        random_suffix = f"{int(time.time())}_{random.randint(1000,9999)}"
        temp_base = Path(tempfile.gettempdir()) / f"chrome_batch_{random_suffix}"
        chrome_options.add_argument(f"--user-data-dir={temp_base}")

        # Window size and position from config
        chrome_options.add_argument(f"--window-size={Config.BROWSER_WINDOW_SIZE}")
        chrome_options.add_argument(f"--window-position={Config.BROWSER_WINDOW_POSITION}")

        # Standard options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Use webdriver-manager for automatic chromedriver management with Windows path fix
        try:
            # Get raw path from webdriver-manager
            raw_path = ChromeDriverManager().install()
            logger.debug(f"webdriver-manager returned path: {raw_path}")

            # --- WINDOWS WORKAROUND FOR PATH BUG ---
            driver_path = Path(raw_path)
            driver_dir = driver_path.parent
            expected_exe_path = driver_dir / "chromedriver.exe"

            logger.debug(f"Checking for expected executable at: {expected_exe_path}")

            if sys.platform == "win32" and expected_exe_path.is_file():
                chromedriver_path = str(expected_exe_path)
                logger.info(f"Using corrected Windows path: {chromedriver_path}")
            else:
                chromedriver_path = raw_path
                logger.debug(f"Using original path: {chromedriver_path}")
            # --- END OF WINDOWS WORKAROUND ---

            service = Service(chromedriver_path)
        except Exception as e:
            logger.error(f"Failed to download ChromeDriver: {e}")
            service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.debug(f"Clean browser created with temp dir: {temp_base}")
        return driver

    def handle_survey_login(self, driver: webdriver.Chrome, access_code: str, batch_status_manager, survey_number: int, total_surveys: int) -> bool:
        """
        Handle complete survey login process
        """
        try:
            base_url = self.config['survey_config']['base_url']
            survey_selector = self.config['survey_config']['survey_selector']
            code_input_selector = self.config['survey_config']['code_input_selector']
            access_code_submit_selector = self.config['survey_config']['access_code_submit_selector']

            logger.info(f"Navigating to {base_url}")
            driver.get(base_url)

            batch_status_manager.set_status_with_progress('running', 1, total_surveys, f'Připojuji se k systému - dotazník {access_code}')
            time.sleep(3)

            logger.info("Looking for survey link...")
            wait = WebDriverWait(driver, 10)
            survey_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, survey_selector)))
            logger.info(f"Found survey link: {survey_link.text[:50]}...")
            batch_status_manager.set_status_with_progress('processing', survey_number, total_surveys, f'Otevírám dotazník - {access_code}')
            survey_link.click()
            time.sleep(3)

            logger.info(f"Entering access code: {access_code}")
            batch_status_manager.set_status_with_progress('processing', survey_number, total_surveys, f'Přihlašuji se pomocí kódu - {access_code}')
            code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, code_input_selector)))
            code_input.clear()
            code_input.send_keys(access_code)
            time.sleep(1)

            logger.info("Submitting access code...")
            submit_button = driver.find_element(By.CSS_SELECTOR, access_code_submit_selector)
            submit_button.click()
            time.sleep(3)

            current_url = driver.current_url
            if "592479" in current_url:
                logger.success(f"Successfully logged in to survey with code: {access_code}")
                batch_status_manager.set_status_with_progress('running', survey_number, total_surveys, f'Úspěšně přihlášen - zahajuji automatické vyplňování')
                return True
            else:
                logger.error(f"Login failed - unexpected URL: {current_url}")
                batch_status_manager.set_status_with_progress('error', survey_number, total_surveys, f'Chyba přihlášení - neplatný kód {access_code}')
                return False
        except Exception as e:
            logger.error(f"Login failed for code {access_code}: {e}")
            try:
                current_url = driver.current_url
                page_title = driver.title
                logger.debug(f"Current URL during error: {current_url}")
                logger.debug(f"Page title during error: {page_title}")
            except:
                pass
            if 'batch_status_manager' in locals():
                batch_status_manager.set_status_with_progress('error', survey_number, total_surveys, f'Chyba přihlášení: {str(e)[:30]}...')
            return False

    def get_birth_year(self) -> str:
        """Get birth year from config"""
        profile_config = self.config.get('user_profile', {})
        year = profile_config.get('birth_year', 1972)
        logger.debug(f"Using birth year from config: {year}")
        return str(year)

    def process_single_survey(self, access_code: str, survey_number: int = 1, total_surveys: int = 1) -> Dict:
        """Process a single survey with clean browser session"""
        survey_result = {
            "access_code": access_code,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "FAILED",
            "error": None,
            "pages_completed": 0,
            "execution_time_seconds": 0
        }
        driver = None
        try:
            logger.info(f"Starting survey processing for code: {access_code}")
            driver = self.create_clean_browser()
            batch_status_manager = StatusIndicatorManager(driver)
            if not self.handle_survey_login(driver, access_code, batch_status_manager, survey_number, total_surveys):
                raise Exception("Login failed")

            birth_year = self.get_birth_year()
            strategy_file = self.config.get('batch_settings', {}).get('strategy_file', "scenarios/optimized_survey_strategy.json")
            logger.info(f"Using strategy file: {strategy_file}")
            playback_system = SmartPlaybackSystem(strategy_file=strategy_file)
            playback_system.driver = driver
            playback_system.session_stats["start_time"] = datetime.now().isoformat()
            batch_status_manager.set_status_with_progress('running', survey_number, total_surveys, f'Zpracovávám dotazník {access_code}')
            playback_system.user_birth_year = birth_year
            logger.debug(f"Set birth year to {birth_year} for survey processing")

            # ... (rest of the logic for running the survey)

        except Exception as e:
            survey_result["status"] = "FAILED"
            survey_result["error"] = str(e)
            logger.error(f"Critical error processing survey {access_code}: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                    logger.debug("Browser cleaned up successfully")
                except:
                    logger.warning("Failed to cleanup browser")
            
            survey_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(survey_result["start_time"])
            end_time = datetime.fromisoformat(survey_result["end_time"])
            survey_result["execution_time_seconds"] = (end_time - start_time).total_seconds()
            
            delay = self.config.get('batch_settings', {}).get('delay_between_surveys', 5)
            if delay > 0:
                logger.info(f"Waiting {delay} seconds before next survey...")
                time.sleep(delay)
        return survey_result

    # ... (the rest of the class methods like process_batch, generate_batch_report)

def main():
    """Main execution function"""
    import argparse
    parser = argparse.ArgumentParser(description='Batch Survey Processor')
    parser.add_argument('--config', default='config/batch_config.json', help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true', help='Test configuration without processing surveys')
    args = parser.parse_args()
    try:
        processor = BatchSurveyProcessor(args.config)
        if args.dry_run:
            logger.info("DRY RUN MODE - Configuration test")
            return
        processor.process_batch()
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
