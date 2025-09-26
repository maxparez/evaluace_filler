#!/usr/bin/env python3
"""
DOM Inspector for Real Dotaznik Analysis

This script opens a GUI browser window for manual navigation to real dotazníky
and tests our PageIdentifier and NavigationManager utilities against real pages.

Usage:
    python src/dom_inspector.py --url "https://example-dotaznik.cz"
    python src/dom_inspector.py --interactive  # Opens blank page for manual navigation
"""

import sys
import time
import argparse
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from loguru import logger

# Import our utilities
from utils.page_identifier import PageIdentifier
from utils.navigation_manager import NavigationManager


class DOMInspector:
    """Interactive DOM inspector for real dotazník analysis"""

    def __init__(self, headless: bool = False):
        self.driver: Optional[webdriver.Chrome] = None
        self.navigation_manager: Optional[NavigationManager] = None
        self.headless = headless

    def setup_browser(self) -> bool:
        """Setup Chrome browser with GUI mode"""
        try:
            chrome_options = Options()
            if not self.headless:
                # GUI mode for manual testing
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument("--window-size=1200,800")
            else:
                chrome_options.add_argument("--headless")

            # Standard Chrome options
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # Try to use system ChromeDriver first
            try:
                service = Service("/usr/bin/chromedriver")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.warning(f"System chromedriver failed: {e}")
                # Fallback to webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Initialize our utilities
            # PageIdentifier uses classmethod, no instantiation needed
            self.navigation_manager = NavigationManager(self.driver)

            logger.success("Browser setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to setup browser: {e}")
            return False

    def navigate_to_url(self, url: str) -> bool:
        """Navigate to specified URL"""
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            logger.success(f"Successfully navigated to {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False

    def analyze_current_page(self) -> Dict[str, Any]:
        """Analyze current page with our utilities"""
        analysis = {
            "url": self.driver.current_url,
            "title": self.driver.title,
            "page_id": None,
            "navigation_buttons": {},
            "selectors_found": {},
            "page_source_length": len(self.driver.page_source)
        }

        try:
            # Test PageIdentifier
            logger.info("Testing PageIdentifier...")
            page_id = PageIdentifier.get_page_id(self.driver)
            analysis["page_id"] = page_id
            logger.info(f"Page ID detected: {page_id}")

            # Test selector presence
            selectors_to_test = [
                ".question-text .ls-label-question",
                ".question-text",
                ".ls-label-question",
                "h1", "h2", ".page-title",
                "#ls-button-submit",
                "#ls-button-previous"
            ]

            for selector in selectors_to_test:
                try:
                    elements = self.driver.find_elements("css selector", selector)
                    analysis["selectors_found"][selector] = {
                        "count": len(elements),
                        "texts": [elem.text.strip()[:50] for elem in elements[:3]]  # First 3 elements
                    }
                except Exception as e:
                    analysis["selectors_found"][selector] = {"error": str(e)}

            # Test NavigationManager
            logger.info("Testing NavigationManager...")
            nav_info = self.navigation_manager.get_navigation_state()
            analysis["navigation_buttons"] = nav_info

            logger.success("Page analysis completed")

        except Exception as e:
            logger.error(f"Error during page analysis: {e}")
            analysis["analysis_error"] = str(e)

        return analysis

    def print_analysis(self, analysis: Dict[str, Any]) -> None:
        """Print formatted analysis results"""
        print("\n" + "="*80)
        print("🔍 DOM ANALYSIS RESULTS")
        print("="*80)
        print(f"URL: {analysis['url']}")
        print(f"Title: {analysis['title']}")
        print(f"Page Source Length: {analysis['page_source_length']} characters")
        print(f"Page ID: {analysis['page_id']}")

        print("\n📍 SELECTOR ANALYSIS:")
        for selector, result in analysis["selectors_found"].items():
            if "error" in result:
                print(f"  ❌ {selector}: ERROR - {result['error']}")
            else:
                count = result["count"]
                texts = result["texts"]
                status = "✅" if count > 0 else "❌"
                print(f"  {status} {selector}: {count} elements")
                if texts:
                    for i, text in enumerate(texts):
                        print(f"     [{i+1}] {text}")

        print("\n🧭 NAVIGATION ANALYSIS:")
        nav_buttons = analysis["navigation_buttons"]
        if nav_buttons:
            print(f"  Next Button: {'✅' if nav_buttons.get('can_go_next', False) else '❌'} - '{nav_buttons.get('next_button_text', '')}' (selector: {nav_buttons.get('next_selector_used', 'none')})")
            print(f"  Prev Button: {'✅' if nav_buttons.get('can_go_back', False) else '❌'} - '{nav_buttons.get('prev_button_text', '')}' (selector: {nav_buttons.get('prev_selector_used', 'none')})")
            print(f"  Is Final Page: {nav_buttons.get('is_final_page', False)}")

        if "analysis_error" in analysis:
            print(f"\n❌ ANALYSIS ERROR: {analysis['analysis_error']}")

        print("="*80)

    def interactive_session(self) -> None:
        """Run interactive session for manual testing"""
        print("\n🚀 DOM Inspector - Interactive Session")
        print("="*50)
        print("Commands:")
        print("  'analyze' or 'a' - Analyze current page")
        print("  'url <URL>' - Navigate to URL")
        print("  'refresh' or 'r' - Refresh current page")
        print("  'quit' or 'q' - Exit session")
        print("="*50)

        while True:
            try:
                command = input("\n> ").strip().lower()

                if command in ['quit', 'q']:
                    break
                elif command in ['analyze', 'a']:
                    analysis = self.analyze_current_page()
                    self.print_analysis(analysis)
                elif command in ['refresh', 'r']:
                    self.driver.refresh()
                    time.sleep(2)
                    logger.info("Page refreshed")
                elif command.startswith('url '):
                    url = command[4:].strip()
                    if self.navigate_to_url(url):
                        # Auto-analyze after navigation
                        analysis = self.analyze_current_page()
                        self.print_analysis(analysis)
                elif command == '':
                    continue
                else:
                    print("❌ Unknown command. Use 'analyze', 'url <URL>', 'refresh', or 'quit'")

            except KeyboardInterrupt:
                print("\n👋 Interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in interactive session: {e}")

    def cleanup(self) -> None:
        """Clean up browser resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="DOM Inspector for real dotazník analysis")
    parser.add_argument("--url", type=str, help="URL to navigate to initially")
    parser.add_argument("--interactive", action="store_true", help="Start interactive session")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    args = parser.parse_args()

    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

    inspector = DOMInspector(headless=args.headless)

    try:
        # Setup browser
        if not inspector.setup_browser():
            logger.error("Failed to setup browser. Exiting.")
            return 1

        # Navigate to URL if provided
        if args.url:
            if inspector.navigate_to_url(args.url):
                analysis = inspector.analyze_current_page()
                inspector.print_analysis(analysis)
            else:
                logger.error("Failed to navigate to initial URL")
                return 1
        elif args.interactive:
            # Start with blank page for manual navigation
            inspector.navigate_to_url("about:blank")

        # Start interactive session
        if args.interactive or not args.url:
            inspector.interactive_session()

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    finally:
        inspector.cleanup()

    return 0


if __name__ == "__main__":
    exit(main())