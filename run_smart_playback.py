#!/usr/bin/env python3
"""
Smart Playback Launcher - Convenient entry point for survey automation
"""

import sys
import os
import subprocess
import requests
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from smart_playback_system import SmartPlaybackSystem

def check_environment():
    """Check if environment is ready for playback"""
    print("🔍 CHECKING ENVIRONMENT...")

    issues = []

    # Check virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        issues.append("❌ Virtual environment not activated")
    else:
        print("✅ Virtual environment: activated")

    # Check browser on port 9222
    try:
        response = requests.get('http://localhost:9222/json', timeout=2)
        if response.status_code == 200:
            tabs = response.json()
            print(f"✅ Browser: running with {len(tabs)} tabs")
        else:
            issues.append("❌ Browser not responding on port 9222")
    except:
        issues.append("❌ Browser not running on port 9222")

    # Check strategy file
    strategy_file = "scenarios/optimized_survey_strategy.json"
    if Path(strategy_file).exists():
        print("✅ Strategy file: found")
    else:
        issues.append(f"❌ Strategy file missing: {strategy_file}")

    # Check ChromeDriver
    try:
        result = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ChromeDriver: installed")
        else:
            issues.append("❌ ChromeDriver not found in PATH")
    except:
        issues.append("❌ ChromeDriver check failed")

    return issues

def fix_common_issues():
    """Show fixes for common issues"""
    print("\n🛠️  COMMON FIXES:")
    print("1. Activate virtual environment:")
    print("   source venv/bin/activate")
    print()
    print("2. Start browser with remote debugging:")
    print("   google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_evaluace &")
    print()
    print("3. Navigate to survey start page in the browser")
    print()

def main():
    print("🎯 SMART PLAYBACK SYSTEM LAUNCHER")
    print("=" * 50)

    # Environment check
    issues = check_environment()

    if issues:
        print("\n❌ ENVIRONMENT ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")

        fix_common_issues()

        print("Fix these issues and try again.")
        return 1

    print("\n✅ ENVIRONMENT READY")
    print()

    # Show instructions
    print("📋 INSTRUCTIONS:")
    print("1. Navigate to the START of your survey in the browser")
    print("2. Make sure you're logged in and ready to begin")
    print("3. The system will automatically:")
    print("   - Detect each page type")
    print("   - Fill forms using optimized strategies")
    print("   - Handle special cases (inclusion, barrier-free)")
    print("   - Navigate through the entire survey")
    print("   - Generate completion report")
    print()

    # Confirmation
    try:
        confirm = input("Ready to start automated survey? [y/N]: ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Cancelled by user.")
            return 0
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        return 0

    # Run Smart Playback System
    print("\n🚀 STARTING SMART PLAYBACK SYSTEM...")
    print("=" * 50)

    try:
        playback = SmartPlaybackSystem()
        results = playback.run_complete_survey()

        # Show final summary
        playback.print_session_summary()

        success_rate = results['pages_successful'] / max(results['pages_processed'], 1) * 100

        if success_rate >= 90:
            print("\n🎉 SURVEY AUTOMATION COMPLETED SUCCESSFULLY!")
        elif success_rate >= 75:
            print("\n⚠️  SURVEY AUTOMATION COMPLETED WITH SOME ISSUES")
        else:
            print("\n❌ SURVEY AUTOMATION HAD SIGNIFICANT ISSUES")

        return 0 if success_rate >= 75 else 1

    except KeyboardInterrupt:
        print("\n\n⏹️  AUTOMATION INTERRUPTED BY USER")
        return 1
    except Exception as e:
        print(f"\n❌ AUTOMATION FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())