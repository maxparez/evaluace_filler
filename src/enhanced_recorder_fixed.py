#!/usr/bin/env python3
"""
Enhanced Recorder for Evaluace Filler - FIXED VERSION
Uses proven working JavaScript from test_persistent_js.py
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

    def add_page_visit(self, page_id: str, url: str, title: str):
        """Add a page visit to the session"""
        page_visit = {
            "page_id": page_id,
            "url": url,
            "title": title,
            "timestamp": datetime.now().isoformat()
        }
        self.page_history.append(page_visit)

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_actions": len(self.actions),
            "pages_visited": len(self.page_history),
            "page_history": self.page_history,
            "actions": self.actions
        }


class EnhancedRecorderFixed:
    """Enhanced Recorder with proven working JavaScript"""

    def __init__(self, reuse_browser: bool = True):
        self.driver: Optional[webdriver.Chrome] = None
        self.browser_manager: Optional[BrowserManager] = None
        self.session: Optional[RecordingSession] = None
        self.is_recording = False
        self.current_page_id = None
        self.reuse_browser = reuse_browser

        # PROVEN WORKING JavaScript (from successful test_persistent_js.py)
        self.capture_js = """
        console.log('=== INJECTING evaluaceRecorder ===');

        window.evaluaceRecorder = {
            actions: [],
            recording: false,

            captureAction: function(type, element, value) {
                console.log('CAPTURE ACTION CALLED:', type, element, value);
                var action = {
                    type: type,
                    selector: element.id ? '#' + element.id : (element.className ? '.' + element.className.split(' ')[0] : element.tagName.toLowerCase()),
                    text: element.textContent ? element.textContent.trim().substring(0, 100) : '',
                    value: value || '',
                    timestamp: new Date().toISOString(),
                    url: window.location.href,
                    tagName: element.tagName,
                    pageId: document.querySelector('.question-text .ls-label-question') ?
                            document.querySelector('.question-text .ls-label-question').textContent.trim() :
                            'unknown'
                };
                this.actions.push(action);
                console.log('ACTION STORED:', action);
                console.log('TOTAL ACTIONS:', this.actions.length);
            },

            startRecording: function() {
                console.log('=== STARTING RECORDING ===');
                if (this.recording) {
                    console.log('Already recording');
                    return;
                }
                this.recording = true;

                document.addEventListener('click', function(e) {
                    console.log('CLICK detected:', e.target);
                    window.evaluaceRecorder.captureAction('click', e.target);
                }, true);

                document.addEventListener('change', function(e) {
                    console.log('CHANGE detected:', e.target);
                    if (e.target.type === 'radio' || e.target.type === 'checkbox') {
                        window.evaluaceRecorder.captureAction('check', e.target, e.target.checked);
                    } else {
                        window.evaluaceRecorder.captureAction('input', e.target, e.target.value);
                    }
                }, true);

                console.log('Recording started successfully');
            },

            stopRecording: function() {
                this.recording = false;
                console.log('Recording stopped');
            },

            getActions: function() {
                return this.actions;
            },

            isAlive: function() {
                return true;
            }
        };

        console.log('=== evaluaceRecorder INJECTED ===');

        // AUTO START RECORDING
        console.log('=== AUTO STARTING RECORDING ===');
        window.evaluaceRecorder.startRecording();
        console.log('=== Recording active:', window.evaluaceRecorder.recording);

        return window.evaluaceRecorder;
        """

    def setup_browser(self) -> bool:
        """Setup Chrome browser for recording"""
        try:
            if self.reuse_browser:
                # Connect to existing persistent browser
                logger.info("Connecting to existing persistent browser")
                manager = BrowserManager()
                if not manager.is_browser_running():
                    logger.error("No browser running on port 9222")
                    return False

                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.success("Connected to existing browser on port 9222")
            else:
                # Create new browser
                logger.info("Creating new browser instance")
                chrome_options = Options()
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument("--window-size=1200,800")

                service = Service("/usr/bin/chromedriver")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)

            if not self.driver:
                logger.error("Failed to create browser instance")
                return False

            logger.success("Browser setup completed for recording")
            return True

        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            return False

    def inject_capture_script(self) -> bool:
        """Inject JavaScript capture script"""
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

        # Setup browser if needed
        if not self.driver:
            if self.reuse_browser:
                self.browser_manager = BrowserManager()

            if not self.setup_browser():
                return False

        self.session = RecordingSession(session_name)

        try:
            # Record current page visit FIRST
            self.record_page_visit()

            # Inject and start JavaScript recording
            if not self.inject_capture_script():
                return False

            self.is_recording = True

            logger.success(f"Recording started: {self.session.session_name}")
            logger.info(f"Initial page recorded: {self.current_page_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False

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
                    page_id=js_action.get('pageId', self.current_page_id),
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
            # Final sync
            synced = self.sync_js_actions()
            logger.info(f"Final sync captured {synced} actions")

            # Try to stop JavaScript recording safely
            try:
                exists = self.driver.execute_script("return typeof window.evaluaceRecorder !== 'undefined';")
                if exists:
                    self.driver.execute_script("window.evaluaceRecorder.stopRecording();")
            except:
                pass

            # Save session
            filename = f"scenarios/recorded_sessions/{self.session.session_name}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.session.to_dict(), f, indent=2, ensure_ascii=False)

            self.is_recording = False
            logger.success(f"Recording saved to: {filename}")
            logger.success(f"Recording stopped. {len(self.session.actions)} actions captured.")

            return filename

        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            return None

    def get_recording_status(self) -> Dict[str, Any]:
        """Get current recording status"""
        if not self.session:
            return {"recording": False, "session": None}

        return {
            "recording": self.is_recording,
            "session": self.session.session_name,
            "actions_captured": len(self.session.actions),
            "pages_visited": len(self.session.page_history),
            "current_page": self.current_page_id
        }

    def cleanup(self, keep_browser_alive: bool = False):
        """Clean up resources"""
        if self.is_recording:
            self.stop_recording()

        if self.driver and not keep_browser_alive:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except:
                pass
        elif keep_browser_alive:
            logger.info("Selenium connection closed, browser kept alive for reuse")