import fitz
from PIL import Image
import pytesseract
from .utils import clean_markdown_to_text

def extract_pdf(abs_path):
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

def extract_image(abs_path):
    img = Image.open(abs_path)
    text = pytesseract.image_to_string(img)
    return {'kind':'image', 'text': text, 'meta': {'width': img.width, 'height': img.height}}

def extract_text(body):
    return {'kind':'text', 'text': clean_markdown_to_text(body)}

def extract_content(primary, assets, body, lang=None):
    if primary['kind']=='pdf' and primary['path']:
        return extract_pdf(primary['path'])
    if primary['kind']=='image' and primary['path']:
        return extract_image(primary['path'])
    return extract_text(body)
