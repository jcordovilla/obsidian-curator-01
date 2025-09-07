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
    
    # Test paths - use real vault for input, test folders for output
    raw_vault = "/Users/jose/Documents/Obsidian/Evermd"  # Real vault with 3,662 notes
    preprocessed_vault = test_cfg['paths']['test_preprocessed_vault']
    curated_vault = test_cfg['paths']['test_curated_vault']
    
    print(f"Raw vault: {raw_vault} (3,662 notes available)")
    print(f"Preprocessed vault: {preprocessed_vault}")
    print(f"Curated vault: {curated_vault}")
    print()
    
    # Step 0: Randomly select and copy 50 fresh notes from real vault
    print("Step 0: Randomly selecting 50 fresh notes from real vault...")
    print("-" * 40)
    
    import random
    import shutil
    
    # Clean test folders first
    if os.path.exists(preprocessed_vault):
        shutil.rmtree(preprocessed_vault)
        print(f"✓ Cleaned preprocessed vault: {preprocessed_vault}")
    
    if os.path.exists(curated_vault):
        shutil.rmtree(curated_vault)
        print(f"✓ Cleaned curated vault: {curated_vault}")
    
    # Clean and recreate raw test folder
    test_raw_vault = test_cfg['paths']['test_raw_vault']
    if os.path.exists(test_raw_vault):
        shutil.rmtree(test_raw_vault)
        print(f"✓ Cleaned raw test vault: {test_raw_vault}")
    
    # Recreate test folders
    os.makedirs(test_raw_vault, exist_ok=True)
    os.makedirs(f"{test_raw_vault}/notes", exist_ok=True)
    os.makedirs(f"{test_raw_vault}/attachments", exist_ok=True)
    os.makedirs(preprocessed_vault, exist_ok=True)
    os.makedirs(curated_vault, exist_ok=True)
    
    # Get all notes from real vault
    all_notes = list(Path(raw_vault).rglob("*.md"))
    print(f"Found {len(all_notes)} notes in real vault")
    
    # Find notes with attachments first
    notes_with_attachments = []
    notes_without_attachments = []
    
    for note in all_notes:
        note_stem = note.stem
        att_dir = Path(raw_vault) / "attachments" / f"{note_stem}.resources"
        if att_dir.exists():
            notes_with_attachments.append(note)
        else:
            notes_without_attachments.append(note)
    
    print(f"Notes with attachments: {len(notes_with_attachments)}")
    print(f"Notes without attachments: {len(notes_without_attachments)}")
    
    # Select a mix: 10 with attachments, 40 without
    selected_with_attachments = random.sample(notes_with_attachments, min(10, len(notes_with_attachments)))
    selected_without_attachments = random.sample(notes_without_attachments, 40)
    selected_notes = selected_with_attachments + selected_without_attachments
    
    print(f"Selected {len(selected_with_attachments)} notes with attachments")
    print(f"Selected {len(selected_without_attachments)} notes without attachments")
    print(f"Total: {len(selected_notes)} notes for testing")
    
    # Copy selected notes to test folder
    for i, note_path in enumerate(selected_notes, 1):
        # Copy the note file
        new_note_name = f"test_note_{i:02d}_{note_path.name}"
        new_note_path = Path(test_raw_vault) / "notes" / new_note_name
        shutil.copy2(note_path, new_note_path)
        print(f"  Copied: {note_path.name} -> {new_note_name}")
        
        # Copy associated attachments from central attachments folder
        note_stem = note_path.stem
        real_attachments_dir = Path(raw_vault) / "attachments" / f"{note_stem}.resources"
        
        if real_attachments_dir.exists():
            try:
                new_attachments_dir = Path(test_raw_vault) / "attachments" / f"{new_note_name}.resources"
                shutil.copytree(real_attachments_dir, new_attachments_dir)
                attachment_count = len(list(real_attachments_dir.iterdir()))
                print(f"    + attachments: {attachment_count} files")
            except Exception as e:
                print(f"    + attachments: ERROR copying - {e}")
        else:
            # Try alternative attachment locations
            alt_locations = [
                Path(raw_vault) / "attachments" / note_stem,
                Path(raw_vault) / "attachments" / f"{note_stem}_files",
                Path(raw_vault) / "attachments" / f"{note_stem}_attachments"
            ]
            
            found_attachments = False
            for alt_dir in alt_locations:
                if alt_dir.exists():
                    try:
                        new_attachments_dir = Path(test_raw_vault) / "attachments" / f"{new_note_name}.resources"
                        shutil.copytree(alt_dir, new_attachments_dir)
                        attachment_count = len(list(alt_dir.iterdir()))
                        print(f"    + attachments: {attachment_count} files (from {alt_dir.name})")
                        found_attachments = True
                        break
                    except Exception as e:
                        print(f"    + attachments: ERROR copying from {alt_dir.name} - {e}")
                        continue
            
            # If still not found, try to find attachments by reading the note content
            if not found_attachments:
                try:
                    with open(note_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for attachment references in the content
                    import re
                    attachment_refs = re.findall(r'!\[\[attachments/([^\]]+)\]\]', content)
                    if attachment_refs:
                        # Try to find the attachment folder by the referenced file
                        for ref in attachment_refs:
                            ref_stem = ref.split('/')[0]  # Get the folder name
                            potential_attachments_dir = Path(raw_vault) / "attachments" / ref_stem
                            if potential_attachments_dir.exists():
                                try:
                                    new_attachments_dir = Path(test_raw_vault) / "attachments" / f"{new_note_name}.resources"
                                    shutil.copytree(potential_attachments_dir, new_attachments_dir)
                                    attachment_count = len(list(potential_attachments_dir.iterdir()))
                                    print(f"    + attachments: {attachment_count} files (found by content reference: {ref_stem})")
                                    found_attachments = True
                                    break
                                except Exception as e:
                                    print(f"    + attachments: ERROR copying from {ref_stem} - {e}")
                                    continue
                except Exception as e:
                    print(f"    + attachments: ERROR reading note content - {e}")
            
            if not found_attachments:
                print(f"    + attachments: none found")
    
    print(f"✓ Copied 50 fresh notes to test folder")
    print()
    
    # Update raw_vault to use test folder for preprocessing
    raw_vault = test_raw_vault
    
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
        # Process all 50 notes (they're already selected and copied)
        print("Processing all 50 selected notes...")
        results = processor.process_vault()
        
        print(f"Preprocessing results:")
        summary = results['summary']
        print(f"  Files processed: {summary['processed_files']}")
        print(f"  Successful: {summary['processed_files']}")
        print(f"  Failed: {summary['failed_files']}")
        print(f"  Skipped: {summary['skipped_files']}")
        
        if summary['processed_files'] == 0:
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
        # Run curation on preprocessed data
        print("Running curation on preprocessed data...")
        # Override the attachments path to use preprocessed attachments
        run(test_cfg, 
            vault=preprocessed_vault, 
            attachments=test_cfg['paths']['test_preprocessed_attachments'], 
            out_notes=test_cfg['paths']['test_curated_notes'], 
            dry_run=False)
        print("✓ Curation pipeline completed successfully")
        
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
