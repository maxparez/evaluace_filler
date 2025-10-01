#!/usr/bin/env python3
"""
Smart Playback System - Complete survey automation using JavaScript injection
Phase 5: Production-ready automated survey filling system
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Optional, List

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from loguru import logger
from selenium.webdriver.common.by import By
from src.browser_manager import BrowserManager
from src.utils.page_identifier import PageIdentifier
from src.utils.javascript_loader import JavaScriptLoader
from src.utils.status_indicator_manager import StatusIndicatorManager
from src.smart_page_matcher import SmartPageMatcher
from src.inclusion_page_handler import InclusionPageHandler
from src.config import Config

class SmartPlaybackSystem:
    """
    Complete automated survey filling system

    Features:
    - JavaScript injection for 100% reliability
    - Pattern-based page recognition
    - Special case handling (inclusion, barrier-free, etc.)
    - Error recovery and fallback strategies
    - Performance monitoring and logging
    """

    def __init__(self, strategy_file: str = "scenarios/optimized_survey_strategy.json"):
        self.browser_manager = BrowserManager()
        self.page_identifier = PageIdentifier()
        self.js_loader = JavaScriptLoader()
        self.status_manager = None  # Will be initialized when driver is available
        self.driver = None

        # Load strategy configuration
        self.strategy_file = strategy_file
        self.strategy_config = {}
        self.load_strategy_config()

        # Execution tracking
        self.session_stats = {
            "session_id": f"playback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": None,
            "end_time": None,
            "pages_processed": 0,
            "pages_successful": 0,
            "pages_failed": 0,
            "strategies_used": {},
            "errors": [],
            "page_sequence": []
        }

    def load_strategy_config(self):
        """Load optimized strategy configuration"""
        try:
            with open(self.strategy_file, 'r', encoding='utf-8') as f:
                self.strategy_config = json.load(f)

            logger.info(f"Loaded strategy config: {len(self.strategy_config.get('default_strategies', {}))} strategies")

        except Exception as e:
            logger.error(f"Failed to load strategy config: {e}")
            raise

    def connect_to_browser(self) -> bool:
        """Connect to persistent browser"""
        try:
            self.driver = self.browser_manager.get_or_create_browser(keep_alive=True)
            if self.driver:
                current_url = self.driver.current_url
                logger.success(f"Connected to browser: {current_url}")

                # Initialize status indicator manager
                self.status_manager = StatusIndicatorManager(self.driver)
                logger.debug("Status indicator manager initialized")

                return True
            else:
                logger.error("Failed to connect to browser")
                return False

        except Exception as e:
            logger.error(f"Browser connection error: {e}")
            return False

    def get_page_strategy(self, page_title: str) -> Optional[Dict]:
        """
        Get filling strategy for current page

        Priority:
        1. Special cases (inclusion, Roma students, final page)
        2. Default strategies (matrix, radio, input)
        3. Fuzzy matching fallback
        """

        # Check special cases first
        special_cases = self.strategy_config.get('special_cases', {})

        for case_name, case_config in special_cases.items():
            page_patterns = case_config.get('page_patterns', [])

            # Check if current page matches any pattern
            for pattern in page_patterns:
                if pattern.lower() in page_title.lower():
                    logger.info(f"Matched special case: {case_name}")

                    # Handle inclusion pages specially
                    if case_name == 'barrier_free_exception':
                        return self.create_barrier_free_strategy(case_config)

                    return case_config.get('strategy', {})

        # Check default strategies with fuzzy matching
        default_strategies = self.strategy_config.get('default_strategies', {})

        # Try keyword matching first - with priority system
        matched_strategies = []

        for strategy_name, strategy_config in default_strategies.items():
            # Skip disabled strategies
            if not strategy_config.get('enabled', True):
                continue

            keywords = strategy_config.get('keywords', [])
            priority = strategy_config.get('priority', 0)

            if keywords:
                # Check for keyword matches
                keyword_matches = [keyword for keyword in keywords if keyword.lower() in page_title.lower()]

                if keyword_matches:
                    # Calculate match score based on longest matching keyword + priority
                    longest_match = max(keyword_matches, key=len)
                    match_score = len(longest_match) + priority

                    logger.debug(f"Strategy {strategy_name}: matches={keyword_matches}, score={match_score}, priority={priority}")
                    matched_strategies.append((match_score, strategy_name, strategy_config))

        # Sort by match score (highest first)
        if matched_strategies:
            matched_strategies.sort(key=lambda x: x[0], reverse=True)
            match_score, strategy_name, strategy_config = matched_strategies[0]

            logger.info(f"Matched strategy by keywords: {strategy_name} (score: {match_score})")
            return strategy_config

        # Fuzzy matching fallback
        fuzzy_config = self.strategy_config.get('fuzzy_matching', {})
        if fuzzy_config.get('enabled', True):
            fallback_strategy = fuzzy_config.get('fallback_strategy', 'MATRIX_RATING_A6')

            if fallback_strategy in default_strategies:
                logger.info(f"Using fuzzy fallback: {fallback_strategy}")
                return default_strategies[fallback_strategy]

        logger.warning(f"No strategy found for page: {page_title[:50]}...")
        return None

    def execute_page_strategy(self, strategy: Dict) -> bool:
        """
        Execute filling strategy using JavaScript injection

        Returns True if successful, False if failed
        """

        if not strategy:
            return False

        strategy_pattern = strategy.get('pattern', 'UNKNOWN')

        try:
            # Track strategy usage
            if strategy_pattern not in self.session_stats['strategies_used']:
                self.session_stats['strategies_used'][strategy_pattern] = 0
            self.session_stats['strategies_used'][strategy_pattern] += 1

            # Execute based on pattern type
            if strategy_pattern == 'INCLUSION_MIXED_STRATEGY':
                return self.execute_inclusion_strategy(strategy)

            elif strategy_pattern == 'MATRIX_RATING':
                return self.execute_matrix_strategy(strategy)

            elif strategy_pattern == 'MATRIX_RANDOM_RATING':
                return self.execute_matrix_random_strategy(strategy)

            elif strategy_pattern == 'RADIO_CHOICE':
                return self.execute_radio_strategy(strategy)

            elif strategy_pattern == 'INPUT_FIELD':
                return self.execute_input_strategy(strategy)

            elif strategy_pattern == 'CHECKBOX_MULTI':
                return self.execute_checkbox_strategy(strategy)

            elif strategy_pattern == 'SKIP':
                return self.execute_skip_strategy(strategy)

            elif strategy_pattern == 'FINAL_PAGE':
                return self.execute_final_page_strategy(strategy)

            else:
                logger.warning(f"Unknown strategy pattern: {strategy_pattern}")
                return False

        except Exception as e:
            logger.error(f"Strategy execution error: {e}")
            self.session_stats['errors'].append(f"Strategy {strategy_pattern}: {str(e)}")
            return False

    def execute_inclusion_strategy(self, strategy: Dict) -> bool:
        """Execute specialized inclusion page strategy using external JavaScript"""
        logger.info("Executing inclusion mixed strategy (barrier-free A1, others A6)")

        try:
            barrier_keywords = strategy.get('barrier_keywords', [])
            if not barrier_keywords:
                logger.error("No barrier keywords provided for inclusion strategy")
                return False

            # Execute external JavaScript function
            result = self.js_loader.execute_script(
                self.driver,
                'barrier_free_inclusion',
                'executeBarrierFreeInclusion',
                barrier_keywords
            )

            if result and isinstance(result, dict):
                logger.success(f"Inclusion strategy executed: {result.get('barrier_free_a1', 0)} A1 + {result.get('regular_a6', 0)} A6")
                return True
            else:
                logger.warning("Inclusion strategy returned no results")
                return False

        except Exception as e:
            logger.error(f"Inclusion strategy failed: {e}")
            return False

    def execute_matrix_strategy(self, strategy: Dict) -> bool:
        """Execute matrix rating strategy using external JavaScript"""
        rating_level = strategy.get('rating_level', 'A5')
        logger.info(f"Executing matrix strategy: rating {rating_level}")

        try:
            # Execute external JavaScript function
            result = self.js_loader.execute_script(
                self.driver,
                'matrix_strategy',
                'executeMatrixStrategy',
                rating_level
            )

            if result:
                total_selected = result.get('totalSelected', 0)
                total_radios = result.get('total', 0)
                clicked = result.get('clicked', 0)
                already_selected = result.get('alreadySelected', 0)

                if total_selected == total_radios and total_radios > 0:
                    logger.success(f"Matrix strategy successful: {total_selected}/{total_radios} radios selected (clicked: {clicked}, already: {already_selected})")
                    return True
                else:
                    logger.warning(f"Matrix incomplete: {total_selected}/{total_radios} radios selected")
                    return False
            else:
                logger.warning(f"Matrix script execution failed")
                return False

        except Exception as e:
            logger.error(f"Matrix strategy failed: {e}")
            return False

    def execute_matrix_random_strategy(self, strategy: Dict) -> bool:
        """Execute matrix strategy with random rating selection using external JavaScript"""
        rating_options = strategy.get('rating_options', ['A5', 'A6', 'A7'])
        logger.info(f"Executing matrix random strategy with options: {rating_options}")

        try:
            # Execute external JavaScript function
            result = self.js_loader.execute_script(
                self.driver,
                'matrix_random_strategy',
                'executeMatrixRandomStrategy',
                rating_options
            )

            if result and isinstance(result, dict):
                total_processed = result.get('total_processed', 0)
                distribution = result.get('rating_distribution', {})

                logger.success(f"Matrix random strategy: {total_processed} radios processed")
                logger.info(f"Rating distribution: {distribution}")

                return total_processed > 0
            else:
                logger.warning("Matrix random script returned no results")
                return False

        except Exception as e:
            logger.error(f"Matrix random strategy failed: {e}")
            return False

    def execute_radio_strategy(self, strategy: Dict) -> bool:
        """Execute radio choice strategy using external JavaScript"""
        selected_answer = strategy.get('selected_answer', '')
        logger.info(f"Executing radio strategy: '{selected_answer}'")

        try:
            # Execute external JavaScript function
            result = self.js_loader.execute_script(
                self.driver,
                'radio_strategy',
                'executeRadioStrategy',
                selected_answer
            )

            if result and result.get('success'):
                logger.success(f"Radio clicked: {result.get('clicked', 'unknown')}")
                return True
            else:
                logger.warning(f"Radio selection failed: {result}")
                return False

        except Exception as e:
            logger.error(f"Radio strategy failed: {e}")
            return False

    def execute_input_strategy(self, strategy: Dict) -> bool:
        """Execute input field strategy using external JavaScript"""
        input_value = strategy.get('input_value', '')

        # Handle CONFIG placeholders
        if input_value == "CONFIG_BIRTH_YEAR":
            # Use birth_year passed from batch processor
            birth_year = getattr(self, 'user_birth_year', '1985')
            input_value = str(birth_year)
            logger.debug(f"Replaced CONFIG_BIRTH_YEAR with: {input_value}")

        logger.info(f"Executing input strategy: '{input_value}'")

        try:
            # Execute external JavaScript function
            result = self.js_loader.execute_script(
                self.driver,
                'input_strategy',
                'executeInputStrategy',
                input_value
            )

            if result and result.get('success', False):
                logger.success(f"Input filled: {result.get('filled', 0)}/{result.get('total', 0)} fields")
                return True
            else:
                logger.warning(f"Input filling failed: {result}")
                return False

        except Exception as e:
            logger.error(f"Input strategy failed: {e}")
            return False

    def execute_checkbox_strategy(self, strategy: Dict) -> bool:
        """Execute checkbox strategy using external JavaScript"""
        selected_indices = strategy.get('selected_indices', [])
        logger.info(f"Executing checkbox strategy: indices {selected_indices}")

        try:
            # Execute external JavaScript function
            result = self.js_loader.execute_script(
                self.driver,
                'checkbox_strategy',
                'executeCheckboxStrategy',
                selected_indices
            )

            if result:
                target_selected = result.get('targetSelected', 0)
                required_count = result.get('requiredCount', 0)

                if target_selected == required_count:
                    logger.success(f"Checkbox strategy successful: {target_selected}/{required_count} target checkboxes selected")
                    return True
                else:
                    logger.warning(f"Checkbox selection incomplete: {target_selected}/{required_count} target checkboxes selected")
                    return False
            else:
                logger.warning(f"Checkbox script execution failed")
                return False

        except Exception as e:
            logger.error(f"Checkbox strategy failed: {e}")
            return False

    def execute_skip_strategy(self, strategy: Dict) -> bool:
        """Execute skip strategy (just navigate)"""
        logger.info("Executing skip strategy")
        return True  # Skip always succeeds

    def execute_final_page_strategy(self, strategy: Dict) -> bool:
        """Execute final page strategy - click final submit button"""
        logger.info("Reached final page - clicking final submit button")

        try:
            # Try different final submit button selectors
            final_submit_selectors = [
                "#ls-button-submit",  # Primary selector for final submit
                "button[value='movesubmit'][name='move']",  # Specific final submit button
                "button:contains('Odeslat')",  # Button with "Odeslat" text
                "input[type='submit'][value*='Odeslat']",
                "button[type='submit']"
            ]

            for selector in final_submit_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.debug(f"Found button with selector {selector}: enabled={button.is_enabled()}, displayed={button.is_displayed()}")

                    if button:
                        if not button.is_enabled():
                            logger.warning(f"Button found but disabled: {selector}")
                            continue
                        if not button.is_displayed():
                            logger.warning(f"Button found but not displayed: {selector}")
                            continue

                        logger.info(f"Clicking final submit button: {selector}")
                        # Try JavaScript click if regular click fails
                        try:
                            button.click()
                        except:
                            logger.warning("Regular click failed, trying JavaScript click")
                            self.driver.execute_script("arguments[0].click();", button)

                        logger.success("🎉 FINAL SUBMIT CLICKED - Waiting for completion page...")
                        time.sleep(Config.NAVIGATION_DELAY + 2)  # Wait for final submission and redirect

                        # Verify completion page
                        try:
                            completion_div = self.driver.find_element(By.CSS_SELECTOR, "div.completed-wrapper")
                            completion_text = self.driver.find_element(By.CSS_SELECTOR, "div.completed-text").text
                            logger.success("✅ SURVEY COMPLETED - Completion page confirmed!")
                            logger.info(f"Completion message: {completion_text[:100]}")
                        except Exception as e:
                            logger.debug(f"Completion page divs not found: {e}")
                            # Check page source for completion text
                            page_source = self.driver.page_source
                            if "Vaše odpovědi byly v pořádku uloženy" in page_source:
                                logger.success("✅ SURVEY COMPLETED - Completion text found!")
                            elif "děkujeme" in page_source.lower() or "completed" in page_source.lower():
                                logger.success("✅ SURVEY COMPLETED - Generic completion indicators found!")
                            else:
                                logger.warning("Could not verify completion page, but final submit was clicked")

                        return True
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue

            logger.warning("No final submit button found - survey may already be completed")
            return True

        except Exception as e:
            logger.error(f"Final page submission failed: {e}")
            return False

    def navigate_to_next_page(self, strategy: Dict) -> bool:
        """Navigate to next page with appropriate delay"""

        if not strategy.get('auto_navigate', True):
            logger.info("Auto-navigation disabled for this strategy")
            return False

        navigation_delay = strategy.get('navigation_delay', 3000) / 1000  # Convert to seconds

        try:
            logger.info(f"Auto-navigating in {navigation_delay} seconds...")
            time.sleep(navigation_delay)

            # JavaScript navigation
            js_navigation = self.strategy_config.get('filling_algorithm', {}).get('navigation_script', '')

            if js_navigation:
                js_code = js_navigation.replace('{navigation_delay}', '0')  # We already waited
            else:
                # Fallback navigation
                js_code = """
                var nextButton = document.querySelector('#ls-button-submit');
                if (nextButton) {
                    nextButton.click();
                    return {success: true, button: 'found'};
                } else {
                    return {success: false, button: 'not_found'};
                }
                """

            result = self.driver.execute_script(js_code)

            if result and result.get('success'):
                logger.success("Navigation successful")

                # Navigation successful - status will be updated when processing new page

                time.sleep(Config.NAVIGATION_DELAY - 1)  # Wait for page load

                # Update status to show we're ready to process the new page
                if self.status_manager:
                    self.status_manager.processing_page(current_page, 'Načítám novou stránku')

                return True
            else:
                logger.warning("Navigation may have failed")
                return False

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False

    def process_current_page(self) -> bool:
        """Process current page with appropriate strategy"""

        try:
            # Get page information
            current_url = self.driver.current_url
            page_id = self.page_identifier.get_page_id(self.driver)

            logger.info(f"Processing page: {page_id[:50]}...")

            # Track page in session stats
            page_info = {
                "page_number": self.session_stats['pages_processed'] + 1,
                "page_id": page_id,
                "url": current_url,
                "timestamp": datetime.now().isoformat()
            }

            self.session_stats['pages_processed'] += 1

            # Get strategy for this page
            strategy = self.get_page_strategy(page_id)

            if not strategy:
                logger.error(f"No strategy found for page")
                if self.status_manager:
                    self.status_manager.require_manual_intervention(
                        "Neznámý typ stránky",
                        "Vyplňte stránku ručně a pokračujte kliknutím na Další"
                    )
                page_info['status'] = 'failed'
                page_info['error'] = 'No strategy found'
                self.session_stats['pages_failed'] += 1
                self.session_stats['page_sequence'].append(page_info)
                return False

            page_info['strategy'] = strategy.get('pattern', 'UNKNOWN')

            # Execute strategy
            success = self.execute_page_strategy(strategy)

            if success:
                logger.success(f"Page strategy executed successfully")
                page_info['status'] = 'success'
                self.session_stats['pages_successful'] += 1

                # Navigate to next page
                if self.navigate_to_next_page(strategy):
                    page_info['navigation'] = 'success'
                else:
                    page_info['navigation'] = 'failed'

            else:
                logger.error(f"Page strategy failed")
                page_info['status'] = 'failed'
                self.session_stats['pages_failed'] += 1

            self.session_stats['page_sequence'].append(page_info)
            return success

        except Exception as e:
            logger.error(f"Page processing error: {e}")
            self.session_stats['errors'].append(f"Page processing: {str(e)}")
            return False

    def create_barrier_free_strategy(self, barrier_config: Dict) -> Dict:
        """Create barrier-free exception strategy for inclusion pages"""
        # Get barrier-free keywords from config
        exception_rules = barrier_config.get('exception_rules', [])
        default_strategy = barrier_config.get('default_strategy', {})

        # Create JavaScript strategy that handles both barrier-free (A1) and regular (A6) questions
        barrier_keywords = []
        for rule in exception_rules:
            barrier_keywords.extend(rule.get('text_contains', []))

        # Use external JavaScript for barrier-free inclusion strategy

        return {
            'pattern': 'INCLUSION_MIXED_STRATEGY',
            'barrier_keywords': barrier_keywords,
            'auto_navigate': True,
            'navigation_delay': 4000,
            'description': 'Mixed inclusion strategy: A1 for barrier-free, A6 for others'
        }

    def run_complete_survey(self, max_pages: int = None) -> Dict:
        """
        Run complete survey automation

        Returns session statistics
        """

        logger.info("🚀 STARTING COMPLETE SURVEY AUTOMATION")
        self.session_stats['start_time'] = datetime.now().isoformat()

        if not self.connect_to_browser():
            return self.session_stats

        try:
            page_count = 0

            # Initialize status indicator
            if self.status_manager:
                self.status_manager.start_automation(1, max_pages)

            # Anti-loop protection variables
            last_page_id = None
            same_page_count = 0
            MAX_SAME_PAGE_ATTEMPTS = 3

            while max_pages is None or page_count < max_pages:
                page_count += 1
                logger.info(f"\n--- PAGE {page_count} ---")

                # Get current page ID for loop detection
                current_page_id = self.page_identifier.get_page_id(self.driver)

                # Anti-loop protection: Check if we're stuck on the same page
                if current_page_id == last_page_id:
                    same_page_count += 1
                    logger.warning(f"⚠️ Same page detected {same_page_count}/{MAX_SAME_PAGE_ATTEMPTS}: {current_page_id[:50]}...")

                    if same_page_count >= MAX_SAME_PAGE_ATTEMPTS:
                        logger.error(f"🔄 LOOP DETECTED: Stuck on page '{current_page_id[:50]}...' for {MAX_SAME_PAGE_ATTEMPTS} attempts")
                        self.session_stats['errors'].append(f"Loop detected on page: {current_page_id[:50]}")
                        if self.status_manager:
                            self.status_manager.automation_error("Detekována smyčka - ukončuji automatizaci")
                        break
                else:
                    same_page_count = 0  # Reset counter on new page
                    last_page_id = current_page_id

                # Update status for current page
                if self.status_manager:
                    self.status_manager.processing_page(page_count, 'Zpracovávám otázky')

                # Process current page
                success = self.process_current_page()

                # Check if we've reached the final page
                if any(indicator in current_page_id.lower() for indicator in ['dostali jste se na konec', 'dokončení', 'odeslat']):
                    logger.success("🎉 Reached final page - survey completed!")
                    if self.status_manager:
                        self.status_manager.automation_completed()
                    break

                # Delay between pages - status will be updated when processing starts

                # Small delay between pages
                time.sleep(Config.FORM_FILL_DELAY)

        except KeyboardInterrupt:
            logger.warning("Survey automation interrupted by user")
            self.session_stats['errors'].append("User interrupted")
            if self.status_manager:
                self.status_manager.automation_error("Přerušeno uživatelem")

        except Exception as e:
            logger.error(f"Survey automation error: {e}")
            self.session_stats['errors'].append(f"Automation error: {str(e)}")
            if self.status_manager:
                self.status_manager.automation_error(f"Systémová chyba: {str(e)}")

        finally:
            self.session_stats['end_time'] = datetime.now().isoformat()
            self.save_session_stats()

        return self.session_stats

    def save_session_stats(self):
        """Save session statistics to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/playback_session_{timestamp}.json"

            os.makedirs("logs", exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.session_stats, f, ensure_ascii=False, indent=2)

            logger.success(f"Session stats saved: {filename}")

        except Exception as e:
            logger.error(f"Failed to save session stats: {e}")

    def print_session_summary(self):
        """Print comprehensive session summary"""
        stats = self.session_stats

        print("\n" + "="*60)
        print("🎯 SMART PLAYBACK SESSION SUMMARY")
        print("="*60)
        print(f"Session ID: {stats['session_id']}")
        print(f"Start Time: {stats['start_time']}")
        print(f"End Time: {stats['end_time']}")
        print()
        print(f"📊 PERFORMANCE:")
        print(f"  Pages Processed: {stats['pages_processed']}")
        print(f"  Pages Successful: {stats['pages_successful']}")
        print(f"  Pages Failed: {stats['pages_failed']}")
        print(f"  Success Rate: {stats['pages_successful']/max(stats['pages_processed'], 1)*100:.1f}%")
        print()
        print(f"🎯 STRATEGIES USED:")
        for strategy, count in stats['strategies_used'].items():
            print(f"  {strategy}: {count} times")
        print()
        if stats['errors']:
            print(f"❌ ERRORS ({len(stats['errors'])}):")
            for error in stats['errors'][:5]:  # First 5 errors
                print(f"  - {error}")
        else:
            print("✅ NO ERRORS")
        print("="*60)

# Main execution
if __name__ == "__main__":
    playback = SmartPlaybackSystem()

    print("🎯 SMART PLAYBACK SYSTEM")
    print("=" * 50)
    print("Ready to automate complete survey.")
    print("Make sure you're on the first page of the survey.")
    print()

    input("Press ENTER to start automation...")

    # Run complete survey
    results = playback.run_complete_survey()

    # Print summary
    playback.print_session_summary()