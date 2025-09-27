#!/usr/bin/env python3
"""
Enhanced Recorder for Evaluace Filler

Records user interactions on dotazník pages using JavaScript injection.
Captures clicks, inputs, and navigation with precise element selectors.
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from loguru import logger

from utils.page_identifier import PageIdentifier
from utils.navigation_manager import NavigationManager
from browser_manager import BrowserManager


class RecordingSession:
    """Manages a single recording session with all captured actions"""

    def __init__(self, session_name: str = None):
        self.session_id = str(uuid.uuid4())
        self.session_name = session_name or f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.actions = []
        self.page_history = []

    def add_action(self, action_type: str, element_selector: str, element_text: str,
                   value: str = None, page_id: str = None, **kwargs):
        """Add an action to the recording"""
        action = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "page_id": page_id or "unknown",
            "element_selector": element_selector,
            "element_text": element_text.strip()[:100] if element_text else "",
            "value": value,
            "metadata": kwargs
        }
        self.actions.append(action)
        logger.info(f"Action recorded: {action_type} on {element_selector}")

    def add_page_visit(self, page_id: str, url: str, title: str):
        """Record page visit"""
        page_visit = {
            "page_id": page_id,
            "url": url,
            "title": title,
            "timestamp": datetime.now().isoformat()
        }
        self.page_history.append(page_visit)
        logger.info(f"Page visit recorded: {page_id}")

    def save_to_json(self, filepath: str = None) -> str:
        """Save recording session to JSON file"""
        if not filepath:
            filepath = f"scenarios/recorded_sessions/{self.session_name}.json"

        session_data = {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_actions": len(self.actions),
            "pages_visited": len(self.page_history),
            "page_history": self.page_history,
            "actions": self.actions
        }

        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        logger.success(f"Recording saved to: {filepath}")
        return filepath


class EnhancedRecorder:
    """Enhanced recorder with JavaScript injection for real-time action capture"""

    def __init__(self, reuse_browser: bool = True):
        self.browser_manager = BrowserManager() if reuse_browser else None
        self.driver: Optional[webdriver.Chrome] = None
        self.session: Optional[RecordingSession] = None
        self.is_recording = False
        self.current_page_id = None
        self.reuse_browser = reuse_browser

        # WORKING JavaScript code (tested in console)
        self.capture_js = """
        console.log('=== INJECTING evaluaceRecorder ===');

        window.evaluaceRecorder = {
            actions: [],
            recording: false,

            generateSelector: function(element) {
                if (element.id) return '#' + element.id;
                if (element.className) return '.' + element.className.split(' ')[0];
                return element.tagName.toLowerCase();
            },

            captureAction: function(type, element, value) {
                console.log('CAPTURE ACTION CALLED:', type, element, value);

                var action = {
                    type: type,
                    selector: this.generateSelector(element),
                    text: element.textContent ? element.textContent.trim().substring(0, 100) : '',
                    value: value || '',
                    timestamp: new Date().toISOString(),
                    url: window.location.href,
                    tagName: element.tagName
                };

                this.actions.push(action);
                console.log('ACTION STORED:', action);
                console.log('TOTAL ACTIONS:', this.actions.length);
            },

            // Start recording
            startRecording: function() {
                console.log('=== startRecording called, current isActive:', this.isActive);
                if (this.isActive) {
                    console.log('Already recording, skipping');
                    return;
                }
                this.isActive = true;
                console.log('=== Recording started, isActive set to:', this.isActive);
                // DON'T clear existing actions - preserve them across navigation
                // this.actions = [];

                // Click event listener
                document.addEventListener('click', function(e) {
                    console.log('CLICK detected:', e.target.tagName, e.target.id, e.target.className);
                    window.evaluaceRecorder.captureAction('click', e.target);
                }, true);

                // Input change listeners
                document.addEventListener('change', function(e) {
                    console.log('CHANGE detected:', e.target.type, e.target.name, e.target.value);
                    if (e.target.type === 'radio' || e.target.type === 'checkbox') {
                        window.evaluaceRecorder.captureAction('check', e.target, e.target.checked);
                    } else {
                        window.evaluaceRecorder.captureAction('input', e.target, e.target.value);
                    }
                }, true);

                // Form submit listener
                document.addEventListener('submit', function(e) {
                    window.evaluaceRecorder.captureAction('submit', e.target);
                }, true);

                console.log('Recording started');
            },

            // Stop recording
            stopRecording: function() {
                this.isActive = false;
                console.log('Recording stopped');
            },

            // Get captured actions
            getActions: function() {
                return this.actions;
            },

            // Clear actions
            clearActions: function() {
                this.actions = [];
            }
        };

        console.log('=== evaluaceRecorder INJECTED ===');

        // FORCE START RECORDING IMMEDIATELY
        console.log('=== FORCE STARTING RECORDING ===');
        window.evaluaceRecorder.startRecording();
        console.log('=== isActive after force start:', window.evaluaceRecorder.isActive);

        // Return initialization status
        return window.evaluaceRecorder;
        """

    def setup_browser(self) -> bool:
        """Setup Chrome browser for recording"""
        try:
            if self.browser_manager:
                # Use browser manager for persistent browser
                logger.info("Using browser manager for persistent browser")
                self.driver = self.browser_manager.get_or_create_browser()
            else:
                # Traditional approach - new browser each time
                logger.info("Creating new browser instance")
                chrome_options = Options()
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument("--window-size=1200,800")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")

                service = Service("/usr/bin/chromedriver")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)

            if self.driver:
                logger.success("Browser setup completed for recording")
                return True
            else:
                logger.error("Failed to get browser instance")
                return False

        except Exception as e:
            logger.error(f"Failed to setup browser: {e}")
            return False

    def inject_capture_script(self) -> bool:
        """Inject JavaScript capture code into page"""
        try:
            result = self.driver.execute_script(self.capture_js)
            logger.success("Capture script injected successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to inject capture script: {e}")
            return False

    def start_recording(self, session_name: str = None) -> bool:
        """Start recording session"""
        if self.is_recording:
            logger.warning("Recording already in progress")
            return False

        self.session = RecordingSession(session_name)

        try:
            # IMPORTANT: Record current page visit FIRST
            self.record_page_visit()

            # Inject and start JavaScript recording
            if not self.inject_capture_script():
                return False

            self.driver.execute_script("window.evaluaceRecorder.startRecording();")
            self.is_recording = True

            logger.success(f"Recording started: {self.session.session_name}")
            logger.info(f"Initial page recorded: {self.current_page_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False

    def get_js_actions_safely(self) -> List[Dict]:
        """Safely get actions from JavaScript, handling missing context"""
        try:
            # Check if our recorder object exists
            exists = self.driver.execute_script("return typeof window.evaluaceRecorder !== 'undefined';")
            if not exists:
                logger.warning("JavaScript recorder context lost - re-injecting")
                self.inject_capture_script()
                return []

            # Get actions
            js_actions = self.driver.execute_script("return window.evaluaceRecorder.getActions();")
            return js_actions or []

        except Exception as e:
            logger.warning(f"Could not get JS actions: {e}")
            return []

    def stop_recording(self) -> Optional[str]:
        """Stop recording and save session"""
        if not self.is_recording:
            logger.warning("No recording in progress")
            return None

        try:
            # Try to stop JavaScript recording safely
            try:
                exists = self.driver.execute_script("return typeof window.evaluaceRecorder !== 'undefined';")
                if exists:
                    self.driver.execute_script("window.evaluaceRecorder.stopRecording();")
            except Exception as e:
                logger.warning(f"Could not stop JS recording cleanly: {e}")

            # Get captured actions from JavaScript
            js_actions = self.get_js_actions_safely()

            # Convert JS actions to our format
            for js_action in js_actions:
                self.session.add_action(
                    action_type=js_action.get('type', 'unknown'),
                    element_selector=js_action.get('selector', ''),
                    element_text=js_action.get('text', ''),
                    value=js_action.get('value', ''),
                    page_id=self.current_page_id,
                    js_metadata=js_action
                )

            # Save session
            filepath = self.session.save_to_json()
            self.is_recording = False

            logger.success(f"Recording stopped. {len(js_actions)} actions captured.")
            return filepath

        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            # Try to save what we have anyway
            if self.session:
                try:
                    filepath = self.session.save_to_json()
                    self.is_recording = False
                    logger.warning(f"Partial recording saved to: {filepath}")
                    return filepath
                except Exception as save_error:
                    logger.error(f"Could not save even partial recording: {save_error}")
            return None

    def record_page_visit(self) -> None:
        """Record current page visit"""
        if not self.session:
            return

        try:
            current_url = self.driver.current_url
            current_title = self.driver.title
            self.current_page_id = PageIdentifier.get_page_id(self.driver)

            self.session.add_page_visit(self.current_page_id, current_url, current_title)

            # Re-inject script on new pages
            self.inject_capture_script()
            if self.is_recording:
                self.driver.execute_script("window.evaluaceRecorder.startRecording();")

        except Exception as e:
            logger.error(f"Failed to record page visit: {e}")

    def sync_js_actions(self) -> int:
        """Sync actions from JavaScript to Python session"""
        if not self.is_recording or not self.session:
            logger.debug("Not recording or no session - skipping sync")
            return 0

        # CHECK FOR NAVIGATION CHANGES (Page ID, not URL - LimeSurvey keeps same URL!)
        try:
            current_page_id = PageIdentifier.get_page_id(self.driver)

            # Check if we've navigated to a new page (different page ID)
            if hasattr(self, 'current_page_id') and self.current_page_id != current_page_id:
                logger.info(f"Page navigation detected (Page ID changed):")
                logger.info(f"  Old page: {self.current_page_id}")
                logger.info(f"  New page: {current_page_id}")

                # Record new page visit and re-inject JavaScript
                self.record_page_visit()
                logger.success("JavaScript re-injected after navigation")

            # Also check if JavaScript context is lost
            elif hasattr(self, 'current_page_id'):
                try:
                    js_exists = self.driver.execute_script("return typeof window.evaluaceRecorder !== 'undefined'")
                    if not js_exists:
                        logger.warning("JavaScript context lost - re-injecting")
                        self.record_page_visit()
                        logger.success("JavaScript re-injected after context loss")
                except:
                    logger.warning("Could not check JavaScript context - assuming lost, re-injecting")
                    self.record_page_visit()

        except Exception as e:
            logger.warning(f"Failed to check navigation: {e}")

        js_actions = self.get_js_actions_safely()
        logger.debug(f"Got {len(js_actions)} JavaScript actions to sync")

        synced_count = 0
        current_action_count = len(self.session.actions)

        for js_action in js_actions:
            # Simple deduplication based on timestamp and selector
            timestamp = js_action.get('timestamp', '')
            selector = js_action.get('selector', '')

            # Check if we already have this action (simple check)
            already_exists = any(
                action.get('js_metadata', {}).get('timestamp') == timestamp and
                action.get('element_selector') == selector
                for action in self.session.actions
            )

            if not already_exists:
                logger.debug(f"Adding new action: {js_action.get('type')} on {selector}")
                self.session.add_action(
                    action_type=js_action.get('type', 'unknown'),
                    element_selector=js_action.get('selector', ''),
                    element_text=js_action.get('text', ''),
                    value=js_action.get('value', ''),
                    page_id=self.current_page_id,
                    js_metadata=js_action
                )
                synced_count += 1
            else:
                logger.debug(f"Skipping duplicate action: {js_action.get('type')} on {selector}")

        if synced_count > 0:
            logger.info(f"Synced {synced_count} new actions from JavaScript")
        else:
            logger.debug("No new actions to sync")

        return synced_count

    def get_recording_status(self) -> Dict[str, Any]:
        """Get current recording status"""
        if not self.session:
            return {"recording": False, "session": None}

        # Sync any pending JS actions first
        if self.is_recording:
            self.sync_js_actions()

        try:
            exists = self.driver.execute_script("return typeof window.evaluaceRecorder !== 'undefined';")
            js_actions_count = 0
            if exists:
                js_actions_count = self.driver.execute_script("return window.evaluaceRecorder.actions.length;")
        except:
            js_actions_count = 0

        return {
            "recording": self.is_recording,
            "session_name": self.session.session_name,
            "session_id": self.session.session_id,
            "actions_captured": len(self.session.actions),
            "js_actions_pending": js_actions_count,
            "pages_visited": len(self.session.page_history),
            "current_page_id": self.current_page_id,
            "js_context_exists": exists if 'exists' in locals() else False
        }

    def cleanup(self, keep_browser_alive: bool = None) -> None:
        """Clean up resources"""
        if self.is_recording:
            self.stop_recording()

        if self.driver:
            try:
                # Use parameter or default to reuse_browser setting
                keep_alive = keep_browser_alive if keep_browser_alive is not None else self.reuse_browser

                if keep_alive and self.browser_manager:
                    # Close Selenium connection but keep browser running
                    self.browser_manager.close_connection_only()
                    logger.info("Selenium connection closed, browser kept alive for reuse")
                else:
                    # Traditional cleanup - close browser completely
                    self.driver.quit()
                    logger.info("Browser closed completely")

                self.driver = None
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

    def force_close_browser(self) -> None:
        """Force close browser completely"""
        if self.browser_manager:
            self.browser_manager.force_close_browser()
        elif self.driver:
            self.driver.quit()

        self.driver = None
        logger.info("Browser force closed")


def main():
    """Demo/test function for Enhanced Recorder"""
    print("🎬 Enhanced Recorder Demo")
    print("=" * 50)

    recorder = EnhancedRecorder()

    try:
        # Setup browser
        if not recorder.setup_browser():
            print("❌ Failed to setup browser")
            return 1

        # Navigate to blank page
        recorder.driver.get("about:blank")
        print("🌐 Browser opened. Navigate to your dotazník.")

        # Start recording
        session_name = f"demo_recording_{datetime.now().strftime('%H%M%S')}"
        print(f"🔴 Starting recording: {session_name}")

        if not recorder.start_recording(session_name):
            print("❌ Failed to start recording")
            return 1

        print("\n📋 INSTRUCTIONS:")
        print("1. Navigate to dotazník in the browser")
        print("2. Fill out some questions")
        print("3. Click navigation buttons")
        print("4. Press ENTER here when done recording")

        input("\n⏹️  Press ENTER to stop recording...")

        # Stop recording
        filepath = recorder.stop_recording()
        if filepath:
            print(f"✅ Recording saved to: {filepath}")

            # Show summary
            status = recorder.get_recording_status()
            print(f"📊 Summary: {status['actions_captured']} actions, {status['pages_visited']} pages")
        else:
            print("❌ Failed to save recording")

    except KeyboardInterrupt:
        print("\n⚠️  Recording interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        recorder.cleanup()

    return 0


if __name__ == "__main__":
    exit(main())