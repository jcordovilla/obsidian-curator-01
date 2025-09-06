import os
import fitz
from PIL import Image
import pytesseract
from .utils import clean_markdown_to_text

TEST_MODE = os.getenv("OC_TEST_MODE") == "1"

def extract_pdf(abs_path):
    if TEST_MODE:
        return {'kind':'pdf','text':'TEST_PDF_TEXT lorem ipsum','pages':3}
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
    if TEST_MODE:
        return {'kind':'image','text':'TEST_OCR_TEXT','meta': {'width': 800, 'height': 600}}
    img = Image.open(abs_path)
    text = pytesseract.image_to_string(img)
    return {'kind':'image', 'text': text, 'meta': {'width': img.width, 'height': img.height}}

def extract_text(body):
    return {'kind':'text', 'text': clean_markdown_to_text(body)}

def extract_content(primary, assets, body, lang=None):
    if TEST_MODE:
        # Map by kind but don't touch filesystem
        if primary['kind']=='pdf':   return extract_pdf(primary.get('path'))
        if primary['kind']=='image': return extract_image(primary.get('path'))
        return {'kind':'text','text':'TEST_NOTE_TEXT for unit tests'}
    if primary['kind']=='pdf' and primary['path']:
        return extract_pdf(primary['path'])
    if primary['kind']=='image' and primary['path']:
        return extract_image(primary['path'])
    return extract_text(body)
