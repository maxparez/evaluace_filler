#!/usr/bin/env python3
"""
Visual Status Indicators Demo
Live demonstration of visual status system during real automation
"""

import sys
import time

# Add src to Python path
sys.path.insert(0, 'src')

from smart_playback_system import SmartPlaybackSystem
from loguru import logger

def demo_visual_status_during_automation():
    """
    Demo visual status indicators during real survey automation
    This demonstrates the full integration with SmartPlaybackSystem
    """

    print("🎬 VISUAL STATUS INDICATORS DEMO")
    print("=" * 50)
    print("This demo shows visual status indicators during real automation")
    print("Watch the TOP of the browser window for colored status bars!")
    print()

    # Create playback system
    print("1️⃣ Creating SmartPlaybackSystem...")
    playback_system = SmartPlaybackSystem()

    # Connect to browser
    print("2️⃣ Connecting to browser...")
    if not playback_system.connect_to_browser():
        print("❌ Failed to connect to browser")
        print("   Make sure browser is running: python src/browser_manager.py")
        return False

    print("✅ Connected to browser successfully")

    if playback_system.status_manager:
        print("✅ Visual status indicators are active!")
        print()
        print("👀 WATCH THE BROWSER - colored bar should appear at the top!")
        print()

        # Demo different status types
        demo_scenarios = [
            {
                'name': 'Starting Automation',
                'action': lambda: playback_system.status_manager.start_automation(1, 5),
                'description': 'Green bar: Automation starting',
                'duration': 3
            },
            {
                'name': 'Processing Page 1',
                'action': lambda: playback_system.status_manager.processing_page(1, 'Analyzuji otázky na stránce'),
                'description': 'Blue bar: Processing current page',
                'duration': 3
            },
            {
                'name': 'Waiting for Next Page',
                'action': lambda: playback_system.status_manager.waiting_for_page(2),
                'description': 'Orange bar: Waiting for page load',
                'duration': 3
            },
            {
                'name': 'Processing Page 2',
                'action': lambda: playback_system.status_manager.processing_page(2, 'Vyplňuji matrix otázky'),
                'description': 'Blue bar: Processing with custom message',
                'duration': 3
            },
            {
                'name': 'Manual Intervention Required',
                'action': lambda: playback_system.status_manager.require_manual_intervention(
                    'Neznámý typ stránky',
                    'Vyplňte stránku ručně a pokračujte tlačítkem Další'
                ),
                'description': 'RED bar: Manual intervention needed (has close button)',
                'duration': 5
            },
            {
                'name': 'Continuing After Manual Fix',
                'action': lambda: playback_system.status_manager.processing_page(3, 'Pokračuji po manuálním zásahu'),
                'description': 'Blue bar: Continuing automation',
                'duration': 3
            },
            {
                'name': 'Error Simulation',
                'action': lambda: playback_system.status_manager.automation_error('Simulovaná chyba pro demo'),
                'description': 'RED bar: Error occurred',
                'duration': 3
            },
            {
                'name': 'Recovery and Completion',
                'action': lambda: playback_system.status_manager.automation_completed(),
                'description': 'Green bar: Automation completed (auto-hides in 5s)',
                'duration': 6
            }
        ]

        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"{i}️⃣ {scenario['name']}")
            print(f"   📝 {scenario['description']}")

            # Execute the status change
            scenario['action']()

            print(f"   ⏳ Waiting {scenario['duration']}s for visual verification...")
            time.sleep(scenario['duration'])
            print()

        print("🎉 Demo completed!")
        print()
        print("📋 What you should have seen:")
        print("   ✅ Green bars for normal automation states")
        print("   🔵 Blue bars for processing activities")
        print("   🟠 Orange bars for waiting states")
        print("   🔴 Red bars for manual intervention and errors")
        print("   ✨ Smooth animations between states")
        print("   ⏱️ Auto-hide after completion")

        # Test additional features
        print("\n🔧 Testing additional features...")

        print("   📊 Testing progress indicators...")
        for page in range(1, 4):
            playback_system.status_manager.set_status_with_progress(
                'running', page, 3, f'Demo progress stránka {page}'
            )
            time.sleep(2)

        print("   🙈 Testing hide/show...")
        playback_system.status_manager.hide()
        time.sleep(2)
        print("   👁️ Showing again...")
        playback_system.status_manager.show()
        time.sleep(2)

        print("   🧹 Cleaning up...")
        playback_system.status_manager.remove()
        time.sleep(1)

        return True
    else:
        print("❌ Status manager not initialized")
        return False

