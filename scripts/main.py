#!/usr/bin/env python3
"""
Obsidian Curator - Main application for analyzing and preprocessing Obsidian notes.

This tool analyzes Obsidian notes converted from Evernote to identify content types,
boilerplate, and useful content for knowledge management.
"""

import argparse
import sys
import os
import yaml
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.analysis import NoteSampler, ContentAnalyzer, TechnicalCharacterizer
from config import VAULT_PATH, SAMPLE_SIZE, OUTPUT_DIR, PREPROCESSING_OUTPUT_PATH


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and preprocess Obsidian notes for knowledge management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --sample                              # Create sample dataset
  python main.py --analyze                             # Analyze existing sample
  python main.py --technical-analysis                  # Technical characterization
  python main.py --sample --analyze --technical-analysis  # Complete analysis
  python main.py --sample-size 200                     # Custom sample size
        """
    )
    
    parser.add_argument(
        '--vault-path', 
        default=VAULT_PATH,
        help=f'Path to Obsidian vault (default: {VAULT_PATH})'
    )
    
    parser.add_argument(
        '--sample-size', 
        type=int, 
        default=SAMPLE_SIZE,
        help=f'Number of notes to sample (default: {SAMPLE_SIZE})'
    )
    
    parser.add_argument(
        '--sample', 
        action='store_true',
        help='Create a new sample dataset'
    )
    
    parser.add_argument(
        '--analyze', 
        action='store_true',
        help='Analyze the sample dataset'
    )
    
    parser.add_argument(
        '--technical-analysis',
        action='store_true',
        help='Perform comprehensive technical characterization for batch processing'
    )
    
    parser.add_argument(
        '--preprocess',
        action='store_true',
        help='Launch the preprocessing pipeline (use preprocess.py for more options)'
    )
    
    parser.add_argument(
        '--output-dir',
        default=OUTPUT_DIR,
        help=f'Output directory for results (default: {OUTPUT_DIR})'
    )
    
    args = parser.parse_args()
    
    # Validate vault path
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    print(f"Obsidian Curator - Vault Analysis Tool")
    print(f"Vault: {vault_path}")
    print(f"Output: {args.output_dir}")
    print("-" * 60)
    
    # Create sample dataset if requested
    if args.sample:
        print("STEP 1: Creating sample dataset...")
        sampler = NoteSampler(args.vault_path)
        dataset = sampler.create_sample_dataset(args.sample_size)
        dataset_path = sampler.save_sample_dataset(dataset)
        print(f"✓ Sample dataset created: {dataset_path}")
        print()
    
    # Analyze dataset if requested
    if args.analyze:
        print("STEP 2: Analyzing content...")
        
        # Load dataset
        dataset_path = Path(args.output_dir) / "sample_dataset.yaml"
        
        if not dataset_path.exists():
            print(f"Error: Sample dataset not found at {dataset_path}")
            print("Run with --sample flag first to create the dataset.")
            sys.exit(1)
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = yaml.safe_load(f)
        
        # Perform analysis
        analyzer = ContentAnalyzer()
        results = analyzer.analyze_dataset(dataset)
        
        # Save results
        analysis_path = analyzer.save_analysis(results)
        
        # Generate and save report
        report = analyzer.generate_report(results)
        report_path = Path(args.output_dir) / "analysis_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✓ Analysis complete: {analysis_path}")
        print(f"✓ Report generated: {report_path}")
        print()
        
        # Display summary
        print("ANALYSIS SUMMARY")
        print("=" * 40)
        summary = results['summary']
        print(f"Total notes analyzed: {summary['total_notes']}")
        print(f"Average word count: {summary['avg_word_count']:.1f}")
        print(f"High boilerplate notes: {summary['high_boilerplate_count']}")
        print()
        
        print("Content categories:")
        for category, count in sorted(summary['categories'].items(), key=lambda x: x[1], reverse=True):
            percentage = count / summary['total_notes'] * 100
            print(f"  {category.replace('_', ' ').title():<20}: {count:>3} ({percentage:>5.1f}%)")
        
        print()
        print("Quality distribution:")
        for quality, count in sorted(summary['quality_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = count / summary['total_notes'] * 100
            print(f"  {quality.title():<20}: {count:>3} ({percentage:>5.1f}%)")
    
    # Technical characterization if requested
    if args.technical_analysis:
        print("STEP 3: Comprehensive technical characterization...")
        
        # Load dataset
        dataset_path = Path(args.output_dir) / "sample_dataset.yaml"
        
        if not dataset_path.exists():
            print(f"Error: Sample dataset not found at {dataset_path}")
            print("Run with --sample flag first to create the dataset.")
            sys.exit(1)
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = yaml.safe_load(f)
        
        # Perform technical characterization
        characterizer = TechnicalCharacterizer()
        tech_results = characterizer.comprehensive_analysis(dataset)
        
        # Save technical characterization
        tech_path = characterizer.save_technical_characterization(tech_results)
        
        # Generate and save coding agent brief
        brief = characterizer.generate_coding_agent_brief(tech_results)
        brief_path = Path(args.output_dir) / "coding_agent_brief.md"
        with open(brief_path, 'w', encoding='utf-8') as f:
            f.write(brief)
        
        print(f"✓ Technical characterization complete: {tech_path}")
        print(f"✓ Coding agent brief generated: {brief_path}")
        print()
        
        print("TECHNICAL CHARACTERIZATION SUMMARY")
        print("=" * 50)
        
        # Display key technical insights
        metadata_analysis = tech_results.get('metadata_analysis', {})
        boilerplate_catalog = tech_results.get('boilerplate_catalog', {})
        processing_recs = tech_results.get('processing_recommendations', {})
        
        print(f"Required metadata fields: {len(metadata_analysis.get('required_fields', []))}")
        print(f"Boilerplate patterns found: {len(boilerplate_catalog.get('exact_matches', {}))}")
        print(f"Web clipping processing priority: {processing_recs.get('web_clipping_processing', {}).get('priority', 'N/A')}")
        print(f"Attachments to process: {tech_results.get('attachment_analysis', {}).get('total_attachments', 0)}")
        print()
        print("📋 CODING AGENT BRIEF READY")
        print("The comprehensive technical characterization has been generated.")
        print("This document contains all specifications needed to build the batch processing application.")
    
    # Launch preprocessing if requested
    if args.preprocess:
        print("STEP 4: Launching preprocessing pipeline...")
        print("For advanced preprocessing options, use: python preprocess.py --help")
        print()
        
        from src.preprocessing import BatchProcessor
        processor = BatchProcessor(vault_path=args.vault_path, output_path=PREPROCESSING_OUTPUT_PATH)
        
        # Run a small sample first
        print("Running preprocessing sample (10 files, dry run)...")
        sample_results = processor.process_sample(sample_size=10, dry_run=True)
        
        print(f"Sample results: {sample_results['success_count']}/{sample_results['sample_size']} successful")
        print("Use 'python preprocess.py' for full vault processing")
    
    if not args.sample and not args.analyze and not args.technical_analysis and not args.preprocess:
        print("No action specified. Use --sample, --analyze, --technical-analysis, and/or --preprocess flags.")
        print("Run 'python main.py --help' for usage information.")


if __name__ == "__main__":
    main()
