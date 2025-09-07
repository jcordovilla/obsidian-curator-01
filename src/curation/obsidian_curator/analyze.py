import math, re
from .llm import embed_text, chat_json

def calculate_content_richness(text, title, meta):
    """Calculate content richness considering content type and quality."""
    # Basic length-based richness
    length_richness = min(1.0, math.log1p(len(text))/8.0)
    
    # Check for business card patterns
    business_card_indicators = [
        'tarjeta de visita', 'business card', 'contact', 'email', 'phone', 'teléfono',
        'director', 'comercial', 'manager', 'ceo', 'cto', 'cfo'
    ]
    
    title_lower = title.lower()
    text_lower = text.lower()
    
    # If it looks like a business card, cap the richness
    if any(indicator in title_lower or indicator in text_lower for indicator in business_card_indicators):
        # Business cards should have low richness regardless of length
        return min(0.3, length_richness)
    
    # Check for other low-value content types
    if 'email' in text_lower and 'phone' in text_lower and len(text) < 500:
        # Looks like contact information
        return min(0.4, length_richness)
    
    # Check for structured content (sections, lists, etc.)
    structure_score = 0
    if text.count('\n## ') > 0:  # Has sections
        structure_score += 0.2
    if text.count('\n- ') > 3 or text.count('\n* ') > 3:  # Has lists
        structure_score += 0.2
    if text.count('\n\n') > 2:  # Has paragraphs
        structure_score += 0.1
    
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

    PROFESSIONAL CONTEXT: This professional needs knowledge across financing methods, emerging technologies, governance practices, and risk management to inform infrastructure investment decisions. Content that provides professional knowledge applicable to infrastructure work should be rated highly, even if not directly about infrastructure projects.

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
