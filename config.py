"""
Configuration settings for the Obsidian Curator application.
"""

import os
import yaml
from pathlib import Path

# Vault configuration
VAULT_PATH = "/Users/jose/Documents/Obsidian/Evermd"
SAMPLE_SIZE = 200
OUTPUT_DIR = "analysis_output"

# Preprocessing output configuration
PREPROCESSING_OUTPUT_PATH = "/Users/jose/Documents/Obsidian/Ever-output"

# Curation output paths (derived from vault path)
CURATION_OUTPUT_PATH = "/Users/jose/Documents/Obsidian/Ever-curated"
CURATION_NOTES_PATH = os.path.join(CURATION_OUTPUT_PATH, "notes")
CURATION_ASSETS_PATH = os.path.join(CURATION_OUTPUT_PATH, "assets")
CURATION_ATTACHMENTS_PATH = os.path.join(VAULT_PATH, "attachments")

# Analysis configuration
ANALYSIS_CATEGORIES = [
    "web_clipping",
    "pdf_annotation", 
    "typed_note",
    "business_card",
    "news_article",
    "technical_document",
    "personal_note",
    "unknown"
]

# Common boilerplate patterns to identify (expanded for technical analysis)
BOILERPLATE_PATTERNS = [
    # Social sharing and navigation
    "AddThis Sharing Buttons",
    "Share This Article", 
    "Share on Facebook",
    "Share on Twitter",
    "Share on LinkedIn",
    "Tweet this",
    "Like this",
    "Follow us on",
    "Subscribe to",
    "Newsletter",
    
    # Web navigation and UI
    "Click here to",
    "Read more",
    "Continue reading",
    "View full article",
    "Back to top",
    "Print this page",
    "Email this article",
    "Bookmark this",
    "Add to favorites",
    
    # Legal and policy
    "Cookie policy",
    "Privacy policy",
    "Terms of service",
    "Terms of use",
    "Legal notice",
    "Disclaimer",
    "Copyright notice",
    
    # Advertising and commercial
    "Advertisement",
    "Sponsored content",
    "Promoted content",
    "Ads by",
    "Advertiser",
    "Sponsored by",
    
    # Comments and interaction
    "Leave a comment",
    "Post a comment",
    "Comments",
    "Reply",
    "Login to comment",
    "Sign up",
    "Register",
    
    # Media and content
    "Photo credit",
    "Image source",
    "Video player",
    "Audio player",
    "Gallery",
    "Slideshow"
]

# Web-specific boilerplate indicators
WEB_BOILERPLATE_INDICATORS = {
    'navigation': [
        'menu', 'navigation', 'navbar', 'breadcrumb', 'home', 'about', 'contact',
        'sitemap', 'search', 'login', 'register', 'cart', 'checkout'
    ],
    'social_media': [
        'facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'pinterest',
        'whatsapp', 'telegram', 'reddit', 'tumblr'
    ],
    'advertising': [
        'advertisement', 'sponsored', 'promoted', 'affiliate', 'partner',
        'banner', 'popup', 'overlay'
    ],
    'ui_elements': [
        'button', 'dropdown', 'modal', 'tooltip', 'accordion', 'tab',
        'slider', 'carousel', 'pagination'
    ],
    'forms': [
        'subscribe', 'newsletter', 'email', 'submit', 'form', 'input',
        'checkbox', 'radio', 'select'
    ]
}

# Metadata fields from Evernote conversion
EVERNOTE_METADATA_FIELDS = [
    "source",
    "date created", 
    "date modified",
    "language",
    "tags"
]

# File patterns
ATTACHMENT_PATTERN = r'!\[\[attachments/[^\]]+\]\]'
URL_PATTERN = r'https?://[^\s\)]+' 
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def get_curation_config():
    """Generate curation configuration from main config."""
    return {
        'paths': {
            'vault': VAULT_PATH,
            'attachments': CURATION_ATTACHMENTS_PATH,
            'out_notes': CURATION_NOTES_PATH,
            'out_assets': CURATION_ASSETS_PATH
        },
        'models': {
            'fast': 'phi3:mini',
            'main': 'llama3.1:8b',
            'embed': 'nomic-embed-text'
        },
        'taxonomy': {
            'categories': ["PPP","Concessions","Roads","Water","Energy","ESG","Governance","Policy","Finance","LATAM","Spain","Indonesia","Africa"]
        },
        'decision': {
            'keep_threshold': 0.68,
            'gray_margin': 0.05
        },
        'priorities': ["pdf","image","text"],
        'summaries': {
            'pdf': {'bullets': 8, 'max_tokens': 900},
            'image': {'bullets': 6, 'max_tokens': 500}
        },
        'language': {
            'default': 'auto'
        }
    }

def update_curation_yaml():
    """Update config.yaml with current configuration."""
    config = get_curation_config()
    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
