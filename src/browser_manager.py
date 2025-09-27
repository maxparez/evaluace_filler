#!/usr/bin/env python3
"""
Browser Manager for Evaluace Filler

Manages persistent browser sessions that can be reused across multiple recorder runs.
Uses Chrome remote debugging to connect to existing browser instances.
"""

import json
import time
import psutil
import requests
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger

try:
    from .config import Config
except ImportError:
    # Fallback for when imported from test or other contexts
    from config import Config


class BrowserManager:
    """Manages persistent browser instances for recorder reuse"""

    def __init__(self, debug_port: int = None, user_data_dir: str = None):
        self.debug_port = debug_port or Config.CHROME_DEBUG_PORT
        self.user_data_dir = user_data_dir or Config.CHROME_USER_DATA_DIR
        self.driver: Optional[webdriver.Chrome] = None

    def is_browser_running(self) -> bool:
        """Check if Chrome is running on our debug port"""
        try:
            response = requests.get(f"http://localhost:{self.debug_port}/json/version", timeout=2)
            return response.status_code == 200
        except:
            return False

    def get_browser_info(self) -> Optional[Dict[str, Any]]:
        """Get information about running browser"""
        try:
            response = requests.get(f"http://localhost:{self.debug_port}/json/version", timeout=2)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.debug(f"Could not get browser info: {e}")
        return None

    def get_active_tabs(self) -> list:
        """Get list of active tabs"""
        try:
            response = requests.get(f"http://localhost:{self.debug_port}/json", timeout=2)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.debug(f"Could not get active tabs: {e}")
        return []

    def start_new_browser(self) -> Optional[webdriver.Chrome]:
        """Start new persistent browser with remote debugging"""
        try:
            chrome_options = Options()

            # Remote debugging setup
            chrome_options.add_argument(f"--remote-debugging-port={self.debug_port}")
            chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")

            # Standard options
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f"--window-size={Config.BROWSER_WINDOW_SIZE}")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            if Config.BROWSER_HEADLESS:
                chrome_options.add_argument("--headless")

            # Keep browser alive
            chrome_options.add_experimental_option("detach", True)

            # Use webdriver-manager for automatic chromedriver management
            chromedriver_path = ChromeDriverManager().install()
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            logger.success(f"New browser started on port {self.debug_port}")
            return self.driver

        except Exception as e:
            logger.error(f"Failed to start new browser: {e}")
            return None

    def connect_to_existing_browser(self, prefer_survey_tab: bool = True) -> Optional[webdriver.Chrome]:
        """Connect to existing browser via remote debugging"""
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"localhost:{self.debug_port}")

            # These options don't apply when connecting to existing browser
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")

            # No service needed when connecting to existing browser
            self.driver = webdriver.Chrome(options=chrome_options)

            logger.success(f"Connected to existing browser on port {self.debug_port}")
            return self.driver

        except Exception as e:
            logger.error(f"Failed to connect to existing browser: {e}")
            return None

    def get_or_create_browser(self, keep_alive: bool = True) -> Optional[webdriver.Chrome]:
        """Get existing browser or create new one"""

        # Check if browser is already running
        if self.is_browser_running():
            logger.info("Found existing browser, connecting...")
            browser_info = self.get_browser_info()
            if browser_info:
                logger.info(f"Browser version: {browser_info.get('Browser', 'unknown')}")

            tabs = self.get_active_tabs()
            logger.info(f"Found {len(tabs)} active tabs")

            # Try to connect
            driver = self.connect_to_existing_browser()
            if driver:
                # Test connection
                try:
                    current_url = driver.current_url
                    logger.info(f"Connected successfully, current URL: {current_url}")
                    self.driver = driver
                    return driver
                except Exception as e:
                    logger.warning(f"Connected but communication failed: {e}")
                    driver.quit()

        # Start new browser
        logger.info("Starting new persistent browser...")
        driver = self.start_new_browser()
        if driver:
            self.driver = driver
            # Navigate to blank page initially
            driver.get("about:blank")

        return driver

    def close_connection_only(self):
        """Close Selenium connection but keep browser running"""
        if self.driver:
            try:
                # Don't call driver.quit() - that would close the browser
                # Just clear our reference
                self.driver = None
                logger.info("Selenium connection closed, browser still running")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

    def force_close_browser(self):
        """Force close the browser completely"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("Browser closed completely")
            except Exception as e:
                logger.error(f"Error force closing browser: {e}")

        # Kill any remaining Chrome processes on our port
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    if f"--remote-debugging-port={self.debug_port}" in cmdline:
                        logger.info(f"Killing Chrome process {proc.info['pid']}")
                        proc.kill()
        except Exception as e:
            logger.debug(f"Error killing Chrome processes: {e}")

    def show_status(self):
        """Show current browser status"""
        print(f"\n🌐 BROWSER STATUS (port {self.debug_port}):")

        if self.is_browser_running():
            print("  ✅ Browser is running")

            browser_info = self.get_browser_info()
            if browser_info:
                print(f"  📋 Version: {browser_info.get('Browser', 'unknown')}")
                print(f"  🔗 WebKit: {browser_info.get('WebKit-Version', 'unknown')}")

            tabs = self.get_active_tabs()
            print(f"  📑 Active tabs: {len(tabs)}")

            for i, tab in enumerate(tabs[:3]):  # Show first 3 tabs
                title = tab.get('title', 'No title')[:50]
                url = tab.get('url', 'No URL')[:60]
                print(f"     [{i+1}] {title}")
                print(f"         {url}")

            if len(tabs) > 3:
                print(f"     ... and {len(tabs) - 3} more tabs")
        else:
            print("  ❌ No browser running")

        if self.driver:
            try:
                current_url = self.driver.current_url
                print(f"  🔗 Selenium connected to: {current_url[:60]}")
            except:
                print("  ⚠️  Selenium connection lost")
        else:
            print("  📡 No Selenium connection")


def main():
    """Test browser manager"""
    print("🌐 BROWSER MANAGER TEST")
    print("=" * 40)

    manager = BrowserManager()

    try:
        manager.show_status()

        print("\n🚀 Getting or creating browser...")
        driver = manager.get_or_create_browser()

        if driver:
            print("✅ Browser ready!")
            manager.show_status()

            print("\n📋 Commands:")
            print("  'status' - show browser status")
            print("  'navigate <url>' - navigate to URL")
            print("  'close' - close connection only (keep browser)")
            print("  'kill' - force close browser")
            print("  'quit' - exit")

            while True:
                try:
                    cmd = input("\n> ").strip().lower()

                    if cmd == 'quit':
                        break
                    elif cmd == 'status':
                        manager.show_status()
                    elif cmd.startswith('navigate '):
                        url = cmd[9:]
                        driver.get(url)
                        print(f"✅ Navigated to: {url}")
                    elif cmd == 'close':
                        manager.close_connection_only()
                        print("✅ Connection closed, browser still running")
                        break
                    elif cmd == 'kill':
                        manager.force_close_browser()
                        print("✅ Browser killed completely")
                        break
                    else:
                        print("❌ Unknown command")

                except KeyboardInterrupt:
                    print("\n👋 Interrupted")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")

        else:
            print("❌ Failed to get browser")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Default: close connection only, keep browser running
        if manager.driver:
            manager.close_connection_only()


if __name__ == "__main__":
    main()