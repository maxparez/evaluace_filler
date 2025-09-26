#!/usr/bin/env python3
"""
Simple Working Recorder - based on successful debug test
Uses PROVEN JavaScript that captures actions correctly
"""

import sys
import os
import time
import json
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from loguru import logger
from browser_manager import BrowserManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from utils.page_identifier import PageIdentifier

# WORKING JavaScript from debug test
WORKING_JS = """
console.log('=== SIMPLE RECORDER INJECTION ===');

window.simpleRecorder = {
    actions: [],
    recording: false,

    captureAction: function(type, element, value) {
        if (!this.recording) return;

        console.log('ACTION CAPTURED:', type, element.tagName);
        var action = {
            id: 'action_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
            timestamp: new Date().toISOString(),
            action_type: type,
            element_selector: element.id ? '#' + element.id :
                           (element.className ? '.' + element.className.split(' ')[0] : element.tagName.toLowerCase()),
            element_text: element.textContent ? element.textContent.trim().substring(0, 100) : '',
            value: value !== undefined ? value : '',
            page_id: document.querySelector('.question-text .ls-label-question') ?
                    document.querySelector('.question-text .ls-label-question').textContent.trim() :
                    'unknown',
            metadata: {
                js_metadata: {
                    pageId: document.querySelector('.question-text .ls-label-question') ?
                           document.querySelector('.question-text .ls-label-question').textContent.trim() :
                           'unknown',
                    selector: element.id ? '#' + element.id :
                             (element.className ? '.' + element.className.split(' ')[0] : element.tagName.toLowerCase()),
                    tagName: element.tagName,
                    text: element.textContent ? element.textContent.trim().substring(0, 100) : '',
                    timestamp: new Date().toISOString(),
                    type: type,
                    url: window.location.href,
                    value: value !== undefined ? value : ''
                }
            }
        };

        this.actions.push(action);
        console.log('ACTION STORED - Total actions:', this.actions.length);
        return action;
    },

    startRecording: function() {
        console.log('=== STARTING SIMPLE RECORDING ===');
        if (this.recording) {
            console.log('Already recording');
            return;
        }
        this.recording = true;

        // Click listener
        document.addEventListener('click', function(e) {
            console.log('CLICK detected:', e.target.tagName, e.target.className);
            window.simpleRecorder.captureAction('click', e.target);
        }, true);

        // Change listener for radio/checkbox/input
        document.addEventListener('change', function(e) {
            console.log('CHANGE detected:', e.target.type, e.target.tagName);
            if (e.target.type === 'radio' || e.target.type === 'checkbox') {
                window.simpleRecorder.captureAction('check', e.target, e.target.checked);
            } else if (e.target.type === 'text' || e.target.type === 'textarea') {
                window.simpleRecorder.captureAction('input', e.target, e.target.value);
            }
        }, true);

        console.log('Simple recording started successfully');
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
    },

    getStatus: function() {
        return {
            actions: this.actions.length,
            recording: this.recording,
            alive: true,
            pageId: document.querySelector('.question-text .ls-label-question') ?
                    document.querySelector('.question-text .ls-label-question').textContent.trim() :
                    'unknown'
        };
    }
};

// Auto start recording
window.simpleRecorder.startRecording();
console.log('=== SIMPLE RECORDER READY ===');

return window.simpleRecorder;
"""

