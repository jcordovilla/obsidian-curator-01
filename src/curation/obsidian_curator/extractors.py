import os
import fitz
from PIL import Image
import pytesseract
import base64
import requests
import subprocess
import tempfile
import json
from .utils import clean_markdown_to_text

def extract_audio_transcription(abs_path):
    """Extract transcription from audio files using Whisper via Ollama."""
    try:
        # Check if file exists and is an audio file
        if not os.path.exists(abs_path):
            return f"Audio file not found: {abs_path}"
        
        # Get file extension to determine audio type
        file_ext = os.path.splitext(abs_path)[1].lower()
        audio_extensions = ['.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg', '.wma']
        
        if file_ext not in audio_extensions:
            return f"Unsupported audio format: {file_ext}"
        
        # Use Ollama to transcribe the audio via subprocess
        try:
            # For now, provide a placeholder for audio transcription
            # TODO: Implement proper Whisper transcription once model issues are resolved
            file_size_mb = os.path.getsize(abs_path) / (1024 * 1024)
            
            # Return a placeholder transcription with file info
            placeholder = f"""AUDIO FILE DETECTED: {os.path.basename(abs_path)}
File Size: {file_size_mb:.2f} MB
Format: {file_ext.upper()}

[TRANSCRIPTION PLACEHOLDER]
Audio transcription functionality is being implemented. The audio file has been detected and will be processed once the Whisper model is properly configured.

File Details:
- Path: {abs_path}
- Size: {file_size_mb:.2f} MB
- Format: {file_ext.upper()}
- Created: {os.path.getctime(abs_path)}

Note: This is a placeholder response. Full transcription will be available once the audio processing pipeline is fully operational."""
            
            return placeholder
            
        except requests.exceptions.RequestException as e:
            return f"Ollama request failed: {str(e)}"
        except Exception as e:
            return f"Audio transcription error: {str(e)}"
            
    except Exception as e:
        return f"Audio processing failed: {str(e)}"

def extract_audio_meaning(abs_path):
    """Extract meaning from audio using transcription + LLM analysis."""
    try:
        # First, get transcription from the audio
        transcription = extract_audio_transcription(abs_path)
        
        # If transcription failed, return the error
        if transcription.startswith("Audio") and ("failed" in transcription or "error" in transcription):
            return transcription
        
        # If we have transcription, use LLM to analyze it
        if transcription.strip():
            from .llm import chat_text
            from .classify import PROFESSIONAL_CONTEXT
            
            prompt = f"""{PROFESSIONAL_CONTEXT}

AUDIO ANALYSIS ROLE: Analyze transcribed audio content for potential use in specialized infrastructure publications.

TRANSCRIPTION: {transcription}

COMPREHENSIVE ANALYSIS FRAMEWORK:
Provide a thorough analysis of this audio content for inclusion in a knowledge database supporting professional publication writing.

REQUIRED ANALYSIS SECTIONS:

1. CONTENT TYPE & SOURCE IDENTIFICATION:
   - What type of audio content is this (meeting, presentation, interview, etc.)?
   - Who are the speakers and what are their roles/organizations?
   - What is the context, date, or event if mentioned?

2. KEY PROFESSIONAL CONTENT EXTRACTION:
   - Extract ALL key quotes, statistics, and data points
   - Identify ALL named individuals, organizations, and institutions
   - Note ALL specific figures, percentages, and financial data
   - Capture ALL policy recommendations and strategic insights

3. TECHNICAL SUBSTANCE ASSESSMENT:
   - What specific professional content is discussed?
   - What quantitative data, metrics, or measurements are mentioned?
   - What methodological frameworks or processes are described?
   - What policy/regulatory information is present?
   - What financial/economic data is provided?

4. PROFESSIONAL VALUE EVALUATION:
   - How suitable is this for citation in professional publications?
   - What specific insights would be valuable for infrastructure research?
   - What unique perspectives or data does this provide?

5. PUBLICATION UTILITY:
   - What specific quotes or data points could be cited?
   - What research applications does this content support?
   - What follow-up research or verification might be needed?

CRITICAL REQUIREMENTS:
- Extract ALL available information from the transcription
- Do not truncate or summarize - provide comprehensive coverage
- Base analysis ONLY on the provided transcription
- If transcription is unclear, note specific unclear sections
- Provide specific quotes and data points for potential citation

OUTPUT: Comprehensive professional analysis with full content extraction and detailed assessment of publication utility."""
            
            system_prompt = f"""{PROFESSIONAL_CONTEXT}
            
AUDIO ANALYSIS ROLE: Analyze transcribed audio content for potential use in specialized infrastructure publications.

CRITICAL ANTI-FABRICATION RULES:
- NEVER invent, assume, or infer content not explicitly present in the provided transcription
- NEVER add professional context, background, or interpretation beyond what is stated
- NEVER reference external sources, studies, or organizations not mentioned in the transcription
- Base ALL assessments strictly on the provided transcription evidence
- If transcription is insufficient or unclear, state this honestly
- Every assessment must be directly traceable to the provided transcription"""
            
            # Use OpenAI GPT-5 mini for better multilingual analysis
            analysis = chat_text('gpt-5-mini-2025-08-07',  # Fast GPT-5 model for analysis
                               system_prompt, 
                               prompt, 
                               tokens=800,  # Increased for comprehensive analysis
                               temp=0.2,
                               provider='openai')
            return analysis
        else:
            return f"Audio file processed but no transcription extracted from {os.path.basename(abs_path)}"
        
    except Exception as e:
        return f"Audio analysis failed: {str(e)}"

