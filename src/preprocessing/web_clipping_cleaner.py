"""
Web clipping content cleaner for removing boilerplate and extracting main content.
Uses Trafilatura for advanced content extraction and enhanced cleaning patterns.
"""

import re
from typing import List, Dict, Tuple, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import BOILERPLATE_PATTERNS, WEB_BOILERPLATE_INDICATORS

# Try to import Trafilatura for advanced content extraction
try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False
    print("Warning: Trafilatura not available. Install with: pip install trafilatura")

# Try to import readability for fallback extraction
try:
    from readability import Document
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False
    print("Warning: readability-lxml not available. Install with: pip install readability-lxml")

# Try to import markdown for proper conversion
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Warning: markdown not available. Install with: pip install markdown")


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
        """Determine if content is a web clipping that needs cleaning (not just referenced content)."""
        # Use the same sophisticated logic as clean_html_like_clipping
        if frontmatter and frontmatter.get('source', '').startswith(('http://', 'https://')):
            content_lower = content.lower()
            
            # Strong indicators of web clipping (not just referenced content)
            web_scraping_indicators = [
                # HTML structure
                '<div', '<span', '<p class=', '<img', '<a href=',
                # Navigation elements
                'menu', 'navigation', 'breadcrumb', 'sidebar',
                # Social/sharing elements  
                'share this', 'follow us', 'subscribe', 'newsletter',
                # Advertisement indicators
                'advertisement', 'sponsored', 'ad server',
                # Common web boilerplate
                'cookie policy', 'privacy policy', 'terms of service',
                'all rights reserved', 'copyright',
                # Publication-specific indicators
                'most viewed', 'most read', 'related articles',
                'read more', 'continue reading'
            ]
            
            # Count indicators present in content
            indicator_count = sum(1 for indicator in web_scraping_indicators 
                                if indicator in content_lower)
            
            # Check content structure
            lines = content.split('\n')
            short_lines = sum(1 for line in lines if 0 < len(line.strip()) < 30)
            total_lines = len([line for line in lines if line.strip()])
            
            link_count = len(re.findall(r'\[([^\]]+)\]\([^)]+\)', content))
            word_count = len(content.split())
            
            # Determine if this is a web clipping based on multiple factors
            return (
                indicator_count >= 2 or  # Multiple web indicators
                (total_lines > 10 and short_lines / total_lines > 0.4) or  # Many short lines
                (word_count > 50 and link_count / word_count > 0.1)  # High link density
            )
        else:
            # No URL source - check for HTML content in body
            web_indicators = ['<div', '<span', '<p class=', 'class=', 'id=']
            return any(indicator in content.lower() for indicator in web_indicators)

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
        
        # Only append line if we're not skipping
        if not skip_section:
            cleaned_lines.append(line)
        i += 1
    
    return cleaned_lines

def is_heavily_html_structured(content: str) -> bool:
    """Check if content is heavily HTML-structured (like ESADE pages)."""
    import re
    
    # Count HTML elements
    html_tags = len(re.findall(r'<[^>]+>', content))
    total_chars = len(content)
    
    # If more than 20% of content is HTML tags, it's heavily structured
    if html_tags > 0 and (html_tags * 10) / total_chars > 0.2:
        return True
    
    # Check for specific patterns that indicate heavy HTML structure
    heavy_html_patterns = [
        r'<table[^>]*>.*?</table>',
        r'<div[^>]*style="[^"]*margin:[^"]*padding:[^"]*"[^>]*>',
        r'<td[^>]*style="[^"]*margin:[^"]*padding:[^"]*"[^>]*>',
        r'<div[^>]*class="[^"]*table[^"]*"[^>]*>',  # Joplin table wrappers
        r'<tbody[^>]*>.*?</tbody>',  # Table body elements
        r'<tr[^>]*>.*?</tr>',  # Table rows
        r'<td[^>]*>.*?</td>',  # Table cells
    ]
    
    pattern_matches = 0
    for pattern in heavy_html_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        pattern_matches += len(matches)
    
    # If we find many table/div structures, it's heavily HTML
    return pattern_matches > 5
    
    # Additional check: if content has very long lines with lots of HTML attributes
    lines = content.split('\n')
    long_html_lines = 0
    for line in lines:
        if len(line) > 500 and '<' in line and '>' in line:
            # Count HTML attributes in the line
            attr_count = len(re.findall(r'\w+="[^"]*"', line))
            if attr_count > 10:  # Many attributes indicate complex HTML structure
                long_html_lines += 1
    
    # If we have many long HTML lines, it's heavily structured
    return long_html_lines > 3

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

