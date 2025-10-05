"""
Configuration settings for the Obsidian Curator application.
"""

import os
import yaml
from pathlib import Path

# Vault configuration
RAW_VAULT_PATH = "/Users/jose/Documents/Obsidian/Evermd"  # Original notes + attachments
PREPROCESSED_VAULT_PATH = "/Users/jose/Documents/Obsidian/Ever-preprocessed"  # Cleaned notes + attachments
CURATED_VAULT_PATH = "/Users/jose/Documents/Obsidian/Ever-curated"  # Enhanced notes + attachments

# Test data configuration
TEST_RAW_PATH = "tests/test_data/raw"  # Test raw notes + attachments
TEST_PREPROCESSED_PATH = "tests/test_data/preprocessed"  # Test preprocessed notes + attachments
TEST_CURATED_PATH = "tests/test_data/curated"  # Test curated notes + attachments

SAMPLE_SIZE = 200
OUTPUT_DIR = "analysis_output"

# Legacy aliases for backward compatibility
VAULT_PATH = RAW_VAULT_PATH
PREPROCESSING_OUTPUT_PATH = PREPROCESSED_VAULT_PATH
CURATION_OUTPUT_PATH = CURATED_VAULT_PATH

# Specific paths within each vault
RAW_NOTES_PATH = os.path.join(RAW_VAULT_PATH, "notes")
RAW_ATTACHMENTS_PATH = os.path.join(RAW_VAULT_PATH, "attachments")

PREPROCESSED_NOTES_PATH = os.path.join(PREPROCESSED_VAULT_PATH, "notes")
PREPROCESSED_ATTACHMENTS_PATH = os.path.join(PREPROCESSED_VAULT_PATH, "attachments")

CURATED_NOTES_PATH = os.path.join(CURATED_VAULT_PATH, "notes")
CURATED_ATTACHMENTS_PATH = os.path.join(CURATED_VAULT_PATH, "attachments")

# Test-specific paths
TEST_RAW_NOTES_PATH = os.path.join(TEST_RAW_PATH, "notes")
TEST_RAW_ATTACHMENTS_PATH = os.path.join(TEST_RAW_PATH, "attachments")

TEST_PREPROCESSED_NOTES_PATH = os.path.join(TEST_PREPROCESSED_PATH, "notes")
TEST_PREPROCESSED_ATTACHMENTS_PATH = os.path.join(TEST_PREPROCESSED_PATH, "attachments")

TEST_CURATED_NOTES_PATH = os.path.join(TEST_CURATED_PATH, "notes")
TEST_CURATED_ATTACHMENTS_PATH = os.path.join(TEST_CURATED_PATH, "attachments")

# Legacy aliases
CURATION_NOTES_PATH = CURATED_NOTES_PATH
CURATION_ASSETS_PATH = CURATED_ATTACHMENTS_PATH
CURATION_ATTACHMENTS_PATH = RAW_ATTACHMENTS_PATH  # Curated notes reference original attachments

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
            'raw_vault': RAW_VAULT_PATH,
            'preprocessed_vault': PREPROCESSED_VAULT_PATH,
            'curated_vault': CURATED_VAULT_PATH,
            'raw_notes': RAW_NOTES_PATH,
            'raw_attachments': RAW_ATTACHMENTS_PATH,
            'preprocessed_notes': PREPROCESSED_NOTES_PATH,
            'preprocessed_attachments': PREPROCESSED_ATTACHMENTS_PATH,
            'curated_notes': CURATED_NOTES_PATH,
            'curated_attachments': CURATED_ATTACHMENTS_PATH,
            # Test paths
            'test_raw_vault': TEST_RAW_PATH,
            'test_preprocessed_vault': TEST_PREPROCESSED_PATH,
            'test_curated_vault': TEST_CURATED_PATH,
            'test_raw_notes': TEST_RAW_NOTES_PATH,
            'test_raw_attachments': TEST_RAW_ATTACHMENTS_PATH,
            'test_preprocessed_notes': TEST_PREPROCESSED_NOTES_PATH,
            'test_preprocessed_attachments': TEST_PREPROCESSED_ATTACHMENTS_PATH,
            'test_curated_notes': TEST_CURATED_NOTES_PATH,
            'test_curated_attachments': TEST_CURATED_ATTACHMENTS_PATH,
            # Legacy aliases for backward compatibility
            'vault': RAW_VAULT_PATH,
            'attachments': RAW_ATTACHMENTS_PATH,
            'out_notes': CURATED_NOTES_PATH,
            'out_assets': CURATED_ATTACHMENTS_PATH
        },
        'models': {
            'fast': 'llama3.1:8b',  # Upgraded to Llama 3.1:8B for better multilingual support
            'main': 'llama3.1:8b',
            'embed': 'nomic-embed-text'
        },
        'taxonomy': {
            'categories': [
                # Core Infrastructure & PPP
                "Infrastructure Investment", "PPP/P3", "Concessions", "Project Finance", "Risk Management",
                
                # Sectors
                "Roads & Transport", "Water & Wastewater", "Energy", "Hospitals & Social Infrastructure", "Railways",
                
                # Digital & Innovation
                "Digital Transformation", "AI & Machine Learning", "Digital Twins", "Geospatial Data", "Process Automation",
                
                # Governance & Strategy
                "Governance & Transparency", "Policy & Regulation", "Strategic Planning", "Asset Management",
                
                # Technical & Analysis
                "Technical Due Diligence", "Feasibility Studies", "Market Intelligence", "Critical Infrastructure Protection",
                
                # Geographic & Sectoral Focus
                "Spain", "Europe", "LATAM", "International Development",
                
                # Cross-cutting Themes
                "ESG & Sustainability", "Climate Resilience", "Innovation & R&D", "Capacity Building"
            ]
        },
    'decision': {
        'keep_threshold': 0.45,  # Keep medium+ value content (0.45-1.0)
        'gray_margin': 0.20      # Triage zone (0.25-0.45), discard <0.25
    },
        'priorities': ["pdf","text","image"],
        'summaries': {
            'pdf': {'bullets': 8, 'max_tokens': 900},
            'image': {'bullets': 6, 'max_tokens': 500}
        },
        'language': {
            'default': 'auto'
        }
    }

def get_test_config():
    """Generate test configuration using test data paths."""
    config = get_curation_config()
    # Override paths to use test data - use preprocessed as input for curation
    config['paths'].update({
        'vault': TEST_PREPROCESSED_PATH,  # Use preprocessed as input
        'attachments': TEST_PREPROCESSED_ATTACHMENTS_PATH,  # Use preprocessed attachments
        'out_notes': TEST_CURATED_NOTES_PATH,
        'out_assets': TEST_CURATED_ATTACHMENTS_PATH,
        'raw_vault': TEST_RAW_PATH,
        'raw_notes': TEST_RAW_NOTES_PATH,
        'raw_attachments': TEST_RAW_ATTACHMENTS_PATH,
        'preprocessed_vault': TEST_PREPROCESSED_PATH,
        'preprocessed_notes': TEST_PREPROCESSED_NOTES_PATH,
        'preprocessed_attachments': TEST_PREPROCESSED_ATTACHMENTS_PATH,
        'curated_vault': TEST_CURATED_PATH,
        'curated_notes': TEST_CURATED_NOTES_PATH,
        'curated_attachments': TEST_CURATED_ATTACHMENTS_PATH
    })
    return config

def update_curation_yaml():
    """Update config.yaml with current configuration."""
    config = get_curation_config()
    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
