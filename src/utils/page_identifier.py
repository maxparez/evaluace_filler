"""
Page Identifier Utility for Evaluace Filler
Provides robust page identification for dotazník pages using consistent selectors.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from loguru import logger


class PageIdentifier:
    """
    Utility class for identifying dotazník pages using consistent selectors.
    Provides both identification and waiting functionality.
    """

    # Primary selector for main question text
    PRIMARY_QUESTION_SELECTOR = ".question-text .ls-label-question"

    # Fallback selectors for special pages
    FALLBACK_SELECTORS = [
        "h1",
        "h2",
        ".page-title",
        ".ls-page-title",
        ".ls-page-header h1",
        ".ls-page-header h2",
        ".main-title"
    ]

    @classmethod
    def get_page_id(cls, driver):
        """
        Get unique identifier for current page based on question text or title.

        Args:
            driver: Selenium WebDriver instance

        Returns:
            str: Page identifier text or fallback identifier
        """
        try:
            # Primary method - main question text
            question_element = driver.find_element(By.CSS_SELECTOR, cls.PRIMARY_QUESTION_SELECTOR)
            page_id = question_element.text.strip()

            if page_id:  # Ensure we have non-empty text
                logger.debug(f"Page identified by question: '{page_id[:50]}...'")
                return page_id

        except NoSuchElementException:
            logger.debug(f"Primary selector '{cls.PRIMARY_QUESTION_SELECTOR}' not found, trying fallbacks")

        # Fallback methods for special pages
        for selector in cls.FALLBACK_SELECTORS:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                page_id = element.text.strip()

                if page_id:  # Ensure we have non-empty text
                    logger.debug(f"Page identified by fallback '{selector}': '{page_id[:50]}...'")
                    return page_id

            except NoSuchElementException:
                continue

        # Final fallback - URL-based identifier
        current_url = driver.current_url
        url_parts = current_url.split('/')
        url_identifier = url_parts[-1] if url_parts[-1] else url_parts[-2]

        # Add timestamp to ensure uniqueness
        timestamp = int(time.time())
        fallback_id = f"page_{url_identifier}_{timestamp}"

        logger.warning(f"No page identifier found, using URL fallback: '{fallback_id}'")
        return fallback_id

    @classmethod
    def wait_for_page_load(cls, driver, timeout=10):
        """
        Wait for page to load by waiting for question element or title to be present.

        Args:
            driver: Selenium WebDriver instance
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if page loaded successfully

        Raises:
            TimeoutException: If page doesn't load within timeout
        """
        logger.debug(f"Waiting for page load (timeout: {timeout}s)")

        wait = WebDriverWait(driver, timeout)

        # Create list of all possible selectors to wait for
        all_selectors = [cls.PRIMARY_QUESTION_SELECTOR] + cls.FALLBACK_SELECTORS

        try:
            # Wait for any of the selectors to be present
            for selector in all_selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    logger.debug(f"Page loaded, found element: '{selector}'")
                    return True
                except TimeoutException:
                    continue

            # If none of the specific selectors worked, wait for body to be present
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            logger.debug("Page loaded (fallback: body element found)")
            return True

        except TimeoutException:
            logger.error(f"Page load timeout after {timeout}s")
            raise

    @classmethod
    def is_final_page(cls, driver):
        """
        Check if current page is a final/completion page.

        Args:
            driver: Selenium WebDriver instance

        Returns:
            bool: True if this appears to be a final page
        """
        page_id = cls.get_page_id(driver).lower()

        final_indicators = [
            "dokončit", "dokončení", "odeslat", "odesláno", "complete", "completion",
            "finish", "finished", "submit", "submitted", "thank you", "děkujeme",
            "úspěšně", "successfully", "hotovo", "done"
        ]

        for indicator in final_indicators:
            if indicator in page_id:
                logger.info(f"Final page detected: contains '{indicator}'")
                return True

        # Check for specific final page elements
        final_selectors = [
            ".completion-page",
            ".thank-you-page",
            ".final-page",
            ".ls-completion",
            "#completion"
        ]

        for selector in final_selectors:
            try:
                driver.find_element(By.CSS_SELECTOR, selector)
                logger.info(f"Final page detected: found element '{selector}'")
                return True
            except NoSuchElementException:
                continue

        return False

    @classmethod
    def get_page_info(cls, driver):
        """
        Get comprehensive information about current page.

        Args:
            driver: Selenium WebDriver instance

        Returns:
            dict: Dictionary with page information
        """
        page_info = {
            'page_id': cls.get_page_id(driver),
            'url': driver.current_url,
            'title': driver.title,
            'is_final': cls.is_final_page(driver),
            'has_question': False,
            'question_selector_used': None,
            'timestamp': time.time()
        }

        # Check which selector was used for identification
        try:
            driver.find_element(By.CSS_SELECTOR, cls.PRIMARY_QUESTION_SELECTOR)
            page_info['has_question'] = True
            page_info['question_selector_used'] = cls.PRIMARY_QUESTION_SELECTOR
        except NoSuchElementException:
            for selector in cls.FALLBACK_SELECTORS:
                try:
                    driver.find_element(By.CSS_SELECTOR, selector)
                    page_info['question_selector_used'] = selector
                    break
                except NoSuchElementException:
                    continue

        return page_info

    @classmethod
    def validate_page_structure(cls, driver):
        """
        Validate that page has expected dotazník structure.

        Args:
            driver: Selenium WebDriver instance

        Returns:
            dict: Validation results
        """
        validation = {
            'is_valid_dotaznik': True,
            'issues': [],
            'warnings': [],
            'elements_found': {}
        }

        # Check for question element
        try:
            question_element = driver.find_element(By.CSS_SELECTOR, cls.PRIMARY_QUESTION_SELECTOR)
            validation['elements_found']['question'] = True

            if not question_element.text.strip():
                validation['warnings'].append("Question element found but has no text")

        except NoSuchElementException:
            validation['elements_found']['question'] = False
            validation['warnings'].append("Primary question selector not found")

        # Check for form elements
        form_selectors = {
            'inputs': 'input',
            'buttons': 'button',
            'selects': 'select',
            'textareas': 'textarea'
        }

        for element_type, selector in form_selectors.items():
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            validation['elements_found'][element_type] = len(elements)

        # Check for navigation elements
        nav_selectors = {
            'next_button': '#ls-button-submit, .ls-move-next-btn',
            'prev_button': '#ls-button-previous, .ls-move-previous-btn'
        }

        for nav_type, selector in nav_selectors.items():
            try:
                driver.find_element(By.CSS_SELECTOR, selector)
                validation['elements_found'][nav_type] = True
            except NoSuchElementException:
                validation['elements_found'][nav_type] = False

        # Determine if this is a valid dotazník page
        has_question = validation['elements_found'].get('question', False)
        has_inputs = validation['elements_found'].get('inputs', 0) > 0
        has_nav = (validation['elements_found'].get('next_button', False) or
                  validation['elements_found'].get('prev_button', False))

        if not (has_question or has_inputs or has_nav):
            validation['is_valid_dotaznik'] = False
            validation['issues'].append("Page doesn't appear to be a dotazník (no question, inputs, or navigation)")

        return validation