"""
Quality validation module for processed notes.
"""

import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class QualityValidator:
    """Validates the quality of processed notes and identifies issues."""
    
    def __init__(self):
        self.validation_rules = self._build_validation_rules()
        self.quality_metrics = [
            'metadata_completeness',
            'content_structure',
            'formatting_consistency',
            'link_integrity',
            'attachment_validity',
            'encoding_quality'
        ]
    
    def _build_validation_rules(self) -> Dict:
        """Build validation rules based on technical specifications."""
        return {
            'metadata': {
                'required_fields': ['title', 'date created', 'date modified', 'language'],
                'date_format': r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
                'language_codes': ['en', 'es', 'ca', 'id', 'fr', 'de', 'it', 'pt'],
                'max_title_length': 200
            },
            'content': {
                'min_content_length': 10,
                'max_line_length': 1000,
                'max_consecutive_empty_lines': 3,
                'required_encoding': 'utf-8'
            },
            'structure': {
                'header_pattern': r'^#{1,6}\s+.+$',
                'list_pattern': r'^\s*[-*+]\s+.+$',
                'numbered_list_pattern': r'^\s*\d+\.\s+.+$',
                'link_pattern': r'\[([^\]]+)\]\(([^)]+)\)',
                'attachment_pattern': r'!\[\[attachments/([^\]]+)\]\]'
            },
            'quality_thresholds': {
                'excellent': 0.9,
                'good': 0.7,
                'acceptable': 0.5,
                'poor': 0.3
            }
        }
    
    def validate_note(self, content: str, frontmatter: Dict, filename: str = '') -> Dict:
        """
        Comprehensive validation of a processed note.
        
        Returns:
            Dict with validation results, quality score, and recommendations
        """
        validation_result = {
            'filename': filename,
            'overall_quality': 'unknown',
            'quality_score': 0.0,
            'validations': {},
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'processing_success': True
        }
        
        # Run individual validations
        validation_result['validations']['metadata'] = self._validate_metadata(frontmatter)
        validation_result['validations']['content'] = self._validate_content(content)
        validation_result['validations']['structure'] = self._validate_structure(content)
        validation_result['validations']['formatting'] = self._validate_formatting(content)
        validation_result['validations']['links'] = self._validate_links(content)
        validation_result['validations']['attachments'] = self._validate_attachments(content)
        
        # Calculate overall quality score
        validation_result['quality_score'] = self._calculate_quality_score(validation_result['validations'])
        validation_result['overall_quality'] = self._determine_quality_level(validation_result['quality_score'])
        
        # Collect issues and recommendations
        self._collect_issues_and_recommendations(validation_result)
        
        return validation_result
    
    def _validate_metadata(self, frontmatter: Dict) -> Dict:
        """Validate metadata completeness and format."""
        validation = {
            'valid': True,
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        rules = self.validation_rules['metadata']
        
        # Check required fields
        missing_fields = []
        for field in rules['required_fields']:
            if field not in frontmatter or not frontmatter[field]:
                missing_fields.append(field)
                validation['valid'] = False
        
        if missing_fields:
            validation['issues'].append(f"Missing required fields: {', '.join(missing_fields)}")
            validation['score'] *= (len(rules['required_fields']) - len(missing_fields)) / len(rules['required_fields'])
        
        # Validate date formats
        for date_field in ['date created', 'date modified']:
            if date_field in frontmatter:
                date_value = str(frontmatter[date_field])
                if not re.match(rules['date_format'], date_value):
                    validation['issues'].append(f"Invalid date format in '{date_field}': {date_value}")
                    validation['score'] *= 0.9
        
        # Validate language code
        if 'language' in frontmatter:
            lang = frontmatter['language']
            if lang not in rules['language_codes']:
                validation['issues'].append(f"Unrecognized language code: {lang}")
                validation['score'] *= 0.95
        
        # Validate title length
        if 'title' in frontmatter:
            title = frontmatter['title']
            if len(title) > rules['max_title_length']:
                validation['issues'].append(f"Title too long ({len(title)} chars, max {rules['max_title_length']})")
                validation['score'] *= 0.9
        
        validation['details'] = {
            'field_count': len(frontmatter),
            'required_field_completion': (len(rules['required_fields']) - len(missing_fields)) / len(rules['required_fields']),
            'has_optional_fields': bool(frontmatter.get('tags') or frontmatter.get('source'))
        }
        
        return validation
    
    def _validate_content(self, content: str) -> Dict:
        """Validate content quality and basic requirements."""
        validation = {
            'valid': True,
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        rules = self.validation_rules['content']
        
        # Check minimum content length
        content_clean = content.strip()
        if len(content_clean) < rules['min_content_length']:
            validation['issues'].append(f"Content too short ({len(content_clean)} chars, min {rules['min_content_length']})")
            validation['valid'] = False
            validation['score'] *= 0.5
        
        # Check for encoding issues
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            validation['issues'].append("Content contains encoding issues")
            validation['score'] *= 0.8
        
        # Check line lengths
        long_lines = [i for i, line in enumerate(content.split('\n'), 1) 
                     if len(line) > rules['max_line_length']]
        if long_lines:
            validation['issues'].append(f"Lines too long: {long_lines[:5]} (showing first 5)")
            validation['score'] *= 0.9
        
        # Check for excessive empty lines
        empty_line_groups = re.findall(r'\n\s*\n(\s*\n)+', content)
        if any(group.count('\n') > rules['max_consecutive_empty_lines'] for group in empty_line_groups):
            validation['issues'].append("Excessive consecutive empty lines found")
            validation['score'] *= 0.95
        
        validation['details'] = {
            'character_count': len(content),
            'word_count': len(content.split()),
            'line_count': len(content.split('\n')),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'empty_line_ratio': content.count('\n\n') / max(content.count('\n'), 1)
        }
        
        return validation
    
    def _validate_structure(self, content: str) -> Dict:
        """Validate content structure and organization."""
        validation = {
            'valid': True,
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        rules = self.validation_rules['structure']
        
        # Analyze structural elements
        headers = re.findall(rules['header_pattern'], content, re.MULTILINE)
        lists = re.findall(rules['list_pattern'], content, re.MULTILINE)
        numbered_lists = re.findall(rules['numbered_list_pattern'], content, re.MULTILINE)
        
        # Check header hierarchy
        header_levels = []
        for header in headers:
            level = len(re.match(r'^#+', header).group(0))
            header_levels.append(level)
        
        # Validate header progression (no skipping levels)
        if header_levels:
            for i in range(1, len(header_levels)):
                if header_levels[i] > header_levels[i-1] + 1:
                    validation['issues'].append(f"Header level skipped: h{header_levels[i-1]} to h{header_levels[i]}")
                    validation['score'] *= 0.95
        
        validation['details'] = {
            'header_count': len(headers),
            'list_count': len(lists),
            'numbered_list_count': len(numbered_lists),
            'has_structure': len(headers) > 0 or len(lists) > 0,
            'header_levels': list(set(header_levels)) if header_levels else []
        }
        
        # Bonus for good structure
        if validation['details']['has_structure']:
            validation['score'] *= 1.1
        
        return validation
    
    def _validate_formatting(self, content: str) -> Dict:
        """Validate formatting consistency."""
        validation = {
            'valid': True,
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        # Check for consistent list formatting
        bullet_styles = set(re.findall(r'^(\s*[-*+])\s', content, re.MULTILINE))
        if len(bullet_styles) > 1:
            validation['issues'].append("Inconsistent bullet list formatting")
            validation['score'] *= 0.9
        
        # Check for consistent emphasis formatting
        bold_styles = []
        if '**' in content:
            bold_styles.append('**')
        if '__' in content:
            bold_styles.append('__')
        
        if len(bold_styles) > 1:
            validation['issues'].append("Mixed bold formatting styles")
            validation['score'] *= 0.95
        
        # Check for proper spacing around headers
        improper_header_spacing = re.findall(r'[^\n]^#+\s', content, re.MULTILINE)
        if improper_header_spacing:
            validation['issues'].append("Headers not properly spaced")
            validation['score'] *= 0.9
        
        validation['details'] = {
            'bullet_styles': list(bullet_styles),
            'bold_styles': bold_styles,
            'consistent_formatting': len(validation['issues']) == 0
        }
        
        return validation
    
    def _validate_links(self, content: str) -> Dict:
        """Validate link integrity and format."""
        validation = {
            'valid': True,
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        rules = self.validation_rules['structure']
        links = re.findall(rules['link_pattern'], content)
        
        broken_links = []
        for text, url in links:
            # Basic URL validation
            if not url.strip():
                broken_links.append(f"Empty URL for link '{text}'")
            elif not (url.startswith('http') or url.startswith('/') or url.startswith('#')):
                broken_links.append(f"Invalid URL format: {url}")
        
        if broken_links:
            validation['issues'].extend(broken_links[:5])  # Limit to first 5
            validation['score'] *= max(0.5, 1 - len(broken_links) / len(links)) if links else 1
        
        validation['details'] = {
            'total_links': len(links),
            'broken_links': len(broken_links),
            'link_ratio': len(links) / max(len(content.split()), 1) if content else 0
        }
        
        return validation
    
    def _validate_attachments(self, content: str) -> Dict:
        """Validate attachment references."""
        validation = {
            'valid': True,
            'score': 1.0,
            'issues': [],
            'details': {}
        }
        
        rules = self.validation_rules['structure']
        attachments = re.findall(rules['attachment_pattern'], content)
        
        # Check attachment path format
        invalid_attachments = []
        for attachment in attachments:
            if not attachment.strip():
                invalid_attachments.append("Empty attachment reference")
            elif '..' in attachment or attachment.startswith('/'):
                invalid_attachments.append(f"Potentially unsafe attachment path: {attachment}")
        
        if invalid_attachments:
            validation['issues'].extend(invalid_attachments)
            validation['score'] *= 0.8
        
        validation['details'] = {
            'total_attachments': len(attachments),
            'invalid_attachments': len(invalid_attachments),
            'attachment_types': list(set(att.split('.')[-1].lower() for att in attachments if '.' in att))
        }
        
        return validation
    
    def _calculate_quality_score(self, validations: Dict) -> float:
        """Calculate overall quality score from individual validations."""
        weights = {
            'metadata': 0.25,
            'content': 0.30,
            'structure': 0.20,
            'formatting': 0.10,
            'links': 0.10,
            'attachments': 0.05
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for category, validation in validations.items():
            if category in weights:
                weight = weights[category]
                score = validation.get('score', 0.0)
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_quality_level(self, score: float) -> str:
        """Determine quality level based on score."""
        thresholds = self.validation_rules['quality_thresholds']
        
        if score >= thresholds['excellent']:
            return 'excellent'
        elif score >= thresholds['good']:
            return 'good'
        elif score >= thresholds['acceptable']:
            return 'acceptable'
        elif score >= thresholds['poor']:
            return 'poor'
        else:
            return 'failed'
    
    def _collect_issues_and_recommendations(self, validation_result: Dict):
        """Collect issues and generate recommendations."""
        all_issues = []
        recommendations = []
        
        # Collect all issues
        for category, validation in validation_result['validations'].items():
            for issue in validation.get('issues', []):
                all_issues.append(f"{category.title()}: {issue}")
        
        validation_result['issues'] = all_issues
        
        # Generate recommendations based on quality level
        quality = validation_result['overall_quality']
        
        if quality in ['failed', 'poor']:
            recommendations.extend([
                'Consider manual review',
                'Check for processing errors',
                'Validate source content quality'
            ])
        elif quality == 'acceptable':
            recommendations.extend([
                'Minor cleanup recommended',
                'Review formatting consistency'
            ])
        elif quality in ['good', 'excellent']:
            recommendations.append('Content meets quality standards')
        
        # Specific recommendations based on issues
        if any('metadata' in issue.lower() for issue in all_issues):
            recommendations.append('Review and complete metadata fields')
        
        if any('format' in issue.lower() for issue in all_issues):
            recommendations.append('Standardize formatting consistency')
        
        if any('link' in issue.lower() for issue in all_issues):
            recommendations.append('Validate and fix broken links')
        
        validation_result['recommendations'] = recommendations
    
    def batch_validate(self, processed_notes: List[Tuple[str, Dict, str]]) -> Dict:
        """
        Validate multiple processed notes and return batch statistics.
        
        Args:
            processed_notes: List of (content, frontmatter, filename) tuples
            
        Returns:
            Dict with validation results and quality statistics
        """
        results = {
            'validations': [],
            'quality_distribution': {
                'excellent': 0,
                'good': 0,
                'acceptable': 0,
                'poor': 0,
                'failed': 0
            },
            'common_issues': {},
            'overall_success_rate': 0.0,
            'recommendations': []
        }
        
        successful_validations = 0
        
        for content, frontmatter, filename in processed_notes:
            validation = self.validate_note(content, frontmatter, filename)
            results['validations'].append(validation)
            
            # Update statistics
            quality = validation['overall_quality']
            results['quality_distribution'][quality] += 1
            
            if validation['processing_success']:
                successful_validations += 1
            
            # Collect common issues
            for issue in validation['issues']:
                issue_type = issue.split(':')[0] if ':' in issue else 'Other'
                results['common_issues'][issue_type] = results['common_issues'].get(issue_type, 0) + 1
        
        # Calculate overall success rate
        total_notes = len(processed_notes)
        results['overall_success_rate'] = successful_validations / total_notes if total_notes > 0 else 0.0
        
        # Generate batch recommendations
        if results['overall_success_rate'] < 0.8:
            results['recommendations'].append('Review processing pipeline - low success rate')
        
        if results['quality_distribution']['failed'] > total_notes * 0.1:
            results['recommendations'].append('High failure rate - check source content quality')
        
        return results
