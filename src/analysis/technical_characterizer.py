"""
Technical Characterization Module for Obsidian Vault Analysis.

This module provides comprehensive technical analysis of note content patterns,
boilerplate identification, and metadata structures to inform batch processing
application development.
"""

import re
import json
import yaml
from typing import Dict, List, Tuple, Set, Optional
from pathlib import Path
from collections import Counter, defaultdict
from .content_analyzer import ContentAnalyzer
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import (
    BOILERPLATE_PATTERNS, WEB_BOILERPLATE_INDICATORS, EVERNOTE_METADATA_FIELDS,
    OUTPUT_DIR, ATTACHMENT_PATTERN, URL_PATTERN, EMAIL_PATTERN
)


class TechnicalCharacterizer(ContentAnalyzer):
    """
    Advanced technical characterization of vault content for batch processing design.
    """
    
    def __init__(self):
        super().__init__()
        self.web_indicators = WEB_BOILERPLATE_INDICATORS
        self.metadata_patterns = {}
        self.content_patterns = {}
        self.boilerplate_catalog = defaultdict(list)
        
    def comprehensive_analysis(self, dataset: List[Dict]) -> Dict:
        """
        Perform comprehensive technical analysis for batch processing specification.
        """
        print(f"Performing comprehensive technical analysis of {len(dataset)} notes...")
        
        # Initialize analysis containers
        analysis_results = {
            'metadata_analysis': self._analyze_metadata_patterns(dataset),
            'content_structure_analysis': self._analyze_content_structures(dataset),
            'boilerplate_catalog': self._catalog_boilerplate_patterns(dataset),
            'attachment_analysis': self._analyze_attachment_patterns(dataset),
            'url_analysis': self._analyze_url_patterns(dataset),
            'formatting_analysis': self._analyze_formatting_patterns(dataset),
            'language_analysis': self._analyze_language_patterns(dataset),
            'content_preservation_specs': self._define_content_preservation_specs(dataset),
            'processing_recommendations': self._generate_processing_recommendations(dataset),
            'batch_processing_specs': self._create_batch_processing_specs(dataset)
        }
        
        return analysis_results
    
    def _analyze_metadata_patterns(self, dataset: List[Dict]) -> Dict:
        """Analyze metadata structure and patterns across all notes."""
        print("  Analyzing metadata patterns...")
        
        metadata_stats = {
            'field_frequency': Counter(),
            'field_formats': defaultdict(set),
            'required_fields': [],
            'optional_fields': [],
            'evernote_fields': Counter(),
            'custom_fields': Counter(),
            'tag_patterns': Counter(),
            'date_formats': set(),
            'source_patterns': Counter(),
            'language_distribution': Counter()
        }
        
        for note_info in dataset:
            if 'error' in note_info:
                continue
                
            frontmatter = note_info.get('frontmatter', {})
            
            # Field frequency analysis
            for field, value in frontmatter.items():
                metadata_stats['field_frequency'][field] += 1
                
                # Analyze field formats
                if isinstance(value, str):
                    metadata_stats['field_formats'][field].add('string')
                elif isinstance(value, list):
                    metadata_stats['field_formats'][field].add('list')
                elif isinstance(value, dict):
                    metadata_stats['field_formats'][field].add('dict')
                else:
                    metadata_stats['field_formats'][field].add(type(value).__name__)
                
                # Categorize fields
                if field in EVERNOTE_METADATA_FIELDS:
                    metadata_stats['evernote_fields'][field] += 1
                else:
                    metadata_stats['custom_fields'][field] += 1
            
            # Tag analysis
            tags = frontmatter.get('tags', [])
            if isinstance(tags, list):
                for tag in tags:
                    metadata_stats['tag_patterns'][str(tag)] += 1
            
            # Date format analysis
            for date_field in ['date created', 'date modified']:
                if date_field in frontmatter:
                    date_str = str(frontmatter[date_field])
                    # Extract date format pattern
                    if re.match(r'\w+, \w+ \d+\w+ \d{4}, \d+:\d+:\d+ \w+', date_str):
                        metadata_stats['date_formats'].add('evernote_full')
                    elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                        metadata_stats['date_formats'].add('iso_date')
                    else:
                        metadata_stats['date_formats'].add('other')
            
            # Source pattern analysis
            source = frontmatter.get('source', '')
            if source:
                if source.startswith('http'):
                    domain = re.findall(r'https?://([^/]+)', source)
                    if domain:
                        metadata_stats['source_patterns'][domain[0]] += 1
                else:
                    metadata_stats['source_patterns']['non_url'] += 1
            
            # Language distribution
            lang = frontmatter.get('language', 'unknown')
            metadata_stats['language_distribution'][lang] += 1
        
        # Determine required vs optional fields
        total_notes = len([n for n in dataset if 'error' not in n])
        for field, count in metadata_stats['field_frequency'].items():
            if count > total_notes * 0.8:  # Present in >80% of notes
                metadata_stats['required_fields'].append(field)
            else:
                metadata_stats['optional_fields'].append(field)
        
        # Convert sets to lists for JSON serialization
        for field in metadata_stats['field_formats']:
            metadata_stats['field_formats'][field] = list(metadata_stats['field_formats'][field])
        metadata_stats['date_formats'] = list(metadata_stats['date_formats'])
        
        return dict(metadata_stats)
    
    def _analyze_content_structures(self, dataset: List[Dict]) -> Dict:
        """Analyze content structure patterns for processing rules."""
        print("  Analyzing content structures...")
        
        structure_stats = {
            'header_patterns': Counter(),
            'list_patterns': Counter(),
            'paragraph_patterns': Counter(),
            'line_length_distribution': [],
            'content_organization': Counter(),
            'markdown_elements': Counter(),
            'content_density': []
        }
        
        for note_info in dataset:
            if 'error' in note_info:
                continue
                
            body = note_info.get('body', '')
            lines = body.split('\n')
            
            # Header analysis
            headers = re.findall(r'^(#+)\s+(.+)$', body, re.MULTILINE)
            for level, title in headers:
                structure_stats['header_patterns'][f'h{len(level)}'] += 1
                if len(title) > 50:
                    structure_stats['header_patterns']['long_title'] += 1
            
            # List analysis
            bullet_lists = re.findall(r'^[\s]*[-\*\+]\s', body, re.MULTILINE)
            numbered_lists = re.findall(r'^[\s]*\d+\.\s', body, re.MULTILINE)
            structure_stats['list_patterns']['bullet_items'] += len(bullet_lists)
            structure_stats['list_patterns']['numbered_items'] += len(numbered_lists)
            
            # Paragraph analysis
            paragraphs = [p.strip() for p in body.split('\n\n') if p.strip()]
            structure_stats['paragraph_patterns']['total'] += len(paragraphs)
            if paragraphs:
                avg_para_length = sum(len(p) for p in paragraphs) / len(paragraphs)
                structure_stats['paragraph_patterns']['avg_length'] = avg_para_length
            
            # Line length distribution
            line_lengths = [len(line) for line in lines if line.strip()]
            if line_lengths:
                structure_stats['line_length_distribution'].extend(line_lengths)
            
            # Content organization patterns
            if body.startswith('#'):
                structure_stats['content_organization']['starts_with_header'] += 1
            if '![[attachments/' in body:
                structure_stats['content_organization']['has_attachments'] += 1
            if body.count('\n\n') > body.count('\n') * 0.3:
                structure_stats['content_organization']['well_paragraphed'] += 1
            
            # Markdown elements
            markdown_elements = {
                'bold': len(re.findall(r'\*\*[^*]+\*\*', body)),
                'italic': len(re.findall(r'\*[^*]+\*', body)) - len(re.findall(r'\*\*[^*]+\*\*', body)),
                'links': len(re.findall(r'\[([^\]]+)\]\([^)]+\)', body)),
                'images': len(re.findall(r'!\[([^\]]*)\]\([^)]+\)', body)),
                'code_inline': len(re.findall(r'`[^`]+`', body)),
                'code_blocks': len(re.findall(r'```[\s\S]*?```', body)),
                'tables': body.count('|') // 3 if '|' in body else 0,
                'horizontal_rules': len(re.findall(r'^---+$', body, re.MULTILINE))
            }
            
            for element, count in markdown_elements.items():
                structure_stats['markdown_elements'][element] += count
            
            # Content density (non-whitespace chars per line)
            if lines:
                non_empty_lines = [line for line in lines if line.strip()]
                if non_empty_lines:
                    density = sum(len(line.strip()) for line in non_empty_lines) / len(non_empty_lines)
                    structure_stats['content_density'].append(density)
        
        # Calculate statistics for distributions
        if structure_stats['line_length_distribution']:
            lengths = structure_stats['line_length_distribution']
            structure_stats['line_length_stats'] = {
                'avg': sum(lengths) / len(lengths),
                'min': min(lengths),
                'max': max(lengths),
                'median': sorted(lengths)[len(lengths)//2]
            }
            # Keep only sample for size
            structure_stats['line_length_distribution'] = lengths[:100]
        
        if structure_stats['content_density']:
            densities = structure_stats['content_density']
            structure_stats['content_density_stats'] = {
                'avg': sum(densities) / len(densities),
                'min': min(densities),
                'max': max(densities)
            }
            structure_stats['content_density'] = densities[:100]
        
        return dict(structure_stats)
    
    def _catalog_boilerplate_patterns(self, dataset: List[Dict]) -> Dict:
        """Create comprehensive catalog of boilerplate patterns found."""
        print("  Cataloging boilerplate patterns...")
        
        boilerplate_catalog = {
            'exact_matches': Counter(),
            'pattern_matches': Counter(),
            'web_ui_elements': Counter(),
            'navigation_elements': Counter(),
            'social_elements': Counter(),
            'advertising_elements': Counter(),
            'form_elements': Counter(),
            'common_phrases': Counter(),
            'html_artifacts': Counter(),
            'evernote_artifacts': Counter(),
            'removal_candidates': []
        }
        
        # Compile regex patterns for different types
        html_pattern = re.compile(r'<[^>]+>')
        evernote_pattern = re.compile(r'(Evernote|Web Clipper|Clearly|Simplified Article)')
        
        for note_info in dataset:
            if 'error' in note_info:
                continue
                
            body = note_info.get('body', '')
            frontmatter = note_info.get('frontmatter', {})
            
            # Check exact boilerplate matches
            for pattern in BOILERPLATE_PATTERNS:
                if pattern.lower() in body.lower():
                    boilerplate_catalog['exact_matches'][pattern] += 1
            
            # Check web UI element patterns
            for category, indicators in self.web_indicators.items():
                category_key = f'{category}_elements'
                if category_key not in boilerplate_catalog:
                    boilerplate_catalog[category_key] = Counter()
                for indicator in indicators:
                    if indicator.lower() in body.lower():
                        boilerplate_catalog[category_key][indicator] += 1
            
            # Common boilerplate phrases (case-insensitive)
            common_phrases = [
                'click here', 'read more', 'continue reading', 'view full',
                'back to top', 'print this', 'email this', 'bookmark',
                'sign up', 'log in', 'register', 'subscribe',
                'follow us', 'like us', 'share this', 'tweet this',
                'related articles', 'recommended', 'trending',
                'advertisement', 'sponsored', 'promoted'
            ]
            
            body_lower = body.lower()
            for phrase in common_phrases:
                if phrase in body_lower:
                    boilerplate_catalog['common_phrases'][phrase] += 1
            
            # HTML artifacts
            html_matches = html_pattern.findall(body)
            for match in html_matches:
                boilerplate_catalog['html_artifacts'][match] += 1
            
            # Evernote-specific artifacts
            evernote_matches = evernote_pattern.findall(body)
            for match in evernote_matches:
                boilerplate_catalog['evernote_artifacts'][match] += 1
            
            # Identify removal candidates (lines that are likely boilerplate)
            lines = body.split('\n')
            for line in lines:
                line_clean = line.strip().lower()
                if line_clean and len(line_clean) < 100:  # Short lines are more likely boilerplate
                    # Check if line contains common boilerplate indicators
                    boilerplate_score = 0
                    for phrase in common_phrases:
                        if phrase in line_clean:
                            boilerplate_score += 1
                    
                    if boilerplate_score > 0 or any(indicator in line_clean for indicators in self.web_indicators.values() for indicator in indicators):
                        boilerplate_catalog['removal_candidates'].append({
                            'text': line.strip(),
                            'score': boilerplate_score,
                            'source_note': note_info.get('filename', 'unknown')
                        })
        
        # Limit removal candidates to most common ones
        boilerplate_catalog['removal_candidates'] = sorted(
            boilerplate_catalog['removal_candidates'],
            key=lambda x: x['score'],
            reverse=True
        )[:50]
        
        return dict(boilerplate_catalog)
    
    def _analyze_attachment_patterns(self, dataset: List[Dict]) -> Dict:
        """Analyze attachment usage patterns."""
        print("  Analyzing attachment patterns...")
        
        attachment_stats = {
            'total_attachments': 0,
            'attachment_types': Counter(),
            'attachment_paths': [],
            'notes_with_attachments': 0,
            'attachment_formats': Counter(),
            'broken_attachments': []
        }
        
        attachment_regex = re.compile(r'!\[\[attachments/([^\]]+)\]\]')
        
        for note_info in dataset:
            if 'error' in note_info:
                continue
                
            body = note_info.get('body', '')
            attachments = attachment_regex.findall(body)
            
            if attachments:
                attachment_stats['notes_with_attachments'] += 1
                attachment_stats['total_attachments'] += len(attachments)
                
                for attachment in attachments:
                    # Extract file extension
                    if '.' in attachment:
                        ext = attachment.split('.')[-1].lower()
                        attachment_stats['attachment_types'][ext] += 1
                    
                    # Store attachment path (first 20 for analysis)
                    if len(attachment_stats['attachment_paths']) < 20:
                        attachment_stats['attachment_paths'].append(attachment)
                    
                    # Categorize by format
                    if any(ext in attachment.lower() for ext in ['.pdf']):
                        attachment_stats['attachment_formats']['pdf'] += 1
                    elif any(ext in attachment.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
                        attachment_stats['attachment_formats']['image'] += 1
                    elif any(ext in attachment.lower() for ext in ['.doc', '.docx', '.txt']):
                        attachment_stats['attachment_formats']['document'] += 1
                    else:
                        attachment_stats['attachment_formats']['other'] += 1
        
        return dict(attachment_stats)
    
    def _analyze_url_patterns(self, dataset: List[Dict]) -> Dict:
        """Analyze URL patterns and sources."""
        print("  Analyzing URL patterns...")
        
        url_stats = {
            'total_urls': 0,
            'notes_with_urls': 0,
            'domain_distribution': Counter(),
            'url_types': Counter(),
            'source_domains': Counter(),
            'broken_url_indicators': []
        }
        
        url_regex = re.compile(r'https?://([^/\s]+)')
        
        for note_info in dataset:
            if 'error' in note_info:
                continue
                
            body = note_info.get('body', '')
            frontmatter = note_info.get('frontmatter', {})
            
            # Analyze URLs in body
            urls = url_regex.findall(body)
            if urls:
                url_stats['notes_with_urls'] += 1
                url_stats['total_urls'] += len(urls)
                
                for domain in urls:
                    url_stats['domain_distribution'][domain] += 1
                    
                    # Categorize URL types
                    if any(social in domain.lower() for social in ['facebook', 'twitter', 'linkedin', 'instagram']):
                        url_stats['url_types']['social_media'] += 1
                    elif any(news in domain.lower() for news in ['news', 'times', 'post', 'guardian', 'reuters']):
                        url_stats['url_types']['news'] += 1
                    elif any(tech in domain.lower() for tech in ['github', 'stackoverflow', 'medium', 'dev']):
                        url_stats['url_types']['tech'] += 1
                    else:
                        url_stats['url_types']['other'] += 1
            
            # Analyze source URLs from metadata
            source = frontmatter.get('source', '')
            if source and source.startswith('http'):
                domain_match = url_regex.search(source)
                if domain_match:
                    url_stats['source_domains'][domain_match.group(1)] += 1
        
        return dict(url_stats)
    
    def _analyze_formatting_patterns(self, dataset: List[Dict]) -> Dict:
        """Analyze formatting and structure patterns."""
        print("  Analyzing formatting patterns...")
        
        formatting_stats = {
            'indentation_patterns': Counter(),
            'spacing_patterns': Counter(),
            'punctuation_patterns': Counter(),
            'capitalization_patterns': Counter(),
            'special_characters': Counter(),
            'encoding_issues': []
        }
        
        for note_info in dataset:
            if 'error' in note_info:
                continue
                
            body = note_info.get('body', '')
            lines = body.split('\n')
            
            # Indentation analysis
            for line in lines:
                if line.strip():
                    leading_spaces = len(line) - len(line.lstrip(' '))
                    leading_tabs = len(line) - len(line.lstrip('\t'))
                    
                    if leading_spaces > 0:
                        formatting_stats['indentation_patterns'][f'spaces_{leading_spaces}'] += 1
                    if leading_tabs > 0:
                        formatting_stats['indentation_patterns'][f'tabs_{leading_tabs}'] += 1
            
            # Spacing patterns
            double_spaces = body.count('  ')
            triple_spaces = body.count('   ')
            multiple_newlines = len(re.findall(r'\n\n+', body))
            
            formatting_stats['spacing_patterns']['double_spaces'] += double_spaces
            formatting_stats['spacing_patterns']['triple_spaces'] += triple_spaces
            formatting_stats['spacing_patterns']['multiple_newlines'] += multiple_newlines
            
            # Special characters that might indicate encoding issues
            special_chars = re.findall(r'[^\x00-\x7F]', body)
            for char in special_chars[:10]:  # Limit to first 10
                formatting_stats['special_characters'][char] += 1
            
            # Look for potential encoding issues
            encoding_indicators = ['Â', '€™', '€œ', '€', 'â€', 'Ã']
            for indicator in encoding_indicators:
                if indicator in body:
                    formatting_stats['encoding_issues'].append({
                        'indicator': indicator,
                        'note': note_info.get('filename', 'unknown')
                    })
        
        # Limit encoding issues list
        formatting_stats['encoding_issues'] = formatting_stats['encoding_issues'][:20]
        
        return dict(formatting_stats)
    
    def _analyze_language_patterns(self, dataset: List[Dict]) -> Dict:
        """Analyze language-specific patterns."""
        print("  Analyzing language patterns...")
        
        language_stats = {
            'language_distribution': Counter(),
            'mixed_language_notes': 0,
            'language_indicators': {},
            'character_sets': Counter()
        }
        
        # Language indicators
        spanish_indicators = ['el', 'la', 'de', 'en', 'y', 'que', 'con', 'por', 'para', 'es', 'del', 'una', 'este']
        english_indicators = ['the', 'and', 'of', 'to', 'in', 'for', 'with', 'on', 'by', 'this', 'that', 'from']
        
        for note_info in dataset:
            if 'error' in note_info:
                continue
                
            frontmatter = note_info.get('frontmatter', {})
            body = note_info.get('body', '').lower()
            
            # Language from metadata
            declared_lang = frontmatter.get('language', 'unknown')
            language_stats['language_distribution'][declared_lang] += 1
            
            # Detect language from content
            spanish_score = sum(1 for indicator in spanish_indicators if f' {indicator} ' in body)
            english_score = sum(1 for indicator in english_indicators if f' {indicator} ' in body)
            
            if spanish_score > 0 and english_score > 0:
                language_stats['mixed_language_notes'] += 1
            
            # Character set analysis
            if re.search(r'[áéíóúñü¿¡]', body):
                language_stats['character_sets']['spanish_chars'] += 1
            if re.search(r'[àèìòùâêîôûäëïöü]', body):
                language_stats['character_sets']['accented_chars'] += 1
            if re.search(r'[αβγδεζηθικλμνξοπρστυφχψω]', body):
                language_stats['character_sets']['greek_chars'] += 1
        
        return dict(language_stats)
    
    def _define_content_preservation_specs(self, dataset: List[Dict]) -> Dict:
        """Define specifications for what content should be preserved."""
        print("  Defining content preservation specifications...")
        
        preservation_specs = {
            'required_metadata': [],
            'optional_metadata': [],
            'content_elements_to_preserve': [],
            'content_elements_to_remove': [],
            'formatting_to_preserve': [],
            'formatting_to_clean': [],
            'attachment_handling': {},
            'url_handling': {}
        }
        
        # Analyze metadata importance
        metadata_analysis = self._analyze_metadata_patterns(dataset)
        preservation_specs['required_metadata'] = metadata_analysis['required_fields']
        preservation_specs['optional_metadata'] = metadata_analysis['optional_fields']
        
        # Content preservation rules
        preservation_specs['content_elements_to_preserve'] = [
            'headers (h1-h6)',
            'paragraphs with substantial content (>50 chars)',
            'lists (bullet and numbered)',
            'tables with data',
            'code blocks',
            'quotes and citations',
            'meaningful links',
            'images and attachments',
            'structured data'
        ]
        
        preservation_specs['content_elements_to_remove'] = [
            'navigation elements',
            'social sharing buttons',
            'advertisement blocks',
            'cookie notices',
            'subscription prompts',
            'comment sections',
            'related articles sections',
            'footer content',
            'header navigation',
            'sidebar content'
        ]
        
        preservation_specs['formatting_to_preserve'] = [
            'markdown headers',
            'paragraph breaks',
            'list formatting',
            'emphasis (bold/italic)',
            'code formatting',
            'table structure',
            'link formatting'
        ]
        
        preservation_specs['formatting_to_clean'] = [
            'excessive whitespace',
            'inconsistent indentation',
            'HTML artifacts',
            'encoding issues',
            'broken formatting'
        ]
        
        preservation_specs['attachment_handling'] = {
            'preserve_references': True,
            'validate_paths': True,
            'supported_formats': ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx'],
            'action_for_broken': 'log_and_remove_reference'
        }
        
        preservation_specs['url_handling'] = {
            'preserve_meaningful_links': True,
            'remove_tracking_parameters': True,
            'validate_accessibility': False,  # Too slow for batch processing
            'convert_to_archive_links': False
        }
        
        return preservation_specs
    
    def _generate_processing_recommendations(self, dataset: List[Dict]) -> Dict:
        """Generate specific processing recommendations for batch processing."""
        print("  Generating processing recommendations...")
        
        recommendations = {
            'web_clipping_processing': {
                'priority': 'HIGH',
                'percentage': 0,
                'specific_actions': [],
                'boilerplate_removal_rules': [],
                'content_extraction_rules': []
            },
            'pdf_annotation_processing': {
                'priority': 'MEDIUM',
                'percentage': 0,
                'specific_actions': [],
                'attachment_validation': True
            },
            'personal_note_processing': {
                'priority': 'LOW',
                'percentage': 0,
                'specific_actions': ['minimal_cleanup', 'standardize_formatting']
            },
            'metadata_standardization': {
                'priority': 'HIGH',
                'actions': []
            },
            'quality_improvement': {
                'actions': []
            }
        }
        
        # Calculate category percentages
        total_notes = len([n for n in dataset if 'error' not in n])
        category_counts = Counter()
        
        for note_info in dataset:
            if 'error' in note_info:
                continue
            analysis = self.analyze_note(note_info)
            category_counts[analysis['category']] += 1
        
        # Update recommendations based on analysis
        if 'web_clipping' in category_counts:
            pct = (category_counts['web_clipping'] / total_notes) * 100
            recommendations['web_clipping_processing']['percentage'] = pct
            recommendations['web_clipping_processing']['specific_actions'] = [
                'remove_social_sharing_elements',
                'remove_navigation_menus',
                'remove_advertisement_blocks',
                'clean_html_artifacts',
                'extract_main_content',
                'preserve_source_attribution'
            ]
        
        if 'pdf_annotation' in category_counts:
            pct = (category_counts['pdf_annotation'] / total_notes) * 100
            recommendations['pdf_annotation_processing']['percentage'] = pct
            recommendations['pdf_annotation_processing']['specific_actions'] = [
                'validate_attachment_paths',
                'extract_pdf_metadata',
                'preserve_annotation_context',
                'ensure_pdf_accessibility'
            ]
        
        if 'personal_note' in category_counts:
            pct = (category_counts['personal_note'] / total_notes) * 100
            recommendations['personal_note_processing']['percentage'] = pct
        
        # Metadata standardization recommendations
        recommendations['metadata_standardization']['actions'] = [
            'standardize_date_formats',
            'normalize_tag_structure',
            'validate_source_urls',
            'ensure_required_fields_present',
            'clean_language_field'
        ]
        
        # Quality improvement recommendations
        recommendations['quality_improvement']['actions'] = [
            'remove_duplicate_content',
            'fix_encoding_issues',
            'standardize_formatting',
            'improve_header_structure',
            'validate_links_and_attachments'
        ]
        
        return recommendations
    
    def _create_batch_processing_specs(self, dataset: List[Dict]) -> Dict:
        """Create detailed specifications for batch processing implementation."""
        print("  Creating batch processing specifications...")
        
        specs = {
            'processing_pipeline': {
                'stages': [
                    'validation_and_backup',
                    'metadata_extraction_and_standardization',
                    'content_classification',
                    'boilerplate_removal',
                    'content_cleaning',
                    'formatting_standardization',
                    'quality_validation',
                    'output_generation'
                ]
            },
            'input_specifications': {
                'file_format': 'markdown',
                'encoding': 'utf-8',
                'frontmatter_format': 'yaml',
                'expected_structure': 'frontmatter + content'
            },
            'output_specifications': {
                'preserve_metadata_fields': [],
                'standardized_frontmatter': True,
                'clean_content_only': True,
                'maintain_file_structure': True
            },
            'processing_rules': {
                'web_clipping_rules': [],
                'pdf_annotation_rules': [],
                'personal_note_rules': [],
                'general_cleaning_rules': []
            },
            'quality_assurance': {
                'validation_checks': [],
                'error_handling': {},
                'logging_requirements': []
            },
            'performance_requirements': {
                'batch_size': 50,
                'estimated_processing_time': '2-5 seconds per note',
                'memory_requirements': 'moderate',
                'parallel_processing': True
            }
        }
        
        # Populate specifications based on analysis
        metadata_analysis = self._analyze_metadata_patterns(dataset)
        specs['output_specifications']['preserve_metadata_fields'] = metadata_analysis['required_fields']
        
        # Web clipping processing rules
        specs['processing_rules']['web_clipping_rules'] = [
            'remove_lines_containing_boilerplate_patterns',
            'extract_content_between_main_headers',
            'remove_social_sharing_blocks',
            'clean_navigation_elements',
            'preserve_source_attribution',
            'maintain_article_structure'
        ]
        
        # Quality assurance specifications
        specs['quality_assurance']['validation_checks'] = [
            'verify_frontmatter_integrity',
            'check_content_not_empty',
            'validate_attachment_references',
            'ensure_proper_encoding',
            'verify_required_metadata_present'
        ]
        
        specs['quality_assurance']['error_handling'] = {
            'missing_metadata': 'log_warning_and_continue',
            'broken_attachments': 'log_error_and_remove_reference',
            'encoding_issues': 'attempt_fix_or_flag',
            'empty_content': 'flag_for_manual_review',
            'processing_failure': 'log_error_and_skip'
        }
        
        specs['quality_assurance']['logging_requirements'] = [
            'processing_statistics',
            'error_summary',
            'quality_metrics',
            'performance_metrics',
            'files_requiring_manual_review'
        ]
        
        return specs
    
    def save_technical_characterization(self, analysis_results: Dict, filename: str = "technical_characterization.json") -> str:
        """Save comprehensive technical characterization."""
        output_path = Path(OUTPUT_DIR) / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Technical characterization saved to: {output_path}")
        return str(output_path)
    
    def generate_coding_agent_brief(self, analysis_results: Dict) -> str:
        """Generate a comprehensive brief for the coding agent."""
        
        brief = f"""# Technical Characterization for Batch Processing Application

## Executive Summary

This document provides comprehensive technical specifications for developing a batch processing application to clean and preprocess Obsidian notes converted from Evernote.

**Vault Statistics:**
- Total notes in sample: {analysis_results.get('metadata_analysis', {}).get('field_frequency', {}).get('title', 'N/A')}
- Primary content types: Web clippings, PDF annotations, Personal notes
- Languages: {', '.join(analysis_results.get('language_analysis', {}).get('language_distribution', {}).keys())}
- Attachment usage: {analysis_results.get('attachment_analysis', {}).get('notes_with_attachments', 0)} notes with attachments

## Metadata Structure Specifications

### Required Fields (Present in >80% of notes):
{self._format_list(analysis_results.get('metadata_analysis', {}).get('required_fields', []))}

### Optional Fields:
{self._format_list(analysis_results.get('metadata_analysis', {}).get('optional_fields', []))}

### Date Format Standardization:
Current formats found: {', '.join(analysis_results.get('metadata_analysis', {}).get('date_formats', []))}
**Recommendation:** Standardize to ISO format (YYYY-MM-DD HH:MM:SS)

## Content Processing Specifications

### Boilerplate Removal Requirements

**High-Priority Removal Patterns:**
{self._format_counter(analysis_results.get('boilerplate_catalog', {}).get('exact_matches', {}), limit=10)}

**Web UI Elements to Remove:**
{self._format_counter(analysis_results.get('boilerplate_catalog', {}).get('navigation_elements', {}), limit=5)}

**Social Media Elements to Remove:**
{self._format_counter(analysis_results.get('boilerplate_catalog', {}).get('social_elements', {}), limit=5)}

### Content Structure Patterns

**Markdown Elements Distribution:**
{self._format_counter(analysis_results.get('content_structure_analysis', {}).get('markdown_elements', {}), limit=8)}

**Header Usage Patterns:**
{self._format_counter(analysis_results.get('content_structure_analysis', {}).get('header_patterns', {}), limit=6)}

## Attachment Handling Specifications

**Attachment Statistics:**
- Total attachments: {analysis_results.get('attachment_analysis', {}).get('total_attachments', 0)}
- Notes with attachments: {analysis_results.get('attachment_analysis', {}).get('notes_with_attachments', 0)}

**File Type Distribution:**
{self._format_counter(analysis_results.get('attachment_analysis', {}).get('attachment_types', {}), limit=10)}

**Processing Requirements:**
- Validate all attachment paths
- Preserve PDF references
- Handle missing attachments gracefully
- Maintain attachment-content relationships

## URL and Link Processing

**Domain Distribution (Top Sources):**
{self._format_counter(analysis_results.get('url_analysis', {}).get('source_domains', {}), limit=10)}

**URL Categories:**
{self._format_counter(analysis_results.get('url_analysis', {}).get('url_types', {}), limit=5)}

## Processing Pipeline Specifications

{self._format_processing_pipeline(analysis_results.get('batch_processing_specs', {}))}

## Content Preservation Rules

**Elements to Preserve:**
{self._format_list(analysis_results.get('content_preservation_specs', {}).get('content_elements_to_preserve', []))}

**Elements to Remove:**
{self._format_list(analysis_results.get('content_preservation_specs', {}).get('content_elements_to_remove', []))}

## Quality Assurance Requirements

**Validation Checks:**
{self._format_list(analysis_results.get('batch_processing_specs', {}).get('quality_assurance', {}).get('validation_checks', []))}

**Error Handling:**
{self._format_dict(analysis_results.get('batch_processing_specs', {}).get('quality_assurance', {}).get('error_handling', {}))}

## Performance Requirements

- **Batch Size:** {analysis_results.get('batch_processing_specs', {}).get('performance_requirements', {}).get('batch_size', 50)} notes per batch
- **Processing Time:** {analysis_results.get('batch_processing_specs', {}).get('performance_requirements', {}).get('estimated_processing_time', 'N/A')}
- **Parallel Processing:** {analysis_results.get('batch_processing_specs', {}).get('performance_requirements', {}).get('parallel_processing', False)}

## Implementation Recommendations

### Priority Processing Categories:

1. **Web Clipping Processing (HIGH PRIORITY)**
   - Percentage of content: {analysis_results.get('processing_recommendations', {}).get('web_clipping_processing', {}).get('percentage', 0):.1f}%
   - Actions: {', '.join(analysis_results.get('processing_recommendations', {}).get('web_clipping_processing', {}).get('specific_actions', []))}

2. **PDF Annotation Processing (MEDIUM PRIORITY)**
   - Percentage of content: {analysis_results.get('processing_recommendations', {}).get('pdf_annotation_processing', {}).get('percentage', 0):.1f}%
   - Actions: {', '.join(analysis_results.get('processing_recommendations', {}).get('pdf_annotation_processing', {}).get('specific_actions', []))}

3. **Personal Note Processing (LOW PRIORITY)**
   - Percentage of content: {analysis_results.get('processing_recommendations', {}).get('personal_note_processing', {}).get('percentage', 0):.1f}%
   - Actions: {', '.join(analysis_results.get('processing_recommendations', {}).get('personal_note_processing', {}).get('specific_actions', []))}

## Technical Implementation Notes

- Use UTF-8 encoding throughout
- Implement robust YAML frontmatter parsing
- Create comprehensive logging system
- Build validation checkpoints
- Implement rollback capabilities
- Design for incremental processing

This characterization provides the technical foundation for building a robust batch processing application that will effectively clean and optimize the Obsidian vault while preserving valuable content and metadata.
"""
        
        return brief
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list for the brief."""
        if not items:
            return "- None specified"
        return '\n'.join(f"- {item}" for item in items)
    
    def _format_counter(self, counter: Counter, limit: int = 5) -> str:
        """Format a counter for the brief."""
        if not counter:
            return "- None found"
        items = counter.most_common(limit)
        return '\n'.join(f"- {item}: {count}" for item, count in items)
    
    def _format_dict(self, d: Dict) -> str:
        """Format a dictionary for the brief."""
        if not d:
            return "- None specified"
        return '\n'.join(f"- {k}: {v}" for k, v in d.items())
    
    def _format_processing_pipeline(self, specs: Dict) -> str:
        """Format processing pipeline specifications."""
        if not specs or 'processing_pipeline' not in specs:
            return "Pipeline specifications not available"
        
        stages = specs['processing_pipeline'].get('stages', [])
        return '\n'.join(f"{i+1}. {stage.replace('_', ' ').title()}" for i, stage in enumerate(stages))


if __name__ == "__main__":
    import yaml
    
    # Load sample dataset
    dataset_path = Path(OUTPUT_DIR) / "sample_dataset.yaml"
    if not dataset_path.exists():
        print("Sample dataset not found. Run note_sampler.py first.")
        exit(1)
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = yaml.safe_load(f)
    
    # Perform comprehensive technical analysis
    characterizer = TechnicalCharacterizer()
    results = characterizer.comprehensive_analysis(dataset)
    
    # Save technical characterization
    characterizer.save_technical_characterization(results)
    
    # Generate and save coding agent brief
    brief = characterizer.generate_coding_agent_brief(results)
    brief_path = Path(OUTPUT_DIR) / "coding_agent_brief.md"
    with open(brief_path, 'w', encoding='utf-8') as f:
        f.write(brief)
    
    print(f"\nTechnical characterization complete!")
    print(f"Detailed analysis: {Path(OUTPUT_DIR) / 'technical_characterization.json'}")
    print(f"Coding agent brief: {brief_path}")
