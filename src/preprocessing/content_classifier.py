"""
Content classification module for identifying note types and processing requirements.
"""

import re
from typing import Dict, List, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import ANALYSIS_CATEGORIES


class ContentClassifier:
    """Classifies note content to determine appropriate processing strategy."""
    
    def __init__(self):
        self.categories = ANALYSIS_CATEGORIES
        self.classification_rules = self._build_classification_rules()
    
    def _build_classification_rules(self) -> Dict:
        """Build classification rules based on technical analysis."""
        return {
            'web_clipping': {
                'indicators': [
                    'has_source_url',
                    'has_boilerplate_patterns',
                    'has_navigation_elements',
                    'has_social_sharing'
                ],
                'required_score': 2,
                'weight': 1.0
            },
            'pdf_annotation': {
                'indicators': [
                    'has_pdf_attachment',
                    'has_attachment_reference',
                    'short_content',
                    'no_source_url'
                ],
                'required_score': 2,
                'weight': 0.9
            },
            'business_card': {
                'indicators': [
                    'has_email',
                    'has_phone_patterns',
                    'has_business_terms',
                    'very_short_content',
                    'has_contact_info'
                ],
                'required_score': 2,
                'weight': 0.8
            },
            'audio_annotation': {
                'indicators': [
                    'has_audio_attachment',
                    'has_attachment_reference',
                    'short_content',
                    'no_source_url'
                ],
                'required_score': 2,
                'weight': 0.9
            },
            'news_article': {
                'indicators': [
                    'has_news_tags',
                    'has_source_url',
                    'has_publication_date',
                    'substantial_content',
                    'has_news_domain'
                ],
                'required_score': 3,
                'weight': 0.7
            },
            'technical_document': {
                'indicators': [
                    'has_code_blocks',
                    'has_technical_terms',
                    'structured_content',
                    'substantial_content',
                    'has_headers'
                ],
                'required_score': 3,
                'weight': 0.6
            },
            'personal_note': {
                'indicators': [
                    'no_source_url',
                    'short_to_medium_content',
                    'simple_structure',
                    'no_attachments',
                    'personal_language'
                ],
                'required_score': 3,
                'weight': 0.5
            }
        }
    
    def classify_note(self, content: str, frontmatter: Dict) -> Dict:
        """
        Classify a note and return classification results.
        
        Returns:
            Dict with classification, confidence, and processing recommendations
        """
        indicators = self._analyze_indicators(content, frontmatter)
        scores = self._calculate_category_scores(indicators)
        
        # Find best match
        best_category = max(scores.items(), key=lambda x: x[1])
        category, confidence = best_category
        
        # If confidence is too low, mark as unknown
        if confidence < 0.3:
            category = 'unknown'
            confidence = 0.0
        
        return {
            'category': category,
            'confidence': confidence,
            'all_scores': scores,
            'indicators': indicators,
            'processing_recommendations': self._get_processing_recommendations(category, indicators)
        }
    
    def _analyze_indicators(self, content: str, frontmatter: Dict) -> Dict:
        """Analyze content for classification indicators."""
        indicators = {}
        
        # Source URL analysis
        source = frontmatter.get('source', '')
        indicators['has_source_url'] = bool(source and 'http' in source)
        
        # Content length analysis
        word_count = len(content.split())
        indicators['very_short_content'] = word_count < 50
        indicators['short_content'] = word_count < 200
        indicators['short_to_medium_content'] = 50 <= word_count <= 500
        indicators['substantial_content'] = word_count > 200
        
        # Attachment analysis
        indicators['has_attachment_reference'] = '![[attachments/' in content
        indicators['has_pdf_attachment'] = '.pdf' in content.lower()
        indicators['has_audio_attachment'] = any(ext in content.lower() for ext in ['.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg', '.wma'])
        indicators['no_attachments'] = not indicators['has_attachment_reference']
        
        # Structure analysis
        indicators['has_headers'] = bool(re.search(r'^#+\s', content, re.MULTILINE))
        indicators['has_code_blocks'] = '```' in content or content.count('`') > 4
        indicators['structured_content'] = (
            indicators['has_headers'] and 
            (content.count('\n\n') > content.count('\n') * 0.2)
        )
        indicators['simple_structure'] = not indicators['structured_content']
        
        # Contact information analysis
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_patterns = [
            r'\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        ]
        
        indicators['has_email'] = bool(re.search(email_pattern, content))
        indicators['has_phone_patterns'] = any(re.search(pattern, content) for pattern in phone_patterns)
        
        # Business terms
        business_terms = [
            'tarjeta de visita', 'business card', 'company', 'corporation',
            'director', 'manager', 'ceo', 'president', 'consultant'
        ]
        indicators['has_business_terms'] = any(term.lower() in content.lower() for term in business_terms)
        indicators['has_contact_info'] = (
            indicators['has_email'] or 
            indicators['has_phone_patterns'] or 
            indicators['has_business_terms']
        )
        
        # Technical terms
        technical_terms = [
            'api', 'database', 'algorithm', 'framework', 'library',
            'function', 'method', 'class', 'variable', 'documentation',
            'specification', 'protocol', 'implementation'
        ]
        indicators['has_technical_terms'] = any(term.lower() in content.lower() for term in technical_terms)
        
        # News indicators
        news_tags = frontmatter.get('tags', [])
        if isinstance(news_tags, list):
            indicators['has_news_tags'] = any('news' in str(tag).lower() for tag in news_tags)
        else:
            indicators['has_news_tags'] = 'news' in str(news_tags).lower()
        
        # Publication date patterns
        date_patterns = [
            r'\b\w+\s+\d{1,2},?\s+\d{4}\b',  # January 1, 2023
            r'\b\d{1,2}\s+\w+\s+\d{4}\b',   # 1 January 2023
            r'By\s+[A-Z][a-z]+.*-\s+\w+\s+\d{1,2}'  # By Author - Month Day
        ]
        indicators['has_publication_date'] = any(re.search(pattern, content) for pattern in date_patterns)
        
        # News domain check
        news_domains = [
            'reuters', 'bbc', 'cnn', 'nytimes', 'guardian', 'economist',
            'ft.com', 'wsj', 'bloomberg', 'ap.org', 'news'
        ]
        indicators['has_news_domain'] = any(domain in source.lower() for domain in news_domains) if source else False
        
        # Boilerplate analysis
        boilerplate_patterns = [
            'share this', 'follow us', 'subscribe', 'newsletter',
            'comments', 'privacy policy', 'cookie', 'advertisement'
        ]
        boilerplate_count = sum(1 for pattern in boilerplate_patterns if pattern.lower() in content.lower())
        indicators['has_boilerplate_patterns'] = boilerplate_count >= 2
        
        # Navigation elements
        nav_elements = ['home', 'about', 'contact', 'search', 'menu', 'login']
        indicators['has_navigation_elements'] = any(elem.lower() in content.lower() for elem in nav_elements)
        
        # Social sharing
        social_terms = ['facebook', 'twitter', 'linkedin', 'share on', 'tweet this']
        indicators['has_social_sharing'] = any(term.lower() in content.lower() for term in social_terms)
        
        # Personal language indicators
        personal_pronouns = ['i ', 'my ', 'me ', 'myself', 'we ', 'our ', 'us ']
        personal_count = sum(content.lower().count(pronoun) for pronoun in personal_pronouns)
        indicators['personal_language'] = personal_count > 3
        
        return indicators
    
    def _calculate_category_scores(self, indicators: Dict) -> Dict:
        """Calculate scores for each category based on indicators."""
        scores = {}
        
        for category, rules in self.classification_rules.items():
            score = 0
            matched_indicators = 0
            
            for indicator in rules['indicators']:
                if indicators.get(indicator, False):
                    matched_indicators += 1
            
            # Calculate base score
            if matched_indicators >= rules['required_score']:
                score = (matched_indicators / len(rules['indicators'])) * rules['weight']
            
            scores[category] = score
        
        return scores
    
    def _get_processing_recommendations(self, category: str, indicators: Dict) -> Dict:
        """Get processing recommendations based on classification."""
        recommendations = {
            'priority': 'medium',
            'actions': [],
            'preserve_elements': [],
            'remove_elements': [],
            'special_handling': []
        }
        
        if category == 'web_clipping':
            recommendations.update({
                'priority': 'high',
                'actions': [
                    'remove_boilerplate',
                    'extract_main_content',
                    'clean_navigation',
                    'preserve_source_attribution'
                ],
                'preserve_elements': ['main_content', 'headers', 'images', 'source_url'],
                'remove_elements': ['navigation', 'social_sharing', 'comments', 'ads'],
                'special_handling': ['validate_source_url', 'extract_article_metadata']
            })
        
        elif category == 'pdf_annotation':
            recommendations.update({
                'priority': 'medium',
                'actions': [
                    'validate_pdf_path',
                    'preserve_annotation_context',
                    'minimal_cleanup'
                ],
                'preserve_elements': ['pdf_reference', 'annotations', 'context'],
                'remove_elements': [],
                'special_handling': ['check_pdf_accessibility', 'extract_pdf_metadata']
            })
        
        elif category == 'personal_note':
            recommendations.update({
                'priority': 'low',
                'actions': [
                    'minimal_cleanup',
                    'standardize_formatting',
                    'preserve_personal_content'
                ],
                'preserve_elements': ['all_content', 'personal_formatting'],
                'remove_elements': [],
                'special_handling': ['gentle_formatting_only']
            })
        
        elif category == 'business_card':
            recommendations.update({
                'priority': 'low',
                'actions': [
                    'extract_contact_info',
                    'standardize_format',
                    'validate_contact_details'
                ],
                'preserve_elements': ['contact_info', 'business_details'],
                'remove_elements': [],
                'special_handling': ['structure_contact_data']
            })
        
        elif category == 'technical_document':
            recommendations.update({
                'priority': 'medium',
                'actions': [
                    'preserve_code_blocks',
                    'maintain_structure',
                    'clean_formatting'
                ],
                'preserve_elements': ['code', 'headers', 'structure', 'technical_content'],
                'remove_elements': ['minimal_boilerplate_only'],
                'special_handling': ['validate_code_formatting', 'preserve_technical_accuracy']
            })
        
        elif category == 'news_article':
            recommendations.update({
                'priority': 'high',
                'actions': [
                    'extract_article_content',
                    'preserve_attribution',
                    'remove_news_boilerplate'
                ],
                'preserve_elements': ['headline', 'content', 'author', 'date', 'source'],
                'remove_elements': ['related_articles', 'comments', 'subscription_prompts'],
                'special_handling': ['extract_publication_metadata']
            })
        
        else:  # unknown
            recommendations.update({
                'priority': 'medium',
                'actions': [
                    'manual_review_required',
                    'minimal_cleanup',
                    'preserve_all_content'
                ],
                'preserve_elements': ['all_content'],
                'remove_elements': [],
                'special_handling': ['flag_for_manual_classification']
            })
        
        return recommendations
    
    def batch_classify(self, notes: List[Tuple[str, Dict, str]]) -> Dict:
        """
        Classify multiple notes and return batch statistics.
        
        Args:
            notes: List of (content, frontmatter, filename) tuples
            
        Returns:
            Dict with classification results and statistics
        """
        results = {
            'classifications': [],
            'category_counts': {},
            'confidence_stats': {
                'high_confidence': 0,  # > 0.7
                'medium_confidence': 0,  # 0.3 - 0.7
                'low_confidence': 0  # < 0.3
            },
            'processing_priorities': {
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }
        
        for content, frontmatter, filename in notes:
            classification = self.classify_note(content, frontmatter)
            classification['filename'] = filename
            results['classifications'].append(classification)
            
            # Update statistics
            category = classification['category']
            confidence = classification['confidence']
            priority = classification['processing_recommendations']['priority']
            
            results['category_counts'][category] = results['category_counts'].get(category, 0) + 1
            results['processing_priorities'][priority] += 1
            
            if confidence > 0.7:
                results['confidence_stats']['high_confidence'] += 1
            elif confidence > 0.3:
                results['confidence_stats']['medium_confidence'] += 1
            else:
                results['confidence_stats']['low_confidence'] += 1
        
        return results
