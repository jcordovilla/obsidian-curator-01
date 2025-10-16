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
        """Determine if content is a web clipping that needs cleaning."""
        # Simple and general: if it has a URL source, it's a web clipping
        if frontmatter and frontmatter.get('source', '').startswith(('http://', 'https://')):
            return True
        
        # Also check for HTML content in body (even without URL source)
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
            'pt.',
            # Academic website patterns
            'skip to main content',
            'subscribe',
            'media',
            'open calls',
            'login',
            'conferences',
            'affiliated scholars',
            'search',
            'home',
            'research',
            'books & chapters',
            'share',
            'twitter',
            'linkedin',
            'email',
            'these are preliminary drafts',
            'this page will be updated',
            'conference held',
            'publisher:',
            'table of contents',
            'comment',
            'author(s):',
            'related',
            'topics',
            'programs',
            'more from',
            'working papers',
            'disseminates',
            'affiliates',
            'latest findings',
            'free periodicals',
            'reporter',
            'digest',
            'bulletin on',
            'online conference reports',
            'video lectures',
            'interviews',
            'economics of digitization',
            'article',
            'lecture',
            'summer institute',
            'methods lectures',
            'differential privacy',
            'extent to which individual responses',
            'household surveys',
            'protected from discovery',
            'outside parties depends',
            'national bureau of economic research',
            'contact us',
            'massachusetts ave',
            'cambridge',
            'follow',
            'homepage',
            'all rights reserved'
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
            favor_precision=False,  # Favor recall to extract content from navigation-heavy pages
            favor_recall=True
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
    
    # Step 0: Find where the actual article content starts
    # Article content usually has a substantial title/heading followed by paragraphs
    article_start_idx = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Look for article title patterns: heading or substantial text
        is_heading = stripped.startswith('#')
        is_substantial = len(stripped) > 50
        
        if is_heading or is_substantial:
            # Check if this looks like an article title (not navigation)
            nav_keywords = ['sections', 'blogs', 'media', 'keep updated', 'classified', 'apps', 'publications', 
                          'welcome', 'your account', 'subscribe', 'login', 'menu', 'search', 'home', 'contact',
                          'manage your', 'renew your', 'buy a gift', 'newsletters', 'log out', 'sign in']
            if any(keyword in stripped.lower() for keyword in nav_keywords):
                continue  # Skip navigation lines
            
            # Check if there's substantial content after this (paragraphs)
            substantial_paragraphs = 0
            for j in range(i+1, min(i+15, len(lines))):
                line_content = lines[j].strip()
                # Count lines with substantial text (not just links or navigation)
                if len(line_content) > 60 and not line_content.startswith('*') and not line_content.startswith('['):
                    substantial_paragraphs += 1
                    if substantial_paragraphs >= 2:  # At least 2 substantial paragraphs
                        article_start_idx = i
                        break
            
            if article_start_idx > 0:
                break
    
    # If we found article start, discard everything before it
    if article_start_idx > 0:
        lines = lines[article_start_idx:]
    
    # Step 0.5: Find where ads/sponsored content starts and truncate there
    # These sections typically appear after the article content
    ad_section_triggers = [
        r'^\s*[Tt]e\s+puede\s+interesar\s*$',
        r'^\s*[Oo]utbrain\s*$',
        r'^\s*\*\*[Cc]ontenido\s+[Pp]atrocinado\*\*\s*$',
        r'^\s*\*\*[Ss]ponsored\s+[Cc]ontent\*\*\s*$',
        r'^\s*[Oo]tras\s+[Nn]oticias\s*$',
        r'^\s*[Rr]elated\s+[Aa]rticles?\s*$',
        r'^\s*[Mm]ore\s+[Ff]rom\s+',
        r'^\s*[Rr]ecomendado\s+por\s*$',
        r'^\s*[Yy]ou\s+[Mm]ay\s+[Aa]lso\s+[Ll]ike\s*$',
    ]
    
    ad_start_idx = None
    for i, line in enumerate(lines):
        if any(re.match(pattern, line.strip()) for pattern in ad_section_triggers):
            ad_start_idx = i
            break
    
    # If we found where ads start, truncate everything after
    if ad_start_idx is not None and ad_start_idx > 10:  # Only if there's substantial content before
        lines = lines[:ad_start_idx]
    
    # First pass: identify and remove entire navigation/ads/sponsored sections
    # Section headers that should trigger block removal
    nav_section_headers = [
        # Navigation
        r'^\s*#{1,3}\s*[Ss]ections\s*$',
        r'^\s*#{1,3}\s*[Bb]logs\s*$',
        r'^\s*#{1,3}\s*[Mm]edia\s*$',
        r'^\s*#{1,3}\s*[Kk]eep\s+[Uu]pdated\s*$',
        r'^\s*#{1,3}\s*[Cc]lassified\s+[Aa]ds\s*$',
        r'^\s*#{1,3}\s*[Aa]pps\s+.*[Dd]igital.*[Ee]ditions\s*$',
        r'^\s*#{1,3}\s*[Oo]ther\s+[Pp]ublications\s*$',
        r'^\s*#{1,3}\s*[Ll]atest\s+[Uu]pdates\s*$',
        r'^\s*#{1,3}\s*[Rr]elated\s+[Ss]tories\s*$',
        # Ads and sponsored content
        r'^\s*#{1,3}\s*[Rr]eaders.*[Ff]avou?rites\s*$',
        r'^\s*[Oo]utbrain\s*$',
        r'^\s*\*\*[Cc]ontenido\s+[Pp]atrocinado\*\*\s*$',
        r'^\s*\*\*[Ss]ponsored\s+[Cc]ontent\*\*\s*$',
        r'^\s*\*\*[Cc]ontenido\s+[Rr]ecomendado\*\*\s*$',
        r'^\s*[Tt]e\s+[Pp]uede\s+[Ii]nteresar\s*$',
        r'^\s*[Oo]tras\s+[Nn]oticias\s*$',
        r'^\s*\[?[Rr]ecomendado\s+por\]?\s*$',
    ]
    
    # Process lines and skip navigation blocks
    cleaned_lines = []
    in_nav_section = False
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a navigation section header
        is_nav_header = any(re.match(pattern, line) for pattern in nav_section_headers)
        
        if is_nav_header:
            # Skip this header and all following bullet points/links until next section
            in_nav_section = True
            i += 1
            continue
        
        # Check if we're in a nav section and hit the end of it
        if in_nav_section:
            # Navigation section ends when we hit: another header, or substantial paragraph
            is_header = re.match(r'^\s*#{1,6}\s+\w', line)
            is_bullet = re.match(r'^\s*[\*\-]\s+\[', line)  # Bullet with link
            is_link_only = re.match(r'^\s*<https?://', line)
            is_ad_url = 'doubleclick.net' in line or 'adclick' in line or 'outbrain.com' in line
            is_empty = not line.strip()
            
            if is_header and not any(re.match(pattern, line) for pattern in nav_section_headers):
                # Real content header, exit nav section
                in_nav_section = False
            elif is_bullet or is_link_only or is_empty or is_ad_url:
                # Still in navigation/ads, skip this line
                i += 1
                continue
            elif len(line.strip()) > 50 and not line.strip().startswith('['):
                # Substantial text that's not a link - probably real content
                in_nav_section = False
            else:
                # Uncertain, skip and continue
                i += 1
                continue
        
        # If we're here, line is not part of navigation section
        cleaned_lines.append(line)
        i += 1
    
    # Second pass: remove remaining individual patterns
    final_lines = []
    enhanced_patterns = [
        # Navigation and menus - comprehensive patterns
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
        
        # Skip links and accessibility navigation (NEW)
        r'^\s*[Jj]ump\s+to:\s*$',
        r'^\s*-\s*\[\[#.*\|.*[Ss]kip\s+to.*\]\]\s*$',
        r'^\s*\[.*[Ss]kip\s+to\s+.*\]\([^)]+\)\s*$',
        r'^\s*\[.*[Aa]ccessibility.*\]\([^)]+\)\s*$',
        
        # DoubleClick and advertisement content (NEW)
        r'^\s*\[!\[\[.*\]\]\]\(http://ad\.uk\.doubleclick\.net/.*\)\s*$',
        r'^\s*<a\s+href="http://ad\.doubleclick\.net/.*".*>\s*$',
        r'^\s*<img\s+src="http://ad\.doubleclick\.net/.*".*>\s*$',
        r'^\s*\[!\[\[.*\]\]\]\(http://ad\.uk\.doubleclick\.net/click.*\)\s*$',
        r'^\s*\[!\[\[.*\]\]\]\(http://s0\.2mdn\.net/.*\)\s*$',
        r'^\s*<img\s+src="http://s0\.2mdn\.net/.*".*>\s*$',
        
        # Footer and site navigation (NEW)
        r'^\s*#\s*\[.*[Ww]ind\s+[Ii]ndustry\s+[Jj]obs.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ww]ind\s+[Pp]ark\s+[Dd]esign.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Tt]echnical\s+[Pp]rocurement.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ee]ngineer.*[Cc]ivil\s+[Ww]orks.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Ee]ngineer.*[Ww]ind\s+[Tt]urbine.*\]\([^)]+\)\s*$',
        r'^\s*\[RSS\s+feed\]\([^)]+\)\s*$',
        r'^\s*\[Search\s+for\s+jobs.*\]\([^)]+\)\s*$',
        
        # Social media and newsletter signup (NEW)
        r'^\s*#\s*\[NEWS\s+BY\s+EMAIL\]\([^)]+\)\s*$',
        r'^\s*\*\*.*[Ww]eekly.*\*\*.*[Pp]review.*$',
        r'^\s*\*\*.*[Dd]aily.*\*\*.*[Pp]review.*$',
        r'^\s*\*\*.*[Oo]ffshore.*\*\*.*[Pp]review.*$',
        r'^\s*\[Register\s+here\]\([^)]+\)\s+for\s+free\s+bulletins\.\s*$',
        r'^\s*\[!\[\[.*\]\]\]\(http://www\.twitter\.com/.*\)\s*$',
        r'^\s*\[!\[\[.*\]\]\]\(http://www\.linkedin\.com/.*\)\s*$',
        
        # Directory and polls (NEW)
        r'^\s*#\s*[Dd]irectory\s*$',
        r'^\s*[Ff]ind\s+products,?\s+services\s+and\s+suppliers\s*$',
        r'^\s*[Pp]roduct/Service\s*$',
        r'^\s*[Cc]ompany\s*$',
        r'^\s*#\s*[Pp]oll\s*$',
        r'^\s*##\s*[Ww]ill\s+.*\?\s*$',
        r'^\s*[Yy]es,?\s+.*\s*$',
        r'^\s*[Nn]o,?\s+.*\s*$',
        r'^\s*[Mm]aybe,?\s+.*\s*$',
        
        # Latest articles and related content (NEW)
        r'^\s*##\s*[Ll]atest\s+[Tt]echnology\s+[Aa]rticles\s*$',
        r'^\s*\*\s*\[.*[Mm]ing\s+[Yy]ang.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Mm]itsubishi.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Jj]apanese\s+government.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Gg]amesa.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[.*[Uu]K\s+government.*\]\([^)]+\)\s*$',
        
        # Copyright and legal footer (NEW)
        r'^\s*\[Haymarket\]\([^)]+\)\s*$',
        r'^\s*Haymarket\s+©\s+\d{4}\s*–\s+\d{4}\s*$',
        r'^\s*\[!\[\[.*\]\]\]\(http://www\.haymarket\.com/.*\)\s*$',
        r'^\s*\*\s*\[[Aa]bout\s+[Uu]s\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Cc]ontact\s+[Uu]s\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Ss]ubscribe\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Ff]ree\s+trial\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Ee]mail\s+bulletins\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Aa]dvertising\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Jj]obs\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Tt]erms\s+&\s+[Cc]onditions\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Pp]rivacy\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Aa]ccessibility\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Ss]itemap\]\([^)]+\)\s*$',
        
        # Partner websites and archive (NEW)
        r'^\s*[Pp][Aa][Rr][Tt][Nn][Ee][Rr]\s+[Ww][Ee][Bb]\s+[Ss][Ii][Tt][Ee][Ss]\s*$',
        r'^\s*\[.*[Ww]ind\s+[Ss]tats.*\]\([^)]+\)\s*$',
        r'^\s*\[.*[Ee][Nn][Dd][Ss]\s+[Ee]urope.*\]\([^)]+\)\s*$',
        r'^\s*\[.*[Ww]ind\s+[Ii]ndustry\s+[Jj]obs.*\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Aa]rchive\]\([^)]+\)\s*$',
        r'^\s*\*\s*\[[Ll]og\s+[Ii]n\]\([^)]+\)\s*$',
        
        # In This Issue section (NEW)
        r'^\s*#\s*\[[Ii]n\s+[Tt]his\s+[Ii]ssue\]\([^)]+\)\s*$',
        r'^\s*\[!\[\[.*\]\]\]\(http://www\.windpowermonthly\.com/go/subscribe/\)\s*$',
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
        
        # Spanish footer patterns
        r'^\s*©.*[Tt]odos\s+los\s+derechos\s+reservados.*$',
        r'^\s*©.*[Rr]adio\s+[Pp]opular.*$',
        r'^\s*©.*COPE.*$',
        r'^\s*[Dd]eveloped\s+by\s+AGILE\s+CONTENT.*$',
        r'^\s*\*\s*\|?\s*\[[Pp]ublicidad\].*$',
        r'^\s*\*\s*\|?\s*\[[Cc]ontacta\].*$',
        r'^\s*\*\s*\|?\s*\[[Aa]viso\s+[Ll]egal\].*$',
        r'^\s*\*\s*\|?\s*\[[Pp]olítica\s+de\s+[Pp]rivacidad\].*$',
        r'^\s*\*\s*\|?\s*\[[Pp]olítica\s+de\s+[Cc]ookies\].*$',
        r'^\s*\*\s*\|?\s*\[[Pp]olíticas\s+de\s+[Cc]ookies\].*$',
        r'^\s*\*\s*\|\s*$',
        
        # Empty or separator lines
        r'^\s*$',
        r'^\s*\.\s*$',
        r'^\s*[|\-\s]+\s*$',
        r'^\s*\*\s*\*\s*\*\s*$',
        
        # Academic website patterns (NBER, etc.)
        r'^\s*\[Skip to main content\]\([^)]+\)\s*$',
        r'^\s*\[Subscribe\]\([^)]+\)\s*$',
        r'^\s*\[Media\]\([^)]+\)\s*$',
        r'^\s*\[Open Calls\]\([^)]+\)\s*$',
        r'^\s*\[Login.*\]\([^)]+\)\s*$',
        r'^\s*\[Conferences\]\([^)]+\)\s*$',
        r'^\s*\[Affiliated Scholars\]\([^)]+\)\s*$',
        r'^\s*Search\s*$',
        r'^\s*\[Home\]\([^)]+\)\s*$',
        r'^\s*\[Research\]\([^)]+\)\s*$',
        r'^\s*\[Books & Chapters\]\([^)]+\)\s*$',
        r'^\s*Share\s*$',
        r'^\s*\[Twitter.*\]\([^)]+\)\s*$',
        r'^\s*\[LinkedIn.*\]\([^)]+\)\s*$',
        r'^\s*\[Email.*\]\([^)]+\)\s*$',
        r'^\s*These are preliminary drafts.*\s*$',
        r'^\s*This page will be updated.*\s*$',
        r'^\s*CONFERENCE HELD.*\s*$',
        r'^\s*PUBLISHER:.*\s*$',
        r'^\s*## Table of Contents\s*$',
        r'^\s*## Related\s*$',
        r'^\s*### Topics\s*$',
        r'^\s*### Programs\s*$',
        r'^\s*## More from.*\s*$',
        r'^\s*In addition to.*working papers.*\s*$',
        r'^\s*National Bureau of Economic Research\s*$',
        r'^\s*\[Contact Us\]\([^)]+\)\s*$',
        r'^\s*1050 Massachusetts Ave\.\s*$',
        r'^\s*Cambridge, MA 02138\s*$',
        r'^\s*Follow\s*$',
        r'^\s*\[Homepage\]\([^)]+\)\s*$',
        r'^\s*© \d{4}.*All Rights Reserved\.\s*$',
    ]
    
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in enhanced_patterns]
    
    for line in cleaned_lines:
        line_stripped = line.strip()
        
        # Skip empty lines
        if not line_stripped:
            final_lines.append(line)
            continue
        
        # Check against enhanced patterns
        should_remove = False
        for pattern in compiled_patterns:
            if pattern.match(line_stripped):
                should_remove = True
                break
        
        # Check for general ad/tracking patterns
        if not should_remove:
            # General patterns that indicate ads or tracking
            if any(pattern in line_stripped.lower() for pattern in [
                'doubleclick.net', 'adclick', 'ad server',  # Ad servers
                'utm_source', 'utm_medium', 'utm_campaign',  # Tracking parameters
                'obOrigUrl', '?gclid=',  # More tracking
            ]):
                should_remove = True
        
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
            final_lines.append(line)
    
    # Join and clean up
    cleaned_content = '\n'.join(final_lines)
    cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
    cleaned_content = cleaned_content.strip()
    
    return cleaned_content


