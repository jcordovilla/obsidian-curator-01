"""
Module for analyzing and characterizing note content types.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from collections import Counter
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import (
    ANALYSIS_CATEGORIES, BOILERPLATE_PATTERNS, ATTACHMENT_PATTERN, 
    URL_PATTERN, EMAIL_PATTERN, OUTPUT_DIR
)


class ContentAnalyzer:
    """Analyzes note content to identify types and characteristics."""
    
    def __init__(self):
        self.boilerplate_patterns = [re.compile(pattern, re.IGNORECASE) 
                                   for pattern in BOILERPLATE_PATTERNS]
        self.attachment_pattern = re.compile(ATTACHMENT_PATTERN)
        self.url_pattern = re.compile(URL_PATTERN)
        self.email_pattern = re.compile(EMAIL_PATTERN)
    
    def analyze_note(self, note_info: Dict) -> Dict:
        """Comprehensive analysis of a single note."""
        if 'error' in note_info:
            return {'error': note_info['error'], 'category': 'unknown'}
        
        body = note_info.get('body', '')
        frontmatter = note_info.get('frontmatter', {})
        
        analysis = {
            'basic_stats': self._get_basic_stats(body),
            'content_indicators': self._analyze_content_indicators(body, frontmatter),
            'boilerplate_score': self._calculate_boilerplate_score(body),
            'structure_analysis': self._analyze_structure(body),
            'metadata_analysis': self._analyze_metadata(frontmatter),
            'category': self._classify_note_type(body, frontmatter),
            'quality_indicators': self._assess_quality(body, frontmatter)
        }
        
        return analysis
    
    def _get_basic_stats(self, body: str) -> Dict:
        """Get basic statistics about the note content."""
        lines = body.split('\n')
        words = body.split()
        
        return {
            'char_count': len(body),
            'word_count': len(words),
            'line_count': len(lines),
            'paragraph_count': len([p for p in body.split('\n\n') if p.strip()]),
            'avg_words_per_line': len(words) / max(len(lines), 1),
            'empty_lines': sum(1 for line in lines if not line.strip())
        }
    
    def _analyze_content_indicators(self, body: str, frontmatter: Dict) -> Dict:
        """Analyze various content indicators."""
        return {
            'has_source_url': bool(frontmatter.get('source')),
            'has_attachments': bool(self.attachment_pattern.search(body)),
            'attachment_count': len(self.attachment_pattern.findall(body)),
            'has_urls': bool(self.url_pattern.search(body)),
            'url_count': len(self.url_pattern.findall(body)),
            'has_emails': bool(self.email_pattern.search(body)),
            'email_count': len(self.email_pattern.findall(body)),
            'has_headers': bool(re.search(r'^#+\s', body, re.MULTILINE)),
            'header_count': len(re.findall(r'^#+\s', body, re.MULTILINE)),
            'has_lists': bool(re.search(r'^[\s]*[-\*\+]\s', body, re.MULTILINE)),
            'has_numbered_lists': bool(re.search(r'^[\s]*\d+\.\s', body, re.MULTILINE)),
            'has_tables': '|' in body and body.count('|') > 2,
            'has_code_blocks': '```' in body or '`' in body,
            'has_quotes': bool(re.search(r'^>', body, re.MULTILINE)),
            'has_bold_text': '**' in body or '__' in body,
            'has_italic_text': '*' in body and '**' not in body,
            'has_links': '[' in body and '](' in body
        }
    
    def _calculate_boilerplate_score(self, body: str) -> Dict:
        """Calculate how much boilerplate content is present."""
        matches = []
        total_matches = 0
        
        for pattern in self.boilerplate_patterns:
            pattern_matches = pattern.findall(body)
            if pattern_matches:
                matches.extend(pattern_matches)
                total_matches += len(pattern_matches)
        
        # Additional boilerplate indicators
        boilerplate_indicators = [
            'click here', 'read more', 'continue reading', 'subscribe',
            'newsletter', 'advertisement', 'sponsored', 'cookie', 'privacy',
            'terms of', 'follow us', 'share on', 'like us', 'tweet',
            'facebook', 'twitter', 'linkedin', 'instagram'
        ]
        
        indicator_matches = sum(1 for indicator in boilerplate_indicators 
                              if indicator.lower() in body.lower())
        
        word_count = len(body.split())
        boilerplate_ratio = (total_matches + indicator_matches) / max(word_count, 1)
        
        return {
            'boilerplate_matches': total_matches,
            'boilerplate_indicators': indicator_matches,
            'boilerplate_ratio': boilerplate_ratio,
            'high_boilerplate': boilerplate_ratio > 0.02,  # More than 2% boilerplate
            'matched_patterns': matches[:10]  # First 10 matches for inspection
        }
    
    def _analyze_structure(self, body: str) -> Dict:
        """Analyze the structural characteristics of the content."""
        lines = body.split('\n')
        
        # Analyze line lengths
        line_lengths = [len(line) for line in lines if line.strip()]
        avg_line_length = sum(line_lengths) / max(len(line_lengths), 1)
        
        # Check for structured patterns
        has_consistent_formatting = False
        if line_lengths:
            std_dev = (sum((x - avg_line_length) ** 2 for x in line_lengths) / len(line_lengths)) ** 0.5
            has_consistent_formatting = std_dev < avg_line_length * 0.5
        
        return {
            'avg_line_length': avg_line_length,
            'max_line_length': max(line_lengths) if line_lengths else 0,
            'has_consistent_formatting': has_consistent_formatting,
            'starts_with_title': body.strip().startswith('#'),
            'has_horizontal_rules': '---' in body or '***' in body,
            'indented_content': bool(re.search(r'^\s{4,}', body, re.MULTILINE)),
            'has_timestamps': bool(re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', body)),
            'has_bullet_points': bool(re.search(r'^[\s]*[-\*\+]\s', body, re.MULTILINE))
        }
    
    def _analyze_metadata(self, frontmatter: Dict) -> Dict:
        """Analyze the frontmatter metadata."""
        return {
            'has_tags': bool(frontmatter.get('tags')),
            'tag_count': len(frontmatter.get('tags', [])),
            'has_source': bool(frontmatter.get('source')),
            'has_title': bool(frontmatter.get('title')),
            'has_dates': bool(frontmatter.get('date created') or frontmatter.get('date modified')),
            'has_language': bool(frontmatter.get('language')),
            'language': frontmatter.get('language', 'unknown'),
            'metadata_fields': list(frontmatter.keys()),
            'metadata_count': len(frontmatter)
        }
    
    def _classify_note_type(self, body: str, frontmatter: Dict) -> str:
        """Classify the note into one of the predefined categories."""
        
        # Web clipping indicators
        if (frontmatter.get('source') and 
            ('http' in str(frontmatter.get('source', '')) or 
             any(pattern.search(body) for pattern in self.boilerplate_patterns))):
            return 'web_clipping'
        
        # PDF annotation indicators
        if ('![[attachments/' in body and '.pdf' in body.lower()):
            return 'pdf_annotation'
        
        # Business card indicators
        if (any(indicator in body.lower() for indicator in 
                ['tarjeta de visita', 'business card', '@', 'tel:', 'phone:']) or
            self.email_pattern.search(body)):
            return 'business_card'
        
        # News article indicators
        if (frontmatter.get('tags') and 
            any(tag in ['NEWS', 'news'] for tag in frontmatter.get('tags', []))):
            return 'news_article'
        
        # Technical document indicators
        if (any(indicator in body.lower() for indicator in 
                ['technical', 'specification', 'documentation', 'manual', 'guide']) or
            body.count('```') > 2):  # Multiple code blocks
            return 'technical_document'
        
        # Personal note indicators (short, no source, simple structure)
        if (not frontmatter.get('source') and 
            len(body.split()) < 200 and 
            not self.attachment_pattern.search(body)):
            return 'personal_note'
        
        return 'unknown'
    
    def _assess_quality(self, body: str, frontmatter: Dict) -> Dict:
        """Assess the quality and usefulness of the content."""
        word_count = len(body.split())
        
        # Quality indicators
        has_structure = bool(re.search(r'^#+\s', body, re.MULTILINE))
        has_content = word_count > 50
        not_mostly_boilerplate = self._calculate_boilerplate_score(body)['boilerplate_ratio'] < 0.1
        has_meaningful_title = bool(frontmatter.get('title') and 
                                  len(frontmatter.get('title', '')) > 5)
        
        quality_score = sum([
            has_structure, has_content, not_mostly_boilerplate, has_meaningful_title
        ]) / 4.0
        
        return {
            'quality_score': quality_score,
            'has_structure': has_structure,
            'sufficient_content': has_content,
            'low_boilerplate': not_mostly_boilerplate,
            'meaningful_title': has_meaningful_title,
            'estimated_usefulness': 'high' if quality_score > 0.75 else 
                                  'medium' if quality_score > 0.5 else 'low'
        }
    
    def analyze_dataset(self, dataset: List[Dict]) -> Dict:
        """Analyze the entire sample dataset."""
        print(f"Analyzing {len(dataset)} notes...")
        
        analyses = []
        category_counts = Counter()
        language_counts = Counter()
        quality_distribution = Counter()
        
        for i, note_info in enumerate(dataset, 1):
            if i % 10 == 0:
                print(f"  Analyzed {i}/{len(dataset)} notes")
            
            analysis = self.analyze_note(note_info)
            analysis['note_info'] = {
                'path': note_info.get('path'),
                'filename': note_info.get('filename'),
                'folder': note_info.get('folder')
            }
            analyses.append(analysis)
            
            category_counts[analysis['category']] += 1
            language_counts[note_info.get('language', 'unknown')] += 1
            quality_distribution[analysis.get('quality_indicators', {}).get('estimated_usefulness', 'unknown')] += 1
        
        # Generate summary statistics
        summary = {
            'total_notes': len(dataset),
            'categories': dict(category_counts),
            'languages': dict(language_counts),
            'quality_distribution': dict(quality_distribution),
            'avg_word_count': sum(a.get('basic_stats', {}).get('word_count', 0) 
                                for a in analyses) / len(analyses),
            'high_boilerplate_count': sum(1 for a in analyses 
                                        if a.get('boilerplate_score', {}).get('high_boilerplate', False)),
            'notes_with_attachments': sum(1 for a in analyses 
                                        if a.get('content_indicators', {}).get('has_attachments', False)),
            'notes_with_urls': sum(1 for a in analyses 
                                 if a.get('content_indicators', {}).get('has_urls', False))
        }
        
        return {
            'summary': summary,
            'detailed_analyses': analyses
        }
    
    def save_analysis(self, analysis_results: Dict, filename: str = "content_analysis.json") -> str:
        """Save analysis results to a file."""
        output_path = Path(OUTPUT_DIR) / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"Analysis results saved to: {output_path}")
        return str(output_path)
    
    def generate_report(self, analysis_results: Dict) -> str:
        """Generate a human-readable analysis report."""
        summary = analysis_results['summary']
        
        report = f"""
