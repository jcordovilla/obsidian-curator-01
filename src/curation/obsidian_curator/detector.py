import re

WIKILINK = r'!\[\[(attachments/[^\]]+?\.(?:pdf|png|jpe?g|webp|tif|tiff|mp3|wav|m4a|ogg|flac))\]\]'
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
    kinds = [a['kind'] for a in assets]
    for pr in priorities:
        if pr in kinds:
            for a in assets:
                if a['kind']==pr:
                    return a
    return {'kind':'text', 'path': None}
