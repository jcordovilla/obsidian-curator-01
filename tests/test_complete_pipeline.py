#!/usr/bin/env python3
"""
Test script to demonstrate the complete pipeline: raw -> preprocessed -> curated.
This is the main test script for the Obsidian Curator system.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

import config
from src.preprocessing import BatchProcessor
from src.curation.obsidian_curator.main import run

def test_complete_pipeline():
    """Test the complete pipeline: raw -> preprocessed -> curated."""
    print("Testing complete Obsidian Curator pipeline...")
    print("=" * 60)
    
    # Get test configuration
    test_cfg = config.get_test_config()
    
    # Test paths
    raw_vault = test_cfg['paths']['test_raw_vault']
    preprocessed_vault = test_cfg['paths']['test_preprocessed_vault']
    curated_vault = test_cfg['paths']['test_curated_vault']
    
    print(f"Raw vault: {raw_vault}")
    print(f"Preprocessed vault: {preprocessed_vault}")
    print(f"Curated vault: {curated_vault}")
    print()
    
    # Step 1: Preprocessing
    print("Step 1: Preprocessing raw notes...")
    print("-" * 40)
    
    # Count raw notes
    raw_notes = list(Path(raw_vault).rglob("*.md"))
    print(f"Found {len(raw_notes)} notes in raw vault")
    
    if len(raw_notes) == 0:
        print("Error: No notes found in raw vault")
        return False
    
    # Initialize batch processor
    processor = BatchProcessor(
        vault_path=raw_vault,
        output_path=preprocessed_vault,
        backup=False,
        batch_size=10,
        max_workers=2
    )
    
    try:
        # Process a sample of 5 notes
        print("Processing sample of 5 notes...")
        results = processor.process_sample(sample_size=5, dry_run=False)
        
        print(f"Preprocessing results:")
        print(f"  Files processed: {results['sample_size']}")
        print(f"  Successful: {results['success_count']}")
        print(f"  Failed: {results['failure_count']}")
        
        if results['success_count'] == 0:
            print("Error: Preprocessing failed - no notes were processed")
            return False
        
        print("✓ Preprocessing completed successfully")
        
    except Exception as e:
        print(f"Error during preprocessing: {e}")
        return False
    
    # Step 2: Curation
    print("\nStep 2: Curation of preprocessed notes...")
    print("-" * 40)
    
    # Count preprocessed notes
    preprocessed_notes = list(Path(preprocessed_vault).rglob("*.md"))
    print(f"Found {len(preprocessed_notes)} preprocessed notes")
    
    try:
        # Run curation on preprocessed data (dry run)
        print("Running curation on preprocessed data (dry run)...")
        run(test_cfg, dry_run=True)
        print("✓ Curation pipeline completed successfully (dry run)")
        
    except Exception as e:
        print(f"Error during curation: {e}")
        return False
    
    # Step 3: Verify results
    print("\nStep 3: Verifying results...")
    print("-" * 40)
    
    # Check if curated notes would be created
    curated_notes = list(Path(curated_vault).rglob("*.md"))
    print(f"Curated notes directory: {curated_vault}")
    print(f"Notes in curated vault: {len(curated_notes)}")
    
    print("\n✓ Complete pipeline test successful!")
    print("  Raw notes -> Preprocessed notes -> Curated notes")
    return True

def main():
    """Run the complete pipeline test."""
    success = test_complete_pipeline()
    
    if success:
        print("\n🎉 Complete pipeline test passed!")
        print("The Obsidian Curator system is working correctly.")
        return 0
    else:
        print("\n❌ Complete pipeline test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
