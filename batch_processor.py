#!/usr/bin/env python3
"""
Batch Survey Processor - Process multiple surveys with clean browser sessions
Handles login, code entry, and complete survey automation for multiple access codes
"""

import sys
import os
import json
import time
import random
import tempfile
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# --- OPRAVA: TOTO MUSÍ BÝT NA SAMOTNÉM ZAČÁTKU ---
# Tento blok přidá adresář 'src' do cesty, kde Python hledá moduly.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
# --- KONEC OPRAVY ---

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

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

        # Use webdriver-manager for automatic chromedriver management with cross-platform path fix
        try:
            # Get raw path from webdriver-manager
            raw_path = ChromeDriverManager().install()
            logger.debug(f"webdriver-manager returned path: {raw_path}")

            # --- CROSS-PLATFORM WORKAROUND FOR PATH BUG ---
            driver_path = Path(raw_path)
            driver_dir = driver_path.parent

            if sys.platform == "win32":
                expected_exe_path = driver_dir / "chromedriver.exe"
                logger.debug(f"Windows: Checking for executable at: {expected_exe_path}")
                if expected_exe_path.is_file():
                    chromedriver_path = str(expected_exe_path)
                    logger.info(f"Using corrected Windows path: {chromedriver_path}")
                else:
                    chromedriver_path = raw_path
                    logger.debug(f"Using original Windows path: {chromedriver_path}")
            else:
                # Linux/Unix workaround
                expected_exe_path = driver_dir / "chromedriver"
                logger.debug(f"Linux: Checking for executable at: {expected_exe_path}")
                if expected_exe_path.is_file():
                    # Ensure executable permissions on Linux
                    import stat
                    expected_exe_path.chmod(expected_exe_path.stat().st_mode | stat.S_IEXEC)
                    chromedriver_path = str(expected_exe_path)
                    logger.info(f"Using corrected Linux path: {chromedriver_path}")
                else:
                    # Look for chromedriver in subdirectories
                    for subdir in driver_dir.iterdir():
                        if subdir.is_dir() and "chromedriver" in subdir.name:
                            potential_exe = subdir / "chromedriver"
                            if potential_exe.is_file():
                                # Ensure executable permissions on Linux
                                import stat
                                potential_exe.chmod(potential_exe.stat().st_mode | stat.S_IEXEC)
                                chromedriver_path = str(potential_exe)
                                logger.info(f"Found chromedriver in subdirectory: {chromedriver_path}")
                                break
                    else:
                        chromedriver_path = raw_path
                        logger.warning(f"Using original problematic path: {chromedriver_path}")
            # --- END OF CROSS-PLATFORM WORKAROUND ---

            service = Service(chromedriver_path)
        except Exception as e:
            logger.error(f"Failed to download ChromeDriver: {e}")
            service = Service()

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.debug(f"Clean browser created with temp dir: {temp_base}")
        return driver

    def handle_survey_login(self, driver: webdriver.Chrome, access_code: str, status_manager: StatusIndicatorManager, survey_number: int, total_surveys: int) -> bool:
        """
        Handle complete survey login process
        1. Navigate to main page
        2. Click survey link
        3. Enter access code
        4. Submit to start survey
        """
        try:
            base_url = self.config['survey_config']['base_url']
            survey_selector = self.config['survey_config']['survey_selector']
            code_input_selector = self.config['survey_config']['code_input_selector']
            access_code_submit_selector = self.config['survey_config']['access_code_submit_selector']

            # Step 1: Navigate to main page
            logger.info(f"Navigating to {base_url}")
            driver.get(base_url)
            status_manager.set_status_with_progress('running', survey_number, total_surveys, f'Připojuji se k systému - dotazník {access_code}')
            time.sleep(3)

            # Step 2: Click survey link
            logger.info("Looking for survey link...")
            wait = WebDriverWait(driver, 10)
            survey_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, survey_selector)))

            logger.info(f"Found survey link: {survey_link.text[:50]}...")
            status_manager.set_status_with_progress('processing', survey_number, total_surveys, f'Otevírám dotazník - {access_code}')
            survey_link.click()
            time.sleep(3)

            # Step 3: Enter access code
            logger.info(f"Entering access code: {access_code}")
            status_manager.set_status_with_progress('processing', survey_number, total_surveys, f'Přihlašuji se pomocí kódu - {access_code}')
            code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, code_input_selector)))
            code_input.clear()
            code_input.send_keys(access_code)
            time.sleep(1)

            # Step 4: Submit access code to enter survey
            logger.info("Submitting access code...")
            submit_button = driver.find_element(By.CSS_SELECTOR, access_code_submit_selector)
            submit_button.click()
            time.sleep(3)

            # Verify we're in the survey
            current_url = driver.current_url

            # Check for invalid code error alert
            try:
                error_alert = driver.find_element(By.CSS_SELECTOR, "ul.alert-danger")
                error_text = error_alert.text
                if "není platný" in error_text or "již byl použit" in error_text:
                    logger.error(f"Invalid access code: {access_code}")
                    logger.warning(f"⚠️ Chybová hláška: {error_text}")
                    print(f"\n{'='*70}")
                    print(f"❌ NEPLATNÝ HASH KÓD: {access_code}")
                    print(f"{'='*70}")
                    print(f"Chyba: {error_text}")
                    print("\nProsím zadejte platný hash kód do prohlížeče a stiskněte Enter.")
                    print("Nebo stiskněte Ctrl+C pro přerušení.\n")
                    input("Stiskněte Enter po zadání platného kódu: ")
                    time.sleep(2)
                    current_url = driver.current_url
            except:
                # No error alert found - continue normally
                pass

            if "592479" in current_url:
                logger.success(f"Successfully logged in to survey with code: {access_code}")
                return True
            else:
                logger.error(f"Login failed - unexpected URL: {current_url}")
                return False

        except Exception as e:
            logger.error(f"Login failed for code {access_code}: {e}")
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

            # Create clean browser
            driver = self.create_clean_browser()

            # Initialize status indicator
            status_manager = StatusIndicatorManager(driver)

            # Handle login
            if not self.handle_survey_login(driver, access_code, status_manager, survey_number, total_surveys):
                raise Exception("Login failed")

            # Update user profile for this survey
            birth_year = self.get_birth_year()
            strategy_file = self.config.get('batch_settings', {}).get('strategy_file', "scenarios/optimized_survey_strategy.json")
            logger.info(f"Using strategy file: {strategy_file}")

            # Create SmartPlaybackSystem with strategy file
            playback_system = SmartPlaybackSystem(strategy_file=strategy_file)
            playback_system.driver = driver
            playback_system.status_manager = status_manager
            playback_system.session_stats["start_time"] = datetime.now().isoformat()
            playback_system.user_birth_year = birth_year
            logger.debug(f"Set birth year to {birth_year} for survey processing")

            # Enable random matrix rating if configured
            use_random_matrix = self.config.get('batch_settings', {}).get('random_matrix', False)
            if use_random_matrix and hasattr(playback_system, 'strategy_config'):
                default_strategies = playback_system.strategy_config.get('default_strategies', {})

                # Enable MATRIX_RANDOM_RATING and disable fixed matrix strategies
                if 'MATRIX_RANDOM_RATING' in default_strategies:
                    default_strategies['MATRIX_RANDOM_RATING']['enabled'] = True
                    default_strategies['MATRIX_RANDOM_RATING']['priority'] = 10  # Higher priority than regular matrix
                    logger.info("🎲 Random matrix rating enabled - will use A5/A6/A7 randomly")

                # Lower priority of fixed matrix strategies when random is enabled
                for strategy_name in ['MATRIX_RATING_A6', 'MATRIX_RATING_A5']:
                    if strategy_name in default_strategies:
                        default_strategies[strategy_name]['priority'] = 0  # Lower priority
            else:
                logger.debug("Using fixed matrix ratings (A6/A5)")

            # Execute survey automation using existing browser
            logger.info("Starting automated survey execution...")

            # Skip browser connection - already connected via login
            playback_system.session_stats["start_time"] = datetime.now().isoformat()

            # Call the main survey loop directly, skipping connect_to_browser()
            page_count = 0

            # Set different max_pages based on access code
            if access_code == "00XcmS":
                max_pages = 10  # Test code - only fill few questions
                logger.info("🧪 TEST MODE: Limited to 10 pages for MATRIX_RANDOM_RATING testing")
            else:
                max_pages = 60  # Full survey

            try:
                logger.info("🚀 STARTING SURVEY AUTOMATION WITH EXISTING BROWSER")

                while max_pages is None or page_count < max_pages:
                    page_count += 1
                    logger.info(f"\n--- PAGE {page_count} ---")

                    page_processed = playback_system.process_current_page()

                    if not page_processed:
                        logger.error(f"Failed to process page {page_count}")
                        # Try to continue to next page anyway

                    # Check if final submit was clicked
                    current_url = driver.current_url
                    page_source = driver.page_source

                    # Check for official completion page with specific div
                    try:
                        completion_div = driver.find_element(By.CSS_SELECTOR, "div.completed-wrapper")
                        completion_text_div = driver.find_element(By.CSS_SELECTOR, "div.completed-text")
                        if completion_div and completion_text_div:
                            logger.success("🎉 SURVEY COMPLETED - Official completion page detected!")
                            logger.info("✅ Completion message: 'Vaše odpovědi byly v pořádku uloženy. Děkujeme.'")
                            break
                    except:
                        pass

                    # Fallback: If we just completed final submit, break immediately
                    if ("děkujeme" in page_source.lower() or
                        "dokončeno" in page_source.lower() or
                        "completed" in current_url.lower() or
                        "thank" in page_source.lower()):
                        logger.success("🎉 SURVEY COMPLETED - Thank you page detected!")
                        break

                    # Check for final page pattern that was just processed
                    if page_processed and "konec evaluačního dotazníku" in page_source:
                        logger.success("🎉 SURVEY COMPLETED - Final submit executed!")
                        break

                    time.sleep(1)

                    if page_count >= max_pages:
                        logger.warning(f"Reached maximum pages limit: {max_pages}")
                        break

                playback_system.session_stats["end_time"] = datetime.now().isoformat()
                playback_system.session_stats["pages_processed"] = page_count

                result = {
                    "success": True,
                    "pages_processed": page_count,
                    "session_stats": playback_system.session_stats
                }

            except Exception as e:
                logger.error(f"Survey automation failed: {e}")
                result = {
                    "success": False,
                    "error": str(e),
                    "pages_processed": page_count
                }

            if result['success']:
                survey_result["status"] = "SUCCESS"
                survey_result["pages_completed"] = result.get('pages_processed', 0)
                logger.success(f"Survey completed successfully for code: {access_code}")
            else:
                survey_result["status"] = "FAILED"
                survey_result["error"] = result.get('error', 'Unknown error')
                logger.error(f"Survey failed for code: {access_code} - {survey_result['error']}")

        except Exception as e:
            survey_result["status"] = "FAILED"
            survey_result["error"] = str(e)
            logger.error(f"Survey processing failed for code {access_code}: {e}")

        finally:
            # Always cleanup browser
            if driver:
                try:
                    driver.quit()
                    logger.debug("Browser cleaned up successfully")
                except:
                    logger.warning("Failed to cleanup browser")

            # Calculate execution time
            survey_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(survey_result["start_time"])
            end_time = datetime.fromisoformat(survey_result["end_time"])
            survey_result["execution_time_seconds"] = (end_time - start_time).total_seconds()

            # Add delay between surveys
            delay = self.config.get('batch_settings', {}).get('delay_between_surveys', 5)
            if delay > 0:
                logger.info(f"Waiting {delay} seconds before next survey...")
                time.sleep(delay)

        return survey_result

    def process_batch(self) -> Dict:
        """Process all surveys in batch"""
        self.batch_stats["start_time"] = datetime.now().isoformat()
        access_codes = self.config.get('access_codes', [])

        # Normalize access codes - remove quotes and whitespace, ensure alphanumeric
        normalized_codes = []
        for code in access_codes:
            # Convert to string and strip whitespace and quotes
            normalized = str(code).strip().strip('"').strip("'")
            if normalized:  # Only add non-empty codes
                normalized_codes.append(normalized)
                logger.debug(f"Normalized code: '{code}' -> '{normalized}'")

        if not normalized_codes:
            logger.error("No valid access codes found after normalization")
            return self.batch_stats

        self.batch_stats["total_surveys"] = len(normalized_codes)

        logger.info(f"Starting batch processing - {len(normalized_codes)} surveys to process")

        for i, access_code in enumerate(normalized_codes, 1):
            logger.info(f"Processing survey {i}/{len(normalized_codes)}: {access_code}")

            result = self.process_single_survey(access_code, survey_number=i, total_surveys=len(normalized_codes))
            self.batch_stats["survey_results"].append(result)

            if result["status"] == "SUCCESS":
                self.batch_stats["completed_surveys"] += 1
            else:
                self.batch_stats["failed_surveys"] += 1

            logger.info(f"Survey {i} completed - Status: {result['status']} - Progress: {self.batch_stats['completed_surveys']}/{len(normalized_codes)} successful")

        self.batch_stats["end_time"] = datetime.now().isoformat()

        # Generate final report
        self.generate_batch_report()

        return self.batch_stats

    def generate_batch_report(self):
        """Generate comprehensive batch processing report"""
        # Calculate total execution time
        start_time = datetime.fromisoformat(self.batch_stats["start_time"])
        end_time = datetime.fromisoformat(self.batch_stats["end_time"])
        total_time = (end_time - start_time).total_seconds()

        # Create report
        report = {
            "batch_summary": self.batch_stats,
            "performance_metrics": {
                "total_execution_time_seconds": total_time,
                "average_survey_time_seconds": total_time / max(1, self.batch_stats["total_surveys"]),
                "success_rate_percent": (self.batch_stats["completed_surveys"] / max(1, self.batch_stats["total_surveys"])) * 100,
                "surveys_per_hour": (self.batch_stats["total_surveys"] / max(1, total_time / 3600))
            }
        }

        # Save report
        os.makedirs('results', exist_ok=True)
        report_file = f"results/batch_report_{self.batch_stats['batch_id']}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Log summary
        logger.info("="*50)
        logger.info("BATCH PROCESSING COMPLETED")
        logger.info("="*50)
        logger.info(f"Batch ID: {self.batch_stats['batch_id']}")
        logger.info(f"Total Surveys: {self.batch_stats['total_surveys']}")
        logger.info(f"Successful: {self.batch_stats['completed_surveys']}")
        logger.info(f"Failed: {self.batch_stats['failed_surveys']}")
        logger.info(f"Success Rate: {report['performance_metrics']['success_rate_percent']:.1f}%")
        logger.info(f"Total Time: {total_time:.1f} seconds")
        logger.info(f"Average Survey Time: {report['performance_metrics']['average_survey_time_seconds']:.1f} seconds")
        logger.info(f"Report saved: {report_file}")
        logger.info("="*50)

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
            logger.info(f"Loaded {len(processor.config.get('access_codes', []))} access codes")
            logger.info("Configuration appears valid")
            return

        # Process batch
        results = processor.process_batch()

        # Exit with appropriate code
        if results["failed_surveys"] == 0:
            logger.success("All surveys completed successfully!")
            sys.exit(0)
        else:
            logger.warning(f"{results['failed_surveys']} surveys failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()