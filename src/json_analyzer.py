#!/usr/bin/env python3
"""
JSON Analyzer for Survey Recording Sessions
Analyzes recorded survey data for completeness and prepares clean JSON for playback system
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any
from loguru import logger

class RecordingSessionAnalyzer:
    """Analyzes recorded survey sessions for quality and completeness"""

    def __init__(self, session_path: str):
        self.session_path = Path(session_path)
        self.data = self.load_session()

    def load_session(self) -> Dict:
        """Load session data from JSON file"""
        try:
            with open(self.session_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load session {self.session_path}: {e}")
            return {}

    def analyze_completeness(self) -> Dict[str, Any]:
        """Analyze session completeness and quality"""
        analysis = {
            "session_info": self.get_session_info(),
            "page_analysis": self.analyze_pages(),
            "action_analysis": self.analyze_actions(),
            "selector_analysis": self.analyze_selectors(),
            "data_quality": self.check_data_quality()
        }
        return analysis

    def get_session_info(self) -> Dict:
        """Extract basic session information"""
        return {
            "session_id": self.data.get("session_id", "unknown"),
            "session_name": self.data.get("session_name", "unknown"),
            "start_time": self.data.get("start_time", "unknown"),
            "end_time": self.data.get("end_time", "unknown"),
            "total_actions": self.data.get("total_actions", 0),
            "pages_visited": self.data.get("pages_visited", 0),
            "file_size_kb": round(self.session_path.stat().st_size / 1024, 2)
        }

    def analyze_pages(self) -> Dict:
        """Analyze page coverage and flow"""
        page_history = self.data.get("page_history", [])

        unique_pages = set()
        page_flow = []

        for page in page_history:
            page_id = page.get("page_id", "unknown")
            unique_pages.add(page_id)
            page_flow.append({
                "page_id": page_id[:50] + "..." if len(page_id) > 50 else page_id,
                "url": page.get("url", "unknown"),
                "timestamp": page.get("timestamp", "unknown")
            })

        return {
            "unique_pages": len(unique_pages),
            "page_flow": page_flow,
            "has_welcome_page": any("evaluační dotazník" in p.get("page_id", "").lower() for p in page_history),
            "has_question_pages": any("?" in p.get("page_id", "") for p in page_history)
        }

    def analyze_actions(self) -> Dict:
        """Analyze recorded actions"""
        actions = self.data.get("actions", [])

        action_types = {}
        pages_with_actions = set()
        selectors_used = set()

        for action in actions:
            action_type = action.get("action_type", "unknown")
            page_id = action.get("page_id", "unknown")
            selector = action.get("element_selector", "unknown")

            action_types[action_type] = action_types.get(action_type, 0) + 1
            pages_with_actions.add(page_id)
            selectors_used.add(selector)

        return {
            "total_actions": len(actions),
            "action_types": action_types,
            "pages_with_actions": len(pages_with_actions),
            "unique_selectors": len(selectors_used),
            "actions_per_page": round(len(actions) / max(len(pages_with_actions), 1), 1)
        }

    def analyze_selectors(self) -> Dict:
        """Analyze selector quality and patterns"""
        actions = self.data.get("actions", [])

        selector_patterns = {
            "radio_buttons": 0,
            "checkboxes": 0,
            "text_inputs": 0,
            "navigation": 0,
            "generic": 0
        }

        all_selectors = set()

        for action in actions:
            selector = action.get("element_selector", "")
            all_selectors.add(selector)

            if "answer" in selector and ("X" in selector or "SQ" in selector):
                if action.get("action_type") == "check":
                    selector_patterns["radio_buttons"] += 1
                elif "checkbox" in selector.lower():
                    selector_patterns["checkboxes"] += 1
            elif "input" in selector.lower():
                selector_patterns["text_inputs"] += 1
            elif "button" in selector or "submit" in selector:
                selector_patterns["navigation"] += 1
            elif selector in [".control-label", ".checkbox-label", "label"]:
                selector_patterns["generic"] += 1

        return {
            "total_unique_selectors": len(all_selectors),
            "selector_patterns": selector_patterns,
            "selector_list": list(all_selectors)
        }

    def check_data_quality(self) -> Dict:
        """Check data quality issues"""
        actions = self.data.get("actions", [])
        page_history = self.data.get("page_history", [])

        issues = []

        # Check for empty actions
        if not actions:
            issues.append("No actions recorded")

        # Check for missing page IDs
        missing_page_ids = sum(1 for action in actions if not action.get("page_id"))
        if missing_page_ids > 0:
            issues.append(f"{missing_page_ids} actions without page_id")

        # Check for missing selectors
        missing_selectors = sum(1 for action in actions if not action.get("element_selector"))
        if missing_selectors > 0:
            issues.append(f"{missing_selectors} actions without selectors")

        # Check for potential duplicates
        action_signatures = []
        for action in actions:
            signature = f"{action.get('page_id', '')}|{action.get('element_selector', '')}|{action.get('action_type', '')}"
            action_signatures.append(signature)

        duplicates = len(action_signatures) - len(set(action_signatures))
        if duplicates > 0:
            issues.append(f"{duplicates} potential duplicate actions")

        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "data_completeness": {
                "has_session_info": bool(self.data.get("session_id")),
                "has_actions": len(actions) > 0,
                "has_page_history": len(page_history) > 0,
                "has_timestamps": any(action.get("timestamp") for action in actions)
            }
        }

    def generate_clean_json(self, output_path: str = None) -> Dict:
        """Generate cleaned JSON optimized for playback system"""
        if not output_path:
            output_path = self.session_path.parent / f"clean_{self.session_path.name}"

        # Create optimized structure for playback
        clean_data = {
            "metadata": {
                "original_session": self.data.get("session_name", "unknown"),
                "cleaned_at": datetime.now().isoformat(),
                "total_actions": len(self.data.get("actions", [])),
                "pages_covered": len(set(action.get("page_id") for action in self.data.get("actions", []))),
                "survey_flow": self.extract_survey_flow()
            },
            "scenarios": self.group_actions_by_page(),
            "navigation_flow": self.extract_navigation_flow()
        }

        # Save cleaned JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)

        logger.success(f"Clean JSON saved to: {output_path}")
        return clean_data

    def extract_survey_flow(self) -> List[str]:
        """Extract the survey page flow for navigation"""
        page_history = self.data.get("page_history", [])
        return [page.get("page_id", "unknown") for page in page_history]

    def group_actions_by_page(self) -> Dict[str, List[Dict]]:
        """Group actions by page for scenario-based playback"""
        actions = self.data.get("actions", [])
        grouped = {}

        for action in actions:
            page_id = action.get("page_id", "unknown")
            if page_id not in grouped:
                grouped[page_id] = []

            # Clean action for playback
            clean_action = {
                "action_type": action.get("action_type"),
                "selector": action.get("element_selector"),
                "value": action.get("value", ""),
                "element_text": action.get("element_text", ""),
                "timestamp": action.get("timestamp")
            }
            grouped[page_id].append(clean_action)

        return grouped

    def extract_navigation_flow(self) -> List[Dict]:
        """Extract navigation pattern for playback system"""
        page_history = self.data.get("page_history", [])
        flow = []

        for i, page in enumerate(page_history):
            flow.append({
                "step": i + 1,
                "page_id": page.get("page_id", "unknown"),
                "url": page.get("url", "unknown"),
                "expected_navigation": "next" if i < len(page_history) - 1 else "complete"
            })

        return flow

    def print_analysis(self):
        """Print comprehensive analysis to console"""
        analysis = self.analyze_completeness()

        print(f"\n📊 ANALYSIS: {self.session_path.name}")
        print("=" * 60)

        # Session info
        info = analysis["session_info"]
        print(f"Session: {info['session_name']}")
        print(f"Actions: {info['total_actions']}")
        print(f"Pages: {info['pages_visited']}")
        print(f"File size: {info['file_size_kb']} KB")

        # Actions analysis
        action_analysis = analysis["action_analysis"]
        print(f"\n🎯 ACTIONS ({action_analysis['total_actions']}):")
        for action_type, count in action_analysis["action_types"].items():
            print(f"  {action_type}: {count}")

        # Selector analysis
        selector_analysis = analysis["selector_analysis"]
        print(f"\n🔍 SELECTORS ({selector_analysis['total_unique_selectors']}):")
        for pattern, count in selector_analysis["selector_patterns"].items():
            if count > 0:
                print(f"  {pattern}: {count}")

        # Data quality
        quality = analysis["data_quality"]
        print(f"\n✅ DATA QUALITY:")
        if quality["has_issues"]:
            for issue in quality["issues"]:
                print(f"  ⚠️  {issue}")
        else:
            print("  🎉 No issues detected")

        print("=" * 60)

def main():
    """Analyze latest recording session"""
    sessions_dir = Path("scenarios/recorded_sessions")

    if not sessions_dir.exists():
        logger.error("Sessions directory not found")
        return

    # Find latest session
    session_files = list(sessions_dir.glob("*.json"))
    if not session_files:
        logger.error("No session files found")
        return

    latest_session = max(session_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"Analyzing latest session: {latest_session.name}")

    # Analyze session
    analyzer = RecordingSessionAnalyzer(latest_session)
    analyzer.print_analysis()

    # Generate clean JSON
    clean_data = analyzer.generate_clean_json()
    logger.success(f"Analysis complete! Clean JSON ready for playback system.")

if __name__ == "__main__":
    main()