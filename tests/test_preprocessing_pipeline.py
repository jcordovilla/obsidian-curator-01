#!/usr/bin/env python3
"""
Test script to verify preprocessing pipeline works with test data.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

import config
from src.preprocessing import BatchProcessor

def test_preprocessing_pipeline():
    """Test preprocessing pipeline with test data."""
    print("Testing preprocessing pipeline with test data...")
    print("=" * 60)
    
    # Get test configuration
    test_cfg = config.get_test_config()
    
    # Test paths
    raw_vault = test_cfg['paths']['test_raw_vault']
    preprocessed_vault = test_cfg['paths']['test_preprocessed_vault']
    
    print(f"Raw vault: {raw_vault}")
    print(f"Preprocessed vault: {preprocessed_vault}")
    print()
    
    # Check if raw test data exists
    if not os.path.exists(raw_vault):
        print(f"Error: Raw test vault does not exist: {raw_vault}")
        return False
    
    # Count notes in raw vault
    raw_notes = list(Path(raw_vault).rglob("*.md"))
    print(f"Found {len(raw_notes)} notes in raw test vault")
    
    if len(raw_notes) == 0:
        print("No notes found in raw test vault. Please add some test notes.")
        return False
    
    # Initialize batch processor
    processor = BatchProcessor(
        vault_path=raw_vault,
        output_path=preprocessed_vault,
        backup=False,  # No backup needed for testing
        batch_size=10,
        max_workers=2
    )
    
    try:
        # Run preprocessing
        print("Running preprocessing...")
        results = processor.process_vault()
        
        print(f"✓ Preprocessing completed successfully")
        summary = results['summary']
        print(f"  Processed: {summary['processed_files']} files")
        print(f"  Failed: {summary['failed_files']} files")
        print(f"  Skipped: {summary['skipped_files']} files")
        
        # Check if preprocessed notes were created
        preprocessed_notes = list(Path(preprocessed_vault).rglob("*.md"))
        print(f"  Created {len(preprocessed_notes)} preprocessed notes")
        
        return True
        
    except Exception as e:
        print(f"✗ Preprocessing failed: {e}")
        return False

def test_web_cleaning_effectiveness():
    """Test that web cleaning is working effectively."""
    print("\nTesting web cleaning effectiveness...")
    print("=" * 60)
    
    # Check a few preprocessed notes for web boilerplate
    test_cfg = config.get_test_config()
    preprocessed_vault = test_cfg['paths']['test_preprocessed_vault']
    
    if not os.path.exists(preprocessed_vault):
        print(f"Error: Preprocessed vault does not exist: {preprocessed_vault}")
        return False
    
    preprocessed_notes = list(Path(preprocessed_vault).rglob("*.md"))
    
    if len(preprocessed_notes) == 0:
        print("No preprocessed notes found.")
        return False
    
    # Check first few notes for web boilerplate
    boilerplate_issues = 0
    for note_path in preprocessed_notes[:3]:  # Check first 3 notes
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common web boilerplate indicators
        boilerplate_indicators = [
            'Share on', 'Follow us', 'Subscribe', 'Advertisement',
            'Privacy policy', 'Terms of service', 'Copyright',
            'Social sharing', 'Navigation', 'Footer'
        ]
        
        found_indicators = []
        for indicator in boilerplate_indicators:
            if indicator.lower() in content.lower():
                found_indicators.append(indicator)
        
        if found_indicators:
            print(f"  {note_path.name}: Found boilerplate indicators: {found_indicators}")
            boilerplate_issues += 1
        else:
            print(f"  {note_path.name}: ✓ Clean")
    
    if boilerplate_issues == 0:
        print("✓ All checked notes are clean of web boilerplate")
        return True
    else:
        print(f"✗ Found boilerplate issues in {boilerplate_issues} notes")
        return False

def main():
    """Run all preprocessing tests."""
    print("Preprocessing Pipeline Test Suite")
    print("=" * 60)
    
    # Test 1: Basic preprocessing
    preprocessing_ok = test_preprocessing_pipeline()
    
    # Test 2: Web cleaning effectiveness
    cleaning_ok = test_web_cleaning_effectiveness()
    
    # Summary
    print("\nTest Results Summary:")
    print("=" * 60)
    print(f"  Preprocessing: {'✓' if preprocessing_ok else '✗'}")
    print(f"  Web Cleaning: {'✓' if cleaning_ok else '✗'}")
    
    if all([preprocessing_ok, cleaning_ok]):
        print("\n✓ All preprocessing tests passed!")
        return True
    else:
        print("\n✗ Some preprocessing tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)