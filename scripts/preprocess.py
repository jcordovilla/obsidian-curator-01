#!/usr/bin/env python3
"""
Obsidian Note Preprocessor - Batch processing application.

This tool preprocesses Obsidian notes by cleaning boilerplate, standardizing metadata,
and optimizing content for knowledge management.
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.preprocessing import BatchProcessor
from config import VAULT_PATH, PREPROCESSING_OUTPUT_PATH


def main():
    parser = argparse.ArgumentParser(
        description="Batch preprocess Obsidian notes for knowledge management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python preprocess.py                                    # Process only new/changed notes (default)
  python preprocess.py --dry-run                          # Test run without changes
  python preprocess.py --sample 20                        # Process 20 sample files
  python preprocess.py --full                             # Process all notes (override incremental)
  python preprocess.py --categories web_clipping          # Process only web clippings
  python preprocess.py --output processed_vault           # Specify output directory
  python preprocess.py --batch-size 100 --workers 8      # High performance settings
        """
    )
    
    parser.add_argument(
        '--vault-path',
        default=VAULT_PATH,
        help=f'Path to Obsidian vault (default: {VAULT_PATH})'
    )
    
    parser.add_argument(
        '--output',
        default=PREPROCESSING_OUTPUT_PATH,
        help=f'Output directory for processed notes (default: {PREPROCESSING_OUTPUT_PATH})'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Analyze and report without making changes'
    )
    
    parser.add_argument(
        '--sample',
        type=int,
        help='Process only a sample of N files for testing'
    )
    
    parser.add_argument(
        '--categories',
        nargs='+',
        choices=['web_clipping', 'pdf_annotation', 'personal_note', 'business_card', 
                'technical_document', 'news_article', 'unknown'],
        help='Process only specific note categories'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Number of files to process in each batch (default: 50)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of parallel workers (default: 4)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Disable backup creation'
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Process all notes (full mode) - normally only new/changed notes are processed'
    )
    
    parser.add_argument(
        '--register-path',
        default='.metadata/note_register.db',
        help='Path to note register database (default: .metadata/note_register.db)'
    )
    
    args = parser.parse_args()
    
    # Validate vault path
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Use the specified output path
    output_path = args.output
    
    print(f"Obsidian Note Preprocessor")
    print(f"Vault: {vault_path}")
    print(f"Output: {output_path}")
    print(f"Dry run: {args.dry_run}")
    if args.categories:
        print(f"Categories: {', '.join(args.categories)}")
    print("-" * 60)
    
    # Initialize batch processor
    processor = BatchProcessor(
        vault_path=str(vault_path),
        output_path=output_path,
        backup=not args.no_backup,
        batch_size=args.batch_size,
        max_workers=args.workers,
        register_path=args.register_path
    )
    
    try:
        if args.sample:
            # Process sample
            print(f"Processing sample of {args.sample} files...")
            results = processor.process_sample(sample_size=args.sample, dry_run=args.dry_run)
            
            print(f"\nSample processing complete:")
            print(f"  Files processed: {results['sample_size']}")
            print(f"  Successful: {results['success_count']}")
            print(f"  Failed: {results['failure_count']}")
            
        elif args.full:
            # Process entire vault (full mode)
            print("Running in full mode (processing all notes)...")
            results = processor.process_vault(
                dry_run=args.dry_run,
                categories_to_process=args.categories
            )
            
            # Display summary
            summary = results['summary']
            print(f"\nProcessing Summary:")
            print(f"  Total files: {summary['total_files']}")
            print(f"  Processed: {summary['processed_files']}")
            print(f"  Failed: {summary['failed_files']}")
            print(f"  Skipped: {summary['skipped_files']}")
            print(f"  Success rate: {summary['success_rate']:.1%}")
            print(f"  Processing time: {summary['processing_time']:.1f}s")
            
            if results['categories']:
                print(f"\nContent Categories:")
                for category, count in sorted(results['categories'].items(), key=lambda x: x[1], reverse=True):
                    print(f"  {category.replace('_', ' ').title()}: {count}")
            
            if results['quality_distribution']:
                print(f"\nQuality Distribution:")
                for quality, count in sorted(results['quality_distribution'].items(), key=lambda x: x[1], reverse=True):
                    print(f"  {quality.title()}: {count}")
            
            if results['errors']:
                print(f"\nErrors (showing first 5):")
                for error in results['errors'][:5]:
                    print(f"  {Path(error['file']).name}: {error['error']}")
        
        else:
            # Default: Incremental processing - only process notes that need preprocessing
            print("Running in incremental mode (default) - processing only new/changed notes...")
            results = processor.process_incremental(dry_run=args.dry_run)
            
            print(f"\nIncremental processing complete:")
            print(f"  Total notes needing processing: {results['total_files']}")
            print(f"  Successfully processed: {results['processed_files']}")
            print(f"  Failed: {results['failed_files']}")
            print(f"  Processing time: {results['processing_time']:.1f}s")
    
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
