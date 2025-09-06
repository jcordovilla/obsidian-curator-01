#!/usr/bin/env python3
"""
Configuration update script for Obsidian Curator.

This script updates config.yaml with the current paths from config.py,
ensuring both configuration files stay in sync.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import update_curation_yaml, get_curation_config

def main():
    """Update config.yaml with current configuration."""
    print("Updating config.yaml with current paths from config.py...")
    
    # Show current configuration
    config = get_curation_config()
    print("\nCurrent path configuration:")
    for key, value in config['paths'].items():
        print(f"  {key}: {value}")
    
    # Update the YAML file
    update_curation_yaml()
    print("\n✓ config.yaml updated successfully!")
    print("Both configuration files are now in sync.")

if __name__ == '__main__':
    main()