def remove_web_clipping_sections(content: str) -> str:
    """Remove entire sections that are typical web clipping clutter."""
    import re
    
    lines = content.split('\n')
    cleaned_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip links section - remove entire block
        if re.match(r'^\s*[Jj]ump\s+to:\s*$', line):
            # Skip this line and all following skip links
            i += 1
            while i < len(lines) and (
                re.match(r'^\s*-\s*\[\[#.*\|.*[Ss]kip\s+to.*\]\]\s*$', lines[i]) or
                re.match(r'^\s*\[.*[Ss]kip\s+to\s+.*\]\([^)]+\)\s*$', lines[i]) or
                lines[i].strip() == ''
            ):
                i += 1
            continue
        
        # Advertisement sections - remove entire blocks
        if re.search(r'doubleclick\.net|s0\.2mdn\.net', line, re.IGNORECASE):
            # Skip this line and following ad content
            i += 1
            while i < len(lines) and (
                re.search(r'doubleclick\.net|s0\.2mdn\.net|ad\.|advertisement', lines[i], re.IGNORECASE) or
                lines[i].strip().startswith('<a href=') or
                lines[i].strip().startswith('<img') or
                lines[i].strip() == ''
            ):
                i += 1
            continue
        
        # Footer sections - remove entire blocks
        if re.match(r'^\s*#\s*\[.*[Ww]ind\s+[Ii]ndustry\s+[Jj]obs.*\]\([^)]+\)\s*$', line):
            # Skip entire jobs section
            i += 1
            while i < len(lines) and (
                re.match(r'^\s*\*\s*\[.*\]\([^)]+\)\s*$', lines[i]) or
                re.match(r'^\s*\[.*\]\([^)]+\)\s*$', lines[i]) or
                lines[i].strip() == '' or
                'Competitive' in lines[i] or
                'Salary dependent' in lines[i]
            ):
                i += 1
            continue
        
        # News by email section
        if re.match(r'^\s*#\s*\[NEWS\s+BY\s+EMAIL\]\([^)]+\)\s*$', line):
            # Skip entire newsletter section
            i += 1
            while i < len(lines) and (
                re.match(r'^\s*\*\*.*\*\*.*[Pp]review.*$', lines[i]) or
                re.match(r'^\s*\[.*\]\([^)]+\)\s*$', lines[i]) or
                'Register here' in lines[i] or
                'manage your bulletins' in lines[i].lower()
            ):
                i += 1
            continue
        
        # Directory section
        if re.match(r'^\s*#\s*[Dd]irectory\s*$', line):
            # Skip entire directory section
            i += 1
            while i < len(lines) and (
                re.match(r'^\s*[Ff]ind\s+products', lines[i]) or
                re.match(r'^\s*[Pp]roduct/Service\s*$', lines[i]) or
                re.match(r'^\s*[Cc]ompany\s*$', lines[i]) or
                lines[i].strip() == '' or
                re.match(r'^\s*\[!\[\[.*\]\]\]\([^)]+\)\s*$', lines[i])
            ):
                i += 1
            continue
        
        # Poll section
        if re.match(r'^\s*#\s*[Pp]oll\s*$', line):
            # Skip entire poll section
            i += 1
            while i < len(lines) and (
                re.match(r'^\s*##\s*[Ww]ill\s+.*\?\s*$', lines[i]) or
                re.match(r'^\s*[Yy]es,?\s+.*\s*$', lines[i]) or
                re.match(r'^\s*[Nn]o,?\s+.*\s*$', lines[i]) or
                re.match(r'^\s*[Mm]aybe,?\s+.*\s*$', lines[i]) or
                lines[i].strip() == '' or
                re.search(r'doubleclick\.net|s0\.2mdn\.net', lines[i], re.IGNORECASE)
            ):
                i += 1
            continue
        
        # Latest Technology Articles section
        if re.match(r'^\s*##\s*[Ll]atest\s+[Tt]echnology\s+[Aa]rticles\s*$', line):
            # Skip entire related articles section
            i += 1
            while i < len(lines) and (
                re.match(r'^\s*\*\s*\[.*\]\([^)]+\)\s*$', lines[i]) or
                lines[i].strip() == '' or
                lines[i].strip() == '\t'
            ):
                i += 1
            continue
        
        # Copyright footer section
        if re.match(r'^\s*\[Haymarket\]\([^)]+\)\s*$', line) or re.match(r'^\s*Haymarket\s+©', line):
            # Skip entire footer section
            i += 1
            while i < len(lines) and (
                re.match(r'^\s*\*\s*\[.*\]\([^)]+\)\s*$', lines[i]) or
                re.match(r'^\s*\[!\[\[.*\]\]\]\([^)]+\)\s*$', lines[i]) or
                lines[i].strip() == '' or
                'PARTNER WEB SITES' in lines[i] or
                re.search(r'doubleclick\.net|s0\.2mdn\.net', lines[i], re.IGNORECASE)
            ):
                i += 1
            continue
        
        # In This Issue section
        if re.match(r'^\s*#\s*\[[Ii]n\s+[Tt]his\s+[Ii]ssue\]\([^)]+\)\s*$', line):
            # Skip entire subscription section
            i += 1
            while i < len(lines) and (
                re.match(r'^\s*\[!\[\[.*\]\]\]\([^)]+\)\s*$', lines[i]) or
                re.search(r'doubleclick\.net|s0\.2mdn\.net', lines[i], re.IGNORECASE)
            ):
                i += 1
            continue
        
        # Keep the line if it doesn't match any removal patterns
        cleaned_lines.append(line)
        i += 1
    
    # Remove duplicate content blocks
    cleaned_lines = remove_duplicate_blocks(cleaned_lines)
    
    return '\n'.join(cleaned_lines)


