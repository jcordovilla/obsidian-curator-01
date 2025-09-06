"""
Web clipping content cleaner for removing boilerplate and extracting main content.
"""

import re
from typing import List, Dict, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import BOILERPLATE_PATTERNS, WEB_BOILERPLATE_INDICATORS


class WebClippingCleaner:
    """Cleans web clipping content by removing boilerplate and preserving valuable content."""
    
    def __init__(self):
        self.boilerplate_patterns = [re.compile(pattern, re.IGNORECASE) 
                                   for pattern in BOILERPLATE_PATTERNS]
        self.web_indicators = WEB_BOILERPLATE_INDICATORS
        
        # Patterns for content that should be removed entirely
        self.removal_patterns = [
            # Social sharing
            re.compile(r'.*share\s+this.*', re.IGNORECASE),
            re.compile(r'.*follow\s+us.*', re.IGNORECASE),
            re.compile(r'.*like\s+us.*', re.IGNORECASE),
            re.compile(r'.*tweet\s+this.*', re.IGNORECASE),
            
            # Navigation
            re.compile(r'.*back\s+to\s+top.*', re.IGNORECASE),
            re.compile(r'.*continue\s+reading.*', re.IGNORECASE),
            re.compile(r'.*read\s+more.*', re.IGNORECASE),
            re.compile(r'.*click\s+here.*', re.IGNORECASE),
            
            # Subscription and registration
            re.compile(r'.*subscribe.*newsletter.*', re.IGNORECASE),
            re.compile(r'.*sign\s+up.*', re.IGNORECASE),
            re.compile(r'.*register.*', re.IGNORECASE),
            
            # Comments
            re.compile(r'.*leave\s+a\s+comment.*', re.IGNORECASE),
            re.compile(r'.*post\s+a\s+comment.*', re.IGNORECASE),
            re.compile(r'.*comments.*below.*', re.IGNORECASE),
            
            # Legal and policy
            re.compile(r'.*privacy\s+policy.*', re.IGNORECASE),
            re.compile(r'.*cookie\s+policy.*', re.IGNORECASE),
            re.compile(r'.*terms\s+of\s+(service|use).*', re.IGNORECASE),
        ]
        
        # Patterns for lines that are likely navigation or boilerplate
        self.navigation_patterns = [
            re.compile(r'^\s*(home|about|contact|search|login|menu)\s*$', re.IGNORECASE),
            re.compile(r'^\s*\|\s*(home|about|contact|search|login|menu)(\s*\|.*)?$', re.IGNORECASE),
        ]
    
    def clean_web_clipping(self, content: str, frontmatter: Dict) -> Tuple[str, Dict]:
        """
        Clean web clipping content by removing boilerplate.
        
        Args:
            content: Raw content string
            frontmatter: Metadata dictionary
            
        Returns:
            Tuple of (cleaned_content, cleaning_stats)
        """
        stats = {
            'original_lines': len(content.split('\n')),
            'original_chars': len(content),
            'removed_lines': 0,
            'removed_chars': 0,
            'boilerplate_matches': [],
            'preserved_elements': []
        }
        
        # Split content into lines for processing
        lines = content.split('\n')
        cleaned_lines = []
        
        # Process each line
        for line in lines:
            if self._should_remove_line(line, stats):
                stats['removed_lines'] += 1
                stats['removed_chars'] += len(line)
                continue
            
            # Clean the line of inline boilerplate
            cleaned_line = self._clean_line(line, stats)
            if cleaned_line.strip():  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
            elif line.strip() == '':  # Preserve intentional empty lines
                cleaned_lines.append('')
        
        # Rejoin content
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Post-processing cleanup
        cleaned_content = self._post_process_content(cleaned_content, stats)
        
        # Update final stats
        stats['final_lines'] = len(cleaned_content.split('\n'))
        stats['final_chars'] = len(cleaned_content)
        stats['reduction_ratio'] = (stats['removed_chars'] / stats['original_chars']) if stats['original_chars'] > 0 else 0
        
        return cleaned_content, stats
    
    def _should_remove_line(self, line: str, stats: Dict) -> bool:
        """Determine if a line should be removed entirely."""
        line_clean = line.strip()
        
        if not line_clean:
            return False  # Keep empty lines for formatting
        
        # Check removal patterns
        for pattern in self.removal_patterns:
            if pattern.search(line):
                stats['boilerplate_matches'].append(f"Removal pattern: {line_clean[:50]}")
                return True
        
        # Check navigation patterns
        for pattern in self.navigation_patterns:
            if pattern.search(line):
                stats['boilerplate_matches'].append(f"Navigation: {line_clean[:50]}")
                return True
        
        # Remove lines that are mostly boilerplate indicators
        boilerplate_count = 0
        word_count = len(line_clean.split())
        
        for category, indicators in self.web_indicators.items():
            for indicator in indicators:
                if indicator.lower() in line_clean.lower():
                    boilerplate_count += 1
        
        # If more than 50% of words are boilerplate indicators, remove the line
        if word_count > 0 and (boilerplate_count / word_count) > 0.5:
            stats['boilerplate_matches'].append(f"High boilerplate ratio: {line_clean[:50]}")
            return True
        
        return False
    
    def _clean_line(self, line: str, stats: Dict) -> str:
        """Clean a line of inline boilerplate while preserving content."""
        cleaned = line
        
        # Remove specific boilerplate phrases
        for pattern in self.boilerplate_patterns:
            if pattern.search(cleaned):
                cleaned = pattern.sub('', cleaned)
                stats['boilerplate_matches'].append(f"Inline removal: {pattern.pattern}")
        
        # Clean up whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _post_process_content(self, content: str, stats: Dict) -> str:
        """Post-process the cleaned content."""
        # Remove excessive empty lines (more than 2 consecutive)
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Clean up whitespace at beginning and end
        content = content.strip()
        
        # Ensure proper spacing after headers
        content = re.sub(r'^(#+\s+.+)$\n(?!\n)', r'\1\n\n', content, flags=re.MULTILINE)
        
        return content
    
    def identify_main_content(self, content: str) -> Tuple[str, int, int]:
        """
        Identify the main content section of a web clipping.
        
        Returns:
            Tuple of (main_content, start_line, end_line)
        """
        lines = content.split('\n')
        
        # Look for content boundaries
        content_start = 0
        content_end = len(lines)
        
        # Find first substantial paragraph (likely start of main content)
        for i, line in enumerate(lines):
            if len(line.strip()) > 100 and not self._is_likely_boilerplate(line):
                content_start = i
                break
        
        # Find last substantial paragraph (likely end of main content)
        for i in range(len(lines) - 1, -1, -1):
            if len(lines[i].strip()) > 50 and not self._is_likely_boilerplate(lines[i]):
                content_end = i + 1
                break
        
        main_content = '\n'.join(lines[content_start:content_end])
        return main_content, content_start, content_end
    
    def _is_likely_boilerplate(self, line: str) -> bool:
        """Quick check if a line is likely boilerplate."""
        line_lower = line.lower()
        
        boilerplate_indicators = [
            'share', 'follow', 'subscribe', 'comment', 'login', 'register',
            'privacy', 'cookie', 'terms', 'advertisement', 'sponsored'
        ]
        
        return any(indicator in line_lower for indicator in boilerplate_indicators)
    
    def extract_article_metadata(self, content: str) -> Dict:
        """Extract article-specific metadata from content."""
        metadata = {}
        
        # Look for author information
        author_patterns = [
            re.compile(r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', re.IGNORECASE),
            re.compile(r'author:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', re.IGNORECASE),
        ]
        
        for pattern in author_patterns:
            match = pattern.search(content)
            if match:
                metadata['author'] = match.group(1)
                break
        
        # Look for publication date
        date_patterns = [
            re.compile(r'(\w+\s+\d{1,2},?\s+\d{4})', re.IGNORECASE),
            re.compile(r'(\d{1,2}\s+\w+\s+\d{4})', re.IGNORECASE),
        ]
        
        for pattern in date_patterns:
            match = pattern.search(content)
            if match:
                metadata['publication_date'] = match.group(1)
                break
        
        return metadata
    
    def is_web_clipping(self, content: str, frontmatter: Dict) -> bool:
        """Determine if content is a web clipping that needs cleaning."""
        # Check for source URL
        if frontmatter.get('source') and 'http' in str(frontmatter['source']):
            return True
        
        # Check for common web clipping indicators
        web_indicators = [
            'AddThis Sharing Buttons',
            'Share This Article',
            'Subscribe to',
            'Follow us on',
            'Click here to'
        ]
        
        content_lower = content.lower()
        indicator_count = sum(1 for indicator in web_indicators if indicator.lower() in content_lower)
        
        # If multiple web indicators present, likely a web clipping
        return indicator_count >= 2

def clean_html_like_clipping(content: str) -> str:
    """Simple function to clean web clipping content."""
    cleaner = WebClippingCleaner()
    cleaned, _ = cleaner.clean_web_clipping(content, {})
    return cleaned