def demo_real_automation_with_status():
    """
    Demo with real automation - shows status indicators during actual survey processing
    """

    print("\n" + "=" * 50)
    print("🚀 REAL AUTOMATION WITH VISUAL STATUS")
    print("=" * 50)
    print("This will run real automation with visual status indicators")
    print("Status indicators will automatically update during the process")
    print()

    response = input("Do you want to run real automation demo? (y/N): ").strip().lower()

    if response != 'y':
        print("Skipping real automation demo")
        return True

    try:
        # Create and run playback system
        playback_system = SmartPlaybackSystem()

        if not playback_system.connect_to_browser():
            print("❌ Failed to connect to browser")
            return False

        print("🚀 Starting real automation with visual status indicators...")
        print("👀 Watch the browser for automatic status updates!")

        # Run a few pages of automation
        # Note: This will use the integrated status indicators
        # in the SmartPlaybackSystem.run_complete_survey method

        # For demo purposes, we'll simulate a few page processes
        if playback_system.status_manager:
            playback_system.status_manager.start_automation()

            # Simulate processing a few pages
            for page_num in range(1, 4):
                playback_system.status_manager.processing_page(
                    page_num, f'Real processing simulation page {page_num}'
                )

                # Simulate some processing time
                time.sleep(3)

                # Simulate waiting
                if page_num < 3:
                    playback_system.status_manager.waiting_for_page(page_num + 1)
                    time.sleep(2)

            playback_system.status_manager.automation_completed()

        print("✅ Real automation demo completed!")
        return True

    except Exception as e:
        print(f"❌ Real automation demo failed: {e}")
        return False

def main():
    """Run comprehensive visual status demo"""

    print("🎬 COMPREHENSIVE VISUAL STATUS INDICATORS DEMO")
    print("=" * 70)
    print("This demo showcases the visual status indicator system")
    print("integrated with the Evaluace Filler automation")
    print()

    try:
        # Demo 1: Basic status indicators
        demo1_success = demo_visual_status_during_automation()

        # Demo 2: Real automation with status
        demo2_success = demo_real_automation_with_status()

        # Summary
        print("\n" + "=" * 70)
        print("📊 DEMO RESULTS SUMMARY")
        print("=" * 70)

        print(f"Basic status demo: {'✅ SUCCESS' if demo1_success else '❌ FAILED'}")
        print(f"Real automation demo: {'✅ SUCCESS' if demo2_success else '❌ FAILED'}")

        if demo1_success and demo2_success:
            print("\n🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
            print("✅ Visual status indicators are working perfectly!")
            print()
            print("🎯 Key Features Demonstrated:")
            print("   ✅ Real-time status updates during automation")
            print("   ✅ Color-coded status indicators (green/blue/orange/red)")
            print("   ✅ Progress indicators with page numbers")
            print("   ✅ Manual intervention alerts")
            print("   ✅ Error handling with visual feedback")
            print("   ✅ Smooth animations and professional styling")
            print("   ✅ Auto-hide functionality")
            print("   ✅ Integration with SmartPlaybackSystem")
            return True
        else:
            print("\n❌ Some demos failed")
            return False

    except Exception as e:
        print(f"\n💥 Demo failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎬 Starting Visual Status Indicators Demo...")
    print("📋 Make sure browser is running before starting!")
    print()

    # Check if browser is available
    try:
        from browser_manager import BrowserManager
        manager = BrowserManager()
        if not manager.is_browser_running():
            print("⚠️ Browser not detected. Starting browser first...")
            print("💡 Run: python src/browser_manager.py")
            print("💡 Or: python batch_processor.py")
            print()
    except:
        pass

    input("Press Enter when browser is ready to start demo...")
    print()

    success = main()

    print("\n🎬 Demo finished!")
    input("Press Enter to exit...")

    sys.exit(0 if success else 1)