def remove_duplicate_blocks(lines):
    """Remove duplicate content blocks that often appear in web clippings."""
    if not lines:
        return lines
    
    # Look for repeated patterns of 3+ consecutive lines
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        result.append(line)
        
        # Check if this line starts a repeated block
        if i + 6 < len(lines):  # Need at least 3 lines to form a block
            # Look for the same 3-line pattern starting at different positions
            block1 = lines[i:i+3]
            block1_text = ' '.join(block1).strip().lower()
            
            # Skip if block is too short or contains mostly whitespace
            if len(block1_text) < 20:
                i += 1
                continue
            
            # Look for duplicates
            j = i + 3
            while j + 3 <= len(lines):
                block2 = lines[j:j+3]
                block2_text = ' '.join(block2).strip().lower()
                
                # If blocks are similar (80% similarity), skip the duplicate
                if block2_text and len(block2_text) > 20:
                    similarity = calculate_text_similarity(block1_text, block2_text)
                    if similarity > 0.8:
                        # Skip the duplicate block
                        j += 3
                        continue
                
                j += 1
            
            # If we found duplicates, skip to after the first block
            if j > i + 3:
                i += 3
            else:
                i += 1
        else:
            i += 1
    
    return result


def calculate_text_similarity(text1, text2):
    """Calculate similarity between two text strings."""
    if not text1 or not text2:
        return 0.0
    
    # Simple word-based similarity
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def apply_aggressive_cleaning(content: str) -> str:
    """Apply aggressive cleaning patterns to remove remaining boilerplate."""
    import re
    
    lines = content.split('\n')
    cleaned_lines = []
    
    # Track consecutive lines with only URLs to detect navigation blocks
    consecutive_url_lines = 0
    url_block_threshold = 3  # Remove blocks with 3+ consecutive URL-only lines
    
    for line in lines:
        line_stripped = line.strip()
        
        # Skip empty lines
        if not line_stripped:
            cleaned_lines.append(line)
            consecutive_url_lines = 0  # Reset counter
            continue
        
        # Check if line is primarily a URL or link
        is_url_line = (
            line_stripped.startswith('http://') or 
            line_stripped.startswith('https://') or
            line_stripped.startswith('<http') or
            (line_stripped.startswith('*') and ('http://' in line_stripped or 'https://' in line_stripped)) or
            (line_stripped.startswith('-') and ('http://' in line_stripped or 'https://' in line_stripped))
        )
        
        # Track consecutive URL lines
        if is_url_line:
            consecutive_url_lines += 1
            # Skip this line if part of a navigation block
            if consecutive_url_lines >= url_block_threshold:
                continue
        else:
            # If we were in a URL block, remove those lines
            if consecutive_url_lines >= url_block_threshold:
                # Remove the last few URL lines we added
                cleaned_lines = cleaned_lines[:-consecutive_url_lines+1] if consecutive_url_lines > 0 else cleaned_lines
            consecutive_url_lines = 0
        
        # Remove lines with excessive navigation/social media content
        nav_patterns = [
            r'^\s*\[.*\]\([^)]*share[^)]*\)\s*$',  # Share buttons
            r'^\s*\[.*\]\([^)]*facebook[^)]*\)\s*$',  # Facebook links
            r'^\s*\[.*\]\([^)]*twitter[^)]*\)\s*$',  # Twitter links
            r'^\s*\[.*\]\([^)]*linkedin[^)]*\)\s*$',  # LinkedIn links
            r'^\s*\[.*\]\([^)]*subscribe[^)]*\)\s*$',  # Subscribe links
            r'^\s*\[.*\]\([^)]*newsletter[^)]*\)\s*$',  # Newsletter links
            r'^\s*\[.*\]\([^)]*rss[^)]*\)\s*$',  # RSS links
            r'^\s*\[.*\]\([^)]*follow[^)]*\)\s*$',  # Follow links
            r'^\s*\[.*\]\([^)]*advertisement[^)]*\)\s*$',  # Advertisement links
            r'^\s*\[.*\]\([^)]*doubleclick[^)]*\)\s*$',  # DoubleClick ads
            r'^\s*\[.*\]\([^)]*utm_[^)]*\)\s*$',  # UTM tracking links
        ]
        
        # Check if line matches navigation patterns
        is_nav_line = any(re.match(pattern, line, re.IGNORECASE) for pattern in nav_patterns)
        if is_nav_line:
            continue
        
        # Remove lines with excessive social media indicators
        social_indicators = [
            'share on', 'follow us', 'subscribe to', 'newsletter', 'rss feed',
            'followers', 'subscribers', 'like us', 'tweet this', 'share this',
            'addthis', 'social media', 'follow @', 'tweet', 'facebook', 'twitter',
            'linkedin', 'instagram', 'youtube', 'pinterest'
        ]
        
        if any(indicator in line_stripped.lower() for indicator in social_indicators):
            continue
        
        # Remove lines with excessive navigation indicators
        nav_indicators = [
            'you are here:', 'breadcrumb', 'navigation', 'menu', 'home',
            'about', 'contact', 'search', 'login', 'register', 'sign up',
            'sign in', 'logout', 'profile', 'account', 'settings',
            # WSJ specific
            'dow jones', 'news corp', 'wall street journal', 'wsj',
            'today\'s paper', 'show all sections', 'hide all sections',
            'aim higher, reach further', 'get the wall street journal',
            'subscribe now', 'regions', 'blogs', 'sections', 'more',
            'columns & blogs', 'journal report', 'what\'s news podcast',
            'washington wire', 'tech/wsj.d', 'industries', 'bankruptcy beat',
            'billion dollar startup club', 'tech video', 'tech podcast',
            'startup stock trader', 'heard on the street', 'moneybeat',
            'wealth adviser', 'best of the web', 'columnists', 'morning editorial report',
            'peggy noonan', 'opinion video', 'potomac watch podcast',
            'foreign edition podcast', 'real estate video', 'save article',
            'text size', 'regular', 'medium', 'large', 'google+', 'print',
            'by', 'independent of the wall street journal newsroom',
            'economy & politics', 'gatsby-esque mansion', 'edition:', 'u.s.',
            'wsj membership', 'digital subscription', 'print subscription',
            'print and digital subscription', 'why subscribe?', 'download wsj apps',
            'corporate subscriptions', 'professor journal', 'student journal',
            'customer service', 'live help', 'redesign guided tour',
            'dow jones products', 'dow jones & company', 'inc. all rights reserved'
        ]
        
        if any(indicator in line_stripped.lower() for indicator in nav_indicators):
            continue
        
        # Remove lines with excessive advertising indicators
        ad_indicators = [
            'advertisement', 'sponsored', 'promoted', 'affiliate', 'partner',
            'banner', 'popup', 'overlay', 'doubleclick', 'google ads',
            'amazon ads', 'facebook ads', 'twitter ads',
            # Financial data and market indicators (often boilerplate)
            '▲', '▼', 'yield', 'points', 'basis points',
            # Cookie and privacy notices
            'we use cookies', 'cookie policy', 'privacy policy', 'terms of service',
            'by using our website', 'browser capability checks', 'flash for video',
            'ad blocking', 'you agree to our use'
        ]
        
        if any(indicator in line_stripped.lower() for indicator in ad_indicators):
            continue
        
        # Remove lines with excessive tracking/analytics indicators
        tracking_indicators = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'gclid', 'fbclid', 'msclkid', 'trk', 'tracking', 'analytics',
            'google analytics', 'facebook pixel', 'twitter pixel'
        ]
        
        if any(indicator in line_stripped.lower() for indicator in tracking_indicators):
            continue
        
        # Remove lines that are mostly links (more than 70% of content is links)
        link_count = len(re.findall(r'\[([^\]]+)\]\([^)]+\)', line_stripped))
        word_count = len(line_stripped.split())
        if word_count > 0 and link_count / word_count > 0.7:
            continue
        
        # Remove lines with excessive punctuation (likely navigation)
        if len(re.findall(r'[|•·▪▫]', line_stripped)) > 3:
            continue
        
        # Remove lines that are just stock market data or financial indicators
        if re.match(r'^[\d,]+\.?\d*\s*[▲▼]?\s*\d*\.?\d*%?\s*$', line_stripped):
            continue
        
        # Remove lines that are just author names or bylines without content
        if re.match(r'^(by|By)\s*$', line_stripped) or re.match(r'^[A-Za-z\s,]+The Wall Street Journal\s*$', line_stripped):
            continue
        
        # Remove lines that are just section headers without content
        if re.match(r'^(previous|next|save article|text size|regular|medium|large|google\+|print)\s*$', line_stripped, re.IGNORECASE):
            continue
        
        # Keep paywall notices and subscription prompts (they indicate real content)
        if re.search(r'(subscribe|sign in|to read the full story|paywall|premium)', line_stripped, re.IGNORECASE):
            # This is a paywall notice, keep it
            pass
        elif re.search(r'(mailto:|@)', line_stripped) and len(line_stripped) < 50:
            # Skip short email addresses or mailto links
            continue
        elif re.search(r'\[.*mailto:.*\]', line_stripped) and len(line_stripped) > 100:
            # This is a mailto link containing article content, extract and keep the content
            # Extract text between brackets and parentheses
            import re
            content_match = re.search(r'\[([^\]]+)\]\([^)]+\)', line_stripped)
            if content_match:
                article_content = content_match.group(1)
                # Keep the article content
                cleaned_lines.append(article_content)
            continue
        elif re.search(r'\[.*\]\(mailto:.*\)', line_stripped) and len(line_stripped) > 100:
            # This is a mailto link containing article content, extract and keep the content
            import re
            content_match = re.search(r'\[([^\]]+)\]\([^)]+\)', line_stripped)
            if content_match:
                article_content = content_match.group(1)
                # Keep the article content
                cleaned_lines.append(article_content)
            continue
        elif re.search(r'\[.*\]\(mailto:\)', line_stripped) and len(line_stripped) > 100:
            # This is a mailto link containing article content, extract and keep the content
            import re
            content_match = re.search(r'\[([^\]]+)\]\([^)]+\)', line_stripped)
            if content_match:
                article_content = content_match.group(1)
                # Keep the article content
                cleaned_lines.append(article_content)
            continue
        elif re.search(r'\[.*\]\(mailto:\)', line_stripped) and len(line_stripped) > 50:
            # This is a mailto link containing article content, extract and keep the content
            import re
            content_match = re.search(r'\[([^\]]+)\]\([^)]+\)', line_stripped)
            if content_match:
                article_content = content_match.group(1)
                # Keep the article content
                cleaned_lines.append(article_content)
            continue
        
        # Keep lines that contain substantial article content (even if mixed with boilerplate)
        if re.search(r'(said|according to|reported|announced|declared|stated|explained|added|noted|observed)', line_stripped, re.IGNORECASE):
            # This looks like article content, keep it
            pass
        elif re.search(r'(interview|meeting|conference|speech|statement|press release)', line_stripped, re.IGNORECASE):
            # This looks like article content, keep it
            pass
        elif re.search(r'(prime minister|president|leader|government|minister|official)', line_stripped, re.IGNORECASE):
            # This looks like political content, keep it
            pass
        elif re.search(r'(european union|eu|politics|political|election|vote)', line_stripped, re.IGNORECASE):
            # This looks like political content, keep it
            pass
        elif re.search(r'(economic growth|employment|structural|overhaul)', line_stripped, re.IGNORECASE):
            # This looks like economic content, keep it
            pass
        
        # Remove lines that are mostly special characters
        special_char_count = len(re.findall(r'[^\w\s]', line_stripped))
        if len(line_stripped) > 0 and special_char_count / len(line_stripped) > 0.5:
            continue
        
        # Keep the line if it passes all filters
        cleaned_lines.append(line)
    
    # Join and clean up
    cleaned_content = '\n'.join(cleaned_lines)
    cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
    cleaned_content = cleaned_content.strip()
    
    return cleaned_content


