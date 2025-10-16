#!/usr/bin/env python3
"""
Performance comparison test between raw and preprocessed notes.
Tests quality, readability, metadata consistency, and attachment handling.
"""

import os
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import Counter, defaultdict
import re

# Import our analysis modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.dirname(__file__))

from src.analysis.content_analyzer import ContentAnalyzer
from src.analysis.technical_characterizer import TechnicalCharacterizer
from src.preprocessing.content_classifier import ContentClassifier
from src.preprocessing.quality_validator import QualityValidator
from src.utils.file_handler import FileHandler


class PerformanceTester:
    """Comprehensive performance testing for raw vs preprocessed notes."""
    
    def __init__(self, 
                 raw_vault_path: str = "/Users/jose/Documents/Obsidian/Evermd",
                 processed_vault_path: str = "/Users/jose/Documents/Obsidian/Ever-output",
                 sample_size: int = 50):
        
        self.raw_vault_path = Path(raw_vault_path)
        self.processed_vault_path = Path(processed_vault_path)
        self.sample_size = sample_size
        
        # Initialize analysis tools
        self.content_analyzer = ContentAnalyzer()
        self.technical_characterizer = TechnicalCharacterizer()
        self.classifier = ContentClassifier()
        self.validator = QualityValidator()
        self.file_handler = FileHandler()
        
        # Results storage
        self.results = {
            'sample_info': {},
            'raw_notes': [],
            'processed_notes': [],
            'comparisons': [],
            'summary': {}
        }
    
    def run_performance_test(self) -> Dict:
        """Run the complete performance comparison test."""
        print("🧪 Starting Performance Comparison Test")
        print("=" * 60)
        
        # Step 1: Select representative sample
        print("📋 Step 1: Selecting representative sample...")
        sample_pairs = self._select_sample_pairs()
        self.results['sample_info'] = {
            'total_pairs': len(sample_pairs),
            'categories': list(set(pair['category'] for pair in sample_pairs))
        }
        print(f"   Selected {len(sample_pairs)} note pairs across {len(self.results['sample_info']['categories'])} categories")
        
        # Step 2: Analyze raw notes
        print("\n📊 Step 2: Analyzing raw notes...")
        raw_results = self._analyze_notes_batch(sample_pairs, 'raw')
        self.results['raw_notes'] = raw_results
        
        # Step 3: Analyze processed notes
        print("\n✨ Step 3: Analyzing processed notes...")
        processed_results = self._analyze_notes_batch(sample_pairs, 'processed')
        self.results['processed_notes'] = processed_results
        
        # Step 4: Compare results
        print("\n🔄 Step 4: Comparing results...")
        comparisons = self._compare_notes(raw_results, processed_results)
        self.results['comparisons'] = comparisons
        
        # Step 5: Generate summary
        print("\n📈 Step 5: Generating summary...")
        summary = self._generate_summary(comparisons)
        self.results['summary'] = summary
        
        # Step 6: Save results
        self._save_results()
        
        return self.results
    
    def _select_sample_pairs(self) -> List[Dict]:
        """Select representative sample pairs from different categories."""
        sample_pairs = []
        
        # Get all processed notes and their categories
        processed_files = list(self.processed_vault_path.rglob("*.md"))
        
        # Group by category using classification
        category_files = defaultdict(list)
        
        print("   Classifying notes to group by category...")
        for i, file_path in enumerate(processed_files[:200]):  # Sample first 200 for classification
            try:
                frontmatter, content = self.file_handler.read_note(file_path)
                classification = self.classifier.classify_note(content, frontmatter)
                category = classification['category']
                category_files[category].append(file_path)
            except Exception as e:
                print(f"   Warning: Could not classify {file_path.name}: {e}")
        
        # Select samples from each category
        samples_per_category = max(1, self.sample_size // len(category_files))
        
        for category, files in category_files.items():
            if not files:
                continue
                
            # Randomly sample from this category
            selected_files = random.sample(files, min(samples_per_category, len(files)))
            
            for processed_file in selected_files:
                # Find corresponding raw file
                relative_path = processed_file.relative_to(self.processed_vault_path)
                raw_file = self.raw_vault_path / relative_path
                
                if raw_file.exists():
                    sample_pairs.append({
                        'category': category,
                        'raw_file': raw_file,
                        'processed_file': processed_file,
                        'filename': raw_file.name
                    })
        
        # If we don't have enough samples, fill with random selection
        if len(sample_pairs) < self.sample_size:
            remaining_files = [f for f in processed_files if f not in [p['processed_file'] for p in sample_pairs]]
            additional_needed = self.sample_size - len(sample_pairs)
            
            for file_path in random.sample(remaining_files, min(additional_needed, len(remaining_files))):
                relative_path = file_path.relative_to(self.processed_vault_path)
                raw_file = self.raw_vault_path / relative_path
                
                if raw_file.exists():
                    sample_pairs.append({
                        'category': 'mixed',
                        'raw_file': raw_file,
                        'processed_file': file_path,
                        'filename': raw_file.name
                    })
        
        return sample_pairs[:self.sample_size]
    
    def _analyze_notes_batch(self, sample_pairs: List[Dict], note_type: str) -> List[Dict]:
        """Analyze a batch of notes (raw or processed)."""
        results = []
        vault_path = self.raw_vault_path if note_type == 'raw' else self.processed_vault_path
        
        for i, pair in enumerate(sample_pairs):
            file_path = pair['raw_file'] if note_type == 'raw' else pair['processed_file']
            
            try:
                print(f"   Analyzing {note_type} note {i+1}/{len(sample_pairs)}: {file_path.name}")
                
                # Read note
                frontmatter, content = self.file_handler.read_note(file_path)
                
                # Basic analysis
                note_info = {
                    'body': content,
                    'frontmatter': frontmatter,
                    'filename': file_path.name,
                    'file_path': str(file_path)
                }
                analysis = self.content_analyzer.analyze_note(note_info)
                
                # Classification
                classification = self.classifier.classify_note(content, frontmatter)
                
                # Quality validation
                validation = self.validator.validate_note(content, frontmatter, file_path.name)
                
                # Technical characterization (simplified for single note)
                technical = {
                    'content_length': len(content),
                    'has_frontmatter': bool(frontmatter),
                    'frontmatter_fields': list(frontmatter.keys()) if frontmatter else []
                }
                
                # Attachment analysis
                attachment_analysis = self._analyze_attachments(content, file_path)
                
                result = {
                    'filename': file_path.name,
                    'category': pair['category'],
                    'file_path': str(file_path),
                    'analysis': analysis,
                    'classification': classification,
                    'validation': validation,
                    'technical': technical,
                    'attachments': attachment_analysis,
                    'file_size': len(content),
                    'frontmatter_size': len(str(frontmatter)) if frontmatter else 0
                }
                
                results.append(result)
                
            except Exception as e:
                print(f"   Error analyzing {file_path.name}: {e}")
                results.append({
                    'filename': file_path.name,
                    'category': pair['category'],
                    'error': str(e),
                    'file_path': str(file_path)
                })
        
        return results
    
    def _analyze_attachments(self, content: str, file_path: Path) -> Dict:
        """Analyze attachment references in the note."""
        attachment_pattern = re.compile(r'!\[\[attachments/([^\]]+)\]\]')
        references = attachment_pattern.findall(content)
        
        analysis = {
            'total_references': len(references),
            'valid_references': 0,
            'missing_references': [],
            'attachment_types': Counter()
        }
        
        # Check if attachments exist
        attachments_path = file_path.parent.parent / "attachments"
        for ref in references:
            attachment_file = attachments_path / ref
            if attachment_file.exists():
                analysis['valid_references'] += 1
                # Determine file type
                ext = attachment_file.suffix.lower()
                analysis['attachment_types'][ext] += 1
            else:
                analysis['missing_references'].append(ref)
        
        return analysis
    
    def _compare_notes(self, raw_results: List[Dict], processed_results: List[Dict]) -> List[Dict]:
        """Compare raw vs processed notes."""
        comparisons = []
        
        # Create lookup for processed results
        processed_lookup = {r['filename']: r for r in processed_results if 'error' not in r}
        
        for raw_result in raw_results:
            if 'error' in raw_result:
                continue
                
            filename = raw_result['filename']
            if filename not in processed_lookup:
                continue
                
            processed_result = processed_lookup[filename]
            
            comparison = {
                'filename': filename,
                'category': raw_result['category'],
                'improvements': [],
                'regressions': [],
                'metrics': {}
            }
            
            # Compare file sizes
            raw_size = raw_result['file_size']
            processed_size = processed_result['file_size']
            size_change = processed_size - raw_size
            size_change_pct = (size_change / raw_size * 100) if raw_size > 0 else 0
            
            comparison['metrics']['size_change'] = size_change
            comparison['metrics']['size_change_pct'] = size_change_pct
            
            if size_change < 0:
                comparison['improvements'].append(f"Content reduced by {abs(size_change_pct):.1f}%")
            elif size_change > 0:
                comparison['regressions'].append(f"Content increased by {size_change_pct:.1f}%")
            
            # Compare quality scores
            raw_quality = raw_result['validation']['overall_quality']
            processed_quality = processed_result['validation']['overall_quality']
            
            quality_improvement = self._compare_quality_scores(raw_quality, processed_quality)
            if quality_improvement > 0:
                comparison['improvements'].append(f"Quality improved: {raw_quality} → {processed_quality}")
            elif quality_improvement < 0:
                comparison['regressions'].append(f"Quality declined: {raw_quality} → {processed_quality}")
            
            # Compare metadata
            raw_metadata = raw_result['analysis']['metadata_analysis']
            processed_metadata = processed_result['analysis']['metadata_analysis']
            
            metadata_improvements = self._compare_metadata(raw_metadata, processed_metadata)
            comparison['improvements'].extend(metadata_improvements)
            
            # Compare attachments
            raw_attachments = raw_result['attachments']
            processed_attachments = processed_result['attachments']
            
            if raw_attachments['total_references'] != processed_attachments['total_references']:
                comparison['regressions'].append(f"Attachment references changed: {raw_attachments['total_references']} → {processed_attachments['total_references']}")
            
            if processed_attachments['missing_references']:
                comparison['regressions'].append(f"Missing attachments: {len(processed_attachments['missing_references'])}")
            
            # Compare boilerplate removal
            raw_boilerplate_ratio = raw_result['analysis']['boilerplate_score']['boilerplate_ratio']
            processed_boilerplate_ratio = processed_result['analysis']['boilerplate_score']['boilerplate_ratio']
            
            if raw_boilerplate_ratio > processed_boilerplate_ratio:
                improvement = raw_boilerplate_ratio - processed_boilerplate_ratio
                comparison['improvements'].append(f"Boilerplate ratio improved by {improvement:.3f}")
            elif processed_boilerplate_ratio > raw_boilerplate_ratio:
                regression = processed_boilerplate_ratio - raw_boilerplate_ratio
                comparison['regressions'].append(f"Boilerplate ratio worsened by {regression:.3f}")
            
            comparisons.append(comparison)
        
        return comparisons
    
    def _compare_quality_scores(self, raw_quality: str, processed_quality: str) -> int:
        """Compare quality scores (returns -1, 0, 1 for worse, same, better)."""
        quality_order = ['failed', 'poor', 'acceptable', 'good', 'excellent']
        raw_score = quality_order.index(raw_quality) if raw_quality in quality_order else 0
        processed_score = quality_order.index(processed_quality) if processed_quality in quality_order else 0
        return processed_score - raw_score
    
    def _compare_metadata(self, raw_metadata: Dict, processed_metadata: Dict) -> List[str]:
        """Compare metadata improvements."""
        improvements = []
        
        # Check date standardization
        if raw_metadata.get('date_issues') and not processed_metadata.get('date_issues'):
            improvements.append("Date format standardized")
        
        # Check tag normalization
        if raw_metadata.get('tag_issues') and not processed_metadata.get('tag_issues'):
            improvements.append("Tags normalized")
        
        # Check field ordering
        if raw_metadata.get('field_order_issues') and not processed_metadata.get('field_order_issues'):
            improvements.append("Metadata fields reordered")
        
        return improvements
    
    def _generate_summary(self, comparisons: List[Dict]) -> Dict:
        """Generate summary statistics from comparisons."""
        if not comparisons:
            return {}
        
        summary = {
            'total_comparisons': len(comparisons),
            'categories': Counter(c['category'] for c in comparisons),
            'improvements': {
                'total_improvements': 0,
                'common_improvements': Counter(),
                'notes_with_improvements': 0
            },
            'regressions': {
                'total_regressions': 0,
                'common_regressions': Counter(),
                'notes_with_regressions': 0
            },
            'size_changes': {
                'notes_reduced': 0,
                'notes_increased': 0,
                'notes_unchanged': 0,
                'avg_size_change_pct': 0
            },
            'quality_changes': {
                'improved': 0,
                'declined': 0,
                'unchanged': 0
            }
        }
        
        size_changes = []
        
        for comparison in comparisons:
            # Count improvements
            improvements = comparison['improvements']
            regressions = comparison['regressions']
            
            if improvements:
                summary['improvements']['notes_with_improvements'] += 1
                summary['improvements']['total_improvements'] += len(improvements)
                for improvement in improvements:
                    summary['improvements']['common_improvements'][improvement] += 1
            
            if regressions:
                summary['regressions']['notes_with_regressions'] += 1
                summary['regressions']['total_regressions'] += len(regressions)
                for regression in regressions:
                    summary['regressions']['common_regressions'][regression] += 1
            
            # Size changes
            size_change_pct = comparison['metrics'].get('size_change_pct', 0)
            size_changes.append(size_change_pct)
            
            if size_change_pct < -5:  # Significant reduction
                summary['size_changes']['notes_reduced'] += 1
            elif size_change_pct > 5:  # Significant increase
                summary['size_changes']['notes_increased'] += 1
            else:
                summary['size_changes']['notes_unchanged'] += 1
        
        # Calculate average size change
        if size_changes:
            summary['size_changes']['avg_size_change_pct'] = sum(size_changes) / len(size_changes)
        
        return summary
    
    def _save_results(self):
        """Save test results to file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"performance_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
    
    def print_summary(self):
        """Print a human-readable summary of the test results."""
        summary = self.results['summary']
        
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        print(f"\n📋 Sample Information:")
        print(f"   Total comparisons: {summary.get('total_comparisons', 0)}")
        print(f"   Categories tested: {', '.join(summary.get('categories', {}).keys())}")
        
        print(f"\n✅ Improvements:")
        improvements = summary.get('improvements', {})
        print(f"   Notes with improvements: {improvements.get('notes_with_improvements', 0)}")
        print(f"   Total improvements: {improvements.get('total_improvements', 0)}")
        
        if improvements.get('common_improvements'):
            print("   Most common improvements:")
            for improvement, count in improvements['common_improvements'].most_common(5):
                print(f"     • {improvement}: {count} notes")
        
        print(f"\n⚠️  Regressions:")
        regressions = summary.get('regressions', {})
        print(f"   Notes with regressions: {regressions.get('notes_with_regressions', 0)}")
        print(f"   Total regressions: {regressions.get('total_regressions', 0)}")
        
        if regressions.get('common_regressions'):
            print("   Most common regressions:")
            for regression, count in regressions['common_regressions'].most_common(3):
                print(f"     • {regression}: {count} notes")
        
        print(f"\n📏 Size Changes:")
        size_changes = summary.get('size_changes', {})
        print(f"   Notes reduced in size: {size_changes.get('notes_reduced', 0)}")
        print(f"   Notes increased in size: {size_changes.get('notes_increased', 0)}")
        print(f"   Notes unchanged: {size_changes.get('notes_unchanged', 0)}")
        print(f"   Average size change: {size_changes.get('avg_size_change_pct', 0):.1f}%")
        
        print(f"\n🎯 Overall Assessment:")
        total_improvements = improvements.get('total_improvements', 0)
        total_regressions = regressions.get('total_regressions', 0)
        
        if total_improvements > total_regressions * 2:
            print("   🎉 EXCELLENT: Significant improvements with minimal regressions")
        elif total_improvements > total_regressions:
            print("   ✅ GOOD: More improvements than regressions")
        elif total_improvements == total_regressions:
            print("   ⚖️  NEUTRAL: Equal improvements and regressions")
        else:
            print("   ⚠️  NEEDS REVIEW: More regressions than improvements")


def main():
    """Main function to run the performance test."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test preprocessing performance")
    parser.add_argument("--sample-size", type=int, default=50, help="Number of note pairs to test")
    parser.add_argument("--raw-vault", default="/Users/jose/Documents/Obsidian/Evermd", help="Path to raw vault")
    parser.add_argument("--processed-vault", default="/Users/jose/Documents/Obsidian/Ever-output", help="Path to processed vault")
    
    args = parser.parse_args()
    
    tester = PerformanceTester(
        raw_vault_path=args.raw_vault,
        processed_vault_path=args.processed_vault,
        sample_size=args.sample_size
    )
    
    results = tester.run_performance_test()
    tester.print_summary()
    
    return results


if __name__ == "__main__":
    main()
