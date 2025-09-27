"""
Navigation Manager for Evaluace Filler
Handles navigation through dotazník pages with robust button detection and page history.
"""

import time
from typing import Optional, List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from loguru import logger

from .page_identifier import PageIdentifier


class NavigationError(Exception):
    """Custom exception for navigation-related errors."""
    pass


class NavigationManager:
    """
    Manages navigation through dotazník pages with support for forward/back navigation,
    page history tracking, and robust button detection.
    """

    # Standard selectors for navigation buttons
    NEXT_BUTTON_SELECTORS = [
        "#ls-button-submit",
        ".ls-move-next-btn",
        "button[value='movenext']",
        "button[name='move'][value='movenext']",
        "input[type='submit'][value='movenext']",
        ".ls-move-submit-btn"
    ]

    PREV_BUTTON_SELECTORS = [
        "#ls-button-previous",
        ".ls-move-previous-btn",
        "button[value='moveprev']",
        "button[name='move'][value='moveprev']",
        "input[type='submit'][value='moveprev']"
    ]

    def __init__(self, driver):
        """
        Initialize NavigationManager.

        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.page_history: List[Dict[str, Any]] = []
        self.current_position = -1

    def get_navigation_state(self):
        """
        Get current navigation state and available options.

        Returns:
            dict: Navigation state information
        """
        nav_state = {
            'can_go_next': False,
            'can_go_back': False,
            'next_button': None,
            'prev_button': None,
            'next_button_text': None,
            'prev_button_text': None,
            'is_final_page': False,
            'next_selector_used': None,
            'prev_selector_used': None
        }

        # Check Next button
        for selector in self.NEXT_BUTTON_SELECTORS:
            try:
                next_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                nav_state['next_button'] = next_btn
                nav_state['can_go_next'] = next_btn.is_enabled() and next_btn.is_displayed()
                nav_state['next_button_text'] = next_btn.text.strip()
                nav_state['next_selector_used'] = selector

                # Check if this looks like a final page button
                button_text = nav_state['next_button_text'].lower()
                final_indicators = ['dokončit', 'dokonč', 'dokon', 'odeslat', 'finish', 'submit', 'complete']
                nav_state['is_final_page'] = any(indicator in button_text for indicator in final_indicators)

                break
            except NoSuchElementException:
                continue

        # Check Previous button
        for selector in self.PREV_BUTTON_SELECTORS:
            try:
                prev_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                nav_state['prev_button'] = prev_btn
                nav_state['can_go_back'] = prev_btn.is_enabled() and prev_btn.is_displayed()
                nav_state['prev_button_text'] = prev_btn.text.strip()
                nav_state['prev_selector_used'] = selector
                break
            except NoSuchElementException:
                continue

        logger.debug(f"Navigation state: next={nav_state['can_go_next']}, "
                    f"back={nav_state['can_go_back']}, final={nav_state['is_final_page']}")

        return nav_state

    def navigate_next(self, wait_for_load=True, timeout=10):
        """
        Navigate to the next page.

        Args:
            wait_for_load: Whether to wait for new page to load
            timeout: Maximum time to wait for page load

        Returns:
            str: New page ID after navigation

        Raises:
            NavigationError: If navigation fails
        """
        nav_state = self.get_navigation_state()

        if not nav_state['can_go_next']:
            raise NavigationError("Cannot navigate next - button not available, disabled, or hidden")

        # Record current page info before navigation
        current_page_info = {
            'page_id': PageIdentifier.get_page_id(self.driver),
            'url': self.driver.current_url,
            'timestamp': time.time(),
            'navigation_direction': 'next'
        }

        logger.info(f"Navigating next from page: '{current_page_info['page_id']}'")

        # Add to history
        self.page_history.append(current_page_info)
        self.current_position = len(self.page_history) - 1

        try:
            # Click the next button
            next_button = nav_state['next_button']
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(0.2)  # Brief pause for scroll
            next_button.click()

            logger.debug(f"Clicked next button: '{nav_state['next_button_text']}'")

            # Wait for new page to load if requested
            if wait_for_load:
                PageIdentifier.wait_for_page_load(self.driver, timeout)

            # Get new page info
            new_page_id = PageIdentifier.get_page_id(self.driver)
            new_url = self.driver.current_url

            logger.info(f"Navigation successful: '{current_page_info['page_id']}' -> '{new_page_id}'")

            return new_page_id

        except Exception as e:
            logger.error(f"Navigation next failed: {e}")
            raise NavigationError(f"Failed to navigate next: {e}")

    def navigate_previous(self, wait_for_load=True, timeout=10):
        """
        Navigate to the previous page.

        Args:
            wait_for_load: Whether to wait for page to load
            timeout: Maximum time to wait for page load

        Returns:
            str: New page ID after navigation

        Raises:
            NavigationError: If navigation fails
        """
        nav_state = self.get_navigation_state()

        if not nav_state['can_go_back']:
            raise NavigationError("Cannot navigate back - button not available, disabled, or hidden")

        current_page_id = PageIdentifier.get_page_id(self.driver)
        logger.info(f"Navigating back from page: '{current_page_id}'")

        try:
            # Click the previous button
            prev_button = nav_state['prev_button']
            self.driver.execute_script("arguments[0].scrollIntoView(true);", prev_button)
            time.sleep(0.2)  # Brief pause for scroll
            prev_button.click()

            logger.debug(f"Clicked previous button: '{nav_state['prev_button_text']}'")

            # Wait for page to load if requested
            if wait_for_load:
                PageIdentifier.wait_for_page_load(self.driver, timeout)

            # Get new page info
            new_page_id = PageIdentifier.get_page_id(self.driver)
            new_url = self.driver.current_url

            # Update history - remove last entry if we went back to a known page
            if self.page_history and self.current_position > 0:
                expected_previous = self.page_history[self.current_position - 1]['page_id']
                if new_page_id == expected_previous:
                    # We're back to a known page, adjust position
                    self.current_position -= 1
                    logger.debug(f"Back to known page, position: {self.current_position}")

            logger.info(f"Back navigation successful: '{current_page_id}' -> '{new_page_id}'")

            return new_page_id

        except Exception as e:
            logger.error(f"Navigation back failed: {e}")
            raise NavigationError(f"Failed to navigate back: {e}")

    def get_current_position(self):
        """
        Get current position in page history.

        Returns:
            int: Current position (0-based), -1 if no history
        """
        return self.current_position

    def get_page_history(self):
        """
        Get complete page history.

        Returns:
            list: List of page information dictionaries
        """
        return self.page_history.copy()

    def can_navigate_back_in_history(self):
        """
        Check if we can navigate back based on history.

        Returns:
            bool: True if back navigation is possible based on history
        """
        return self.current_position > 0

    def get_navigation_summary(self):
        """
        Get summary of navigation capabilities and history.

        Returns:
            dict: Navigation summary
        """
        nav_state = self.get_navigation_state()

        return {
            'current_page': PageIdentifier.get_page_id(self.driver),
            'navigation_state': nav_state,
            'history_length': len(self.page_history),
            'current_position': self.current_position,
            'can_go_back_in_history': self.can_navigate_back_in_history(),
            'is_final_page': nav_state['is_final_page'] or PageIdentifier.is_final_page(self.driver)
        }

    def reset_history(self):
        """Reset navigation history."""
        self.page_history.clear()
        self.current_position = -1
        logger.info("Navigation history reset")

    def wait_for_navigation_buttons(self, timeout=5):
        """
        Wait for navigation buttons to be present and enabled.

        Args:
            timeout: Maximum time to wait

        Returns:
            dict: Available navigation options after waiting
        """
        logger.debug(f"Waiting for navigation buttons (timeout: {timeout}s)")

        wait = WebDriverWait(self.driver, timeout)

        # Wait for either next or previous button to be present and enabled
        try:
            # Create a combined condition for any navigation button
            all_nav_selectors = self.NEXT_BUTTON_SELECTORS + self.PREV_BUTTON_SELECTORS
            combined_selector = ", ".join(all_nav_selectors)

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, combined_selector)))

            # Additional wait for button to be enabled
            time.sleep(0.5)

            nav_state = self.get_navigation_state()
            logger.debug("Navigation buttons ready")

            return nav_state

        except TimeoutException:
            logger.warning(f"Navigation buttons not ready after {timeout}s")
            return self.get_navigation_state()

    def find_navigation_elements(self):
        """
        Find and return all navigation elements on current page.

        Returns:
            dict: Dictionary of found navigation elements
        """
        elements = {
            'next_buttons': [],
            'prev_buttons': [],
            'other_nav_elements': []
        }

        # Find all next buttons
        for selector in self.NEXT_BUTTON_SELECTORS:
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    elements['next_buttons'].append({
                        'element': button,
                        'selector': selector,
                        'text': button.text.strip(),
                        'enabled': button.is_enabled(),
                        'displayed': button.is_displayed()
                    })
            except Exception as e:
                logger.debug(f"Error finding next buttons with '{selector}': {e}")

        # Find all previous buttons
        for selector in self.PREV_BUTTON_SELECTORS:
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    elements['prev_buttons'].append({
                        'element': button,
                        'selector': selector,
                        'text': button.text.strip(),
                        'enabled': button.is_enabled(),
                        'displayed': button.is_displayed()
                    })
            except Exception as e:
                logger.debug(f"Error finding prev buttons with '{selector}': {e}")

        # Find other potential navigation elements
        other_selectors = [
            'input[type="submit"]',
            'button[type="submit"]',
            '.btn-primary',
            '.btn-success',
            '.continue-btn',
            '.submit-btn'
        ]

        for selector in other_selectors:
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    # Skip if already found in next/prev buttons
                    if (any(button == nb['element'] for nb in elements['next_buttons']) or
                        any(button == pb['element'] for pb in elements['prev_buttons'])):
                        continue

                    elements['other_nav_elements'].append({
                        'element': button,
                        'selector': selector,
                        'text': button.text.strip(),
                        'enabled': button.is_enabled(),
                        'displayed': button.is_displayed()
                    })
            except Exception as e:
                logger.debug(f"Error finding other nav elements with '{selector}': {e}")

        return elements