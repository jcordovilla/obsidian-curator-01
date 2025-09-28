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
            prompt = f"""Analyze this text extracted from an image. Be conservative and factual - only describe what you can reasonably infer from the OCR text.

OCR Text: {ocr_text}

CRITICAL: Do not invent or hallucinate content. If the OCR text is unclear, garbled, or insufficient to determine the image content, state that clearly.

AVOID false assumptions about infrastructure relevance. Just because numbers or technical terms appear doesn't mean it's infrastructure-related.

Describe what the image likely shows based ONLY on the OCR text evidence:"""
            
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

def extract_pdf(abs_path, max_pages=10, max_chars=5000):
    """
    Extract text from PDF with performance optimizations.
    
    Args:
        abs_path: Path to PDF file
        max_pages: Maximum pages to process (default 10 for performance)
        max_chars: Maximum characters to extract (default 5000 for LLM efficiency)
    """
    try:
        doc = fitz.open(abs_path)
        total_pages = len(doc)
        texts = []
        total_chars = 0
        
        # Process limited number of pages for performance
        pages_to_process = min(max_pages, total_pages)
        
        for page_num in range(pages_to_process):
            page = doc[page_num]
            t = page.get_text("text").strip()
            
            # Skip OCR for performance - if no text, just note it
            if not t:
                t = f"[Page {page_num + 1}: Image/scan content - text not extractable]"
            
            texts.append(t)
            total_chars += len(t)
            
            # Stop if we have enough content for summarization
            if total_chars >= max_chars:
                texts.append(f"\n[Content truncated after {page_num + 1} pages for processing efficiency...]")
                break
        
        # Add note if we didn't process all pages
        if pages_to_process < total_pages:
            texts.append(f"\n[Note: Processed {pages_to_process} of {total_pages} pages for efficiency]")
        
        extracted_text = "\n\n".join(texts)
        
        return {
            'kind': 'pdf', 
            'text': extracted_text[:max_chars],  # Hard limit for LLM processing
            'pages': total_pages,
            'pages_processed': pages_to_process
        }
        
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

def resolve_attachment_path(relative_path, attachments_root, note_path=None):
    """Resolve attachment path, handling note-specific folder structures."""
    if not attachments_root or relative_path.startswith('/'):
        return relative_path
    
    # Remove 'attachments/' prefix from path since attachments_root already points to attachments dir
    if relative_path.startswith('attachments/'):
        relative_path = relative_path[12:]  # Remove 'attachments/' prefix
    
    # Try the direct path first
    direct_path = os.path.join(attachments_root, relative_path)
    if os.path.exists(direct_path):
        return direct_path
    
    # If note_path is provided, try note-specific folder structure
    if note_path:
        note_stem = os.path.splitext(os.path.basename(note_path))[0]
        # Extract the folder name from the relative path (e.g., "Topología.resources" from "Topología.resources/file.pdf")
        path_parts = relative_path.split('/')
        if len(path_parts) > 1:
            folder_name = path_parts[0]
            file_name = '/'.join(path_parts[1:])
            
            # Try note-specific folder: note_stem.folder_name
            note_specific_path = os.path.join(attachments_root, f"{note_stem}.{folder_name}", file_name)
            if os.path.exists(note_specific_path):
                return note_specific_path
            
            # Try just the note_stem.resources pattern (common test data structure)
            simple_note_path = os.path.join(attachments_root, f"{note_stem}.resources", file_name)
            if os.path.exists(simple_note_path):
                return simple_note_path
            
            # Try note_stem.md.resources pattern (test data structure)
            md_note_path = os.path.join(attachments_root, f"{note_stem}.md.resources", file_name)
            if os.path.exists(md_note_path):
                return md_note_path
    
    # Fall back to original path
    return direct_path

def extract_text(body):
    return {'kind':'text', 'text': clean_markdown_to_text(body)}

def extract_content(primary, assets, body, lang=None, attachments_root=None, note_path=None):
    if primary['kind']=='pdf' and primary['path']:
        # Resolve relative path to absolute path
        abs_path = resolve_attachment_path(primary['path'], attachments_root, note_path)
        result = extract_pdf(abs_path)
        # If PDF extraction failed or returned empty content, fall back to markdown
        if not result.get('text', '').strip():
            return extract_text(body)
        return result
    if primary['kind']=='image' and primary['path']:
        # Resolve relative path to absolute path
        abs_path = resolve_attachment_path(primary['path'], attachments_root, note_path)
        result = extract_image(abs_path)
        # If image extraction failed or returned empty content, fall back to markdown
        if not result.get('text', '').strip():
            return extract_text(body)
        return result
    return extract_text(body)
