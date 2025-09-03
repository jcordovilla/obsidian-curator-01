"""
Metadata standardization module for Obsidian notes.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class MetadataStandardizer:
    """Standardizes metadata across Obsidian notes."""
    
    def __init__(self):
        self.required_fields = ['date created', 'date modified', 'language', 'title']
        self.optional_fields = ['source', 'tags']
        self.date_patterns = {
            'evernote_full': r'(\w+), (\w+) (\d+)\w+ (\d{4}), (\d+):(\d+):(\d+) (\w+)',
            'iso_date': r'(\d{4}-\d{2}-\d{2})',
            'iso_datetime': r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
        }
    
    def standardize_metadata(self, frontmatter: Dict, filename: str = '') -> Dict:
        """
        Standardize metadata fields according to specifications.
        
        Args:
            frontmatter: Original metadata dictionary
            filename: Filename for title fallback
            
        Returns:
            Standardized metadata dictionary
        """
        standardized = {}
        
        # Standardize required fields
        standardized['title'] = self._standardize_title(frontmatter, filename)
        standardized['date created'] = self._standardize_date(frontmatter.get('date created'))
        standardized['date modified'] = self._standardize_date(frontmatter.get('date modified'))
        standardized['language'] = self._standardize_language(frontmatter.get('language', 'en'))
        
        # Handle optional fields
        if 'source' in frontmatter and frontmatter['source']:
            standardized['source'] = self._standardize_source(frontmatter['source'])
        
        if 'tags' in frontmatter and frontmatter['tags']:
            standardized['tags'] = self._standardize_tags(frontmatter['tags'])
        
        # Preserve any custom fields not in our standard set
        for key, value in frontmatter.items():
            if key not in self.required_fields + self.optional_fields and value:
                standardized[key] = value
        
        return standardized
    
    def _standardize_title(self, frontmatter: Dict, filename: str) -> str:
        """Standardize the title field."""
        title = frontmatter.get('title', '')
        
        if not title and filename:
            # Use filename without extension as title
            title = Path(filename).stem
        
        if not title:
            title = 'Untitled Note'
        
        # Clean up title
        title = title.strip()
        title = re.sub(r'\s+', ' ', title)  # Normalize whitespace
        
        return title
    
    def _standardize_date(self, date_value: Optional[str]) -> Optional[str]:
        """Standardize date to ISO format."""
        if not date_value:
            return None
        
        date_str = str(date_value).strip()
        
        # Try to parse Evernote format
        evernote_match = re.match(self.date_patterns['evernote_full'], date_str)
        if evernote_match:
            try:
                # Parse Evernote format: "Wednesday, July 11th 2018, 12:19:06 pm"
                parts = evernote_match.groups()
                month_name = parts[1]
                day = int(re.sub(r'\D', '', parts[2]))  # Remove ordinal suffix
                year = int(parts[3])
                hour = int(parts[4])
                minute = int(parts[5])
                second = int(parts[6])
                am_pm = parts[7].lower()
                
                # Convert to 24-hour format
                if am_pm == 'pm' and hour != 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0
                
                # Convert month name to number
                month_map = {
                    'january': 1, 'february': 2, 'march': 3, 'april': 4,
                    'may': 5, 'june': 6, 'july': 7, 'august': 8,
                    'september': 9, 'october': 10, 'november': 11, 'december': 12
                }
                month = month_map.get(month_name.lower(), 1)
                
                dt = datetime(year, month, day, hour, minute, second)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
                
            except (ValueError, KeyError):
                pass
        
        # Try to parse ISO format
        iso_match = re.match(self.date_patterns['iso_datetime'], date_str)
        if iso_match:
            return iso_match.group(1)
        
        iso_date_match = re.match(self.date_patterns['iso_date'], date_str)
        if iso_date_match:
            return f"{iso_date_match.group(1)} 00:00:00"
        
        # If we can't parse it, return the original
        return date_str
    
    def _standardize_language(self, language: str) -> str:
        """Standardize language codes."""
        if not language:
            return 'en'
        
        lang = language.lower().strip()
        
        # Map common language variations
        language_map = {
            'english': 'en',
            'spanish': 'es',
            'catalan': 'ca',
            'indonesian': 'id',
            'french': 'fr',
            'german': 'de',
            'italian': 'it',
            'portuguese': 'pt'
        }
        
        return language_map.get(lang, lang)
    
    def _standardize_source(self, source: str) -> str:
        """Standardize source URLs."""
        if not source:
            return ''
        
        source = source.strip()
        
        # Ensure URL has protocol
        if source and not source.startswith(('http://', 'https://')):
            if '.' in source:  # Looks like a URL
                source = f'https://{source}'
        
        return source
    
    def _standardize_tags(self, tags) -> List[str]:
        """Standardize tags list."""
        if not tags:
            return []
        
        if isinstance(tags, str):
            # Split string tags
            tags = [t.strip() for t in tags.split(',')]
        
        if not isinstance(tags, list):
            return []
        
        # Clean and normalize tags
        clean_tags = []
        for tag in tags:
            tag = str(tag).strip()
            if tag:
                # Remove special characters, normalize case
                tag = re.sub(r'[^\w\s-]', '', tag)
                tag = tag.upper()  # Normalize to uppercase
                clean_tags.append(tag)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in clean_tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        
        return unique_tags
    
    def validate_metadata(self, metadata: Dict) -> Dict:
        """Validate standardized metadata."""
        validation = {
            'valid': True,
            'missing_required': [],
            'warnings': [],
            'errors': []
        }
        
        # Check required fields
        for field in self.required_fields:
            if field not in metadata or not metadata[field]:
                validation['missing_required'].append(field)
                validation['valid'] = False
        
        # Validate date formats
        for date_field in ['date created', 'date modified']:
            if date_field in metadata and metadata[date_field]:
                if not self._is_valid_iso_datetime(metadata[date_field]):
                    validation['warnings'].append(f'Invalid date format: {date_field}')
        
        # Validate language
        if metadata.get('language') and len(metadata['language']) > 3:
            validation['warnings'].append('Language code may be too long')
        
        return validation
    
    def _is_valid_iso_datetime(self, date_str: str) -> bool:
        """Check if date string is valid ISO format."""
        try:
            datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return True
        except ValueError:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return True
            except ValueError:
                return False
