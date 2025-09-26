#!/usr/bin/env python3
"""
Helper script to load access codes from text file into batch config
"""

import json
import sys
from pathlib import Path

def load_codes_from_file(codes_file: str, config_file: str = "config/batch_config.json"):
    """Load access codes from text file and update batch config"""

    # Read codes from file
    codes = []
    try:
        with open(codes_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    codes.append(line)

        print(f"Loaded {len(codes)} access codes from {codes_file}")

    except Exception as e:
        print(f"Error reading codes file: {e}")
        return False

    # Load existing config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config file: {e}")
        return False

    # Update codes
    config['access_codes'] = codes

    # Save updated config
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"Updated {config_file} with {len(codes)} access codes")
        return True

    except Exception as e:
        print(f"Error writing config file: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python load_codes_from_file.py <codes_file.txt>")
        print("Example: python load_codes_from_file.py config/real_access_codes.txt")
        sys.exit(1)

    codes_file = sys.argv[1]

    if not Path(codes_file).exists():
        print(f"File not found: {codes_file}")
        sys.exit(1)

    if load_codes_from_file(codes_file):
        print("Success! Ready to run batch processing.")
        sys.exit(0)
    else:
        print("Failed to load codes.")
        sys.exit(1)

if __name__ == "__main__":
    main()