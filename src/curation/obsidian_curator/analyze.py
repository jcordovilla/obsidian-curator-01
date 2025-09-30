import math, re
from .llm import embed_text, chat_json

# Import unified professional context
from .classify import PROFESSIONAL_CONTEXT

def calculate_content_richness(text, title, meta):
    """Calculate content richness considering content type and quality."""
    # Basic length-based richness
    length_richness = min(1.0, math.log1p(len(text))/8.0)
    
    title_lower = title.lower()
    text_lower = text.lower()
    
    # Check for low-value content types that should be heavily penalized
    low_value_indicators = [
        # Screenshots and images without content
        'snapshot', 'captura', 'screenshot', 'image', 'picture',
        # Business cards and contact info
        'tarjeta de visita', 'business card', 'contact', 'email', 'phone', 'teléfono',
        'director', 'comercial', 'manager', 'ceo', 'cto', 'cfo',
        # Bills and invoices
        'bill', 'invoice', 'factura', 'movistar', 'adsl',
        # Simple lists without analysis
        'clientes', 'customers', 'companies', 'empresas',
        # Software documentation and tools
        'waternetgen', 'software', 'extension', 'epanet', 'tool', 'utility', 'manual', 'documentation',
        'download', 'version', 'exe', 'zip', 'install', 'setup', 'tutorial',
        # Company websites and marketing
        'website', 'homepage', 'navigation', 'menu', 'footer', 'header',
        'about us', 'contact us', 'get in touch', 'our team', 'office locations',
        # Personal content
        'audio', 'video', 'reminder', 'todo', 'task', 'personal', 'wallet', 'recovery'
    ]
    
    # If it looks like low-value content, heavily penalize
    if any(indicator in title_lower or indicator in text_lower for indicator in low_value_indicators):
        # Low-value content should have very low richness
        return min(0.1, length_richness * 0.1)
    
    # Check for content that's just lists or names without analysis
    if len(text) < 200 and (text.count('\n- ') > 5 or text.count('\n* ') > 5):
        # Just a list without substantial content
        return min(0.3, length_richness * 0.5)
    
    # Check for content that's mostly boilerplate or navigation
    if text.count('http://') > 10 and len(text) < 1000:
        # Too many links, likely navigation/boilerplate
        return min(0.4, length_richness * 0.6)
    
    # Check for website navigation patterns
    nav_patterns = ['skip to main content', 'footer', 'header', 'navigation', 'menu',
                   'get in touch', 'contact us', 'about us', 'our team', 'office locations',
                   'read more', 'click here', 'learn more']
    nav_count = sum(1 for pattern in nav_patterns if pattern in text_lower)
    if nav_count > 3 and len(text) < 2000:
        # Likely website navigation content
        return min(0.3, length_richness * 0.4)
    
    # Check for content that's mostly just images
    if text.count('![') > 2 and len(text) < 300:
        # Mostly images, likely low-value
        return min(0.2, length_richness * 0.3)
    
    # Check for structured content (sections, lists, etc.)
    structure_score = 0
    if text.count('\n## ') > 0:  # Has sections
        structure_score += 0.2
    if text.count('\n- ') > 3 or text.count('\n* ') > 3:  # Has lists
        structure_score += 0.2
    if text.count('\n\n') > 2:  # Has paragraphs
        structure_score += 0.1
    
    # Check for professional content indicators
    professional_indicators = [
        'analysis', 'report', 'study', 'research', 'project', 'investment',
        'infrastructure', 'finance', 'governance', 'risk', 'management',
        'technology', 'development', 'strategy', 'policy', 'regulation'
    ]
    
    if any(indicator in text_lower for indicator in professional_indicators):
        structure_score += 0.2
    
    # Combine length and structure
    final_richness = min(1.0, length_richness + structure_score)
    return final_richness

