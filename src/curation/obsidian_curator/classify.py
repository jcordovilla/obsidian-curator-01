from .llm import chat_json

CLASSIFY_SYS = """You are an expert classifier and relevance scorer for an expert Civil Engineering consultant specializing in infrastructure investment, digital transformation, and public-private partnerships (PPP/P3).
Align with a strict professional relevance rubric: require concrete substance (data, methods, frameworks, case evidence, legislation, contracts). Be conservative and avoid keyword-only matches.
Use ONLY the following CANONICAL CATEGORIES (max 7) when assigning categories:
- Finance & Economics
- Policy & Governance
- Risk & Sustainability
- Technology & Innovation
- Knowledge & Professional Practice
Map any broader/alternative labels to the closest canonical category. Sector (e.g., transport/water/energy) and geography (e.g., Spain/Europe/LATAM/Africa) must be expressed as tags/entities, not categories.
Return strict JSON only (no prose, no markdown, no code fences)."""

def classify_json(content, meta, cfg):
    text = content.get('text','')[:4000]
    title = meta.get("title","")
    
    # Enhanced prompt with professional context
    user = f"""Classify this content for an infrastructure expert's knowledge base. Follow the relevance agent rubric: only assign high relevance when the material contains concrete professional detail (technical/financial/governance specifics, methods, data, frameworks, case studies). Do not rely on keywords without evidence.

TITLE: {title}
CONTENT: {text}

AVAILABLE CATEGORIES: {", ".join(cfg["taxonomy"]["categories"])}

CANONICAL CATEGORIES (use only these for "categories"; map others here):
- Finance & Economics
- Policy & Governance
- Risk & Sustainability
- Technology & Innovation
- Knowledge & Professional Practice

Rules
- Choose 1–3 categories ONLY from the CANONICAL CATEGORIES above.
- Put sector (transport/water/energy/etc.) and geography (Spain/Europe/LATAM/Africa/etc.) in "tags" or "entities", NOT in "categories".
- Tags must be 3–8 items, specific, lower-case, hyphenated where sensible (e.g., "project-finance", "value-for-money", "ppp-contract", "spain", "transport").
- Entities should extract salient "organizations", "projects", "technologies", and "locations" (0–6 each), deduplicated, canonical names.
- Compute "relevance_score" ∈ [0,1] conservatively:
    - If CONTENT directly satisfies a canonical category with concrete detail → ≥ 0.70.
    - If generic/high-level with little technical substance → 0.31–0.69.
    - If personal/administrative/boilerplate or only filenames/links → ≤ 0.30 (cap ≤ 0.25 if only links/placeholders).
    - If CONTENT < 100 words or mostly navigation/boilerplate → cap relevance_score ≤ 0.40.

Return JSON with exactly:
- "categories": List of 1–3 canonical categories only
- "tags": List of 3–8 professional tags (include sector/geography as tags, not categories)
- "entities": Object with arrays "organizations", "projects", "technologies", "locations" (0–6 each)
- "relevance_score": Number 0–1 indicating professional relevance

Return strict JSON only."""
    
    data = chat_json(cfg['models']['fast'], system=CLASSIFY_SYS, user=user, tokens=600)
    cats = data.get('categories',[])
    tags = data.get('tags',[])
    ents = data.get('entities',{})
    relevance = data.get('relevance_score', 0.5)
    
    return cats, tags, ents