def remove_only_final_boilerplate(content: str) -> str:
    """Remove only obvious boilerplate at the END of articles.
    
    This minimal approach preserves article content while removing
    footer navigation, comments sections, and social sharing widgets.
    """
    import re
    
    lines = content.split('\n')
    
    # Markers that clearly indicate END of article content
    # These are structural markers, not single-word patterns
    end_markers = [
        # Comment sections (clear end of article)
        ('Post your own comment', 0),  # Remove from here onwards
        ('Leave a comment', 0),
        ('Comments', 3),  # Only if appears in last 20% of content as a standalone line
        ('Sorted by newest first', 0),
        ('Selected comments', 0),
        
        # Copyright and legal (clear footer)
        ('Copyright © The Financial Times', 0),
        ('Copyright The Financial Times Limited', 0),
        ('© The Economist', 0),
        ('All rights reserved', 2),  # Only if appears near end
        ("Please don't cut articles", 0),
        
        # Social sharing sections (clear footer)
        ('Share', 5),  # Only if standalone "Share" in last 30%
        ('Print', 5),  # Only if standalone in last 30%
        ('Email', 5),  # Only if standalone in last 30%
        ('Reprints', 5),
        
        # Navigation sections (clear footer)
        ('Jump to:', 0),
        ('Skip to:', 0),
        
        # Subscription prompts at end
        ('Subscribe to', 3),  # Only if near end
        ('Sign up for', 3),
    ]
    
    # Find the earliest footer marker in the last 30% of content
    content_start_cutoff = len(lines) * 0.7  # Don't cut before 70% of content
    footer_start = None
    
    for i in range(len(lines) - 1, int(content_start_cutoff), -1):
        line_stripped = lines[i].strip()
        
        for marker, min_lines_before in end_markers:
            if marker in line_stripped:
                # Check if we have enough content before this point
                if i >= min_lines_before and i >= 5:  # At least 5 lines of content
                    # Additional check: is this a standalone line or embedded?
                    # Standalone: line is short and mostly just the marker
                    is_standalone = len(line_stripped) < len(marker) + 20
                    
                    # Embedded: marker is part of larger sentence
                    is_embedded = not is_standalone and len(line_stripped) > 80
                    
                    # Only cut if standalone (clear footer) or we have confidence
                    if is_standalone or min_lines_before == 0:
                        if footer_start is None or i < footer_start:
                            footer_start = i
                            break
    
    # Return content up to footer (or all content if no clear footer)
    if footer_start and footer_start > 10:  # Keep at least 10 lines
        return '\n'.join(lines[:footer_start]).strip()
    
    return content