def get_llm_relevance_score(text, title, meta, cfg):
    """Use LLM to assess professional relevance for publication-ready content."""
    
    # Truncate text for LLM processing
    text_sample = text[:3000] if len(text) > 3000 else text
    
    # Extract metadata for better credibility assessment
    source = meta.get('source', 'Not specified')
    language = meta.get('language', 'Unknown')
    date_created = meta.get('date created', 'Unknown')
    date_modified = meta.get('date modified', 'Unknown')
    
    prompt = f"""{PROFESSIONAL_CONTEXT}

RELEVANCE ANALYSIS ROLE: Evaluate content for inclusion in a specialized knowledge database supporting professional publication writing.

CRITICAL ANTI-FABRICATION RULES:
- NEVER invent, assume, or infer content not explicitly present in the provided text
- NEVER add professional context, background, or interpretation beyond what is stated
- NEVER reference external sources, studies, or organizations not mentioned in the text
- Base ALL assessments strictly on the provided document metadata and content
- If content is insufficient for proper evaluation, state this honestly
- Every assessment must be directly traceable to the source material

DOCUMENT METADATA:
Title: {title}
Source: {source}
Language: {language}
Created: {date_created}
Modified: {date_modified}

CONTENT: {text_sample}

EVALUATION DIMENSIONS:
Rate each dimension (0-1) based on suitability for professional publications:

1. PROFESSIONAL RELEVANCE: How valuable is this for infrastructure investment publications?
   - PUBLICATION-READY (0.8-1.0): Primary sources, research reports, technical analysis, case studies with concrete data
   - PROFESSIONALLY USEFUL (0.6-0.79): Expert commentary, sector analysis, methodological frameworks
   - BACKGROUND VALUE (0.4-0.59): General industry information, basic concepts, contextual material  
   - LIMITED VALUE (0.2-0.39): Tangentially related content, marketing materials, news without analysis
   - NO VALUE (0.0-0.19): Personal notes, unrelated content, corrupted data

2. SOURCE CREDIBILITY: How trustworthy and authoritative is the source?
   - AUTHORITATIVE (0.8-1.0): Government agencies, established research institutions, peer-reviewed sources
   - CREDIBLE (0.6-0.79): Industry publications, professional organizations, expert practitioners
   - MODERATE (0.4-0.59): Trade publications, company reports, conference presentations
   - QUESTIONABLE (0.2-0.39): Blogs, social media, unverified sources
   - UNRELIABLE (0.0-0.19): Anonymous sources, clearly biased material, broken links

3. CONTENT DEPTH: How substantial and detailed is the technical content?
   - COMPREHENSIVE (0.8-1.0): Detailed methodology, extensive data, thorough analysis
   - SUBSTANTIAL (0.6-0.79): Good technical detail, some data/evidence, clear frameworks
   - ADEQUATE (0.4-0.59): Basic technical content, limited data, general frameworks
   - SUPERFICIAL (0.2-0.39): High-level overview, minimal detail, mostly descriptive
   - INSUFFICIENT (0.0-0.19): No technical substance, only headlines/summaries

CRITICAL EXCLUSIONS (automatic 0.0-0.2 scores):
- Personal documents, bills, to-do lists, reminders
- Software manuals, user guides (unless infrastructure-specific)
- Marketing materials, company websites, promotional content
- Corrupted files, placeholder content, navigation elements
- News headlines without analysis or expert commentary

CONTEXT: Content will be used to support writing of academic papers, industry reports, investment analyses, and policy briefings. Prioritize material that provides citable evidence, concrete data, and professional insights.

Return JSON: {{"relevance": 0.xx, "credibility": 0.xx, "depth": 0.xx, "reasoning": "concise explanation focusing on publication utility"}}"""

    try:
        result = chat_json(cfg['models']['fast'], 
                          system=f"""{PROFESSIONAL_CONTEXT}
                          
EXPERT EVALUATOR ROLE: You are an expert evaluator for professional knowledge curation.

CRITICAL ANTI-FABRICATION RULES:
- NEVER invent, assume, or infer content not explicitly present in the provided text
- NEVER add professional context, background, or interpretation beyond what is stated
- NEVER reference external sources, studies, or organizations not mentioned in the text
- Base ALL assessments strictly on the provided document metadata and content
- If content is insufficient for proper evaluation, state this honestly
- Every assessment must be directly traceable to the source material

Return strict JSON only.""",
                          user=prompt, 
                          tokens=400, 
                          temp=0.3)  # Higher temperature for more creative relevance reasoning
        
        return {
            'relevance': min(1.0, max(0.0, result.get('relevance', 0.5))),
            'credibility': min(1.0, max(0.0, result.get('credibility', 0.5))),
            'depth': min(1.0, max(0.0, result.get('depth', 0.5))),  # Changed from novelty to depth
            'llm_reasoning': result.get('reasoning', 'No reasoning provided')
        }
    except Exception as e:
        print(f"Warning: LLM relevance scoring failed: {e}")
        # Fallback to basic heuristics
        return {
            'relevance': 0.3,
            'credibility': 0.4,
            'depth': 0.3,
            'llm_reasoning': 'LLM scoring failed, using fallback'
        }

def analyze_features(content, meta, cfg, relevance_score=None):
    """Analyze content features with LLM-powered professional relevance assessment."""
    text = content.get('text','')
    title = meta.get('title', '')
    
    embedding = embed_text(text, cfg['models']['embed']) if text else None
    
    # Get LLM-based professional relevance assessment
    llm_scores = get_llm_relevance_score(text, title, meta, cfg)
    
    features = {
        'length_chars': len(text),
        'has_numbers': any(ch.isdigit() for ch in text),
        'sections': text.count('\n## '),
        'embedding': embedding,
        'relevance': llm_scores['relevance'],
        'credibility': llm_scores['credibility'],
        'depth': llm_scores['depth'],  # Changed from novelty to depth
        'richness': calculate_content_richness(text, title, meta),  # More sophisticated richness calculation
        'llm_reasoning': llm_scores['llm_reasoning']
    }
    return features

def score_usefulness(feats, cfg):
    """Score usefulness using LLM-assessed professional relevance for publications."""
    # Publication-focused weights - emphasize relevance and depth for citation quality
    w = dict(relevance=0.45, credibility=0.25, depth=0.20, richness=0.10)
    
    # Weighted combination optimized for publication utility
    score = (w['relevance'] * feats['relevance'] +
             w['credibility'] * feats['credibility'] +
             w['depth'] * feats['depth'] +
             w['richness'] * feats['richness'])
    
    return max(0.0, min(1.0, score))

def decide(score, decision_cfg):
    th = decision_cfg['keep_threshold']
    m  = decision_cfg['gray_margin']
    if score >= th: return 'keep'
    if score <= th - m: return 'discard'
    return 'triage'
