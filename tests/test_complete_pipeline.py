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

def test_complete_pipeline(num_notes=10, preserve_previous=True, seed=None):
    """Test the complete pipeline: raw -> preprocessed -> curated.
    
    Args:
        num_notes: Number of notes to test
        preserve_previous: If True, move previous results to dated backup folder
        seed: Optional random seed for reproducible results
    """
    print(f"Testing complete Obsidian Curator pipeline with {num_notes} notes...")
    if seed is not None:
        print(f"Using random seed: {seed}")
    if preserve_previous:
        print("Previous results will be preserved in dated folders")
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
    
    # Step 0: Randomly select and copy notes from real vault
    print(f"Step 0: Randomly selecting {num_notes} fresh notes from real vault...")
    print("-" * 40)
    
    import random
    import shutil
    from datetime import datetime
    
    # Set random seed for reproducible results or ensure randomness
    if seed is not None:
        random.seed(seed)
        print(f"✓ Set random seed to {seed} for reproducible results")
    else:
        # Use current time as seed to ensure different selections between runs
        import time
        auto_seed = int(time.time() * 1000) % 1000000
        random.seed(auto_seed)
        print(f"✓ Using automatic random seed: {auto_seed} (for true randomization)")
    
    # Get test raw vault path
    test_raw_vault = test_cfg['paths']['test_raw_vault']
    
    # Preserve previous results if requested
    if preserve_previous:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_base = "tests/test_data/archive"
        
        # Create archive directory
        os.makedirs(backup_base, exist_ok=True)
        
        # Move existing results to timestamped backup
        for vault_name, vault_path in [("raw", test_raw_vault), 
                                      ("preprocessed", preprocessed_vault),
                                      ("curated", curated_vault)]:
            if os.path.exists(vault_path):
                backup_path = f"{backup_base}/{timestamp}_{vault_name}"
                shutil.move(vault_path, backup_path)
                print(f"✓ Archived {vault_name} vault: {backup_path}")
    else:
        # Clean test folders (original behavior)
        if os.path.exists(preprocessed_vault):
            shutil.rmtree(preprocessed_vault)
            print(f"✓ Cleaned preprocessed vault: {preprocessed_vault}")
        
        if os.path.exists(curated_vault):
            shutil.rmtree(curated_vault)
            print(f"✓ Cleaned curated vault: {curated_vault}")
        
        # Clean and recreate raw test folder
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
    
    # For incremental testing, exclude already tested notes
    excluded_notes = set()
    if preserve_previous and os.path.exists("tests/test_data/archive"):
        # Get list of previously tested notes from all archives
        for archive_dir in os.listdir("tests/test_data/archive"):
            archive_path = f"tests/test_data/archive/{archive_dir}"
            if os.path.isdir(archive_path) and archive_dir.endswith("_raw"):
                raw_archive = f"{archive_path}/notes"
                if os.path.exists(raw_archive):
                    for note_file in os.listdir(raw_archive):
                        if note_file.startswith("test_note_") and note_file.endswith(".md"):
                            # Extract original note name
                            original_name = note_file.replace("test_note_", "").split("_", 1)[1]
                            excluded_notes.add(original_name)
        
        if excluded_notes:
            print(f"📋 Incremental mode: Excluding {len(excluded_notes)} previously tested notes")
            all_notes = [note for note in all_notes if note.name not in excluded_notes]
            print(f"📋 Available for testing: {len(all_notes)} new notes")
    
    # Categorize notes by attachment status for reporting
    # Build a mapping of sanitized names to actual attachment directories
    attachments_dir = Path(raw_vault) / "attachments"
    attachment_mapping = {}
    if attachments_dir.exists():
        for att_dir in attachments_dir.iterdir():
            if att_dir.is_dir() and att_dir.name.endswith('.resources'):
                # Remove .resources extension to get the base name
                base_name = att_dir.name[:-10]
                attachment_mapping[base_name] = att_dir
    
    def sanitize_filename(filename):
        """Sanitize filename the same way Obsidian/Evernote does for attachment directories."""
        # Convert multiple spaces to double underscores, single spaces to single underscores
        import re
        sanitized = re.sub(r'\s{2,}', '__', filename)  # Multiple spaces -> __
        sanitized = re.sub(r'\s', '_', sanitized)      # Single spaces -> _
        return sanitized
    
    notes_with_attachments = []
    notes_without_attachments = []
    
    for note in all_notes:
        note_stem = note.stem
        
        # Try exact match first
        exact_att_dir = Path(raw_vault) / "attachments" / f"{note_stem}.resources"
        if exact_att_dir.exists():
            notes_with_attachments.append(note)
            continue
            
        # Try sanitized match
        sanitized_stem = sanitize_filename(note_stem)
        if sanitized_stem in attachment_mapping:
            notes_with_attachments.append(note)
            continue
            
        # No attachments found
        notes_without_attachments.append(note)
    
    print(f"Notes with attachments: {len(notes_with_attachments)}")
    print(f"Notes without attachments: {len(notes_without_attachments)}")
    
    # TRUE RANDOM SELECTION: Sample from ALL notes regardless of attachments
    # This fixes the selection bias that was causing repeated notes
    if len(all_notes) < num_notes:
        print(f"⚠️  Warning: Only {len(all_notes)} notes available, selecting all")
        selected_notes = all_notes
    else:
        selected_notes = random.sample(all_notes, num_notes)
    
    # Report the mix we actually got
    selected_with_attachments = []
    selected_without_attachments = []
    for note in selected_notes:
        note_stem = note.stem
        att_dir = Path(raw_vault) / "attachments" / f"{note_stem}.resources"
        if att_dir.exists():
            selected_with_attachments.append(note)
        else:
            selected_without_attachments.append(note)
    
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
        
        # Copy associated attachments using the same sanitized matching logic
        note_stem = note_path.stem
        real_attachments_dir = None
        
        # Try exact match first
        exact_att_dir = Path(raw_vault) / "attachments" / f"{note_stem}.resources"
        if exact_att_dir.exists():
            real_attachments_dir = exact_att_dir
        else:
            # Try sanitized match
            sanitized_stem = sanitize_filename(note_stem)
            if sanitized_stem in attachment_mapping:
                real_attachments_dir = attachment_mapping[sanitized_stem]
        
        if real_attachments_dir and real_attachments_dir.exists():
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
    
    print(f"✓ Copied {len(selected_notes)} fresh notes to test folder")
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
        # Process all selected notes (they're already selected and copied)
        print(f"Processing all {len(selected_notes)} selected notes...")
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
    
    # Show archive information if preserving
    if preserve_previous and os.path.exists("tests/test_data/archive"):
        archives = [d for d in os.listdir("tests/test_data/archive") if d.endswith("_curated")]
        if archives:
            print(f"\n📁 Previous results preserved in tests/test_data/archive/")
            print(f"   {len(archives)} test runs archived")
            latest = max(archives)
            print(f"   Latest: {latest}")
    
    return True

