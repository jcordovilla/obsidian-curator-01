import re

WIKILINK = r'!\[\[(attachments/[^\]]+?\.(?:pdf|png|jpe?g|webp|tif|tiff|mp3|wav|m4a|ogg|flac|aac|wma))\]\]'
MDIMG    = r'!\[[^\]]*\]\((attachments/[^)]+)\)'

def detect_assets(body:str, attachments_root:str):
    paths = set()
    for pat in (WIKILINK, MDIMG):
        for m in re.finditer(pat, body, flags=re.IGNORECASE):
            paths.add(m.group(1))
    assets = []
    for p in sorted(paths):
        ext = p.split('.')[-1].lower()
        if ext == 'pdf':
            kind = 'pdf'
        elif ext in ('mp3', 'wav', 'm4a', 'ogg', 'flac'):
            kind = 'audio'
        else:
            kind = 'image'
        assets.append({'path': p, 'kind': kind})
    return assets

def choose_primary(assets, body, priorities):
    if not assets:
        return {'kind':'text', 'path': None}
    
    # Extract text content (excluding frontmatter and image references)
    text_content = body
    # Remove frontmatter
    if text_content.startswith('---'):
        parts = text_content.split('---', 2)
        if len(parts) >= 3:
            text_content = parts[2]
    
    # Remove image references to get actual text
    text_content = re.sub(r'!\[\[.*?\]\]', '', text_content)
    text_content = re.sub(r'!\[.*?\]\(.*?\)', '', text_content)
    text_only = text_content.strip()
    
    # Count meaningful text (ignore whitespace and short fragments)
    word_count = len([w for w in text_only.split() if len(w) > 2])
    
    # Check for low-value content types that should be rejected
    low_value_indicators = [
        'business card', 'contact', 'email', 'phone', 'teléfono',
        'award', 'medal', 'letter', 'notification', 'congratulations',
        'notebook', 'page', 'empty', 'minimal', 'brief',
        'username', 'account', 'login', 'password', 'user'
    ]
    
    # If content contains low-value indicators, still use text but mark for rejection
    if any(indicator in text_only.lower() for indicator in low_value_indicators):
        # Return text but the scoring will catch this as low-value
        return {'kind':'text', 'path': None}
    
    # If there's substantial text content (>100 words), prioritize text over images
    # Only use images/PDFs as primary when text is minimal
    if word_count > 100:
        # Override priority: substantial text means text is primary
        # Only use PDF if present (PDF still takes priority over text)
        for pr in priorities:
            if pr == 'pdf':
                if pr in [a['kind'] for a in assets]:
                    for a in assets:
                        if a['kind'] == pr:
                            return a
        # Return text as primary if substantial text exists
        return {'kind':'text', 'path': None}
    
    # For minimal text, use standard priority
    kinds = [a['kind'] for a in assets]
    for pr in priorities:
        if pr in kinds:
            for a in assets:
                if a['kind']==pr:
                    return a
    return {'kind':'text', 'path': None}