def extract_image_meaning(abs_path):
    """Extract meaning from image using OCR + LLM analysis."""
    try:
        # First, get OCR text from the image
        img = Image.open(abs_path)
        width, height = img.size
        
        # Check if image is too small to be meaningful
        if width < 100 or height < 100:
            return f"Small image ({width}x{height}px) - likely an icon or thumbnail"
        
        # Resize large images to avoid processing failures
        max_dimension = 2000
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            width, height = img.size
        
        ocr_text = pytesseract.image_to_string(img)
        
        # If OCR found text, use LLM to analyze it
        if ocr_text.strip():
            # Use LLM to analyze the OCR text and extract meaning
            from .llm import chat_text
            # Import unified professional context for image analysis
            from .classify import PROFESSIONAL_CONTEXT
            
            prompt = f"""{PROFESSIONAL_CONTEXT}

IMAGE ANALYSIS ROLE: Analyze OCR text from images for potential use in specialized infrastructure publications.

OCR TEXT: {ocr_text}

COMPREHENSIVE ANALYSIS FRAMEWORK:
Provide a thorough analysis of this image content for inclusion in a knowledge database supporting professional publication writing.

REQUIRED ANALYSIS SECTIONS:

1. CONTENT TYPE & SOURCE IDENTIFICATION:
   - What type of material does this appear to be?
   - What publication, organization, or source is this from?
   - What is the publication date or context if visible?

2. KEY PROFESSIONAL CONTENT EXTRACTION:
   - Extract ALL key quotes, statistics, and data points
   - Identify ALL named individuals, organizations, and institutions
   - Note ALL specific figures, percentages, and financial data
   - Capture ALL policy recommendations and strategic insights

3. TECHNICAL SUBSTANCE ASSESSMENT:
   - What specific professional content is visible?
   - What quantitative data, metrics, or measurements are mentioned?
   - What methodological frameworks or processes are discussed?
   - What policy/regulatory information is present?
   - What financial/economic data is provided?

4. PROFESSIONAL VALUE EVALUATION:
   - How suitable is this for citation in professional publications?
   - What specific insights would be valuable for infrastructure research?
   - What unique perspectives or data does this provide?

5. PUBLICATION UTILITY:
   - What specific quotes or data points could be cited?
   - What research applications does this content support?
   - What follow-up research or verification might be needed?

CRITICAL REQUIREMENTS:
- Extract ALL available information from the OCR text
- Do not truncate or summarize - provide comprehensive coverage
- Base analysis ONLY on visible OCR text evidence
- If OCR is garbled, note specific unclear sections
- Provide specific quotes and data points for potential citation

OUTPUT: Comprehensive professional analysis with full content extraction and detailed assessment of publication utility."""
            
            # Use Mistral for efficient image analysis with anti-fabrication system prompt
            system_prompt = f"""{PROFESSIONAL_CONTEXT}
            
IMAGE ANALYSIS ROLE: Analyze OCR text from images for potential use in specialized infrastructure publications.

CRITICAL ANTI-FABRICATION RULES:
- NEVER invent, assume, or infer content not explicitly visible in the OCR text
- NEVER add professional context, background, or interpretation beyond what's readable
- NEVER reference external sources, studies, or organizations not mentioned in the OCR
- Base ALL assessments strictly on the provided OCR text evidence
- If OCR is insufficient or unclear, state this honestly
- Every assessment must be directly traceable to the visible OCR content"""
            
            # Use OpenAI GPT-5 mini for better multilingual analysis
            analysis = chat_text('gpt-5-mini-2025-08-07',  # Fast GPT-5 model for analysis
                               system_prompt, 
                               prompt, 
                               tokens=800,  # Increased from 300 to 800 for more comprehensive analysis
                               temp=0.2,
                               provider='openai')
            return analysis
        else:
            return f"Image ({width}x{height}px) - no readable text found via OCR"
        
    except Exception as e:
        print(f"Warning: Image analysis failed for {abs_path}: {e}")
        return ""