def main():
    """Run the complete pipeline test."""
    import sys
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the complete Obsidian Curator pipeline')
    parser.add_argument('num_notes', type=int, nargs='?', default=10, 
                       help='Number of notes to test (default: 10)')
    parser.add_argument('--seed', type=int, 
                       help='Random seed for reproducible results')
    parser.add_argument('--no-preserve', action='store_true', 
                       help='Don\'t preserve previous results (delete them)')
    parser.add_argument('--incremental', action='store_true',
                       help='Incremental mode: only test new notes, keep existing triage')
    
    # Handle both old-style (positional) and new-style (argparse) arguments
    if len(sys.argv) == 2 and sys.argv[1].isdigit():
        # Old style: just number of notes
        args = parser.parse_args([sys.argv[1]])
    else:
        args = parser.parse_args()
    
    preserve_previous = not args.no_preserve
    
    if args.incremental:
        print("🔄 Incremental mode: Testing new notes while preserving triage decisions")
        preserve_previous = True  # Force preservation in incremental mode
    
    success = test_complete_pipeline(args.num_notes, preserve_previous, args.seed)
    
    if success:
        print("\n🎉 Complete pipeline test passed!")
        print("The Obsidian Curator system is working correctly.")
        return 0
    else:
        print("\n❌ Complete pipeline test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
