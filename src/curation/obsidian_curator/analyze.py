import math, re
from .llm import embed_text, chat_json

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

def get_llm_relevance_score(text, title, cfg):
    """Use LLM to assess professional relevance for infrastructure expert."""
    
    # Truncate text for LLM processing
    text_sample = text[:3000] if len(text) > 3000 else text
    
    prompt = f"""You are evaluating content for a senior infrastructure investment professional who works across multiple domains including financing, technology, governance, and risk management.

    TITLE: {title}
    CONTENT: {text_sample}

    Rate this content on:
    - relevance: How relevant is this to the professional knowledge needs of a senior infrastructure investment specialist? (0-1)
    - credibility: How credible is the source? (0-1) 
    - novelty: How novel/insightful is the content? (0-1)

    RELEVANCE GUIDELINES:
    - HIGHLY RELEVANT (0.8-1.0): Direct infrastructure projects, PPPs, project finance, digital transformation, emerging technologies, financial instruments, technical analysis, case studies, professional reports
    - MODERATELY RELEVANT (0.5-0.7): Alternative financing methods, business development, professional practices, sector analysis, technology applications, academic content, financial services
    - LOW RELEVANCE (0.2-0.4): General business content, social media marketing, personal productivity
    - IRRELEVANT (0.0-0.1): Personal documents, bills, casual notes, unrelated content

    CRITICAL EXCLUSIONS - Rate as IRRELEVANT (0.0-0.1):
    - Software documentation, user manuals, technical tutorials (unless about infrastructure-specific tools)
    - Company websites, marketing materials, navigation pages
    - Personal notes, reminders, to-do lists
    - News headlines without analysis or insights
    - Generic business advice not specific to infrastructure
    - Screenshots or images without substantive professional content
    - Audio/video files without transcripts or descriptions

    PROFESSIONAL CONTEXT: This professional needs knowledge across financing methods, emerging technologies, governance practices, and risk management to inform infrastructure investment decisions. Content must provide actionable professional knowledge, not just mention infrastructure topics.

    IMPORTANT: Be conservative. If content appears to be documentation, tutorials, basic news, or company marketing rather than professional analysis or insights, rate relevance as LOW (0.2) or IRRELEVANT (0.0-0.1).

    Return JSON: {{"relevance": 0.xx, "credibility": 0.xx, "novelty": 0.xx, "reasoning": "brief explanation"}}"""

    try:
        result = chat_json(cfg['models']['fast'], 
                          system="You are an expert evaluator for professional knowledge curation. Return strict JSON only.",
                          user=prompt, 
                          tokens=400, 
                          temp=0.3)  # Higher temperature for more creative relevance reasoning
        
        return {
            'relevance': min(1.0, max(0.0, result.get('relevance', 0.5))),
            'credibility': min(1.0, max(0.0, result.get('credibility', 0.5))),
            'novelty': min(1.0, max(0.0, result.get('novelty', result.get('novelity', 0.5)))),  # Handle typo in LLM response
            'reasoning': result.get('reasoning', 'No reasoning provided')
        }
    except Exception as e:
        print(f"Warning: LLM relevance scoring failed: {e}")
        # Fallback to basic heuristics
        return {
            'relevance': 0.3,
            'credibility': 0.4,
            'novelty': 0.3,
            'reasoning': 'LLM scoring failed, using fallback'
        }

def analyze_features(content, meta, cfg, relevance_score=None):
    """Analyze content features with LLM-powered professional relevance assessment."""
    text = content.get('text','')
    title = meta.get('title', '')
    
    embedding = embed_text(text, cfg['models']['embed']) if text else None
    
    # Get LLM-based professional relevance assessment
    llm_scores = get_llm_relevance_score(text, title, cfg)
    
    features = {
        'length_chars': len(text),
        'has_numbers': any(ch.isdigit() for ch in text),
        'sections': text.count('\n## '),
        'embedding': embedding,
        'relevance': llm_scores['relevance'],
        'credibility': llm_scores['credibility'],
        'novelty': llm_scores['novelty'],
        'richness': calculate_content_richness(text, title, meta),  # More sophisticated richness calculation
        'llm_reasoning': llm_scores['reasoning']
    }
    return features

def score_usefulness(feats, cfg):
    """Score usefulness using LLM-assessed professional relevance."""
    # More balanced weights - relevance is key but not overwhelming
    w = dict(relevance=0.70, credibility=0.20, novelty=0.05, richness=0.05)
    
    # Simple weighted combination of LLM scores plus content richness
    score = (w['relevance'] * feats['relevance'] +
             w['credibility'] * feats['credibility'] +
             w['novelty'] * feats['novelty'] +
             w['richness'] * feats['richness'])
    
    return max(0.0, min(1.0, score))

def decide(score, decision_cfg):
    th = decision_cfg['keep_threshold']
    m  = decision_cfg['gray_margin']
    if score >= th: return 'keep'
    if score <= th - m: return 'discard'
    return 'triage'
