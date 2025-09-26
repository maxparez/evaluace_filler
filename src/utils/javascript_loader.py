#!/usr/bin/env python3
"""
JavaScript Loader Utility
Handles loading and execution of external JavaScript files
"""

import os
from pathlib import Path
from typing import Dict, Any
from loguru import logger

class JavaScriptLoader:
    """Utility class for loading and managing external JavaScript files"""

    def __init__(self, js_scripts_dir: str = None):
        """Initialize JavaScript loader with scripts directory"""
        if js_scripts_dir is None:
            # Default to src/js_scripts relative to this file
            current_dir = Path(__file__).parent.parent
            self.js_scripts_dir = current_dir / 'js_scripts'
        else:
            self.js_scripts_dir = Path(js_scripts_dir)

        self._script_cache = {}
        logger.debug(f"JavaScript loader initialized with directory: {self.js_scripts_dir}")

    def load_script(self, script_name: str) -> str:
        """Load JavaScript code from external file"""
        script_path = self.js_scripts_dir / f"{script_name}.js"

        # Check cache first
        if script_name in self._script_cache:
            logger.debug(f"Using cached JavaScript: {script_name}")
            return self._script_cache[script_name]

        try:
            if not script_path.exists():
                raise FileNotFoundError(f"JavaScript file not found: {script_path}")

            with open(script_path, 'r', encoding='utf-8') as f:
                js_code = f.read()

            # Cache the loaded script
            self._script_cache[script_name] = js_code
            logger.debug(f"Loaded JavaScript file: {script_path}")

            return js_code

        except Exception as e:
            logger.error(f"Failed to load JavaScript {script_name}: {e}")
            raise

    def execute_script(self, driver, script_name: str, function_name: str, *args) -> Any:
        """Load and execute JavaScript function with parameters"""
        try:
            # Load the script
            js_code = self.load_script(script_name)

            # Prepare function call
            args_js = []
            for arg in args:
                if isinstance(arg, str):
                    args_js.append(f'"{arg}"')
                elif isinstance(arg, list):
                    args_js.append(str(arg).replace("'", '"'))
                else:
                    args_js.append(str(arg))

            args_str = ', '.join(args_js)

            # Combine script with function call
            full_js = f"""
            {js_code}

            return {function_name}({args_str});
            """

            logger.debug(f"Executing {function_name} from {script_name}")
            result = driver.execute_script(full_js)

            logger.debug(f"JavaScript execution result: {result}")
            return result

        except Exception as e:
            logger.error(f"Failed to execute {function_name} from {script_name}: {e}")
            raise

    def clear_cache(self):
        """Clear the script cache"""
        self._script_cache.clear()
        logger.debug("JavaScript cache cleared")

    def list_available_scripts(self) -> list:
        """List all available JavaScript files"""
        try:
            js_files = []
            if self.js_scripts_dir.exists():
                for file_path in self.js_scripts_dir.glob('*.js'):
                    js_files.append(file_path.stem)
            return sorted(js_files)
        except Exception as e:
            logger.error(f"Failed to list JavaScript files: {e}")
            return []

    def validate_scripts(self) -> Dict[str, bool]:
        """Validate that all expected JavaScript files exist"""
        expected_scripts = [
            'barrier_free_inclusion',
            'matrix_strategy',
            'matrix_random_strategy',
            'input_strategy',
            'radio_strategy',
            'checkbox_strategy'
        ]

        validation_results = {}
        for script_name in expected_scripts:
            script_path = self.js_scripts_dir / f"{script_name}.js"
            validation_results[script_name] = script_path.exists()

        return validation_results