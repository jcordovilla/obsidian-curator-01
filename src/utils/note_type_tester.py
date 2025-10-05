#!/usr/bin/env python3
"""
Note Type Tester

Crawls the source vault to find one example of each note type,
then tests the complete pipeline performance on this diverse sample.
Provides comprehensive evaluation of system performance across different content types.
"""

import argparse
import json
import logging
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.preprocessing.web_clipping_cleaner import clean_html_like_clipping
import config


class NoteTypeTester:
    """Crawls vault to find diverse note types and tests pipeline performance."""
    
    def __init__(self, source_vault: str):
        self.source_vault = Path(source_vault)
        self.note_types = {}
        self.test_results = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the tester."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f'note_type_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def classify_note_type(self, note_path: Path) -> str:
        """Classify a note into one of the main types."""
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter
            frontmatter = None
            if content.startswith('---'):
                try:
                    import yaml
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        content_body = parts[2]
                    else:
                        content_body = content
                except:
                    content_body = content
            else:
                content_body = content
            
            # Check for attachments
            attachments_dir = self.source_vault / "attachments"
            attachment_folder = attachments_dir / f"{note_path.stem}.resources"
            has_pdf = attachment_folder.exists() and any(
                f.suffix.lower() == '.pdf' for f in attachment_folder.iterdir() if f.is_file()
            )
            has_audio = attachment_folder.exists() and any(
                f.suffix.lower() in ['.mp3', '.wav', '.m4a', '.ogg', '.flac'] 
                for f in attachment_folder.iterdir() if f.is_file()
            )
            
            # Classify based on content and structure
            content_lower = content_body.lower()
            
            # Web clipping indicators
            if any(indicator in content_lower for indicator in [
                'skip to', 'jump to', 'navigation', 'menu', 'footer',
                'subscribe', 'newsletter', 'cookie', 'privacy policy',
                'share on', 'follow us', 'social media'
            ]):
                return 'web_clipping'
            
            # PDF document indicators
            if has_pdf or 'pdf' in content_lower or 'document' in frontmatter.get('type', '').lower():
                return 'pdf_document'
            
            # Audio note indicators
            if has_audio or 'audio' in content_lower or 'transcription' in content_lower:
                return 'audio_note'
            
            # Image note indicators (OCR content)
            if any(indicator in content_lower for indicator in [
                'image', 'photo', 'screenshot', 'scan', 'ocr'
            ]) or len(content_body.strip()) < 200:
                return 'image_note'
            
            # Web reference indicators
            if content_body.count('http') > 3 or 'source:' in content_lower:
                return 'web_reference'
            
            # Structured note indicators
            if content_body.count('#') > 3 or '##' in content_body:
                return 'structured_note'
            
            # Short note indicators
            if len(content_body.strip()) < 100:
                return 'short_note'
            
            # Default to text note
            return 'text_note'
            
        except Exception as e:
            self.logger.warning(f"Error classifying {note_path.name}: {e}")
            return 'unknown'
    
    def crawl_for_note_types(self) -> Dict[str, Path]:
        """Crawl the vault to find one example of each note type."""
        self.logger.info(f"🔍 Crawling {self.source_vault} for diverse note types...")
        
        # Get all markdown files recursively (vault structure has files in subdirectories)
        all_notes = list(self.source_vault.rglob("*.md"))
        
        # Filter out files in .obsidian directory and other system directories
        all_notes = [
            note for note in all_notes 
            if not any(part.startswith('.') for part in note.parts)
        ]
        
        random.shuffle(all_notes)  # Randomize order
        
        found_types = {}
        type_counts = {}
        
        for note_path in all_notes:
            if len(found_types) >= 8:  # Stop when we have examples of main types
                break
                
            note_type = self.classify_note_type(note_path)
            
            if note_type not in type_counts:
                type_counts[note_type] = 0
            type_counts[note_type] += 1
            
            # Take first example of each type
            if note_type not in found_types:
                found_types[note_type] = note_path
                self.logger.info(f"  ✅ Found {note_type}: {note_path.name}")
        
        self.logger.info(f"\n📊 Note type distribution in sample:")
        for note_type, count in sorted(type_counts.items()):
            status = "✅" if note_type in found_types else "❌"
            self.logger.info(f"  {status} {note_type}: {count} notes")
        
        return found_types
    
    def test_preprocessing(self, note_path: Path) -> Dict:
        """Test preprocessing on a single note."""
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Extract frontmatter
            frontmatter = None
            if original_content.startswith('---'):
                try:
                    import yaml
                    parts = original_content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        content_body = parts[2]
                    else:
                        content_body = original_content
                except:
                    content_body = original_content
            else:
                content_body = original_content
            
            # Test preprocessing
            cleaned_content = clean_html_like_clipping(content_body, frontmatter)
            
            # Calculate metrics
            if frontmatter is not None:
                original_body_length = len(content_body)
                cleaned_length = len(cleaned_content)
                reduction_percentage = ((original_body_length - cleaned_length) / original_body_length * 100) if original_body_length > 0 else 0
                original_length = len(original_content)
            else:
                original_length = len(original_content)
                cleaned_length = len(cleaned_content)
                reduction_percentage = ((original_length - cleaned_length) / original_length * 100) if original_length > 0 else 0
            
            return {
                'success': True,
                'original_length': original_length,
                'cleaned_length': cleaned_length,
                'reduction_percentage': reduction_percentage,
                'note_type': self.classify_note_type(note_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'note_type': self.classify_note_type(note_path)
            }
    
    def run_pipeline_test(self, note_types: Dict[str, Path]) -> Dict:
        """Run the complete pipeline test on the diverse sample."""
        self.logger.info(f"\n🚀 Running pipeline test on {len(note_types)} diverse notes...")
        
        # Create temporary test directories
        test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_raw_dir = Path(f"tests/test_data/raw_{test_timestamp}")
        test_preprocessed_dir = Path(f"tests/test_data/preprocessed_{test_timestamp}")
        test_curated_dir = Path(f"tests/test_data/curated_{test_timestamp}")
        
        # Create directories
        test_raw_dir.mkdir(parents=True, exist_ok=True)
        test_preprocessed_dir.mkdir(parents=True, exist_ok=True)
        test_curated_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'timestamp': test_timestamp,
            'note_types_tested': {},
            'preprocessing_results': {},
            'curation_results': {},
            'summary': {}
        }
        
        # Copy notes to test directory
        self.logger.info("📁 Setting up test environment...")
        for note_type, note_path in note_types.items():
            dest_path = test_raw_dir / note_path.name
            import shutil
            shutil.copy2(note_path, dest_path)
            results['note_types_tested'][note_type] = {
                'original_path': str(note_path),
                'test_path': str(dest_path)
            }
        
        # Test preprocessing
        self.logger.info("🧹 Testing preprocessing...")
        preprocessing_success = 0
        preprocessing_total = len(note_types)
        
        for note_type, note_path in note_types.items():
            self.logger.info(f"  Processing {note_type}: {note_path.name}")
            result = self.test_preprocessing(note_path)
            results['preprocessing_results'][note_type] = result
            
            if result['success']:
                preprocessing_success += 1
                self.logger.info(f"    ✅ {result['reduction_percentage']:.1f}% reduction")
            else:
                self.logger.error(f"    ❌ Failed: {result['error']}")
        
        # Test curation (simplified - just check if it would work)
        self.logger.info("🎯 Testing curation readiness...")
        curation_ready = 0
        
        for note_type, note_path in note_types.items():
            try:
                # Basic check if note would be processed by curation
                with open(note_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Simple validation
                if len(content.strip()) > 50:  # Has substantial content
                    curation_ready += 1
                    results['curation_results'][note_type] = {
                        'ready': True,
                        'content_length': len(content)
                    }
                else:
                    results['curation_results'][note_type] = {
                        'ready': False,
                        'reason': 'Insufficient content'
                    }
                    
            except Exception as e:
                results['curation_results'][note_type] = {
                    'ready': False,
                    'reason': f'Error: {e}'
                }
        
        # Generate summary
        results['summary'] = {
            'total_note_types': len(note_types),
            'preprocessing_success_rate': (preprocessing_success / preprocessing_total * 100) if preprocessing_total > 0 else 0,
            'curation_ready_rate': (curation_ready / len(note_types) * 100),
            'average_reduction': sum(
                r.get('reduction_percentage', 0) 
                for r in results['preprocessing_results'].values() 
                if r.get('success', False)
            ) / max(1, preprocessing_success)
        }
        
        # Cleanup test directories
        import shutil
        if test_raw_dir.exists():
            shutil.rmtree(test_raw_dir)
        if test_preprocessed_dir.exists():
            shutil.rmtree(test_preprocessed_dir)
        if test_curated_dir.exists():
            shutil.rmtree(test_curated_dir)
        
        return results
    
    def print_results(self, results: Dict):
        """Print comprehensive test results."""
        print("\n" + "="*80)
        print("🎯 NOTE TYPE DIVERSITY TEST RESULTS")
        print("="*80)
        
        # Summary
        summary = results['summary']
        print(f"\n📊 SUMMARY:")
        print(f"  Total Note Types Tested: {summary['total_note_types']}")
        print(f"  Preprocessing Success Rate: {summary['preprocessing_success_rate']:.1f}%")
        print(f"  Curation Ready Rate: {summary['curation_ready_rate']:.1f}%")
        print(f"  Average Content Reduction: {summary['average_reduction']:.1f}%")
        
        # Note Types Found
        print(f"\n📝 NOTE TYPES FOUND:")
        for note_type, info in results['note_types_tested'].items():
            print(f"  ✅ {note_type}: {Path(info['original_path']).name}")
        
        # Preprocessing Results
        print(f"\n🧹 PREPROCESSING RESULTS:")
        for note_type, result in results['preprocessing_results'].items():
            if result['success']:
                print(f"  ✅ {note_type}: {result['reduction_percentage']:.1f}% reduction "
                      f"({result['original_length']} → {result['cleaned_length']} chars)")
            else:
                print(f"  ❌ {note_type}: FAILED - {result['error']}")
        
        # Curation Readiness
        print(f"\n🎯 CURATION READINESS:")
        for note_type, result in results['curation_results'].items():
            status = "✅" if result['ready'] else "❌"
            reason = f" - {result['reason']}" if not result['ready'] else ""
            content_len = result.get('content_length', 0)
            print(f"  {status} {note_type}: {content_len} chars{reason}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if summary['preprocessing_success_rate'] < 100:
            print(f"  ⚠️  Preprocessing issues detected - investigate failed note types")
        
        if summary['curation_ready_rate'] < 100:
            print(f"  ⚠️  Some note types may not be suitable for curation")
        
        if summary['average_reduction'] > 30:
            print(f"  ✅ Good clutter removal - system is aggressive on web content")
        elif summary['average_reduction'] < 10:
            print(f"  ✅ Conservative cleaning - preserving personal content")
        else:
            print(f"  ✅ Balanced cleaning approach")
        
        print(f"\n📈 OVERALL ASSESSMENT:")
        if summary['preprocessing_success_rate'] >= 90 and summary['curation_ready_rate'] >= 80:
            print(f"  🎉 EXCELLENT: System handles diverse content types well")
        elif summary['preprocessing_success_rate'] >= 75 and summary['curation_ready_rate'] >= 60:
            print(f"  ✅ GOOD: System generally handles diverse content")
        else:
            print(f"  ⚠️  NEEDS IMPROVEMENT: Some content types causing issues")
        
        print("\n" + "="*80)
    
    def run_full_test(self) -> Dict:
        """Run the complete note type diversity test."""
        self.logger.info("🚀 Starting Note Type Diversity Test")
        self.logger.info("="*60)
        
        # Step 1: Crawl for diverse note types
        note_types = self.crawl_for_note_types()
        
        if not note_types:
            raise ValueError("No note types found in the vault")
        
        # Step 2: Run pipeline test
        results = self.run_pipeline_test(note_types)
        
        # Step 3: Print results
        self.print_results(results)
        
        # Step 4: Save results
        output_file = f"analysis_output/note_type_test_{results['timestamp']}.json"
        Path("analysis_output").mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"\n💾 Results saved to: {output_file}")
        
        return results


def main():
    """Main entry point for the note type tester."""
    parser = argparse.ArgumentParser(
        description="Test pipeline performance across diverse note types"
    )
    parser.add_argument(
        '--source-vault',
        default=config.RAW_VAULT_PATH,
        help='Path to the source vault (default: from config.py)'
    )
    parser.add_argument(
        '--output',
        help='Custom output file for results'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize tester
        tester = NoteTypeTester(args.source_vault)
        
        # Run the test
        results = tester.run_full_test()
        
        # Save to custom output if specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Additional results saved to: {args.output}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