def extract_content_with_trafilatura(content: str) -> Optional[str]:
    """Extract main content using Trafilatura (best practices approach)."""
    if not TRAFILATURA_AVAILABLE:
        return None
    
    try:
        # Convert markdown to HTML-like format for Trafilatura
        html_content = content
        
        # Extract main content
        extracted = trafilatura.extract(
            html_content,
            include_comments=False,
            include_tables=True,
            include_images=False,
            include_links=False,
            include_formatting=True,
            favor_precision=True,  # Favor precision over recall
            favor_recall=False
        )
        
        if extracted and len(extracted.strip()) > 100:
            return extracted.strip()
        
        return None
    except Exception as e:
        print(f"Trafilatura extraction failed: {e}")
        return None


def extract_content_with_readability(content: str) -> Optional[str]:
    """Extract main content using Readability (fallback approach)."""
    if not READABILITY_AVAILABLE:
        return None
    
    try:
        # Convert markdown to HTML-like format for Readability
        # This is a simple conversion - Readability works better with HTML
        html_content = content
        
        # Extract main content
        doc = Document(html_content)
        extracted = doc.summary()
        
        if extracted and len(extracted.strip()) > 100:
            # Clean up HTML tags
            extracted = re.sub(r'<[^>]+>', '', extracted)
            extracted = re.sub(r'\s+', ' ', extracted).strip()
            return extracted
        
        return None
    except Exception as e:
        print(f"Readability extraction failed: {e}")
        return None


def markdown_to_html(markdown_content: str) -> str:
    """Convert Markdown content to HTML for Trafilatura processing."""
    if not MARKDOWN_AVAILABLE:
        # Fallback: simple conversion
        html = markdown_content
        # Convert basic Markdown to HTML
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', html, flags=re.MULTILINE)
        return f'<div>{html}</div>'
    
    # Use markdown library for proper conversion
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    html = md.convert(markdown_content)
    
    # Wrap in a proper HTML structure
    return f'<html><body>{html}</body></html>'


def html_to_markdown(html_content: str) -> str:
    """Convert HTML content back to Markdown."""
    # Remove HTML tags but preserve structure
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', html_content, flags=re.DOTALL)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', text, flags=re.DOTALL)
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', text, flags=re.DOTALL)
    text = re.sub(r'<h5[^>]*>(.*?)</h5>', r'##### \1', text, flags=re.DOTALL)
    text = re.sub(r'<h6[^>]*>(.*?)</h6>', r'###### \1', text, flags=re.DOTALL)
    
    # Convert links
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)
    
    # Convert lists
    text = re.sub(r'<ul[^>]*>', '', text)
    text = re.sub(r'</ul>', '', text)
    text = re.sub(r'<ol[^>]*>', '', text)
    text = re.sub(r'</ol>', '', text)
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', text, flags=re.DOTALL)
    
    # Convert emphasis
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)
    text = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', text, flags=re.DOTALL)
    
    # Convert paragraphs
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text, flags=re.DOTALL)
    
    # Convert line breaks
    text = re.sub(r'<br[^>]*>', '\n', text)
    
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()


