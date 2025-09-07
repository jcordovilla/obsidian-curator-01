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
        Clean web clipping content by removing boilerplate using conservative approach.
        
        Args:
            content: Raw content string
            frontmatter: Metadata dictionary
            
        Returns:
            Tuple of (cleaned_content, cleaning_stats)
        """
        # Use the conservative cleaning function
        cleaned_content = clean_html_like_clipping(content, frontmatter)
        
        # Calculate stats
        original_lines = len(content.split('\n'))
        final_lines = len(cleaned_content.split('\n'))
        removed_lines = original_lines - final_lines
        removed_chars = len(content) - len(cleaned_content)
        
        stats = {
            'original_lines': original_lines,
            'original_chars': len(content),
            'removed_lines': removed_lines,
            'removed_chars': removed_chars,
            'final_lines': final_lines,
            'final_chars': len(cleaned_content),
            'reduction_ratio': removed_chars / len(content) if len(content) > 0 else 0,
            'boilerplate_matches': [],
            'preserved_elements': []
        }
        
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

def convert_html_tables_to_markdown(content: str) -> str:
    """Convert HTML tables to Markdown tables."""
    import re
    
    # Find HTML tables wrapped in divs (like Joplin exports)
    table_pattern = r'<div[^>]*class="[^"]*table[^"]*"[^>]*><table[^>]*>(.*?)</table></div>'
    
    def convert_table(match):
        table_html = match.group(1)
        
        # Extract table rows
        row_pattern = r'<tr[^>]*>(.*?)</tr>'
        rows = re.findall(row_pattern, table_html, re.DOTALL)
        
        if not rows:
            return match.group(0)  # Return original if no rows found
        
        markdown_rows = []
        
        for i, row in enumerate(rows):
            # Extract cells
            cell_pattern = r'<t[dh][^>]*>(.*?)</t[dh]>'
            cells = re.findall(cell_pattern, row, re.DOTALL)
            
            if not cells:
                continue
                
            # Clean cell content
            cleaned_cells = []
            for cell in cells:
                # Convert <ul><li> to markdown lists
                cell = re.sub(r'<ul[^>]*>', '', cell)
                cell = re.sub(r'</ul>', '', cell)
                cell = re.sub(r'<li[^>]*>', '• ', cell)
                cell = re.sub(r'</li>', '\n', cell)
                
                # Convert <br> to line breaks
                cell = re.sub(r'<br[^>]*>', '\n', cell)
                
                # Remove other HTML tags but preserve text
                cell_text = re.sub(r'<[^>]+>', '', cell)
                
                # Decode HTML entities
                cell_text = cell_text.replace('&amp;', '&')
                cell_text = cell_text.replace('&nbsp;', ' ')
                cell_text = cell_text.replace('&lt;', '<')
                cell_text = cell_text.replace('&gt;', '>')
                
                # Clean up whitespace and preserve line breaks
                lines = [line.strip() for line in cell_text.split('\n') if line.strip()]
                cell_text = '\n'.join(lines)
                
                cleaned_cells.append(cell_text)
            
            if cleaned_cells:
                # Create markdown row
                markdown_row = '| ' + ' | '.join(cleaned_cells) + ' |'
                markdown_rows.append(markdown_row)
                
                # Add separator row after header (first row)
                if i == 0:
                    separator = '| ' + ' | '.join(['---'] * len(cleaned_cells)) + ' |'
                    markdown_rows.append(separator)
        
        if markdown_rows:
            return '\n'.join(markdown_rows)
        else:
            return match.group(0)  # Return original if conversion failed
    
    # Apply table conversion
    content = re.sub(table_pattern, convert_table, content, flags=re.DOTALL | re.IGNORECASE)
    
    return content

def remove_boilerplate_sections(content_lines: List[str]) -> List[str]:
    """Remove entire sections that are clearly boilerplate from web clippings."""
    import re
    
    cleaned_lines = []
    skip_section = False
    i = 0
    
    while i < len(content_lines):
        line = content_lines[i]
        line_lower = line.lower().strip()
        
        # Check if this line starts a boilerplate section
        if any(pattern in line_lower for pattern in [
            'more from the economist',
            'most viewed',
            'most commented', 
            'advertisement',
            'follow the economist',
            'from our networks',
            'stock exchange',
            'top gainer',
            'top loser',
            'job listings',
            'classified ads',
            'partners:',
            'copyright',
            'all rights reserved',
            'sharethis',
            'read also:',
            'related articles',
            'latest updates',
            'most viewed',
            'most commented',
            'social media tools',
            'more sharing',
            'sharing services',
            'share services',
            'post your say',
            'selected comments',
            'comments',
            'follow',
            'post comment',
            'powered by',
            'look for more jobs',
            'latest travelog',
            'top travelog',
            'share your travel',
            'find more about',
            'news',
            'views',
            'life',
            'services',
            'pt.'
        ]):
            # Skip this section until we find a clear end or another main heading
            skip_section = True
            i += 1
            continue
        
        # Check if we should stop skipping (new main heading or clear content)
        if skip_section:
            if (line.startswith('# ') or 
                line.startswith('## ') or
                (line.strip() and not line.startswith('*') and not line.startswith('![') and 
                 not any(word in line_lower for word in ['advertisement', 'follow', 'share', 'subscribe', 'copyright']))):
                skip_section = False
            else:
                i += 1
                continue
        
        cleaned_lines.append(line)
        i += 1
    
    return cleaned_lines

def is_heavily_html_structured(content: str) -> bool:
    """Check if content is heavily HTML-structured (like ESADE pages)."""
    import re
    
    # Count HTML elements
    html_tags = len(re.findall(r'<[^>]+>', content))
    total_chars = len(content)
    
    # If more than 30% of content is HTML tags, it's heavily structured
    if html_tags > 0 and (html_tags * 10) / total_chars > 0.3:
        return True
    
    # Check for specific patterns that indicate heavy HTML structure
    heavy_html_patterns = [
        r'<table[^>]*>.*?</table>',
        r'<div[^>]*style="[^"]*margin:[^"]*padding:[^"]*"[^>]*>',
        r'<td[^>]*style="[^"]*margin:[^"]*padding:[^"]*"[^>]*>',
    ]
    
    pattern_matches = 0
    for pattern in heavy_html_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        pattern_matches += len(matches)
    
    # If we find many table/div structures, it's heavily HTML
    return pattern_matches > 10

def clean_heavily_html_structured(content: str, frontmatter: Dict = None) -> str:
    """Clean heavily HTML-structured content by extracting only meaningful text."""
    import re
    
    # Extract frontmatter if present
    frontmatter_text = ""
    content_start = 0
    
    if content.startswith('---'):
        end_marker = content.find('---', 3)
        if end_marker != -1:
            frontmatter_text = content[:end_marker + 3]
            content_start = end_marker + 3
    
    # Remove all HTML tags and attributes
    cleaned = re.sub(r'<[^>]+>', '', content[content_start:])
    
    # Decode HTML entities
    cleaned = cleaned.replace('&amp;', '&')
    cleaned = cleaned.replace('&nbsp;', ' ')
    cleaned = cleaned.replace('&lt;', '<')
    cleaned = cleaned.replace('&gt;', '>')
    cleaned = cleaned.replace('&quot;', '"')
    cleaned = cleaned.replace('&#39;', "'")
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    
    # Remove lines that are mostly whitespace or very short
    lines = cleaned.split('\n')
    meaningful_lines = []
    
    for line in lines:
        line = line.strip()
        if len(line) > 10 and not re.match(r'^[|\-\s]+$', line):
            meaningful_lines.append(line)
    
    # If we have meaningful content, return it with frontmatter
    if meaningful_lines:
        result = frontmatter_text + '\n\n' + '\n'.join(meaningful_lines)
        return result
    else:
        # If no meaningful content found, return a minimal note
        return frontmatter_text + '\n\n# Content could not be extracted\n\nThis web clipping contained mostly HTML structure with little readable content.'

def clean_html_like_clipping(content: str, frontmatter: Dict = None) -> str:
    """Conservative web clipping cleaner that removes obvious boilerplate while preserving main content."""
    import re
    
    # Check if this is heavily HTML-structured content
    if is_heavily_html_structured(content):
        return clean_heavily_html_structured(content, frontmatter)
    
    # First, convert HTML tables to Markdown tables
    content = convert_html_tables_to_markdown(content)
    
    # Split into lines for processing
    lines = content.split('\n')
    cleaned_lines = []
    
    # Skip frontmatter
    in_frontmatter = False
    frontmatter_end = 0
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                cleaned_lines.append(line)
            else:
                frontmatter_end = i
                cleaned_lines.append(line)
                break
        elif in_frontmatter:
            cleaned_lines.append(line)
    
    # Process the rest of the content
    content_lines = lines[frontmatter_end + 1:]
    
    # Check if this is a web clipping (has source URL in frontmatter)
    is_web_clipping = False
    if frontmatter and frontmatter.get('source') and 'http' in str(frontmatter['source']):
        is_web_clipping = True
    elif frontmatter_end > 0:
        # Fallback to manual parsing if frontmatter not provided
        frontmatter_text = '\n'.join(lines[:frontmatter_end+1])
        if 'source:' in frontmatter_text and 'http' in frontmatter_text:
            is_web_clipping = True
    
    # For web clippings, remove entire boilerplate sections
    if is_web_clipping:
        content_lines = remove_boilerplate_sections(content_lines)
    
    # Conservative patterns to remove - only very obvious boilerplate
    conservative_patterns = [
        # Social media sharing buttons
        r'^\s*\*\s*\[.*[Tt]witter.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ff]acebook.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ll]inkedin.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ww]hatsapp.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ss]hare.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ff]ollow.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ss]ubscribe.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]weet.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ll]ike.*\]\(http[^)]+\)\s*$',
        
        # Navigation menu items - more comprehensive patterns
        r'^\s*\*\s*\[.*[Mm]enu.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Hh]ome.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Bb]io.*[Hh]ome.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Cc]ertifications.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Rr]eferences.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ee]ndorsements.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ss]ecurity.*[Aa]rticles.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Pp]rojects.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Pp]rofessional.*[Dd]evelopment.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ii]nfo[Ss]ec.*[Tt]oolkit.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ff]avorite.*[Qq]uotes.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Bb]ataan.*[Mm]emorial.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Uu][Ss].*[Aa]ir.*[Ff]orce.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]omb.*[Oo]f.*[Uu]nknowns.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Cc]asual.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Bb]ataan.*[Mm]arch.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ww]ounded.*[Ww]arriors.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Mm]otorcycle.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Yy]ou[Tt]ube.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ss]ite.*[Mm]ap.*\]\(http[^)]+\)\s*$',
        
        # General navigation patterns
        r'^\s*\*\s*\[.*[Aa]bout.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Cc]ontact.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ss]earch.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Nn]avigation.*\]\(http[^)]+\)\s*$',
        
        # Accessibility and skip links
        r'^\s*\[.*[Aa]ccessibility.*\]\(http[^)]+\)\s*$',
        r'^\s*\[.*[Ss]kip.*\]\(http[^)]+\)\s*$',
        
        # Legal and policy links
        r'^\s*\*\s*\[.*[Pp]rivacy.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Cc]ookie.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]erms.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Cc]opyright.*\]\(http[^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ll]egal.*\]\(http[^)]+\)\s*$',
        
        # Empty or minimal content
        r'^\s*\.\s*$',
        r'^\s*[\|\-\s]+\s*$',
        r'^\s*$',
        
        # Very specific web boilerplate phrases
        r'^\s*[Cc]omments have not been enabled.*',
        r'^\s*[Ff]ollow the topics mentioned.*',
        r'^\s*[Ff]ollow the authors.*',
        r'^\s*[Tt]ake a tour.*',
        r'^\s*[Ww]elcome to the New.*',
        
        # Advertisement and promotional content
        r'^\s*[Aa]dvertisement.*',
        r'^\s*[Ss]ponsored.*',
        r'^\s*[Pp]romoted.*',
        r'^\s*[Aa]d\s*$',
        
        # Social media and sharing
        r'^\s*[Ss]hare.*',
        r'^\s*[Ff]ollow.*',
        r'^\s*[Ff]ollow [Uu]s.*',
        r'^\s*[Ll]ike.*',
        r'^\s*[Tt]weet.*',
        r'^\s*[Ss]ubscribe.*',
        r'^\s*[Mm]y [Ss]ubscription.*',
        
        # Navigation and menus
        r'^\s*\*?\s*\[.*[Mm]enu.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Hh]ome.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Bb]usiness.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Nn]ational.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Ww]orld.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Ss]ports.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Ll]ife.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Vv]iews.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Ee]ditor.*[Cc]hoice.*\]\(http[^)]+\)\s*$',
        
        # Footer and copyright content
        r'^\s*[Cc]opyright.*',
        r'^\s*©.*',
        r'^\s*[Aa]ll rights reserved.*',
        r'^\s*[Pp]artners?:.*',
        r'^\s*[Ff]rom [Oo]ur [Nn]etworks.*',
        r'^\s*[Mm]ost [Vv]iewed.*',
        r'^\s*[Mm]ost [Cc]ommented.*',
        r'^\s*[Tt]op [Gg]ainer.*',
        r'^\s*[Tt]op [Ll]oser.*',
        
        # Stock market data and tables
        r'^\s*[A-Z]{3,4}\s+.*\s+\d+.*\s*[+-]?\d+\.?\d*%?\s*$',
        r'^\s*[Pp]rice\s*$',
        r'^\s*%?\s*[Cc]hange\s*$',
        r'^\s*[Ss]tock [Ee]xchange.*',
        
        # Job listings and classifieds
        r'^\s*[Jj]ob.*',
        r'^\s*[Cc]areer.*',
        r'^\s*[Cc]lassified.*',
        r'^\s*[Ll]ook for more jobs.*',
        
        # Related articles and recommendations
        r'^\s*[Rr]ead also:.*',
        r'^\s*[Rr]elated.*',
        r'^\s*[Mm]ore from.*',
        r'^\s*[Ll]atest.*',
        r'^\s*[Rr]ecommended.*',
        r'^\s*[Vv]iew tips.*',
        r'^\s*[Gg]ive feedback.*',
        r'^\s*[Ss]upport.*',
        r'^\s*[Ll]egal & Privacy.*',
        r'^\s*[Ss]ervices.*',
        
        # Social media and sharing sections
        r'^\s*#\s*[Ss]ocial [Mm]edia.*',
        r'^\s*[Mm]ore [Ss]haring.*',
        r'^\s*[Ss]hare.*[Ss]ervices.*',
        r'^\s*[Ss]haring [Tt]ools.*',
        
        # Header navigation and logos
        r'^\s*!\[\[.*\]\].*\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Hh]eadlines.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Aa]rchipelago.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Jj]akarta.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Pp]hotos.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Vv]ideos.*\]\(http[^)]+\)\s*$',
        r'^\s*\*?\s*\[.*[Oo]utlook.*\]\(http[^)]+\)\s*$',
        
        # Footer sections
        r'^\s*##\s*[Pp]ost [Yy]our [Ss]ay.*',
        r'^\s*[Ss]elected comments.*',
        r'^\s*\d+\s+comments.*',
        r'^\s*\+\s*[Ff]ollow.*',
        r'^\s*[Pp]ost comment as.*',
        r'^\s*\[Powered by.*\]\(http[^)]+\)\s*$',
        
        # Related articles and news sections
        r'^\s*\*\s*\d+\s*$',
        r'^\s*\*\s*\[.*\]\(http[^)]+\)\s*$',
        r'^\s*[Ll]ook for more jobs.*',
        r'^\s*\[Look for more jobs.*\]\(http[^)]+\)\s*$',
        
        # Travel and entertainment sections
        r'^\s*[Ll]atest TRAVELOG.*',
        r'^\s*[Tt]op TRAVELOG.*',
        r'^\s*[Ss]hare your travel experience.*',
        r'^\s*[Ff]ind more about your.*',
        
        # Footer navigation
        r'^\s*####\s*[Nn]ews.*',
        r'^\s*####\s*[Vv]iews.*',
        r'^\s*####\s*[Ll]ife.*',
        r'^\s*####\s*[Ss]ervices.*',
        r'^\s*PT\.\s+.*',
        
        # Duplicate URLs and tracking parameters
        r'^<http[^>]*utm_[^>]*>$',
        r'^<http[^>]*\?utm_[^>]*>$',
        r'^\s*<http[^>]*#><http[^>]*#><http[^>]*#>\s*$',
        
        # Social media icon links
        r'^\s*\*\s*\[\[#\|.*\]\]\s*$',
        r'^\s*\*\s*\[\[#\|!\[.*\]\(http[^)]+\)\]\]\s*$',
        
        # Section separators and empty content
        r'^\s*###\s*$',
        r'^\s*---+\s*$',
        r'^\s*\*\*\*\s*$',
        r'^\s*[Tt]ools.*',
        r'^\s*[Mm]ore from the FT Group.*',
        r'^\s*[Mm]arkets data delayed.*',
        r'^\s*[Tt]he Financial Times.*',
        r'^\s*[Ii]nternational Edition.*',
        r'^\s*[Ss]earch the FT.*',
        r'^\s*[Ss]witch to UK Edition.*',
        r'^\s*[Tt]op sections.*',
        r'^\s*FT recommends.*',
        
        # Related articles and recommendations
        r'^\s*##\s*\[.*\]\(https://www\.ft\.com/content/[^)]+\)\s*Premium\s*$',
        r'^\s*##\s*\[.*\]\(https://www\.ft\.com/content/[^)]+\)\s*$',
        r'^\s*##\s*\[.*\]\(http[^)]+\)\s*Premium\s*$',
        r'^\s*##\s*\[.*\]\(http[^)]+\)\s*$',
        r'^\s*[A-Za-z].*[Ss]urvey finds.*',
        r'^\s*[A-Za-z].*[Ee]xpected to fuel.*',
        r'^\s*[A-Za-z].*[Ss]hould support.*',
        r'^\s*[A-Za-z].*[Tt]arget.*[Uu]nlikely.*',
        r'^\s*[A-Za-z].*[Oo]ptimism.*[Qq]uarter.*',
        r'^\s*[A-Za-z].*[Gg]rowth.*[Rr]ecover.*',
        r'^\s*[A-Za-z].*[Ss]tability.*[Pp]olicy.*',
        r'^\s*[A-Za-z].*[Ll]osing.*[Ii]nvestors.*',
        r'^\s*[A-Za-z].*[Bb]oost.*[Ff]iscal.*',
        
        # FT-specific navigation and footer
        r'^\s*##\s*myFT\s*$',
        r'^\s*###\s*[Ww]elcome to the New.*',
        r'^\s*###\s*[Ss]upport\s*$',
        r'^\s*###\s*[Ll]egal & Privacy\s*$',
        r'^\s*\*\s*FT recommends\s*$',
        r'^\s*None\s*$',
        r'^\s*<https://www\.ft\.com/content/[^>]+>\s*$',
        
        # Author links and bylines
        r'^\s*EM Squared\s*\[.*\]\(https://www\.ft\.com/stream/authorsId/[^)]+\)\s*$',
        r'^\s*[A-Za-z]+\s*[A-Za-z]+\s*\[.*\]\(https://www\.ft\.com/stream/authorsId/[^)]+\)\s*$',
    ]
    
    # Compile patterns for efficiency
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in conservative_patterns]
    
    # Process each line
    for line in content_lines:
        line_stripped = line.strip()
        
        # Skip empty lines
        if not line_stripped:
            cleaned_lines.append(line)  # Keep empty lines for formatting
            continue
        
        # For non-web clippings, be very conservative
        if not is_web_clipping:
            # Only remove obvious separator lines
            should_remove = False
            obvious_boilerplate = [
                r'^\s*\|.*\|\s*$',  # Table rows with just separators
                r'^\s*\.\s*$',  # Just a dot
                r'^\s*[|\-\s]+\s*$',  # Separator lines
            ]
            for pattern in obvious_boilerplate:
                if re.match(pattern, line_stripped):
                    should_remove = True
                    break
            
            # Keep everything else for non-web clippings
            if not should_remove:
                cleaned_lines.append(line)
        else:
            # For web clippings, use conservative cleaning
            should_remove = False
            for pattern in compiled_patterns:
                if pattern.match(line_stripped):
                    should_remove = True
                    break
            
            # Additional conservative checks
            if not should_remove:
                # Only remove lines that are clearly navigation (mostly links with nav words)
                link_count = len(re.findall(r'\[([^\]]+)\]\([^)]+\)', line_stripped))
                word_count = len(line_stripped.split())
                if word_count > 0 and link_count / word_count > 0.7:  # More than 70% links
                    # Check if it contains navigation words
                    nav_words = ['home', 'about', 'contact', 'search', 'menu', 'navigation', 'sections', 'most', 'read', 'viewed', 'commented', 'share', 'follow', 'subscribe']
                    nav_count = sum(1 for word in nav_words if word.lower() in line_stripped.lower())
                    if nav_count > 0:
                        should_remove = True
            
            # Keep the line if it doesn't match removal patterns
            if not should_remove:
                cleaned_lines.append(line)
    
    # Join the cleaned content
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Post-process to remove excessive whitespace
    cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
    cleaned_content = cleaned_content.strip()
    
    return cleaned_content