def simple_recording_session():
    """Complete recording session with working JavaScript"""

    print("🚀 SIMPLE WORKING RECORDER")
    print("=" * 50)

    # Connect to existing browser
    manager = BrowserManager()
    if not manager.is_browser_running():
        print("❌ No browser running on port 9222")
        return

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(options=chrome_options)

    session_data = {
        "session_id": f"simple_recorder_{datetime.now().strftime('%H%M%S')}",
        "session_name": f"simple_recorder_{datetime.now().strftime('%H%M%S')}",
        "start_time": datetime.now().isoformat(),
        "total_actions": 0,
        "pages_visited": 0,
        "page_history": [],
        "actions": []
    }

    all_actions = []
    page_history = []
    last_page_id = None

    try:
        current_url = driver.current_url
        print(f"📍 Starting page: {current_url}")

        if "evaluace.opjak.cz" not in current_url:
            print("⚠️  Navigate to survey page first")
            input("Press ENTER when on survey page...")

        # Initial page record
        page_id = PageIdentifier.get_page_id(driver)
        page_record = {
            "page_id": page_id,
            "url": driver.current_url,
            "title": driver.title,
            "timestamp": datetime.now().isoformat()
        }
        page_history.append(page_record)
        last_page_id = page_id

        print(f"📝 Initial page: {page_id[:60]}")

        # Inject working JavaScript
        print("\n💉 Injecting WORKING JavaScript...")
        driver.execute_script(WORKING_JS)
        print("✅ JavaScript injected and recording started")

        print(f"\n🎬 RECORDING SESSION ACTIVE!")
        print(f"📋 Instructions:")
        print(f"  1. Fill out the survey completely")
        print(f"  2. Navigate through ALL pages")
        print(f"  3. Press ENTER here when finished")
        print(f"  4. Script will auto-detect page changes and re-inject JS")

        # Monitoring loop
        print(f"\n📊 Monitoring (will auto-stop after 10 minutes)...")

        for i in range(120):  # 120 * 5 seconds = 10 minutes max
            time.sleep(5)

            try:
                # Check if JavaScript still exists
                js_exists = driver.execute_script("return typeof window.simpleRecorder !== 'undefined';")
                current_page_id = PageIdentifier.get_page_id(driver)

                # Handle page navigation
                if current_page_id != last_page_id:
                    print(f"\n🧭 Page navigation detected:")
                    print(f"   From: {last_page_id[:50]}")
                    print(f"   To:   {current_page_id[:50]}")

                    # Record new page
                    page_record = {
                        "page_id": current_page_id,
                        "url": driver.current_url,
                        "title": driver.title,
                        "timestamp": datetime.now().isoformat()
                    }
                    page_history.append(page_record)
                    last_page_id = current_page_id

                    # Re-inject JavaScript if lost
                    js_exists = False

                if not js_exists:
                    print(f"🔄 Re-injecting JavaScript...")
                    driver.execute_script(WORKING_JS)
                    print(f"✅ JavaScript re-injected")

                # Get current actions
                current_actions = driver.execute_script("return window.simpleRecorder.getActions();")
                if current_actions and len(current_actions) > len(all_actions):
                    new_count = len(current_actions) - len(all_actions)
                    all_actions = current_actions.copy()
                    print(f"📊 [{i*5+5}s] Actions: {len(all_actions)} (+{new_count}), Pages: {len(page_history)}")
                elif i % 12 == 0:  # Every minute
                    print(f"📊 [{i*5+5}s] Actions: {len(all_actions)}, Pages: {len(page_history)} (monitoring...)")

            except Exception as e:
                print(f"⚠️  Monitor error: {e}")
                continue

        print(f"\n⏹️  Auto-stop after 10 minutes. Press ENTER for final results...")
        input()

        # Final sync
        try:
            print(f"\n🔄 Final action sync...")
            final_actions = driver.execute_script("return window.simpleRecorder.getActions();")
            if final_actions:
                all_actions = final_actions
                print(f"📥 Final actions: {len(all_actions)}")
        except:
            print("⚠️  Final sync failed, using last known actions")

        # Prepare session data
        session_data.update({
            "end_time": datetime.now().isoformat(),
            "total_actions": len(all_actions),
            "pages_visited": len(page_history),
            "page_history": page_history,
            "actions": all_actions
        })

        # Save session
        filename = f"scenarios/recorded_sessions/simple_recorder_{datetime.now().strftime('%H%M%S')}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Session saved: {filename}")
        print(f"\n📊 FINAL RESULTS:")
        print(f"  Total actions: {len(all_actions)}")
        print(f"  Pages visited: {len(page_history)}")

        if all_actions:
            print(f"\n🎯 CAPTURED ACTIONS (last 10):")
            for i, action in enumerate(all_actions[-10:]):
                timestamp = action.get('timestamp', '')[:19].replace('T', ' ')
                page_id = action.get('page_id', 'Unknown')[:40]
                print(f"  [{len(all_actions)-10+i+1:2}] {timestamp} | {action['action_type']:8} | {action['element_selector'][:40]}")
                print(f"      Page: {page_id}")

        if page_history:
            print(f"\n📄 PAGES VISITED:")
            for i, page in enumerate(page_history):
                print(f"  [{i+1:2}] {page['page_id'][:60]}")

        print(f"\n🎉 SIMPLE RECORDING COMPLETE!")
        print(f"✅ Session ready for playback system!")

    except Exception as e:
        print(f"❌ Recording error: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n🏁 RECORDING SESSION FINISHED")

if __name__ == "__main__":
    simple_recording_session()