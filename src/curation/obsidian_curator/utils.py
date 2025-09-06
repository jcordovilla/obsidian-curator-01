import os, re, yaml

def iter_markdown_notes(root):
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.lower().endswith(".md"):
                yield os.path.join(dirpath, fn)

def parse_front_matter(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            fm = yaml.safe_load(text[3:end])
            body = text[end+4:]
            return fm or {}, body
    return {}, text

# imports for cleaning and standardizing from the preprocessing module (existing code)
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

def clean_markdown_to_text(md: str) -> str:
    try:
        from preprocessing.web_clipping_cleaner import clean_html_like_clipping
        return clean_html_like_clipping(md)
    except ImportError:
        # Fallback to simple text cleaning
        import re
        # Remove markdown headers, links, and basic formatting
        cleaned = re.sub(r'^#+\s*', '', md, flags=re.MULTILINE)
        cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
        cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)
        cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)
        return cleaned.strip()