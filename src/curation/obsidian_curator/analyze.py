import math, re
from .llm import embed_text, chat_json

def get_llm_relevance_score(text, title, cfg):
    """Use LLM to assess professional relevance for infrastructure expert."""
    
    # Truncate text for LLM processing
    text_sample = text[:3000] if len(text) > 3000 else text
    
    prompt = f"""You are evaluating content for a senior consultant specializing in infrastructure investment, digital transformation, and PPPs.

TITLE: {title}
CONTENT: {text_sample}

    RELEVANT CONTENT (score 0.7-1.0):
        1. Finance & Economics
        Technical and financial analysis of infrastructure projects, PPPs, and concessions
        M&A activity, investment flows, and market intelligence in infrastructure sectors
        Financing instruments, blended finance, and project finance structures
        Infrastructure economics, value for money assessments, and fiscal impacts
        2. Policy & Governance
        Policy documents, regulatory frameworks, and legislative frameworks
        International development policies, multilateral guidelines, and donor frameworks
        Procurement strategies, contracting models, PPP governance, and institutional practices
        Historical precedents, comparative case law, and accumulated professional know-how
        3. Risk & Sustainability
        Risk management, uncertainty modeling, and scenario planning in infrastructure delivery
        Sustainability, resilience, climate adaptation, and environmental impact assessments
        4. Technology & Innovation
        Innovation, digital transformation, and smart infrastructure systems
        Embedded technologies: IoT, intelligent buildings, monitoring and control systems
        Data-driven insights: Big Data, AI, predictive analytics, and scenario modeling
        5. Knowledge & Professional Practice
        Industry reports from professional bodies and government agencies
        Infrastructure project case studies and evaluations with technical and operational depth
        Professional insights, expert commentary, and applied technical analysis
        News and media sources with financial, technical, or strategic relevance
        Knowledge management practices, methodologies, and professional standards
        Online platforms, data repositories, and embedded knowledge systems for infrastructure
        Historical precedents, comparative case law, and accumulated professional know-how

    IRRELEVANT CONTENT (score 0.0-0.3):
    - Personal bills, receipts, service calls
    - Utility readings, consumption data, household records
    - Casual notes, social media, random thoughts
    - Contact info, phone numbers, basic records
    - Shopping, marketplace apps (Wallapop, Vibbo), consumer services
    - Social networking, travel, appointments
    - Generic news without technical substance
    - Any content without professional technical depth

Return JSON:
- "relevance": 0.0-1.0 (professional relevance)
- "credibility": 0.0-1.0 (source quality, technical depth)
- "novelty": 0.0-1.0 (unique insights, strategic value)
- "reasoning": Brief explanation

Be strict: only high-quality professional content scores above 0.6."""

    try:
        result = chat_json(cfg['models']['fast'], 
                          system="You are an expert evaluator for professional knowledge curation. Return strict JSON only.",
                          user=prompt, 
                          tokens=400, 
                          temp=0.2)  # Slightly higher temperature for better reasoning
        
        return {
            'relevance': min(1.0, max(0.0, result.get('relevance', 0.5))),
            'credibility': min(1.0, max(0.0, result.get('credibility', 0.5))),
            'novelty': min(1.0, max(0.0, result.get('novelty', 0.5))),
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
        'richness': min(1.0, math.log1p(len(text))/8.0),  # Keep mathematical richness
        'llm_reasoning': llm_scores['reasoning']
    }
    return features

def score_usefulness(feats, cfg):
    """Score usefulness using LLM-assessed professional relevance."""
    # LLM-driven weights - let the AI assessment dominate
    w = dict(relevance=0.60, credibility=0.25, novelty=0.10, richness=0.05)
    
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