# Obsidian Vault Content Analysis Report

## Summary Statistics
- **Total Notes Analyzed**: {summary['total_notes']}
- **Average Word Count**: {summary['avg_word_count']:.1f}
- **Notes with High Boilerplate**: {summary['high_boilerplate_count']} ({summary['high_boilerplate_count']/summary['total_notes']*100:.1f}%)
- **Notes with Attachments**: {summary['notes_with_attachments']} ({summary['notes_with_attachments']/summary['total_notes']*100:.1f}%)
- **Notes with URLs**: {summary['notes_with_urls']} ({summary['notes_with_urls']/summary['total_notes']*100:.1f}%)

## Content Categories
"""
        for category, count in sorted(summary['categories'].items(), key=lambda x: x[1], reverse=True):
            percentage = count / summary['total_notes'] * 100
            report += f"- **{category.replace('_', ' ').title()}**: {count} notes ({percentage:.1f}%)\n"
        
        report += f"""
## Languages
"""
        for language, count in sorted(summary['languages'].items(), key=lambda x: x[1], reverse=True):
            percentage = count / summary['total_notes'] * 100
            report += f"- **{language}**: {count} notes ({percentage:.1f}%)\n"
        
        report += f"""
## Quality Distribution
"""
        for quality, count in sorted(summary['quality_distribution'].items(), key=lambda x: x[1], reverse=True):
            percentage = count / summary['total_notes'] * 100
            report += f"- **{quality.title()} Quality**: {count} notes ({percentage:.1f}%)\n"
        
        return report


if __name__ == "__main__":
    import yaml
    
    # Load sample dataset
    dataset_path = Path(OUTPUT_DIR) / "sample_dataset.yaml"
    if not dataset_path.exists():
        print("Sample dataset not found. Run note_sampler.py first.")
        exit(1)
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = yaml.safe_load(f)
    
    # Analyze the dataset
    analyzer = ContentAnalyzer()
    results = analyzer.analyze_dataset(dataset)
    
    # Save results
    analyzer.save_analysis(results)
    
    # Generate and display report
    report = analyzer.generate_report(results)
    print(report)
    
    # Save report
    report_path = Path(OUTPUT_DIR) / "analysis_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nDetailed analysis saved to: {Path(OUTPUT_DIR) / 'content_analysis.json'}")
    print(f"Report saved to: {report_path}")
