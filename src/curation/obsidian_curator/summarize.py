from .llm import chat_text

# Import unified professional context
from .classify import PROFESSIONAL_CONTEXT

SUM_SYS = f"""{PROFESSIONAL_CONTEXT}

SUMMARIZATION ROLE: You create professional summaries STRICTLY based on provided source material.

CRITICAL ANTI-FABRICATION RULES:
- NEVER invent, elaborate, or create content not explicitly present in the source
- NEVER reference external sources, studies, organizations, or data not mentioned in the provided text
- NEVER add professional context, background, or interpretation beyond what is stated
- If source material is insufficient, incomplete, or unclear, state this honestly
- Every claim must be directly traceable to the provided text

SUMMARY PRINCIPLES:
- EVIDENCE: Only surface claims explicitly stated in the provided text
- CITATIONS: Use page references ONLY if present in the source text
- FORMAT: If insufficient content exists for requested format, provide diagnostic explanation
- TONE: Professional, factual, but strictly limited to source content
- DATA: Extract ONLY numeric estimates and methodologies explicitly mentioned in source
- ATTRIBUTION: Never invent source attribution not present in the text

INTEGRITY OVER FORMAT:
- Honest assessment of insufficient content is preferable to fabricated summaries
- If source lacks professional substance, state this directly
- Do not force professional interpretation onto minimal or unclear content
- Accuracy and truthfulness are more important than completing requested format"""

def summarize_content(content, meta, cats, cfg):
    kind = content.get('kind', 'text')
    title = meta.get('title', '') or ""
    categories = ", ".join(cats) if cats else ""
    text = content.get('text', '') or ""
    pages = content.get('pages', None)
    
    # Extract provenance metadata for better summarization
    source = meta.get('source', '')
    date_created = meta.get('date created', '')
    date_modified = meta.get('date modified', '')
    language = meta.get('language', 'en')
    
    # Fabrication prevention: Check for insufficient content
    if len(text.strip()) < 50:
        return f"**INSUFFICIENT CONTENT FOR PROFESSIONAL SUMMARY**\n\nSource contains insufficient material for professional analysis.\n\n**Available content**: {text.strip()[:200] if text.strip() else 'No readable text found'}\n\n**Assessment**: This note lacks the substantive content required for professional publication use."
    
    if kind=='pdf':
        prompt = f"""CRITICAL ANTI-FABRICATION INSTRUCTIONS:
- ONLY use information explicitly present in the provided text extract
- DO NOT invent, elaborate, or create any content not directly stated in the source
- If the extract lacks sufficient detail for any section, state "Information not available in extract"
- NEVER cite sources, studies, or data not mentioned in the provided text
- If page references cannot be identified from the extract, do not include them

DOCUMENT DETAILS:
Title: {title}
Source: {source if source else 'Not specified'}
Created: {date_created if date_created else 'Not specified'}
Modified: {date_modified if date_modified else 'Not specified'}
Language: {language}
Categories: {categories}
Pages: {pages}
TEXT EXTRACT TO ANALYZE: {text}

CREATE SUMMARY ONLY FROM THE ABOVE TEXT EXTRACT:

**PUBLICATION ABSTRACT** (150-200 words)
Summarize ONLY what is explicitly stated in the text extract above. If the extract is incomplete or unclear, state this limitation.

**TECHNICAL CONTRIBUTIONS** (up to 8 points)
• List ONLY technical points explicitly mentioned in the text extract
• Use page references ONLY if clearly indicated in the extract
• If fewer than 8 points are available in the extract, provide only what exists

**CITATION-READY EXCERPTS**
* Quote ONLY verbatim text from the extract above
* Include page references ONLY if present in the extract
* If no suitable quotes exist in the extract, state "No quotable excerpts available in extract"

**RESEARCH APPLICATIONS** (80-120 words)
Assess value based ONLY on what is described in the text extract. If the extract is insufficient to make assessments, state this clearly.

FINAL CHECK: Ensure every claim in your summary can be traced directly to the provided text extract. Do not add context, background, or elaboration not present in the source."""

        provider = cfg['models'].get('provider', 'openai')
        return chat_text(cfg['models']['main'], system=SUM_SYS, user=prompt, tokens=900, temp=0.2, provider=provider)
        
    if kind=='image':
        prompt = f"""Summarize this image and any OCR'd text for an infrastructure expert. Be precise and avoid speculation.

IMAGE DETAILS:
Title: {title}
Source: {source if source else 'Not specified'}
Created: {date_created if date_created else 'Not specified'}
Modified: {date_modified if date_modified else 'Not specified'}
Language: {language}
Categories: {categories}
OCR_TEXT: {text}

Provide:
1) DESCRIPTION (1 short paragraph): What the image shows (type: photo/diagram/scan), key observable elements, and any metadata (size, orientation, EXIF if available).
2) KEY OBSERVATIONS (4-6 bullets): Concrete details visible or read via OCR (labels, figures, annotations). Mention likely provenance only if supported by metadata.
3) USE-IN-WRITING (2-3 short suggestions): Where this image could support an argument in a technical brief or report (e.g., "illustrates risk of slope failure; cite with photo + caption").
4) CONFIDENCE & ACTION (1 sentence): How reliable the image is as evidence and whether OCR/text extraction should be verified.

Do not invent contextual history or attribution. If OCR is empty, clearly state that and describe only visual features."""
        
        provider = cfg['models'].get('provider', 'openai')
        return chat_text(cfg['models']['fast'], system=SUM_SYS, user=prompt, tokens=500, temp=0.2, provider=provider)
        
    # Text content
    prompt = f"""CRITICAL ANTI-FABRICATION INSTRUCTIONS:
- ONLY summarize content explicitly present in the provided text
- DO NOT invent, elaborate, add context, or create information not in the source
- If the text lacks substance for any section, state "Insufficient information in source"
- NEVER reference external sources, studies, or data not mentioned in the text
- Do not assume professional context unless explicitly stated in the content

DOCUMENT DETAILS:
Title: {title}
Source: {source if source else 'Not specified'}
Created: {date_created if date_created else 'Not specified'}
Modified: {date_modified if date_modified else 'Not specified'}
Language: {language}
Categories: {categories}
ACTUAL CONTENT TO ANALYZE: {text}

ANALYZE ONLY THE ABOVE CONTENT:

**PUBLICATION SUMMARY** (100-150 words)
Describe ONLY what is explicitly present in the provided content. If the content is minimal, brief, or unclear, state this honestly.

**TECHNICAL HIGHLIGHTS** (as many as actually exist)
• List ONLY technical points explicitly mentioned in the content
• Do not invent methodologies, frameworks, or data not present
• If no technical highlights exist in the content, state "No technical content available"

**RESEARCH VALUE** (60-80 words)
Assess based ONLY on what is actually described in the content. If the content lacks professional substance or is unclear, state this directly.

VERIFICATION REQUIREMENT: Every statement in your summary must be directly traceable to the provided content. Do not add professional interpretation, context, or elaboration beyond what is explicitly stated."""
    
    provider = cfg['models'].get('provider', 'openai')
    return chat_text(cfg['models']['fast'], system=SUM_SYS, user=prompt, tokens=400, temp=0.2, provider=provider)
