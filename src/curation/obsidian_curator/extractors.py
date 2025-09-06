import os
import fitz
from PIL import Image
import pytesseract
from .utils import clean_markdown_to_text

def extract_pdf(abs_path):
    try:
        doc = fitz.open(abs_path)
        texts = []
        for page in doc:
            t = page.get_text("text").strip()
            if not t:
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                t = pytesseract.image_to_string(img)
            texts.append(t)
        return {'kind':'pdf', 'text': "\n\n".join(texts), 'pages': len(doc)}
    except FileNotFoundError:
        print(f"Warning: PDF file not found: {abs_path}")
        return {'kind':'pdf', 'text': '', 'pages': 0}
    except Exception as e:
        print(f"Warning: PDF extraction failed for {abs_path}: {e}")
        return {'kind':'pdf', 'text': '', 'pages': 0}

def extract_image(abs_path):
    try:
        img = Image.open(abs_path)
        text = pytesseract.image_to_string(img)
        return {'kind':'image', 'text': text, 'meta': {'width': img.width, 'height': img.height}}
    except FileNotFoundError:
        print(f"Warning: Image file not found: {abs_path}")
        return {'kind':'image', 'text': '', 'meta': {}}
    except Exception as e:
        print(f"Warning: Image extraction failed for {abs_path}: {e}")
        return {'kind':'image', 'text': '', 'meta': {}}

def extract_text(body):
    return {'kind':'text', 'text': clean_markdown_to_text(body)}

def extract_content(primary, assets, body, lang=None, attachments_root=None):
    if primary['kind']=='pdf' and primary['path']:
        # Resolve relative path to absolute path
        if attachments_root and not primary['path'].startswith('/'):
            # Remove 'attachments/' prefix from path since attachments_root already points to attachments dir
            relative_path = primary['path']
            if relative_path.startswith('attachments/'):
                relative_path = relative_path[12:]  # Remove 'attachments/' prefix
            abs_path = os.path.join(attachments_root, relative_path)
        else:
            abs_path = primary['path']
        return extract_pdf(abs_path)
    if primary['kind']=='image' and primary['path']:
        # Resolve relative path to absolute path
        if attachments_root and not primary['path'].startswith('/'):
            # Remove 'attachments/' prefix from path since attachments_root already points to attachments dir
            relative_path = primary['path']
            if relative_path.startswith('attachments/'):
                relative_path = relative_path[12:]  # Remove 'attachments/' prefix
            abs_path = os.path.join(attachments_root, relative_path)
        else:
            abs_path = primary['path']
        return extract_image(abs_path)
    return extract_text(body)
