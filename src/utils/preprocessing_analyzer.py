#!/usr/bin/env python3
"""
Preprocessing Analysis Script

This script analyzes the diversity of note types in the source vault and evaluates
the effectiveness of preprocessing patterns against real-world content.

Features:
1. Selects a large sample (100) of random notes from the source vault
2. Analyzes diversity of note types (web clipping, PDF, text-only, etc.)
3. Studies clutter/boilerplate patterns
4. Tests preprocessing effectiveness on all sample notes
5. Evaluates and proposes improvements
"""

import sys
import os
import random
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import json
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

import config
from src.preprocessing.web_clipping_cleaner import clean_html_like_clipping


class PreprocessingAnalyzer:
    """Analyzes preprocessing effectiveness across diverse note types."""
    
    def __init__(self, sample_size: int = 100, source_vault: str = None):
        self.sample_size = sample_size
        self.source_vault = source_vault or "/Users/jose/Documents/Obsidian/Evermd"
        self.results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'sample_size': sample_size,
            'source_vault': self.source_vault,
            'note_types': defaultdict(int),
            'clutter_patterns': defaultdict(int),
            'preprocessing_results': [],
            'effectiveness_summary': {},
            'improvement_recommendations': []
        }
    
    def select_random_sample(self) -> List[Path]:
        """Select a random sample of notes from the source vault."""
        print(f"🔍 Selecting {self.sample_size} random notes from {self.source_vault}...")
        
        # Get all notes from the vault
        all_notes = list(Path(self.source_vault).rglob("*.md"))
        print(f"Found {len(all_notes)} total notes in vault")
        
        if len(all_notes) < self.sample_size:
            print(f"⚠️  Warning: Only {len(all_notes)} notes available, using all")
            return all_notes
        
        # Select random sample
        random.seed(42)  # For reproducible results
        selected_notes = random.sample(all_notes, self.sample_size)
        print(f"✅ Selected {len(selected_notes)} random notes")
        
        return selected_notes
    
    def analyze_note_types(self, notes: List[Path]) -> Dict[str, int]:
        """Analyze the diversity of note types in the sample."""
        print(f"\n📊 Analyzing note types...")
        
        type_counts = defaultdict(int)
        type_examples = defaultdict(list)
        
        for note_path in notes:
            note_type = self._classify_note_type(note_path)
            type_counts[note_type] += 1
            if len(type_examples[note_type]) < 3:  # Keep 3 examples per type
                type_examples[note_type].append(note_path.name)
        
        print("Note Type Distribution:")
        for note_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(notes)) * 100
            print(f"  {note_type}: {count} ({percentage:.1f}%)")
            print(f"    Examples: {', '.join(type_examples[note_type])}")
        
        self.results['note_types'] = dict(type_counts)
        return dict(type_counts)
    
    def _classify_note_type(self, note_path: Path) -> str:
        """Classify a note into different types based on content and attachments."""
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return f"error_reading"
        
        # Check for attachments
        attachments_dir = Path(self.source_vault) / "attachments" / f"{note_path.stem}.resources"
        has_attachments = attachments_dir.exists()
        
        # Check content patterns
        has_html_tags = bool(re.search(r'<[^>]+>', content))
        has_web_source = bool(re.search(r'https?://', content))
        has_frontmatter = content.startswith('---')
        
        # Check for specific content indicators
        has_pdf_attachments = bool(re.search(r'\.pdf', content, re.IGNORECASE))
        has_image_attachments = bool(re.search(r'\.(jpg|jpeg|png|gif|bmp)', content, re.IGNORECASE))
        has_audio_attachments = bool(re.search(r'\.(mp3|wav|m4a|ogg)', content, re.IGNORECASE))
        
        # Determine primary type
        if has_html_tags and has_web_source:
            return "web_clipping"
        elif has_pdf_attachments or (has_attachments and 'pdf' in content.lower()):
            return "pdf_document"
        elif has_image_attachments:
            return "image_notes"
        elif has_audio_attachments:
            return "audio_notes"
        elif has_web_source and not has_html_tags:
            return "web_reference"
        elif has_frontmatter and len(content) > 1000:
            return "structured_note"
        elif len(content) < 200:
            return "short_note"
        else:
            return "text_note"
    
    def analyze_clutter_patterns(self, notes: List[Path]) -> Dict[str, int]:
        """Analyze clutter and boilerplate patterns across the sample."""
        print(f"\n🧹 Analyzing clutter patterns...")
        
        pattern_counts = defaultdict(int)
        pattern_examples = defaultdict(list)
        
        # Define clutter patterns to look for
        clutter_patterns = {
            'navigation_menus': r'(home|menu|search|contact|about|subscribe|login)',
            'skip_links': r'(skip to|jump to|main content|main nav)',
            'advertisements': r'(doubleclick|googleadservices|adsense|advertisement)',
            'social_media': r'(facebook|twitter|linkedin|instagram|share)',
            'footer_content': r'(privacy|terms|copyright|©|all rights reserved)',
            'email_signup': r'(newsletter|subscribe|sign up|email)',
            'cookie_notices': r'(cookie|consent|accept|decline)',
            'html_tags': r'<[^>]+>',
            'urls': r'https?://[^\s]+',
            'markdown_links': r'\[([^\]]+)\]\([^)]+\)',
            'html_entities': r'&[a-zA-Z]+;',
            'navigation_breadcrumbs': r'[^>]+>\s*[^>]+>\s*',
            'sponsored_content': r'(sponsored|outbrain|recommended|you may also like)',
            'tracking_pixels': r'(tracking|analytics|gtag|fbq)',
            'site_navigation': r'(sections|categories|archives|tags)'
        }
        
        for note_path in notes:
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
            except Exception:
                continue
            
            for pattern_name, pattern in clutter_patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    pattern_counts[pattern_name] += len(matches)
                    if len(pattern_examples[pattern_name]) < 2:
                        pattern_examples[pattern_name].append({
                            'file': note_path.name,
                            'matches': matches[:3]  # First 3 matches
                        })
        
        print("Clutter Pattern Frequency:")
        for pattern_name, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern_name}: {count} instances")
            if pattern_examples[pattern_name]:
                example = pattern_examples[pattern_name][0]
                print(f"    Example: {example['file']} -> {example['matches']}")
        
        self.results['clutter_patterns'] = dict(pattern_counts)
        return dict(pattern_counts)
    
    def test_preprocessing_effectiveness(self, notes: List[Path]) -> List[Dict[str, Any]]:
        """Test preprocessing effectiveness on all sample notes."""
        print(f"\n🔧 Testing preprocessing effectiveness...")
        
        preprocessing_results = []
        
        for i, note_path in enumerate(notes, 1):
            print(f"  Processing {i}/{len(notes)}: {note_path.name}")
            
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
            except Exception as e:
                preprocessing_results.append({
                    'file': note_path.name,
                    'error': f"Failed to read file: {e}",
                    'success': False
                })
                continue
            
            # Extract frontmatter if present
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
            try:
                cleaned_content = clean_html_like_clipping(content_body, frontmatter)
                
                # Calculate metrics - compare like with like
                # If we separated frontmatter, compare body to body
                if frontmatter is not None:
                    original_body_length = len(content_body)
                    cleaned_length = len(cleaned_content)
                    reduction_percentage = ((original_body_length - cleaned_length) / original_body_length * 100) if original_body_length > 0 else 0
                    original_length = len(original_content)  # Keep full length for reference
                else:
                    # No frontmatter separation, compare full content
                    original_length = len(original_content)
                    cleaned_length = len(cleaned_content)
                    reduction_percentage = ((original_length - cleaned_length) / original_length * 100) if original_length > 0 else 0
                
                # Count remaining clutter patterns
                remaining_clutter = self._count_remaining_clutter(cleaned_content)
                
                result = {
                    'file': note_path.name,
                    'success': True,
                    'original_length': original_length,
                    'cleaned_length': cleaned_length,
                    'reduction_percentage': reduction_percentage,
                    'remaining_clutter': remaining_clutter,
                    'note_type': self._classify_note_type(note_path),
                    'has_attachments': (Path(self.source_vault) / "attachments" / f"{note_path.stem}.resources").exists()
                }
                
                preprocessing_results.append(result)
                
            except Exception as e:
                preprocessing_results.append({
                    'file': note_path.name,
                    'error': f"Preprocessing failed: {e}",
                    'success': False
                })
        
        self.results['preprocessing_results'] = preprocessing_results
        return preprocessing_results
    
    def _count_remaining_clutter(self, content: str) -> Dict[str, int]:
        """Count remaining clutter patterns in cleaned content."""
        clutter_patterns = {
            'navigation_menus': r'(home|menu|search|contact|about|subscribe|login)',
            'skip_links': r'(skip to|jump to|main content|main nav)',
            'advertisements': r'(doubleclick|googleadservices|adsense|advertisement)',
            'social_media': r'(facebook|twitter|linkedin|instagram|share)',
            'footer_content': r'(privacy|terms|copyright|©|all rights reserved)',
            'email_signup': r'(newsletter|subscribe|sign up|email)',
            'html_tags': r'<[^>]+>',
            'urls': r'https?://[^\s]+'
        }
        
        remaining = {}
        for pattern_name, pattern in clutter_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            remaining[pattern_name] = len(matches)
        
        return remaining
    
    def evaluate_effectiveness(self, preprocessing_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate overall preprocessing effectiveness."""
        print(f"\n📈 Evaluating preprocessing effectiveness...")
        
        successful_results = [r for r in preprocessing_results if r.get('success', False)]
        failed_results = [r for r in preprocessing_results if not r.get('success', False)]
        
        if not successful_results:
            print("❌ No successful preprocessing results to evaluate")
            return {}
        
        # Calculate overall statistics
        avg_reduction = sum(r['reduction_percentage'] for r in successful_results) / len(successful_results)
        avg_original_length = sum(r['original_length'] for r in successful_results) / len(successful_results)
        avg_cleaned_length = sum(r['cleaned_length'] for r in successful_results) / len(successful_results)
        
        # Analyze by note type
        type_effectiveness = defaultdict(list)
        for result in successful_results:
            note_type = result.get('note_type', 'unknown')
            type_effectiveness[note_type].append(result['reduction_percentage'])
        
        type_stats = {}
        for note_type, reductions in type_effectiveness.items():
            type_stats[note_type] = {
                'count': len(reductions),
                'avg_reduction': sum(reductions) / len(reductions),
                'min_reduction': min(reductions),
                'max_reduction': max(reductions)
            }
        
        # Count remaining clutter patterns
        total_remaining_clutter = defaultdict(int)
        for result in successful_results:
            for pattern, count in result.get('remaining_clutter', {}).items():
                total_remaining_clutter[pattern] += count
        
        # Identify problematic patterns
        problematic_patterns = {k: v for k, v in total_remaining_clutter.items() if v > 10}
        
        effectiveness_summary = {
            'total_notes': len(preprocessing_results),
            'successful_notes': len(successful_results),
            'failed_notes': len(failed_results),
            'success_rate': len(successful_results) / len(preprocessing_results) * 100,
            'avg_reduction_percentage': avg_reduction,
            'avg_original_length': avg_original_length,
            'avg_cleaned_length': avg_cleaned_length,
            'type_effectiveness': type_stats,
            'total_remaining_clutter': dict(total_remaining_clutter),
            'problematic_patterns': problematic_patterns
        }
        
        # Print summary
        print(f"Overall Effectiveness:")
        print(f"  Success Rate: {effectiveness_summary['success_rate']:.1f}%")
        print(f"  Average Reduction: {avg_reduction:.1f}%")
        print(f"  Average Original Length: {avg_original_length:.0f} characters")
        print(f"  Average Cleaned Length: {avg_cleaned_length:.0f} characters")
        
        print(f"\nEffectiveness by Note Type:")
        for note_type, stats in sorted(type_stats.items(), key=lambda x: x[1]['avg_reduction'], reverse=True):
            print(f"  {note_type}: {stats['avg_reduction']:.1f}% avg reduction ({stats['count']} notes)")
        
        if problematic_patterns:
            print(f"\nProblematic Patterns (still present):")
            for pattern, count in sorted(problematic_patterns.items(), key=lambda x: x[1], reverse=True):
                print(f"  {pattern}: {count} instances")
        
        self.results['effectiveness_summary'] = effectiveness_summary
        return effectiveness_summary
    
    def generate_improvement_recommendations(self, effectiveness_summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving preprocessing."""
        print(f"\n💡 Generating improvement recommendations...")
        
        recommendations = []
        
        # Analyze success rate
        success_rate = effectiveness_summary.get('success_rate', 0)
        if success_rate < 95:
            recommendations.append(f"Improve error handling - {100-success_rate:.1f}% of notes failed preprocessing")
        
        # Analyze reduction effectiveness
        avg_reduction = effectiveness_summary.get('avg_reduction_percentage', 0)
        if avg_reduction < 20:
            recommendations.append(f"Low content reduction ({avg_reduction:.1f}%) - consider more aggressive cleaning patterns")
        elif avg_reduction > 60:
            recommendations.append(f"High content reduction ({avg_reduction:.1f}%) - verify important content isn't being removed")
        
        # Analyze problematic patterns
        problematic_patterns = effectiveness_summary.get('problematic_patterns', {})
        for pattern, count in problematic_patterns.items():
            if count > 20:
                recommendations.append(f"High remaining {pattern} ({count} instances) - add more specific cleaning patterns")
        
        # Analyze note type effectiveness
        type_effectiveness = effectiveness_summary.get('type_effectiveness', {})
        for note_type, stats in type_effectiveness.items():
            if stats['avg_reduction'] < 10 and stats['count'] > 5:
                recommendations.append(f"Low effectiveness for {note_type} notes - consider type-specific cleaning")
        
        if not recommendations:
            recommendations.append("Preprocessing appears to be working well - monitor for edge cases")
        
        print("Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        self.results['improvement_recommendations'] = recommendations
        return recommendations
    
    def save_results(self, output_file: str = None):
        """Save analysis results to JSON file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"preprocessing_analysis_{timestamp}.json"
        
        output_path = Path("analysis_output") / output_file
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_path}")
        return output_path
    
    def run_analysis(self):
        """Run the complete preprocessing analysis."""
        print("🚀 Starting Preprocessing Analysis")
        print("=" * 60)
        
        # Step 1: Select random sample
        sample_notes = self.select_random_sample()
        
        # Step 2: Analyze note types
        note_types = self.analyze_note_types(sample_notes)
        
        # Step 3: Analyze clutter patterns
        clutter_patterns = self.analyze_clutter_patterns(sample_notes)
        
        # Step 4: Test preprocessing effectiveness
        preprocessing_results = self.test_preprocessing_effectiveness(sample_notes)
        
        # Step 5: Evaluate effectiveness
        effectiveness_summary = self.evaluate_effectiveness(preprocessing_results)
        
        # Step 6: Generate recommendations
        recommendations = self.generate_improvement_recommendations(effectiveness_summary)
        
        # Step 7: Save results
        output_file = self.save_results()
        
        print("\n✅ Analysis Complete!")
        print(f"Results saved to: {output_file}")
        
        return self.results


def main():
    """Main entry point for the preprocessing analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze preprocessing effectiveness across diverse note types')
    parser.add_argument('--sample-size', type=int, default=100,
                       help='Number of notes to sample (default: 100)')
    parser.add_argument('--source-vault', type=str,
                       default='/Users/jose/Documents/Obsidian/Evermd',
                       help='Path to source vault (default: /Users/jose/Documents/Obsidian/Evermd)')
    parser.add_argument('--output', type=str,
                       help='Output file name (default: auto-generated with timestamp)')
    
    args = parser.parse_args()
    
    analyzer = PreprocessingAnalyzer(
        sample_size=args.sample_size,
        source_vault=args.source_vault
    )
    
    results = analyzer.run_analysis()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