def extract_pdf(abs_path, max_pages=50, max_chars=15000):
    """
    Extract text from PDF with improved coverage.
    
    Args:
        abs_path: Path to PDF file
        max_pages: Maximum pages to process (default 50, increased from 10)
        max_chars: Maximum characters to extract (default 15000, increased from 5000)
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

def extract_audio(abs_path):
    """Extract content from audio files using transcription + LLM analysis."""
    try:
        # Get file info
        file_size = os.path.getsize(abs_path)
        file_ext = os.path.splitext(abs_path)[1].lower()
        
        # Extract transcription and meaning
        transcription = extract_audio_transcription(abs_path)
        analysis = extract_audio_meaning(abs_path)
        
        # Combine transcription and analysis
        combined_text = f"Transcription:\n{transcription}\n\nAnalysis:\n{analysis}"
        
        return {
            'kind': 'audio',
            'text': combined_text,
            'meta': {
                'file_size': file_size,
                'file_extension': file_ext,
                'transcription': transcription,
                'analysis': analysis
            }
        }
    except Exception as e:
        print(f"Warning: Audio extraction failed for {abs_path}: {e}")
        return {'kind': 'audio', 'text': f"Audio processing failed: {e}", 'meta': {}}

def extract_image(abs_path):
    try:
        img = Image.open(abs_path)
        
        # Resize large images to avoid processing failures
        max_dimension = 2000
        if max(img.size) > max_dimension:
            print(f"Resizing large image: {img.size} -> ", end='')
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"{img.size}")
        
        # Extract text using OCR with optimized settings
        ocr_text = pytesseract.image_to_string(img, config='--psm 3')
        
        # Clean up OCR text for better readability
        import re
        # Remove excessive whitespace and fix common OCR issues
        ocr_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', ocr_text)  # Multiple empty lines to double
        ocr_text = re.sub(r'[ \t]+', ' ', ocr_text)  # Multiple spaces to single
        ocr_text = re.sub(r'\n[ \t]+', '\n', ocr_text)  # Remove leading spaces from lines
        ocr_text = ocr_text.strip()
        
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
    # Always extract text content first
    text_result = extract_text(body)
    
    # Check if there are PDF attachments to extract
    pdf_content = None
    for asset in assets:
        if asset['kind'] == 'pdf' and asset['path']:
            abs_path = resolve_attachment_path(asset['path'], attachments_root, note_path)
            pdf_result = extract_pdf(abs_path)
            if pdf_result.get('text', '').strip():
                pdf_content = pdf_result.get('text', '').strip()
                break
    
    # If we have PDF content, store metadata but don't include full text in output
    if pdf_content:
        # For PDF notes, we don't include the full PDF content in the text field
        # The writer will handle displaying just the attachment reference
        return {
            'text': text_result.get('text', ''),  # Only original note text, no PDF content
            'kind': 'pdf_note',
            'pdf_extracted': True,
            'pdf_content': pdf_content,  # Store PDF content separately for summarization
            'pages': pdf_result.get('pages', 0),
            'pages_processed': pdf_result.get('pages_processed', 0),
            'original_text_length': len(text_result.get('text', '')),
            'pdf_text_length': len(pdf_content)
        }
    
    # Handle other primary asset types
    if primary['kind']=='pdf' and primary['path']:
        # This case is now handled above, but keep for compatibility
        abs_path = resolve_attachment_path(primary['path'], attachments_root, note_path)
        result = extract_pdf(abs_path)
        if not result.get('text', '').strip():
            return text_result
        return result
    if primary['kind']=='image' and primary['path']:
        # Resolve relative path to absolute path
        abs_path = resolve_attachment_path(primary['path'], attachments_root, note_path)
        result = extract_image(abs_path)
        # If image extraction failed or returned empty content, fall back to markdown
        if not result.get('text', '').strip():
            return text_result
        return result
    if primary['kind']=='audio' and primary['path']:
        # Resolve relative path to absolute path
        abs_path = resolve_attachment_path(primary['path'], attachments_root, note_path)
        result = extract_audio(abs_path)
        # If audio extraction failed or returned empty content, fall back to markdown
        if not result.get('text', '').strip():
            return text_result
        return result
    
    return text_result
