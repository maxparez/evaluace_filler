#!/usr/bin/env python3
"""
Smart Page Matcher - Fast JSON-based page lookup and pattern matching
Optimized for survey automation with fuzzy matching and caching
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher
from loguru import logger

@dataclass
class PageMatch:
    """Result of page matching operation"""
    page_title: str
    pattern: str
    confidence: float
    selectors: List[str]
    config: Dict
    exact_match: bool

class SmartPageMatcher:
    """
    Fast JSON-based page matcher with fuzzy matching and caching

    Performance characteristics:
    - Exact match: O(1) - hash table lookup
    - Fuzzy match: O(n) where n = number of pages (max 52)
    - Cached patterns: O(1) after first computation
    """

    def __init__(self, scenario_file: str):
        """Initialize with JSON scenario file"""
        self.scenario_file = scenario_file
        self.data = {}
        self.pages_index = {}
        self.pattern_cache = {}
        self.keyword_cache = {}

        self.load_scenarios()
        self._build_search_indices()

    def load_scenarios(self):
        """Load and parse JSON scenario file"""
        try:
            with open(self.scenario_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            logger.info(f"Loaded {len(self.data.get('pages', {}))} pages from {self.scenario_file}")

        except Exception as e:
            logger.error(f"Failed to load scenarios: {e}")
            raise

    def _build_search_indices(self):
        """Build search indices for O(1) lookups"""
        pages = self.data.get('pages', {})

        # Primary index: exact page title
        self.pages_index = pages

        # Secondary index: keywords
        for page_title, config in pages.items():
            keywords = config.get('keywords', [])
            for keyword in keywords:
                if keyword not in self.keyword_cache:
                    self.keyword_cache[keyword] = []
                self.keyword_cache[keyword].append(page_title)

        logger.debug(f"Built indices: {len(self.pages_index)} pages, {len(self.keyword_cache)} keywords")

    def find_page_match(self, current_page_title: str, threshold: float = 0.8) -> Optional[PageMatch]:
        """
        Find best matching page configuration

        Algorithm:
        1. Try exact match (O(1))
        2. Try fuzzy match (O(n))
        3. Try keyword matching (O(k) where k = keywords)
        4. Return best match above threshold
        """

        # 1. Exact match - fastest path
        if current_page_title in self.pages_index:
            config = self.pages_index[current_page_title]
            return PageMatch(
                page_title=current_page_title,
                pattern=config.get('pattern', 'UNKNOWN'),
                confidence=1.0,
                selectors=config.get('specific_selectors', []),
                config=config,
                exact_match=True
            )

        # 2. Fuzzy matching - check similarity with all known pages
        best_match = None
        best_score = 0.0

        for known_title, config in self.pages_index.items():
            # Calculate similarity
            similarity = SequenceMatcher(None, current_page_title.lower(), known_title.lower()).ratio()

            # Boost score for keyword matches
            keywords = config.get('keywords', [])
            keyword_boost = 0
            for keyword in keywords:
                if keyword.lower() in current_page_title.lower():
                    keyword_boost += 0.1

            final_score = min(similarity + keyword_boost, 1.0)

            if final_score > best_score and final_score >= threshold:
                best_score = final_score
                best_match = PageMatch(
                    page_title=known_title,
                    pattern=config.get('pattern', 'UNKNOWN'),
                    confidence=final_score,
                    selectors=config.get('specific_selectors', []),
                    config=config,
                    exact_match=False
                )

        # 3. Log result
        if best_match:
            logger.info(f"Matched '{current_page_title[:50]}...' → '{best_match.page_title[:50]}...' ({best_match.confidence:.2f})")
        else:
            logger.warning(f"No match found for '{current_page_title[:50]}...' (threshold: {threshold})")

        return best_match

    def get_pattern_config(self, pattern: str) -> Dict:
        """Get configuration for specific pattern type"""
        return self.data.get('page_patterns', {}).get(pattern, {})

    def get_filling_strategy(self, page_title: str) -> Optional[Dict]:
        """
        Get complete filling strategy for a page

        Returns:
        {
            'pattern': 'MATRIX_RATING',
            'selectors': ['#answer592479X111X4433SQ001-A5', ...],
            'default_rating': 'A5',
            'auto_navigate': True,
            'navigation_delay': 3000
        }
        """
        match = self.find_page_match(page_title)
        if not match:
            return None

        pattern_config = self.get_pattern_config(match.pattern)

        strategy = {
            'pattern': match.pattern,
            'confidence': match.confidence,
            'exact_match': match.exact_match,
            'selectors': match.selectors,
            **pattern_config,  # Merge pattern defaults
            **match.config     # Override with page-specific config
        }

        return strategy

    def list_all_pages(self) -> List[str]:
        """Return list of all known page titles"""
        return list(self.pages_index.keys())

    def get_pattern_statistics(self) -> Dict[str, int]:
        """Get statistics about pattern usage"""
        stats = {}
        for config in self.pages_index.values():
            pattern = config.get('pattern', 'UNKNOWN')
            stats[pattern] = stats.get(pattern, 0) + 1
        return stats

# Quick testing function
if __name__ == "__main__":
    # Test the matcher
    matcher = SmartPageMatcher('scenarios/improved_survey_structure.json')

    # Test cases
    test_pages = [
        "Uveďte, prosím, do jaké míry souhlasíte s následujícími výroky vztahujícími se k Vaší škole v oblasti čtenářské gramotnosti.",
        "Využili jste pomoc při tvorbě žádosti?",  # Partial match
        "Kolik je vám let?",  # Should match birth year question
        "Completely unknown page title"  # Should not match
    ]

    print("=== SMART PAGE MATCHER TEST ===")
    for test_page in test_pages:
        print(f"\\nTesting: '{test_page}'")
        strategy = matcher.get_filling_strategy(test_page)
        if strategy:
            print(f"  Pattern: {strategy['pattern']}")
            print(f"  Confidence: {strategy['confidence']:.2f}")
            print(f"  Selectors: {len(strategy.get('selectors', []))} found")
        else:
            print("  No match found")

    print(f"\\n=== PATTERN STATISTICS ===")
    for pattern, count in matcher.get_pattern_statistics().items():
        print(f"{pattern}: {count} pages")