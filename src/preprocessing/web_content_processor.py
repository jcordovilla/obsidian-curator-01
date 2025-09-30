"""
Web Content Processor for fetching and processing linked publications.

This module handles web content that points to academic publications,
research papers, and other valuable content that should be processed
as if it were a PDF attachment.
"""

import requests
import time
from typing import Dict, Optional, Tuple
from pathlib import Path
import re
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)

class WebContentProcessor:
    """Processes web content by fetching linked publications."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 30
        self.max_retries = 3
        
    def is_publication_url(self, url: str) -> bool:
        """Check if URL points to a publication that should be processed."""
        if not url or not url.startswith(('http://', 'https://')):
            return False
            
        # Academic and research publication indicators
        publication_indicators = [
            'nber.org', 'jstor.org', 'scholar.google', 'arxiv.org', 'ssrn.com',
            'researchgate.net', 'academia.edu', 'springer.com', 'elsevier.com',
            'wiley.com', 'sagepub.com', 'tandfonline.com', 'cambridge.org',
            'oxfordjournals.org', 'mitpress.mit.edu', 'harvard.edu',
            'stanford.edu', 'princeton.edu', 'yale.edu', 'chicagobooth.edu',
            'wharton.upenn.edu', 'sloan.mit.edu', 'kellogg.northwestern.edu',
            'gsb.stanford.edu', 'hbs.edu', 'anderson.ucla.edu',
            'papers.ssrn.com', 'ideas.repec.org', 'econpapers.repec.org',
            'repec.org', 'cepr.org', 'brookings.edu', 'rand.org',
            'worldbank.org', 'imf.org', 'oecd.org', 'bis.org',
            'federalreserve.gov', 'ecb.europa.eu', 'bankofengland.co.uk'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in publication_indicators)
    
    def fetch_web_content(self, url: str) -> Optional[Dict]:
        """Fetch and process web content from a publication URL."""
        if not self.is_publication_url(url):
            logger.info(f"URL not identified as publication: {url}")
            return None
            
        try:
            logger.info(f"Fetching web content from: {url}")
            
            for attempt in range(self.max_retries):
                try:
                    response = self.session.get(url, timeout=self.timeout)
                    response.raise_for_status()
                    
                    # Check if content is substantial
                    content_length = len(response.text)
                    if content_length < 1000:  # Too short to be a real publication
                        logger.warning(f"Content too short ({content_length} chars): {url}")
                        return None
                    
                    # Extract content using basic HTML parsing
                    content = self._extract_content(response.text, url)
                    
                    if not content or len(content.strip()) < 500:
                        logger.warning(f"Extracted content too short: {url}")
                        return None
                    
                    return {
                        'url': url,
                        'title': self._extract_title(response.text),
                        'content': content,
                        'source': url,
                        'content_type': 'web_publication',
                        'word_count': len(content.split()),
                        'success': True
                    }
                    
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise
                        
        except Exception as e:
            logger.error(f"Failed to fetch web content from {url}: {e}")
            return None
    
    def _extract_title(self, html: str) -> str:
        """Extract title from HTML content."""
        import re
        
        # Try various title extraction methods
        title_patterns = [
            r'<title[^>]*>(.*?)</title>',
            r'<h1[^>]*>(.*?)</h1>',
            r'<meta property="og:title" content="([^"]*)"',
            r'<meta name="title" content="([^"]*)"'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                title = match.group(1).strip()
                # Clean up HTML entities and tags
                title = re.sub(r'<[^>]+>', '', title)
                title = re.sub(r'&[a-zA-Z0-9#]+;', ' ', title)
                title = re.sub(r'\s+', ' ', title).strip()
                if title and len(title) > 10:
                    return title
        
        return "Web Publication"
    
    def _extract_content(self, html: str, url: str) -> str:
        """Extract main content from HTML, focusing on academic publications."""
        import re
        
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.IGNORECASE | re.DOTALL)
        
        # Try to find main content areas
        content_patterns = [
            r'<main[^>]*>(.*?)</main>',
            r'<article[^>]*>(.*?)</article>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*main[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*body[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*id="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*id="[^"]*main[^"]*"[^>]*>(.*?)</div>',
        ]
        
        content = ""
        for pattern in content_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            if matches:
                # Take the longest match (likely the main content)
                content = max(matches, key=len)
                break
        
        if not content:
            # Fallback: extract all paragraph and heading content
            content = html
        
        # Convert HTML to text
        content = self._html_to_text(content)
        
        # Clean up the content
        content = self._clean_extracted_content(content)
        
        return content
    
    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text."""
        import re
        
        # Remove HTML tags but preserve structure
        text = re.sub(r'<br[^>]*>', '\n', html)
        text = re.sub(r'</(p|div|h[1-6]|li|td|th)>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        html_entities = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"',
            '&apos;': "'", '&nbsp;': ' ', '&copy;': '©',
            '&reg;': '®', '&trade;': '™'
        }
        
        for entity, char in html_entities.items():
            text = text.replace(entity, char)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()
    
    def _clean_extracted_content(self, content: str) -> str:
        """Clean up extracted content."""
        import re
        
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                cleaned_lines.append('')
                continue
            
            # Skip common web boilerplate
            skip_patterns = [
                r'^Skip to main content$',
                r'^Subscribe$',
                r'^Login$',
                r'^Search$',
                r'^Home$',
                r'^Follow us$',
                r'^Share$',
                r'^Print$',
                r'^Email$',
                r'^Download$',
                r'^PDF$',
                r'^Abstract$',
                r'^Keywords$',
                r'^JEL Classification$',
                r'^DOI:',
                r'^Published:',
                r'^Copyright',
                r'^All rights reserved',
                r'^National Bureau of Economic Research',
                r'^Contact Us$',
                r'^Follow$',
                r'^Homepage$',
                r'^\d{4}.*All Rights Reserved',
                r'^Cambridge, MA',
                r'^Massachusetts Ave',
            ]
            
            should_skip = any(re.match(pattern, line, re.IGNORECASE) for pattern in skip_patterns)
            
            if not should_skip and len(line) > 10:  # Keep substantial lines
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def process_note_with_web_content(self, content: str, frontmatter: Dict) -> Optional[Dict]:
        """Process a note that contains web publication links."""
        source_url = frontmatter.get('source', '')
        
        if not self.is_publication_url(source_url):
            return None
        
        web_content = self.fetch_web_content(source_url)
        if not web_content:
            return None
        
        # Combine original content with fetched content
        combined_content = f"{content}\n\n---\n\n# Web Publication Content\n\n{web_content['content']}"
        
        return {
            'enhanced_content': combined_content,
            'web_publication': web_content,
            'enhanced_metadata': {
                'web_title': web_content['title'],
                'web_url': web_content['url'],
                'web_word_count': web_content['word_count'],
                'content_enhanced': True
            }
        }
