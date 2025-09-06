import math, re
from .llm import embed_text, chat_json

def get_llm_relevance_score(text, title, cfg):
    """Use LLM to assess professional relevance for infrastructure expert."""
    
    # Truncate text for LLM processing
    text_sample = text[:3000] if len(text) > 3000 else text
    
    prompt = f"""You are a professional evaluator for a senior consultant specializing in infrastructure investment, digital transformation, and PPPs. 

    CRITICAL: Content related to INFRASTRUCTURE PROJECTS, PPPs, CONCESSIONS, PROJECT FINANCE, DIGITAL TRANSFORMATION, or ACADEMIC CONFERENCES on these topics should score above 0.5.

    TITLE: {title}
    CONTENT: {text_sample}

    Scoring rubric
    - Relevance (0.00–1.00)
    - 0.80–1.00: Directly addresses RELEVANT CONTENT with specific technical/financial/governance detail (metrics, models, legislation, contracts, case studies).
    - 0.50–0.79: Related to RELEVANT CONTENT with some professional substance or context.
    - 0.20–0.49: Tangentially related but lacks professional depth or specifics.
    - 0.00–0.19: Matches IRRELEVANT CONTENT or has no professional depth.
    - Caps: if CONTENT < 100 words, mostly navigation/boilerplate, or only filenames/links without context → relevance ≤ 0.30.
    - Credibility (0.00–1.00)
    - 0.80–1.00: Multilaterals/government/pro bodies, peer-review, official stats, primary docs, reputable outlets with citations.
    - 0.50–0.79: Trade press/technical blogs with sources; identifiable authors.
    - 0.00–0.49: Anonymous/marketing/social posts/unverified claims.
    - Cap credibility ≤ 0.50 if no author/date/source.
    - Novelty (0.00–1.00)
    - 0.80–1.00: Distinctive analysis/data/methods, new policy/market shifts, lessons learned.
    - 0.50–0.79: Familiar material with some non-trivial insight.
    - 0.00–0.49: Generic definitions or repetitive content.

    RELEVANT CONTENT (score 0.7-1.0):
    - Finance & Economics
    - Technical and financial analysis of infrastructure projects, PPPs, and concessions
    - M&A activity, investment flows, and market intelligence in infrastructure sectors
    - Financing instruments, blended finance, and project finance structures
    - Infrastructure economics, value for money assessments, and fiscal impacts
    - Policy & Governance
    - Policy documents, regulatory frameworks, and legislative frameworks
    - International development policies, multilateral guidelines, and donor frameworks
    - Procurement strategies, contracting models, PPP governance, and institutional practices
    - Historical precedents, comparative case law, and accumulated professional know-how
    - Risk & Sustainability
    - Risk management, uncertainty modeling, and scenario planning in infrastructure delivery
    - Sustainability, resilience, climate adaptation, and environmental impact assessments
    - Technology & Innovation
    - Innovation, digital transformation, and smart infrastructure systems
    - Embedded technologies: IoT, intelligent buildings, monitoring and control systems
    - Data-driven insights: Big Data, AI, predictive analytics, and scenario modeling
    - Knowledge & Professional Practice
    - Industry reports from professional bodies and government agencies
    - Infrastructure project case studies and evaluations with technical and operational depth
    - Professional insights, expert commentary, and applied technical analysis
    - News and media sources with financial, technical, or strategic relevance
    - Knowledge management practices, methodologies, and professional standards
    - Online platforms, data repositories, and embedded knowledge systems for infrastructure
    - Historical precedents, comparative case law, and accumulated professional know-how
    - Academic conferences, symposiums, and research proceedings on infrastructure topics
    - Professional development materials and training resources for infrastructure practitioners
    - Research papers, case studies, and technical reports from infrastructure organizations

    IRRELEVANT CONTENT (score 0.0–0.3):
    - Bills/receipts, invoices, service calls, warranties
    - Utility readings, household/consumption logs, appliance records
    - Contact cards, bare phone/email lists, business cards without context
    - Casual notes, personal diaries, social posts, random thoughts
    - Shopping/marketplace (Wallapop, Vibbo), consumer services, promo emails
    - Travel/appointments/calendars, confirmations, booking codes
    - Generic news headlines without technical/financial specifics
    - Navigation/cookie banners, menu/sidebar scrapings, clipper boilerplate
    - Short fragments (<50 words) or placeholders without substantive content
    - Code/config/logs unrelated to infrastructure/PPP practice
    - Personal identification documents (passports, IDs, insurance numbers)
    - Government forms unrelated to infrastructure projects
    - Personal correspondence or administrative documents
    - Any content NOT directly about infrastructure, PPPs, or digital transformation

    Output requirements
    - Return a single JSON object (no prose, no markdown, no code fences) with exactly these keys in this order:
    - "relevance": number in [0,1], rounded to two decimals
    - "credibility": number in [0,1], rounded to two decimals
    - "novelty": number in [0,1], rounded to two decimals
    - "reasoning": string ≤ 30 words explaining the scores
    - If relevance ≥ 0.70, explicitly name the satisfied RELEVANT category by number and name in "reasoning".
    - If CONTENT is empty or only links/filenames with no context, set relevance ≤ 0.25 and explain briefly."""

    try:
        result = chat_json(cfg['models']['fast'], 
                          system="You are an expert evaluator for professional knowledge curation. Return strict JSON only.",
                          user=prompt, 
                          tokens=400, 
                          temp=0.2)  # Slightly higher temperature for better reasoning
        
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
        'richness': min(1.0, math.log1p(len(text))/8.0),  # Keep mathematical richness
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
