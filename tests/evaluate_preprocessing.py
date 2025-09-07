#!/usr/bin/env python3
"""
Preprocessing Pipeline Evaluator

This script compares raw notes with their preprocessed versions to evaluate
the effectiveness of the preprocessing pipeline. It provides detailed analysis
of content changes, boilerplate removal, and overall quality improvements.

Usage:
    python tests/evaluate_preprocessing.py
"""

import sys
import os
from pathlib import Path
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

import config

class PreprocessingEvaluator:
    """Evaluates the effectiveness of the preprocessing pipeline."""
    
    def __init__(self, raw_vault: str, preprocessed_vault: str):
        self.raw_vault = Path(raw_vault)
        self.preprocessed_vault = Path(preprocessed_vault)
        self.results = {
            'evaluation_date': datetime.now().isoformat(),
            'total_notes': 0,
            'processed_notes': 0,
            'failed_notes': 0,
            'detailed_results': [],
            'summary_stats': {},
            'boilerplate_analysis': {},
            'content_quality_metrics': {}
        }
    
    def find_note_pairs(self) -> List[Tuple[Path, Path]]:
        """Find matching pairs of raw and preprocessed notes."""
        pairs = []
        
        # Get all preprocessed notes
        preprocessed_notes = list(self.preprocessed_vault.rglob("*.md"))
        
        for preprocessed_note in preprocessed_notes:
            # Extract the test note name (e.g., test_note_01_OriginalName.md)
            if preprocessed_note.name.startswith("test_note_"):
                # Find corresponding raw note
                raw_note = self.raw_vault / "notes" / preprocessed_note.name
                if raw_note.exists():
                    pairs.append((raw_note, preprocessed_note))
                else:
                    print(f"⚠️  No raw note found for: {preprocessed_note.name}")
        
        return pairs
    
    def analyze_content_changes(self, raw_content: str, preprocessed_content: str) -> Dict[str, Any]:
        """Analyze changes between raw and preprocessed content."""
        analysis = {
            'raw_length': len(raw_content),
            'preprocessed_length': len(preprocessed_content),
            'length_change': len(preprocessed_content) - len(raw_content),
            'length_change_percent': 0,
            'lines_removed': 0,
            'lines_added': 0,
            'html_tags_removed': 0,
            'boilerplate_patterns_found': [],
            'content_preserved': True,
            'quality_improvements': []
        }
        
        # Calculate length change percentage
        if analysis['raw_length'] > 0:
            analysis['length_change_percent'] = (analysis['length_change'] / analysis['raw_length']) * 100
        
        # Count lines
        raw_lines = raw_content.split('\n')
        preprocessed_lines = preprocessed_content.split('\n')
        analysis['lines_removed'] = len(raw_lines) - len(preprocessed_lines)
        
        # Count HTML tags
        html_pattern = re.compile(r'<[^>]+>')
        raw_html_count = len(html_pattern.findall(raw_content))
        preprocessed_html_count = len(html_pattern.findall(preprocessed_content))
        analysis['html_tags_removed'] = raw_html_count - preprocessed_html_count
        
        # Check for boilerplate patterns - comprehensive list matching our cleaning patterns
        boilerplate_patterns = [
            # Social media and sharing
            r'Powered by Livefyre',
            r'Subscribe to.*newsletter',
            r'Follow us on.*social',
            r'Share this.*article',
            r'Share on.*(twitter|facebook|linkedin)',
            r'Follow.*us',
            r'Like.*us',
            r'Tweet.*this',
            r'Subscribe.*to',
            r'My.*subscription',
            
            # Navigation and menus
            r'Menu.*navigation',
            r'Home.*about.*contact',
            r'Navigation.*menu',
            r'Sections.*menu',
            r'Most.*read',
            r'Most.*viewed',
            r'Most.*commented',
            r'Skip.*to.*content',
            r'Jump.*to',
            
            # Related content and recommendations
            r'Related articles?',
            r'You might also like',
            r'More from.*section',
            r'Recommended.*for.*you',
            r'Read also',
            r'More from',
            r'Latest.*updates',
            r'Recommended.*content',
            
            # Comments and interaction
            r'Comments?.*section',
            r'Leave.*comment',
            r'Post.*comment',
            r'Comments.*below',
            r'Selected comments',
            r'Post your say',
            
            # Advertisement and sponsored content
            r'Advertisement',
            r'Sponsored.*content',
            r'Promoted.*content',
            r'Ad\s*$',
            
            # Legal and policy
            r'Cookie.*policy',
            r'Privacy.*policy',
            r'Terms.*of.*service',
            r'Terms.*and.*conditions',
            r'Copyright',
            r'All rights reserved',
            r'Legal.*notice',
            r'Disclaimer',
            
            # Footer and header content
            r'Footer.*content',
            r'Header.*navigation',
            r'Social.*media.*links',
            r'Powered by',
            r'Built with',
            
            # Job listings and classifieds
            r'Job.*listings',
            r'Career.*opportunities',
            r'Classified.*ads',
            r'Look for more jobs',
            
            # Travel and entertainment
            r'Travel.*entertainment',
            r'Latest.*travelog',
            r'Top.*travelog',
            r'Share.*travel',
            
            # Stock market and financial data
            r'Stock.*exchange',
            r'Top.*gainer',
            r'Top.*loser',
            r'Price.*change',
            
            # FT-specific patterns
            r'FT recommends',
            r'myFT',
            r'International Edition',
            r'Search the FT',
            r'Switch to UK Edition',
            r'Top sections',
            r'Markets data delayed',
            r'The Financial Times',
            
            # Generic web boilerplate
            r'From our networks',
            r'Partners?:',
            r'Support',
            r'Services',
            r'Legal & Privacy',
            r'Give feedback',
            r'View tips'
        ]
        
        for pattern in boilerplate_patterns:
            if re.search(pattern, raw_content, re.IGNORECASE):
                analysis['boilerplate_patterns_found'].append(pattern)
        
        # Check if key content is preserved
        # Use a more comprehensive approach to determine content preservation
        
        # Calculate content density (non-whitespace characters per line)
        raw_lines = [line.strip() for line in raw_content.split('\n') if line.strip()]
        preprocessed_lines = [line.strip() for line in preprocessed_content.split('\n') if line.strip()]
        
        if len(raw_lines) == 0:
            analysis['content_preserved'] = True
        else:
            # Calculate average content density
            raw_density = sum(len(line) for line in raw_lines) / len(raw_lines) if raw_lines else 0
            preprocessed_density = sum(len(line) for line in preprocessed_lines) / len(preprocessed_lines) if preprocessed_lines else 0
            
            # Check if we have reasonable content preservation
            # Content is preserved if:
            # 1. We have at least 50% of the original content length, OR
            # 2. We have at least 30% of the original lines with good density, OR
            # 3. The preprocessed content has good density (avg > 50 chars per line)
            
            length_ratio = analysis['preprocessed_length'] / analysis['raw_length'] if analysis['raw_length'] > 0 else 0
            line_ratio = len(preprocessed_lines) / len(raw_lines) if len(raw_lines) > 0 else 0
            
            content_preserved = (
                length_ratio >= 0.5 or  # At least 50% of content length preserved
                (line_ratio >= 0.3 and preprocessed_density >= 30) or  # At least 30% of lines with good density
                preprocessed_density >= 50  # Good content density
            )
            
            analysis['content_preserved'] = content_preserved
        
        # Identify quality improvements
        if analysis['html_tags_removed'] > 0:
            analysis['quality_improvements'].append('HTML tags cleaned')
        if analysis['lines_removed'] > 0:
            analysis['quality_improvements'].append('Boilerplate content removed')
        if len(analysis['boilerplate_patterns_found']) > 0:
            analysis['quality_improvements'].append('Boilerplate patterns detected and cleaned')
        
        # Assess content quality improvements
        analysis['content_quality_score'] = self.assess_content_quality(raw_content, preprocessed_content)
        
        # Check for specific valuable content preservation
        analysis['valuable_content_preserved'] = self.check_valuable_content_preservation(raw_content, preprocessed_content)
        
        return analysis
    
    def assess_content_quality(self, raw_content: str, preprocessed_content: str) -> float:
        """Assess the quality improvement of preprocessed content (0-100 scale)."""
        score = 50.0  # Base score
        
        # HTML cleaning bonus
        html_pattern = re.compile(r'<[^>]+>')
        raw_html_count = len(html_pattern.findall(raw_content))
        preprocessed_html_count = len(html_pattern.findall(preprocessed_content))
        if raw_html_count > 0 and preprocessed_html_count < raw_html_count:
            score += min(20, (raw_html_count - preprocessed_html_count) * 2)
        
        # Boilerplate removal bonus
        boilerplate_indicators = ['share', 'follow', 'subscribe', 'advertisement', 'cookie', 'privacy', 'terms']
        raw_boilerplate_count = sum(1 for indicator in boilerplate_indicators if indicator in raw_content.lower())
        preprocessed_boilerplate_count = sum(1 for indicator in boilerplate_indicators if indicator in preprocessed_content.lower())
        if raw_boilerplate_count > preprocessed_boilerplate_count:
            score += min(15, (raw_boilerplate_count - preprocessed_boilerplate_count) * 3)
        
        # Content density improvement
        raw_lines = [line.strip() for line in raw_content.split('\n') if line.strip()]
        preprocessed_lines = [line.strip() for line in preprocessed_content.split('\n') if line.strip()]
        
        if raw_lines and preprocessed_lines:
            raw_density = sum(len(line) for line in raw_lines) / len(raw_lines)
            preprocessed_density = sum(len(line) for line in preprocessed_lines) / len(preprocessed_lines)
            if preprocessed_density > raw_density:
                score += min(10, (preprocessed_density - raw_density) / 2)
        
        # Penalty for excessive content loss
        length_ratio = len(preprocessed_content) / len(raw_content) if len(raw_content) > 0 else 0
        if length_ratio < 0.2:  # Less than 20% content preserved
            score -= 30
        elif length_ratio < 0.5:  # Less than 50% content preserved
            score -= 15
        
        return max(0, min(100, score))
    
    def check_valuable_content_preservation(self, raw_content: str, preprocessed_content: str) -> Dict[str, bool]:
        """Check if valuable content elements are preserved."""
        valuable_indicators = {
            'headings': r'^#+\s+.+$',
            'links': r'\[([^\]]+)\]\([^)]+\)',
            'lists': r'^\s*[-*+]\s+',
            'tables': r'^\s*\|.*\|',
            'code_blocks': r'```',
            'quotes': r'^>\s+',
            'dates': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'numbers': r'\b\d+\b',
            'proper_nouns': r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        }
        
        preservation = {}
        for content_type, pattern in valuable_indicators.items():
            raw_count = len(re.findall(pattern, raw_content, re.MULTILINE))
            preprocessed_count = len(re.findall(pattern, preprocessed_content, re.MULTILINE))
            
            if raw_count == 0:
                preservation[content_type] = True  # No content to preserve
            else:
                # Consider preserved if we have at least 70% of the original
                preservation[content_type] = preprocessed_count >= (raw_count * 0.7)
        
        return preservation
    
    def evaluate_note_pair(self, raw_note: Path, preprocessed_note: Path) -> Dict[str, Any]:
        """Evaluate a single note pair."""
        try:
            # Read both files
            with open(raw_note, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            with open(preprocessed_note, 'r', encoding='utf-8') as f:
                preprocessed_content = f.read()
            
            # Analyze content changes
            content_analysis = self.analyze_content_changes(raw_content, preprocessed_content)
            
            # Parse frontmatter
            raw_meta = self.parse_frontmatter(raw_content)
            preprocessed_meta = self.parse_frontmatter(preprocessed_content)
            
            result = {
                'note_name': raw_note.name,
                'raw_path': str(raw_note),
                'preprocessed_path': str(preprocessed_note),
                'raw_metadata': raw_meta,
                'preprocessed_metadata': preprocessed_meta,
                'content_analysis': content_analysis,
                'evaluation_status': 'success',
                'issues_found': [],
                'recommendations': []
            }
            
            # Check for issues
            if not content_analysis['content_preserved']:
                result['issues_found'].append('Significant content loss detected')
                result['recommendations'].append('Review preprocessing rules for this content type')
            
            # Only flag as excessive if we lose more than 80% of content
            if content_analysis['length_change_percent'] < -80:
                result['issues_found'].append('Excessive content reduction (>80%)')
                result['recommendations'].append('Review preprocessing rules for this content type')
            
            if content_analysis['html_tags_removed'] == 0 and 'html' in raw_content.lower():
                result['issues_found'].append('HTML content not properly cleaned')
                result['recommendations'].append('Improve HTML cleaning patterns')
            
            # Check if boilerplate was properly removed
            remaining_boilerplate = []
            for pattern in content_analysis['boilerplate_patterns_found']:
                if re.search(pattern, preprocessed_content, re.IGNORECASE):
                    remaining_boilerplate.append(pattern)
            
            if remaining_boilerplate:
                result['issues_found'].append(f'Boilerplate still present: {remaining_boilerplate}')
                result['recommendations'].append('Enhance boilerplate removal patterns')
            
            # Check content quality score
            quality_score = content_analysis.get('content_quality_score', 50)
            if quality_score < 40:
                result['issues_found'].append(f'Low content quality score: {quality_score:.1f}/100')
                result['recommendations'].append('Review preprocessing effectiveness')
            
            # Check valuable content preservation
            valuable_content = content_analysis.get('valuable_content_preserved', {})
            lost_content_types = [content_type for content_type, preserved in valuable_content.items() if not preserved]
            if lost_content_types:
                result['issues_found'].append(f'Valuable content lost: {lost_content_types}')
                result['recommendations'].append('Improve content preservation patterns')
            
            return result
            
        except Exception as e:
            return {
                'note_name': raw_note.name,
                'raw_path': str(raw_note),
                'preprocessed_path': str(preprocessed_note),
                'evaluation_status': 'error',
                'error': str(e),
                'issues_found': ['File processing error'],
                'recommendations': ['Check file encoding and format']
            }
    
    def parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from content."""
        if not content.startswith('---'):
            return {}
        
        try:
            parts = content.split('---', 2)
            if len(parts) >= 3:
                import yaml
                return yaml.safe_load(parts[1]) or {}
        except Exception:
            pass
        
        return {}
    
    def calculate_summary_stats(self, detailed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics from detailed results."""
        successful_results = [r for r in detailed_results if r['evaluation_status'] == 'success']
        
        if not successful_results:
            return {}
        
        # Content length statistics
        length_changes = [r['content_analysis']['length_change_percent'] for r in successful_results]
        html_tags_removed = [r['content_analysis']['html_tags_removed'] for r in successful_results]
        
        # Boilerplate removal statistics
        total_boilerplate_patterns = sum(len(r['content_analysis']['boilerplate_patterns_found']) for r in successful_results)
        notes_with_boilerplate = len([r for r in successful_results if r['content_analysis']['boilerplate_patterns_found']])
        
        # Content preservation statistics
        content_preserved_count = len([r for r in successful_results if r['content_analysis']['content_preserved']])
        
        # Content quality statistics
        quality_scores = [r['content_analysis'].get('content_quality_score', 50) for r in successful_results]
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 50
        
        # Valuable content preservation statistics
        valuable_content_stats = {}
        if successful_results:
            valuable_content_types = ['headings', 'links', 'lists', 'tables', 'code_blocks', 'quotes', 'dates', 'numbers', 'proper_nouns']
            for content_type in valuable_content_types:
                preserved_count = len([r for r in successful_results 
                                     if r['content_analysis'].get('valuable_content_preserved', {}).get(content_type, True)])
                valuable_content_stats[content_type] = {
                    'preserved_count': preserved_count,
                    'preservation_rate': preserved_count / len(successful_results) if successful_results else 0
                }
        
        # Issue statistics
        total_issues = sum(len(r['issues_found']) for r in detailed_results)
        notes_with_issues = len([r for r in detailed_results if r['issues_found']])
        
        return {
            'total_notes_evaluated': len(detailed_results),
            'successful_evaluations': len(successful_results),
            'failed_evaluations': len(detailed_results) - len(successful_results),
            'content_length_stats': {
                'average_length_change_percent': sum(length_changes) / len(length_changes) if length_changes else 0,
                'min_length_change_percent': min(length_changes) if length_changes else 0,
                'max_length_change_percent': max(length_changes) if length_changes else 0,
                'notes_with_length_reduction': len([c for c in length_changes if c < 0]),
                'notes_with_length_increase': len([c for c in length_changes if c > 0])
            },
            'html_cleaning_stats': {
                'total_html_tags_removed': sum(html_tags_removed),
                'average_html_tags_removed': sum(html_tags_removed) / len(html_tags_removed) if html_tags_removed else 0,
                'notes_with_html_cleaning': len([h for h in html_tags_removed if h > 0])
            },
            'boilerplate_removal_stats': {
                'total_boilerplate_patterns_found': total_boilerplate_patterns,
                'notes_with_boilerplate': notes_with_boilerplate,
                'average_patterns_per_note': total_boilerplate_patterns / len(successful_results) if successful_results else 0
            },
            'content_preservation_stats': {
                'notes_with_content_preserved': content_preserved_count,
                'content_preservation_rate': content_preserved_count / len(successful_results) if successful_results else 0
            },
            'content_quality_stats': {
                'average_quality_score': avg_quality_score,
                'min_quality_score': min(quality_scores) if quality_scores else 0,
                'max_quality_score': max(quality_scores) if quality_scores else 0,
                'notes_with_high_quality': len([s for s in quality_scores if s >= 70])
            },
            'valuable_content_stats': valuable_content_stats,
            'issue_stats': {
                'total_issues_found': total_issues,
                'notes_with_issues': notes_with_issues,
                'average_issues_per_note': total_issues / len(detailed_results) if detailed_results else 0
            }
        }
    
    def generate_report(self) -> str:
        """Generate a comprehensive evaluation report."""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("PREPROCESSING PIPELINE EVALUATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Evaluation Date: {self.results['evaluation_date']}")
        report_lines.append(f"Raw Vault: {self.raw_vault}")
        report_lines.append(f"Preprocessed Vault: {self.preprocessed_vault}")
        report_lines.append("")
        
        # Summary statistics
        stats = self.results['summary_stats']
        report_lines.append("SUMMARY STATISTICS")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Notes Evaluated: {stats.get('total_notes_evaluated', 0)}")
        report_lines.append(f"Successful Evaluations: {stats.get('successful_evaluations', 0)}")
        report_lines.append(f"Failed Evaluations: {stats.get('failed_evaluations', 0)}")
        report_lines.append("")
        
        # Content length analysis
        length_stats = stats.get('content_length_stats', {})
        report_lines.append("CONTENT LENGTH ANALYSIS")
        report_lines.append("-" * 40)
        report_lines.append(f"Average Length Change: {length_stats.get('average_length_change_percent', 0):.1f}%")
        report_lines.append(f"Notes with Length Reduction: {length_stats.get('notes_with_length_reduction', 0)}")
        report_lines.append(f"Notes with Length Increase: {length_stats.get('notes_with_length_increase', 0)}")
        report_lines.append("")
        
        # HTML cleaning analysis
        html_stats = stats.get('html_cleaning_stats', {})
        report_lines.append("HTML CLEANING ANALYSIS")
        report_lines.append("-" * 40)
        report_lines.append(f"Total HTML Tags Removed: {html_stats.get('total_html_tags_removed', 0)}")
        report_lines.append(f"Average HTML Tags Removed per Note: {html_stats.get('average_html_tags_removed', 0):.1f}")
        report_lines.append(f"Notes with HTML Cleaning: {html_stats.get('notes_with_html_cleaning', 0)}")
        report_lines.append("")
        
        # Boilerplate removal analysis
        boilerplate_stats = stats.get('boilerplate_removal_stats', {})
        report_lines.append("BOILERPLATE REMOVAL ANALYSIS")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Boilerplate Patterns Found: {boilerplate_stats.get('total_boilerplate_patterns_found', 0)}")
        report_lines.append(f"Notes with Boilerplate: {boilerplate_stats.get('notes_with_boilerplate', 0)}")
        report_lines.append(f"Average Patterns per Note: {boilerplate_stats.get('average_patterns_per_note', 0):.1f}")
        report_lines.append("")
        
        # Content preservation analysis
        preservation_stats = stats.get('content_preservation_stats', {})
        report_lines.append("CONTENT PRESERVATION ANALYSIS")
        report_lines.append("-" * 40)
        report_lines.append(f"Content Preservation Rate: {preservation_stats.get('content_preservation_rate', 0):.1%}")
        report_lines.append(f"Notes with Content Preserved: {preservation_stats.get('notes_with_content_preserved', 0)}")
        report_lines.append("")
        
        # Content quality analysis
        quality_stats = stats.get('content_quality_stats', {})
        report_lines.append("CONTENT QUALITY ANALYSIS")
        report_lines.append("-" * 40)
        report_lines.append(f"Average Quality Score: {quality_stats.get('average_quality_score', 0):.1f}/100")
        report_lines.append(f"Quality Score Range: {quality_stats.get('min_quality_score', 0):.1f} - {quality_stats.get('max_quality_score', 0):.1f}")
        report_lines.append(f"High Quality Notes (≥70): {quality_stats.get('notes_with_high_quality', 0)}")
        report_lines.append("")
        
        # Valuable content preservation analysis
        valuable_stats = stats.get('valuable_content_stats', {})
        if valuable_stats:
            report_lines.append("VALUABLE CONTENT PRESERVATION")
            report_lines.append("-" * 40)
            for content_type, stats_data in valuable_stats.items():
                preservation_rate = stats_data.get('preservation_rate', 0)
                preserved_count = stats_data.get('preserved_count', 0)
                report_lines.append(f"{content_type.title()}: {preservation_rate:.1%} ({preserved_count} notes)")
            report_lines.append("")
        
        # Issue analysis
        issue_stats = stats.get('issue_stats', {})
        report_lines.append("ISSUE ANALYSIS")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Issues Found: {issue_stats.get('total_issues_found', 0)}")
        report_lines.append(f"Notes with Issues: {issue_stats.get('notes_with_issues', 0)}")
        report_lines.append(f"Average Issues per Note: {issue_stats.get('average_issues_per_note', 0):.1f}")
        report_lines.append("")
        
        # Detailed results for notes with issues
        notes_with_issues = [r for r in self.results['detailed_results'] if r['issues_found']]
        if notes_with_issues:
            report_lines.append("NOTES WITH ISSUES")
            report_lines.append("-" * 40)
            for result in notes_with_issues[:10]:  # Show first 10
                report_lines.append(f"• {result['note_name']}")
                for issue in result['issues_found']:
                    report_lines.append(f"  - {issue}")
                for rec in result['recommendations']:
                    report_lines.append(f"  → {rec}")
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    def run_evaluation(self) -> Dict[str, Any]:
        """Run the complete evaluation process."""
        print("🔍 Starting preprocessing pipeline evaluation...")
        print(f"Raw vault: {self.raw_vault}")
        print(f"Preprocessed vault: {self.preprocessed_vault}")
        print()
        
        # Find note pairs
        print("📋 Finding note pairs...")
        note_pairs = self.find_note_pairs()
        print(f"Found {len(note_pairs)} note pairs to evaluate")
        print()
        
        if not note_pairs:
            print("❌ No note pairs found. Check vault paths and note naming.")
            return self.results
        
        # Evaluate each pair
        print("🔬 Evaluating note pairs...")
        detailed_results = []
        
        for i, (raw_note, preprocessed_note) in enumerate(note_pairs, 1):
            print(f"  [{i:2d}/{len(note_pairs)}] Evaluating: {raw_note.name}")
            result = self.evaluate_note_pair(raw_note, preprocessed_note)
            detailed_results.append(result)
            
            # Show quick status
            if result['evaluation_status'] == 'success':
                length_change = result['content_analysis']['length_change_percent']
                issues = len(result['issues_found'])
                status = "✅" if issues == 0 else f"⚠️  ({issues} issues)"
                print(f"      {status} Length change: {length_change:+.1f}%")
            else:
                print(f"      ❌ Error: {result.get('error', 'Unknown error')}")
        
        # Store results
        self.results['total_notes'] = len(note_pairs)
        self.results['processed_notes'] = len([r for r in detailed_results if r['evaluation_status'] == 'success'])
        self.results['failed_notes'] = len([r for r in detailed_results if r['evaluation_status'] == 'error'])
        self.results['detailed_results'] = detailed_results
        self.results['summary_stats'] = self.calculate_summary_stats(detailed_results)
        
        print()
        print("📊 Evaluation complete!")
        print(f"  Total notes: {self.results['total_notes']}")
        print(f"  Successfully evaluated: {self.results['processed_notes']}")
        print(f"  Failed evaluations: {self.results['failed_notes']}")
        
        return self.results

def main():
    """Main evaluation function."""
    # Get test configuration
    test_cfg = config.get_test_config()
    
    raw_vault = test_cfg['paths']['test_raw_vault']
    preprocessed_vault = test_cfg['paths']['test_preprocessed_vault']
    
    # Create evaluator
    evaluator = PreprocessingEvaluator(raw_vault, preprocessed_vault)
    
    # Run evaluation
    results = evaluator.run_evaluation()
    
    # Generate and display report
    report = evaluator.generate_report()
    print("\n" + report)
    
    # Save detailed results
    output_file = f"tests/evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    main()
