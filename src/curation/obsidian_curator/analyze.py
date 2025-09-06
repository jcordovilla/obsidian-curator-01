import math
from .llm import embed_text

def analyze_features(content, meta, cfg):
    text = content.get('text','')
    embedding = embed_text(text, cfg['models']['embed']) if text else None
    features = {
        'length_chars': len(text),
        'has_numbers': any(ch.isdigit() for ch in text),
        'sections': text.count('\n## '),
        'embedding': embedding,
        'relevance': 0.0,     # TODO
        'credibility': 0.5,   # TODO
        'richness': min(1.0, math.log1p(len(text))/10.0),
        'novelty': 0.5        # TODO
    }
    return features

def score_usefulness(feats, cfg):
    w = dict(relevance=0.35, credibility=0.20, richness=0.20, novelty=0.15, reuse=0.10)
    reuse = 1.0 if feats['length_chars']>400 else 0.3
    score = (w['relevance']*feats['relevance'] +
             w['credibility']*feats['credibility'] +
             w['richness']*feats['richness'] +
             w['novelty']*feats['novelty'] +
             w['reuse']*reuse)
    return max(0.0, min(1.0, score))

def decide(score, decision_cfg):
    th = decision_cfg['keep_threshold']
    m  = decision_cfg['gray_margin']
    if score >= th: return 'keep'
    if score <= th - m: return 'discard'
    return 'triage'