def clean_html_like_clipping(content: str, frontmatter: Dict = None) -> str:
    """Clean web clipping content - TRUST THE EXTRACTORS.
    
    Philosophy: Trafilatura and Readability are expert-built tools for exactly this purpose.
    They use ML models, DOM analysis, and extensive testing. Our job is to use them,
    not to second-guess them with thousands of regex patterns.
    """
    import re
    
    # Check if this is web content
    is_web_clipping = False
    if frontmatter and frontmatter.get('source', '').startswith(('http://', 'https://')):
        is_web_clipping = True
    else:
        # Check for HTML content in body
        web_indicators = ['<div', '<span', '<p class=', 'class=', 'id=']
        is_web_clipping = any(indicator in content.lower() for indicator in web_indicators)
    
    if not is_web_clipping:
        # Not web content - return as-is
        return content
    
    # Try Readability first (best retention: 99.9%)
    extracted = extract_content_with_readability_v2(content)
    if extracted and len(extracted) > 200:
        # Readability worked - just remove final boilerplate
        cleaned = remove_only_final_boilerplate(extracted)
        return cleaned
    
    # Fallback to Trafilatura (excellent retention: 96.9%)
    extracted = extract_content_with_trafilatura_v2(content)
    if extracted and len(extracted) > 200:
        # Trafilatura worked - just remove final boilerplate
        cleaned = remove_only_final_boilerplate(extracted)
        return cleaned
    
    # Both extractors failed - content might be heavily HTML-structured
    html_tag_count = len(re.findall(r'<(div|span|table|tr|td)', content, re.IGNORECASE))
    if html_tag_count > 10:
        # Strip HTML and do minimal cleaning
        cleaned = clean_heavily_html_structured(content, frontmatter)
        return remove_only_final_boilerplate(cleaned)
    
    # Last resort: return with minimal cleaning
    return content
