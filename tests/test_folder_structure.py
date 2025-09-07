#!/usr/bin/env python3
"""
Test script to demonstrate the new test folder structure.
This script shows how to use the test configuration for running tests.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

import config
from src.curation.obsidian_curator.main import run

def test_folder_structure():
    """Test the new folder structure and configuration."""
    print("Testing new folder structure...")
    print("=" * 50)
    
    # Get test configuration
    test_cfg = config.get_test_config()
    
    print("Test folder structure:")
    print(f"Raw test vault: {test_cfg['paths']['raw_vault']}")
    print(f"  - Notes: {test_cfg['paths']['raw_notes']}")
    print(f"  - Attachments: {test_cfg['paths']['raw_attachments']}")
    print()
    print(f"Preprocessed test vault: {test_cfg['paths']['preprocessed_vault']}")
    print(f"  - Notes: {test_cfg['paths']['preprocessed_notes']}")
    print(f"  - Attachments: {test_cfg['paths']['preprocessed_attachments']}")
    print()
    print(f"Curated test vault: {test_cfg['paths']['curated_vault']}")
    print(f"  - Notes: {test_cfg['paths']['curated_notes']}")
    print(f"  - Attachments: {test_cfg['paths']['curated_attachments']}")
    print()
    
    # Check if test folders exist
    print("Checking test folder structure:")
    for path_name, path_value in [
        ('raw_vault', test_cfg['paths']['raw_vault']),
        ('raw_notes', test_cfg['paths']['raw_notes']),
        ('raw_attachments', test_cfg['paths']['raw_attachments']),
        ('preprocessed_vault', test_cfg['paths']['preprocessed_vault']),
        ('preprocessed_notes', test_cfg['paths']['preprocessed_notes']),
        ('preprocessed_attachments', test_cfg['paths']['preprocessed_attachments']),
        ('curated_vault', test_cfg['paths']['curated_vault']),
        ('curated_notes', test_cfg['paths']['curated_notes']),
        ('curated_attachments', test_cfg['paths']['curated_attachments'])
    ]:
        exists = os.path.exists(path_value)
        status = "✓" if exists else "✗"
        print(f"  {status} {path_name}: {path_value}")
    
    print()
    print("Test configuration ready for use!")

def run_test_curation():
    """Run a test curation on a few notes."""
    print("\nRunning test curation...")
    print("=" * 30)
    
    test_cfg = config.get_test_config()
    
    # Run curation on test data
    try:
        run(test_cfg, dry_run=True)
        print("✓ Test curation completed successfully (dry run)")
    except Exception as e:
        print(f"✗ Test curation failed: {e}")

if __name__ == "__main__":
    test_folder_structure()
    run_test_curation()