def extract_content_with_trafilatura_v2(markdown_content: str) -> Optional[str]:
    """Extract main content using Trafilatura with proper Markdown→HTML→Markdown conversion."""
    if not TRAFILATURA_AVAILABLE:
        return None
    
    try:
        # Step 1: Convert Markdown to HTML
        html_content = markdown_to_html(markdown_content)
        
        # Step 2: Use Trafilatura on HTML
        extracted_html = trafilatura.extract(
            html_content,
            include_comments=False,
            include_tables=True,
            include_images=False,
            include_links=True,
            include_formatting=True,
            favor_precision=True,  # Favor precision over recall
            favor_recall=False
        )
        
        if not extracted_html or len(extracted_html.strip()) < 100:
            return None
        
        # Step 3: Convert extracted HTML back to Markdown
        extracted_markdown = html_to_markdown(extracted_html)
        
        if len(extracted_markdown.strip()) > 100:
            return extracted_markdown.strip()
        
        return None
        
    except Exception as e:
        print(f"Trafilatura v2 extraction failed: {e}")
        return None


def extract_content_with_readability_v2(markdown_content: str) -> Optional[str]:
    """Extract main content using Readability with proper Markdown→HTML→Markdown conversion."""
    if not READABILITY_AVAILABLE:
        return None
    
    try:
        # Step 1: Convert Markdown to HTML
        html_content = markdown_to_html(markdown_content)
        
        # Step 2: Use Readability on HTML
        doc = Document(html_content)
        extracted_html = doc.summary()
        
        if not extracted_html or len(extracted_html.strip()) < 100:
            return None
        
        # Step 3: Convert extracted HTML back to Markdown
        extracted_markdown = html_to_markdown(extracted_html)
        
        if len(extracted_markdown.strip()) > 100:
            return extracted_markdown.strip()
        
        return None
        
    except Exception as e:
        print(f"Readability v2 extraction failed: {e}")
        return None


