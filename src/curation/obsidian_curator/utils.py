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
from preprocessing.web_clipping_cleaner import clean_html_like_clipping  # your existing
from preprocessing.metadata_standardizer import normalize_front_matter   # your existing

def clean_markdown_to_text(md: str) -> str:
    # call your cleaner instead of the simple placeholder
    return clean_html_like_clipping(md)