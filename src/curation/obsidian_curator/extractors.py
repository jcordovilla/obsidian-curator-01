import os
import fitz
from PIL import Image
import pytesseract
import base64
import requests
from .utils import clean_markdown_to_text

def extract_image_meaning(abs_path):
    """Extract meaning from image using OCR + LLM analysis."""
    try:
        # First, get OCR text from the image
        img = Image.open(abs_path)
        width, height = img.size
        
        # Check if image is too small to be meaningful
        if width < 100 or height < 100:
            return f"Small image ({width}x{height}px) - likely an icon or thumbnail"
        
        ocr_text = pytesseract.image_to_string(img)
        
        # If OCR found text, use LLM to analyze it
        if ocr_text.strip():
            # Use LLM to analyze the OCR text and extract meaning
            from .llm import chat_text
            prompt = f"""Analyze this text extracted from an image and describe what the image contains, focusing on any diagrams, charts, or visual information that would be relevant for infrastructure investment, PPPs, or project finance.

OCR Text: {ocr_text}

Describe what you think the image shows based on this text:"""
            
            # Use a simple text model since vision models aren't available
            analysis = chat_text('gemma3:4b', 
                               "You are an expert at analyzing technical content from images.", 
                               prompt, 
                               tokens=300, 
                               temp=0.2)
            return analysis
        else:
            return f"Image ({width}x{height}px) - no readable text found via OCR"
        
    except Exception as e:
        print(f"Warning: Image analysis failed for {abs_path}: {e}")
        return ""

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
        
        # Extract text using OCR
        ocr_text = pytesseract.image_to_string(img)
        
        # Extract meaning using vision model
        vision_text = extract_image_meaning(abs_path)
        
        # Combine OCR and vision analysis
        combined_text = f"OCR Text:\n{ocr_text}\n\nVision Analysis:\n{vision_text}"
        
        return {
            'kind': 'image',
            'text': combined_text, 
            'meta': {
                'width': img.width, 
                'height': img.height,
                'ocr_text': ocr_text,
                'vision_analysis': vision_text
            }
        }
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
        result = extract_pdf(abs_path)
        # If PDF extraction failed or returned empty content, fall back to markdown
        if not result.get('text', '').strip():
            return extract_text(body)
        return result
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
        result = extract_image(abs_path)
        # If image extraction failed or returned empty content, fall back to markdown
        if not result.get('text', '').strip():
            return extract_text(body)
        return result
    return extract_text(body)