def apply_enhanced_cleaning(content: str) -> str:
    """Apply enhanced cleaning patterns based on investigation findings."""
    lines = content.split('\n')
    cleaned_lines = []
    
    # Enhanced patterns for better boilerplate removal
    enhanced_patterns = [
        # Navigation and menus - more comprehensive patterns
        r'^\s*#\s*[Ss]ections\s*$',
        r'^\s*#\s*[Bb]logs\s*$',
        r'^\s*#\s*[Aa]pps.*[Dd]igital.*[Ee]ditions\s*$',
        r'^\s*#\s*[Oo]ther.*[Pp]ublications\s*$',
        r'^\s*#\s*[Ff]rom.*[Tt]he.*[Ee]conomist.*[Gg]roup\s*$',
        r'^\s*#\s*[Mm]edia\s*$',
        r'^\s*#\s*[Tt]oday.*[Vv]ideo\s*$',
        r'^\s*#\s*[Cc]lassified.*[Aa]ds\s*$',
        r'^\s*#\s*[Kk]eep.*[Uu]pdated\s*$',
        
        # Dots and strange characters
        r'^\.\s*\.\s*\.\s*\.+$',
        r'^\.\s*\.\s*\.\s*\.\s*\.\s*\.\s*\.+$',
        r'^\.{10,}$',
        
        # Ad server HTML
        r'^<http://adserver\.adtech\.de/.*>$',
        r'^\[http://adserver\.adtech\.de/.*\]\(.*\)$',
        r'^<a href="http://adserver\.adtech\.de/.*".*$',
        r'^<img.*adserver\.adtech\.de.*>$',
        
        # Navigation breadcrumbs
        r'^\[.*\]\(http://.*\)\s*>\s*$',
        r'^\[.*\]\(http://.*\)\s*>\s*\[.*\]\(http://.*\)\s*>\s*$',
        
        # Empty table structures
        r'^\|\s*\|\s*\|\s*$',
        r'^\|\s*:---:\s*\|\s*:---:\s*\|\s*:---:\s*\|\s*$',
        r'^\|\s*---\s*\|\s*:---\s*\|\s*---\s*\|\s*$',
        
        # Footer contact information
        r'^\* Main Office\s*$',
        r'^\* Recharge AS\s*$',
        r'^\* Christian Kroghs gt\.\s*$',
        r'^\* NO-0186 Oslo\s*$',
        r'^\* Local Offices\s*$',
        r'^\* Publisher:\s*$',
        r'^\* Editor-in-Chief:\s*$',
        r'^\* Managing Director:\s*$',
        r'^\* Online news editor:\s*$',
        
        # Navigation menu items
        r'^\s*\*\s*\[.*[Ll]atest.*[Uu]pdates.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ll]eaders.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Bb]riefing.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Uu]nited.*[Ss]tates.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]he.*[Aa]mericas.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Aa]sia.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Cc]hina.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Mm]iddle.*[Ee]ast.*[Aa]nd.*[Aa]frica.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ee]urope.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Bb]ritain.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ii]nternational.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Bb]usiness.*[Ff]inance.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ff]inance.*[Aa]nd.*[Ee]conomics.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ss]cience.*[Aa]nd.*[Tt]echnology.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Bb]ooks.*[Aa]nd.*[Aa]rts.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Oo]bituary.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ss]pecial.*[Rr]eports.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]echnology.*[Qq]uarterly.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Dd]ebates.*\]\([^)]+\)\s*$',
        
        # Blog navigation
        r'^\s*\*\s*\[.*[Bb]agehot.*[Nn]otebook.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Bb]artleby.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Bb]uttonwood.*[Nn]otebook.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Dd]emocracy.*[Ii]n.*[Aa]merica.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ee]rasmus.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ff]ree.*[Ee]xchange.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Gg]ame.*[Tt]heory.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Gg]raphic.*[Dd]etail.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Gg]ulliver.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Kk]affeeklatsch.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Pp]rospero.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]he.*[Ee]conomist.*[Ee]xplains.*\]\([^)]+\)\s*$',
        
        # Apps and digital editions
        r'^\s*\*\s*\[.*[Tt]he.*[Ee]conomist.*[Aa]pps.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ee]spresso.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Gg]lobal.*[Bb]usiness.*[Rr]eview.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ww]orld.*[Ii]n.*[Ff]igures.*\]\([^)]+\)\s*$',
        
        # Other publications
        r'^\s*\*\s*\[.*1843.*[Mm]agazine.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]he.*[Ww]orld.*[Ii]n.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]he.*[Ww]orld.*[Ii]f.*\]\([^)]+\)\s*$',
        
        # From The Economist Group
        r'^\s*\*\s*\[.*[Ee]vents.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Oo]nline.*[Gg]MAT.*[Pp]rep.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Oo]nline.*[Gg]RE.*[Pp]rep.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ee]xecutive.*[Ee]ducation.*[Nn]avigator.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ww]hich.*[Mm]BA.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Jj]obs.*[Bb]oard.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ll]earning.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]he.*[Ee]conomist.*[Ss]tore.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]he.*[Ee]conomist.*[Ii]ntelligence.*[Uu]nit.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]he.*[Ee]conomist.*[Cc]orporate.*[Nn]etwork.*\]\([^)]+\)\s*$',
        
        # Media
        r'^\s*\*\s*\[.*[Aa]udio.*[Ee]dition.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ee]conomist.*[Ff]ilms.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ee]conomist.*[Rr]adio.*\]\([^)]+\)\s*$',
        
        # Login and subscription forms
        r'^\s*[Ll]og\s+in\s+or\s+sign\s+up.*$',
        r'^\s*[Ee]-mail\s+address\s*$',
        r'^\s*[Pp]assword\s*$',
        r'^\s*[Kk]eep\s+me\s+logged\s+in\s*$',
        r'^\s*\[.*[Ff]orgot\s+password.*\]\([^)]+\)\s*$',
        r'^\s*[Nn]ew\s+to.*[Tt]he.*[Ee]conomist.*\?.*$',
        r'^\s*\[.*[Ss]ign\s+up\s+now.*\]\([^)]+\)\s*$',
        r'^\s*\[.*[Aa]ctivate.*[Dd]igital.*[Ss]ubscription.*\]\([^)]+\)\s*$',
        r'^\s*\[.*[Mm]anage.*[Ss]ubscription.*\]\([^)]+\)\s*$',
        r'^\s*\[.*[Rr]enew.*[Ss]ubscription.*\]\([^)]+\)\s*$',
        
        # Topics and navigation
        r'^\s*\[.*[Tt]opics.*\]\([^)]+\)\s*$',
        
        # Current edition and more links
        r'^\s*\[.*[Cc]urrent\s+edition.*\]\([^)]+\)\s*$',
        r'^\s*\[.*[Mm]ore.*\]\([^)]+\)\s*$',
        
        # Latest Stories section
        r'^\s*#\s*[Ll]atest.*[Ss]tories\s*$',
        r'^\s*\*\s*###\s*\[.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Gg]ulliver.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Dd]emocracy.*[Ii]n.*[Aa]merica.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Pp]rospero.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Oo]pen.*[Ff]uture.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ee]rasmus.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*[0-9]+\s+days?\s+ago\s*$',
        r'^\s*\[.*[Ss]ee\s+more.*\]\([^)]+\)\s*$',
        
        # Newsletter and subscription
        r'^\s*\*\*[Gg]et\s+our\s+daily\s+newsletter\*\*\s*$',
        r'^\s*[Uu]pgrade\s+your\s+inbox.*$',
        
        # Footer content
        r'^\s*##\s*[Cc]lassified.*[Aa]ds\s*$',
        r'^\s*\*\s*\[.*[Hh]elp.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Oo]pen.*[Ff]uture.*\]\([^)]+\)\s*$',
        r'^\s*###\s*[Kk]eep.*[Uu]pdated\s*$',
        r'^\s*\*\s*\[.*[Ss]ubscribe.*[Tt]he.*[Ee]conomist.*[Nn]ewsletters.*\]\([^)]+\)\s*$',
        r'^\s*\*\*[Ss]ign\s+up\s+to\s+get\s+more\s+from.*[Tt]he.*[Ee]conomist.*\*\*\s*$',
        r'^\s*[Gg]et\s+3\s+free\s+articles.*$',
        r'^\s*\*\s*\[.*[Aa]dvertise.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Rr]eprints.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Cc]areers.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Mm]edia.*[Cc]entre.*\]\([^)]+\)\s*$',
        r'^\s*[Pp]ublished\s+since.*1843.*$',
        r'^\s*[Aa] severe\s+contest.*$',
        
        # Legal and policy
        r'^\s*\*\s*\[.*[Tt]erms.*[Oo]f.*[Uu]se.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Pp]rivacy.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Cc]ookie.*[Pp]olicy.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*[Mm]anage\s+[Cc]ookies\s*$',
        r'^\s*\*\s*\[.*[Aa]ccessibility.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Mm]odern.*[Ss]lavery.*[Ss]tatement.*\]\([^)]+\)\s*$',
        r'^\s*[Oo]ur\s+site\s+uses\s+cookies.*$',
        r'^\s*[Tt]o\s+receive\s+the\s+best\s+experience.*$',
        r'^\s*[Vv]iew\s+our.*[Cc]ookie\s+policy.*$',
        r'^\s*[Mm]anage\s+your\s+cookies.*$',
        r'^\s*[Aa]llow\s*$',
        
        # Empty or separator lines
        r'^\s*$',
        r'^\s*\.\s*$',
        r'^\s*[|\-\s]+\s*$',
        r'^\s*\*\s*\*\s*\*\s*$',
    ]
    
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in enhanced_patterns]
    
    for line in lines:
        line_stripped = line.strip()
        
        # Skip empty lines
        if not line_stripped:
            cleaned_lines.append(line)
            continue
        
        # Check against enhanced patterns
        should_remove = False
        for pattern in compiled_patterns:
            if pattern.match(line_stripped):
                should_remove = True
                break
        
        # Additional checks for link-heavy lines
        if not should_remove:
            link_count = len(re.findall(r'\[([^\]]+)\]\([^)]+\)', line_stripped))
            word_count = len(line_stripped.split())
            if word_count > 0 and link_count / word_count > 0.7:  # More than 70% links
                nav_words = ['home', 'about', 'contact', 'search', 'menu', 'navigation', 'sections', 'most', 'read', 'viewed', 'commented', 'share', 'follow', 'subscribe', 'latest', 'leaders', 'briefing', 'united', 'states', 'americas', 'asia', 'china', 'europe', 'britain', 'international', 'business', 'finance', 'economics', 'science', 'technology', 'books', 'arts', 'obituary', 'special', 'reports', 'technology', 'quarterly', 'debates']
                nav_count = sum(1 for word in nav_words if word.lower() in line_stripped.lower())
                if nav_count > 0:
                    should_remove = True
        
        # Keep the line if it doesn't match removal patterns
        if not should_remove:
            cleaned_lines.append(line)
    
    # Join and clean up
    cleaned_content = '\n'.join(cleaned_lines)
    cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
    cleaned_content = cleaned_content.strip()
    
    return cleaned_content


