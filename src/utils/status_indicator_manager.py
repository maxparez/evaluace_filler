#!/usr/bin/env python3
"""
Status Indicator Manager
Python wrapper for managing visual status indicators during automation
"""

from typing import Optional
from loguru import logger


class StatusIndicatorManager:
    """Manages visual status indicators in the browser during automation"""

    def __init__(self, driver):
        """Initialize with Selenium WebDriver instance"""
        self.driver = driver
        self.js_loader = None
        self.status_js_loaded = False

        # Import JavaScript loader
        try:
            from javascript_loader import JavaScriptLoader
            self.js_loader = JavaScriptLoader()
            logger.debug("StatusIndicatorManager initialized with JavaScriptLoader")
        except ImportError:
            logger.warning("JavaScriptLoader not available, using inline JS")

    def _ensure_status_js_loaded(self) -> bool:
        """Ensure status indicator JavaScript is loaded in the browser"""

        # Always check if the JavaScript object is available, regardless of loaded flag
        try:
            # Check if AutomationStatusIndicator exists and is properly initialized
            js_check = """
            return typeof window.AutomationStatusIndicator !== 'undefined' &&
                   typeof window.AutomationStatusIndicator.setStatusWithProgress === 'function';
            """
            is_available = self.driver.execute_script(js_check)

            if is_available and self.status_js_loaded:
                return True

        except Exception as e:
            logger.debug(f"JavaScript availability check failed: {e}")
            is_available = False

        # If not available or not loaded, load and initialize
        try:
            logger.debug("Loading/reloading status indicator JavaScript...")

            # Load status indicator JavaScript
            if self.js_loader:
                status_js = self.js_loader.load_script('status_indicator')
                self.driver.execute_script(status_js)
                logger.debug("Status indicator JS loaded via JavaScriptLoader")
            else:
                # Fallback: Load from file directly
                import os
                from pathlib import Path

                js_path = Path(__file__).parent.parent / 'js_scripts' / 'status_indicator.js'
                if js_path.exists():
                    with open(js_path, 'r', encoding='utf-8') as f:
                        status_js = f.read()
                    self.driver.execute_script(status_js)
                    logger.debug("Status indicator JS loaded from file")
                else:
                    logger.error(f"Status indicator JS file not found: {js_path}")
                    return False

            # Verify the object is now available
            is_available = self.driver.execute_script(js_check)

            if not is_available:
                logger.error("AutomationStatusIndicator object not available after loading")
                return False

            # Initialize the status indicator
            result = self.driver.execute_script("return window.AutomationStatusIndicator.init();")

            if result:
                self.status_js_loaded = True
                logger.success("Status indicator system initialized successfully")
                return True
            else:
                logger.error("Failed to initialize status indicator system")
                return False

        except Exception as e:
            logger.error(f"Failed to load status indicator JS: {e}")
            return False

    def set_status(self, status: str, custom_text: Optional[str] = None) -> bool:
        """Set the status of the visual indicator

        Args:
            status: Status key (running, processing, waiting, manual_required, error, completed, inactive)
            custom_text: Optional custom text override

        Returns:
            bool: Success status
        """
        if not self._ensure_status_js_loaded():
            return False

        try:
            if custom_text:
                result = self.driver.execute_script(
                    "return window.AutomationStatusIndicator.setStatus(arguments[0], arguments[1]);",
                    status, custom_text
                )
            else:
                result = self.driver.execute_script(
                    "return window.AutomationStatusIndicator.setStatus(arguments[0]);",
                    status
                )

            if result:
                logger.debug(f"Status set to: {status}" + (f" - {custom_text}" if custom_text else ""))

            return bool(result)

        except Exception as e:
            logger.error(f"Failed to set status: {e}")
            return False

    def set_status_with_progress(self, status: str, current: int, total: Optional[int] = None, action: Optional[str] = None) -> bool:
        """Set status with progress information

        Args:
            status: Status key
            current: Current step/page number
            total: Total steps/pages (optional)
            action: Current action description

        Returns:
            bool: Success status
        """
        if not self._ensure_status_js_loaded():
            return False

        try:
            # Double-check that the object is available before calling
            check_js = """
            return typeof window.AutomationStatusIndicator !== 'undefined' &&
                   typeof window.AutomationStatusIndicator.setStatusWithProgress === 'function';
            """

            if not self.driver.execute_script(check_js):
                logger.warning("AutomationStatusIndicator not available, attempting to reload...")
                if not self._ensure_status_js_loaded():
                    logger.error("Failed to reload status indicator JavaScript")
                    return False

            result = self.driver.execute_script(
                "return window.AutomationStatusIndicator.setStatusWithProgress(arguments[0], arguments[1], arguments[2], arguments[3]);",
                status, current, total, action
            )

            return bool(result)

        except Exception as e:
            logger.error(f"Failed to set status with progress: {e}")
            logger.debug(f"Status: {status}, Current: {current}, Total: {total}, Action: {action}")

            # Try to diagnose the issue
            try:
                exists = self.driver.execute_script("return typeof window.AutomationStatusIndicator;")
                logger.debug(f"AutomationStatusIndicator type: {exists}")

                if exists != 'undefined':
                    methods = self.driver.execute_script(
                        "return Object.getOwnPropertyNames(window.AutomationStatusIndicator);"
                    )
                    logger.debug(f"Available methods: {methods}")

            except Exception as diag_e:
                logger.debug(f"Diagnostic check failed: {diag_e}")

            return False

    def set_manual_required(self, reason: str, suggestion: Optional[str] = None) -> bool:
        """Set manual intervention required status

        Args:
            reason: Reason for manual intervention
            suggestion: Suggested action for user

        Returns:
            bool: Success status
        """
        if not self._ensure_status_js_loaded():
            return False

        try:
            result = self.driver.execute_script(
                "return window.AutomationStatusIndicator.setManualRequired(arguments[0], arguments[1]);",
                reason, suggestion or ""
            )

            logger.warning(f"Manual intervention required: {reason}")
            return bool(result)

        except Exception as e:
            logger.error(f"Failed to set manual required status: {e}")
            return False

    def show(self) -> bool:
        """Show the status indicator"""
        if not self._ensure_status_js_loaded():
            return False

        try:
            self.driver.execute_script("window.AutomationStatusIndicator.show();")
            return True
        except Exception as e:
            logger.error(f"Failed to show status indicator: {e}")
            return False

    def hide(self) -> bool:
        """Hide the status indicator"""
        if not self._ensure_status_js_loaded():
            return False

        try:
            self.driver.execute_script("window.AutomationStatusIndicator.hide();")
            return True
        except Exception as e:
            logger.error(f"Failed to hide status indicator: {e}")
            return False

    def remove(self) -> bool:
        """Remove the status indicator completely"""
        if not self.status_js_loaded:
            return True  # Already removed/not loaded

        try:
            self.driver.execute_script("window.AutomationStatusIndicator.remove();")
            self.status_js_loaded = False
            return True
        except Exception as e:
            logger.error(f"Failed to remove status indicator: {e}")
            return False

    def get_current_status(self) -> Optional[str]:
        """Get the current status of the indicator

        Returns:
            str: Current status or None if not available
        """
        if not self._ensure_status_js_loaded():
            return None

        try:
            status = self.driver.execute_script("return window.AutomationStatusIndicator.getStatus();")
            return status
        except Exception as e:
            logger.error(f"Failed to get current status: {e}")
            return None

    def is_visible(self) -> bool:
        """Check if the status indicator is currently visible

        Returns:
            bool: True if visible, False otherwise
        """
        if not self._ensure_status_js_loaded():
            return False

        try:
            visible = self.driver.execute_script("return window.AutomationStatusIndicator.isVisible();")
            return bool(visible)
        except Exception as e:
            logger.error(f"Failed to check visibility: {e}")
            return False

    # Convenience methods for common statuses
    def start_automation(self, page_number: int = 1, total_pages: Optional[int] = None):
        """Start automation status"""
        self.set_status_with_progress('running', page_number, total_pages, 'Zahajuji automatické vyplňování')

    def processing_page(self, page_number: int, action: str = 'Zpracovávám'):
        """Processing page status"""
        self.set_status_with_progress('processing', page_number, None, action)

    def waiting_for_page(self, page_number: int):
        """Deprecated: Page transition status (now skipped for smoother UX)"""
        # No longer used - transitions are too fast and disruptive
        pass

    def automation_completed(self):
        """Automation completed successfully"""
        self.set_status('completed')

    def automation_error(self, error_message: str):
        """Automation error occurred"""
        self.set_status('error', f'❌ Chyba: {error_message}')

    def require_manual_intervention(self, reason: str, suggestion: str = 'Zkontrolujte stránku a pokračujte ručně'):
        """Require manual intervention"""
        self.set_manual_required(reason, suggestion)