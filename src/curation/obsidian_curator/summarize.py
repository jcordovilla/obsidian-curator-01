from .llm import chat_text

SUM_SYS = """You produce conservative, professional summaries for a Chartered Civil Engineer specializing in infrastructure investment, digital transformation and PPPs. Require concrete substance (data, methods, frameworks, case evidence, legislation, contracts). Avoid keyword-only matches. Write for senior practitioners: clear, factual, and citation-aware when possible. 

Global expectations:
- Tone: professional, concise, and factual for senior practitioners.
- Evidence rules: if a claim is not directly supported by the provided text, label it as 'unsupported' rather than asserting it.
- Citation: when the input includes page or section markers, preserve them in summaries (e.g., "(p.3)"). When no page markers exist, do not invent them.
- Output discipline: obey the user prompt format exactly (headings, bullets, counts). If unable to comply (e.g., insufficient text), return a short, explicit diagnostic (e.g., "insufficient substance: only links/filenames").
- Data handling: extract and surface numeric estimates, modelling approaches, and key assumptions when present; flag estimates lacking context.
- Confidentiality & safety: do not expose or invent personal contact details or private credentials.
- Language & style: use neutral language, avoid superlatives unless supported; keep single-paragraph abstracts at the requested length.

Do not fabricate missing data. If the user requests an output structure you cannot fill due to missing evidence, return the structure with placeholders and short notes explaining what's missing."""

def summarize_content(content, meta, cats, cfg):
    kind = content.get('kind', 'text')
    title = meta.get('title', '') or ""
    categories = ", ".join(cats) if cats else ""
    text = content.get('text', '') or ""
    pages = content.get('pages', None)
    
    if kind=='pdf':
        prompt = f"""Summarize this PDF for a senior infrastructure consultant. Be conservative: only surface claims supported by text. If page numbers can be identified, tag items with (p.X).

TITLE: {title}
CATEGORIES: {categories}
PAGES: {pages}
EXTRACT: {text}

Produce exactly the following sections:
1) PROFESSIONAL ABSTRACT (120-150 words): Concise, factual summary emphasizing the document's technical/financial/governance contributions, methods, and main conclusions. Use neutral, professional language.
2) KEY FINDINGS (8 bullets): Each bullet a single sentence with the strongest claims, data points or methodological notes. When possible, append a page hint like (p.3). Be specific (e.g., metrics, cost estimates, models used).
3) QUOTABLES (2 short quotes <= 30 words each): Extract verbatim sentences or fragments clearly identified with page refs.
4) WHY IT MATTERS (one short paragraph <= 60 words): Practical implications for infrastructure investment, PPPs or digital transformation and a note on confidence (high/medium/low) based on evidence in the text.

Tone: conservative, evidence-first. Do not invent data. If evidence is absent for a claim, flag it as "unsupported"."""

        return chat_text(cfg['models']['main'], system=SUM_SYS, user=prompt, tokens=900, temp=0.2)
        
    if kind=='image':
        prompt = f"""Summarize this image and any OCR'd text for an infrastructure expert. Be precise and avoid speculation.

TITLE: {title}
CATEGORIES: {categories}
OCR_TEXT: {text}

Provide:
1) DESCRIPTION (1 short paragraph): What the image shows (type: photo/diagram/scan), key observable elements, and any metadata (size, orientation, EXIF if available).
2) KEY OBSERVATIONS (4-6 bullets): Concrete details visible or read via OCR (labels, figures, annotations). Mention likely provenance only if supported by metadata.
3) USE-IN-WRITING (2-3 short suggestions): Where this image could support an argument in a technical brief or report (e.g., "illustrates risk of slope failure; cite with photo + caption").
4) CONFIDENCE & ACTION (1 sentence): How reliable the image is as evidence and whether OCR/text extraction should be verified.

Do not invent contextual history or attribution. If OCR is empty, clearly state that and describe only visual features."""
        
        return chat_text(cfg['models']['fast'], system=SUM_SYS, user=prompt, tokens=500, temp=0.2)
        
    # Text content
    prompt = f"""Summarize this text note for a senior infrastructure practitioner. Be conservative: emphasise methods, data, technical detail and implications.

TITLE: {title}
CATEGORIES: {categories}
CONTENT: {text}

Output exactly:
1) PROFESSIONAL SUMMARY (80-120 words): Key technical/financial/governance insights, methods used, and main takeaways.
2) KEY POINTS (3-4 bullets): Specific actionable details or evidence (numbers, frameworks, named models).
3) RELEVANCE (1 sentence): State which canonical category is satisfied (Finance & Economics | Policy & Governance | Risk & Sustainability | Technology & Innovation | Knowledge & Professional Practice) and why, referencing concrete text.

Constraints: If the content lacks technical substance (e.g., <100 words, only links or placeholders), state that explicitly and keep relevance low. Avoid speculation and do not invent facts."""
    
    return chat_text(cfg['models']['fast'], system=SUM_SYS, user=prompt, tokens=400, temp=0.2)