def clean_html_like_clipping(content: str, frontmatter: Dict = None) -> str:
    """Enhanced web clipping cleaner using proper Trafilatura integration."""
    import re
    
    # Check if this is a web clipping (not just a note with URL source)
    is_web_clipping = False
    
    if frontmatter and frontmatter.get('source', '').startswith(('http://', 'https://')):
        # URL source exists, but check if content shows signs of web scraping
        content_lower = content.lower()
        
        # Strong indicators of web clipping (not just referenced content)
        web_scraping_indicators = [
            # HTML structure
            '<div', '<span', '<p class=', '<img', '<a href=',
            # Navigation elements
            'menu', 'navigation', 'breadcrumb', 'sidebar',
            # Social/sharing elements  
            'share this', 'follow us', 'subscribe', 'newsletter',
            # Advertisement indicators
            'advertisement', 'sponsored', 'ad server',
            # Common web boilerplate
            'cookie policy', 'privacy policy', 'terms of service',
            'all rights reserved', 'copyright',
            # Publication-specific indicators
            'most viewed', 'most read', 'related articles',
            'read more', 'continue reading'
        ]
        
        # Count indicators present in content
        indicator_count = sum(1 for indicator in web_scraping_indicators 
                            if indicator in content_lower)
        
        # Also check content structure - web clippings often have:
        # - Many short lines (navigation/menu items)
        # - High ratio of links to text
        lines = content.split('\n')
        short_lines = sum(1 for line in lines if 0 < len(line.strip()) < 30)
        total_lines = len([line for line in lines if line.strip()])
        
        link_count = len(re.findall(r'\[([^\]]+)\]\([^)]+\)', content))
        word_count = len(content.split())
        
        # Determine if this is a web clipping based on multiple factors
        is_web_clipping = (
            indicator_count >= 2 or  # Multiple web indicators
            (total_lines > 10 and short_lines / total_lines > 0.4) or  # Many short lines
            (word_count > 50 and link_count / word_count > 0.1)  # High link density
        )
    else:
        # No URL source - check for HTML content in body
        web_indicators = ['<div', '<span', '<p class=', 'class=', 'id=']
        is_web_clipping = any(indicator in content.lower() for indicator in web_indicators)
    
    if not is_web_clipping:
        return content
    
    # Try Trafilatura first (best results) - now with proper Markdown→HTML→Markdown conversion
    extracted = extract_content_with_trafilatura_v2(content)
    if extracted:
        return extracted
    
    # Fallback to Readability
    extracted = extract_content_with_readability_v2(content)
    if extracted:
        return extracted
    
    # If both fail, fall back to enhanced cleaning patterns
    if is_heavily_html_structured(content):
        return clean_heavily_html_structured(content, frontmatter)
    
    # Convert HTML tables to Markdown first
    content = convert_html_tables_to_markdown(content)
    
    # Apply enhanced cleaning patterns
    cleaned_content = apply_enhanced_cleaning(content)
    
    return cleaned_content
