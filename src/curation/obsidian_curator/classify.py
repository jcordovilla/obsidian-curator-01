from .llm import chat_json

# Unified Professional Context for all agents
PROFESSIONAL_CONTEXT = """You are an AI assistant for a Senior Infrastructure Investment Specialist and Chartered Civil Engineer who:
- Writes specialized articles and publications for industry journals
- Develops investment theses and due diligence reports  
- Advises on PPP/P3 structures and digital transformation
- Requires evidence-based, citable content with clear provenance

KNOWLEDGE BASE PURPOSE: Curate high-quality source material for:
- Academic and industry publications
- Investment memoranda and reports
- Policy briefings and technical analyses
- Professional presentations and case studies

QUALITY STANDARDS: Content must be:
- Factually accurate with clear attribution
- Technically substantive with concrete details
- Professionally relevant to infrastructure investment
- Citation-ready with proper source documentation"""

CLASSIFY_SYS = f"""{PROFESSIONAL_CONTEXT}

CLASSIFICATION ROLE: You classify content for this specialized knowledge database.
Align with strict professional relevance: require concrete substance (data, methods, frameworks, case evidence, legislation, contracts). Be conservative and avoid keyword-only matches.

CRITICAL: You MUST use ONLY the 5 CANONICAL CATEGORIES below. Do NOT create new categories or use sector/geography terms as categories.

CANONICAL CATEGORIES (select 1-3 only):
- Finance & Economics: Financial instruments, economic analysis, cost-benefit studies, investment frameworks
- Policy & Governance: Regulation, legislation, institutional frameworks, governance structures
- Risk & Sustainability: Risk assessment, ESG factors, resilience planning, sustainability metrics
- Technology & Innovation: Digital transformation, emerging technologies, innovation frameworks
- Knowledge & Professional Practice: Standards, methodologies, case studies, best practices

TAXONOMY MAPPING: Map broader domain concepts to canonical categories:
- Infrastructure sectors (transport/water/energy/hospitals/railways) → relevant canonical category
- Geographic regions (Spain/Europe/LATAM/Africa) → use as tags/entities, NOT categories
- Technical domains → Technology & Innovation or Knowledge & Professional Practice
- Financial concepts → Finance & Economics
- Regulatory topics → Policy & Governance
- Environmental/social topics → Risk & Sustainability

Return strict JSON only (no prose, no markdown, no code fences)."""

def classify_json(content, meta, cfg):
    text = content.get('text','')[:4000]
    title = meta.get("title","")
    
    # Enhanced prompt with unified professional context
    user = f"""Classify this content for a specialized knowledge database supporting professional publication writing.

TITLE: {title}
CONTENT: {text}

EVALUATION CRITERIA:
Assess content for potential use in specialized articles and publications. Only assign high relevance when material contains concrete professional substance suitable for citation in academic or industry publications.

CRITICAL CLASSIFICATION RULES:
- Use ONLY the 5 canonical categories defined in the system prompt
- Never create new categories or use sector/geography terms as categories
- Map infrastructure sectors (transport/water/energy) to appropriate canonical categories
- Put geography (Spain/Europe/LATAM/Africa) in tags/entities, NOT categories
- Tags: 5-10 specific, professional terms, lower-case, hyphenated (e.g., "project-finance", "due-diligence", "ppp-contract")
- Entities: Extract organizations, projects, technologies, locations (0-6 each), use canonical names

PUBLICATION READINESS SCORING (0-1):
- CITATION-READY (≥0.80): Primary sources, research reports, legislation, technical standards with clear attribution
- PROFESSIONAL ANALYSIS (0.60-0.79): Secondary analysis, expert commentary, case studies with substantial detail
- BACKGROUND MATERIAL (0.40-0.59): General information, basic explanations, limited technical depth
- UNSUITABLE (≤0.39): Personal notes, marketing materials, incomplete information, no clear source

Special caps:
- Content <100 words or mostly boilerplate: cap at 0.40
- Only links/placeholders without substance: cap at 0.25
- No clear source attribution: reduce score by 0.15

Return JSON with exactly:
- "categories": List of 1-3 canonical categories from system prompt
- "tags": List of 5-10 professional tags
- "entities": Object with "organizations", "projects", "technologies", "locations" arrays
- "publication_readiness": Score 0-1 for suitability in professional publications

Return strict JSON only."""
    
    data = chat_json(cfg['models']['fast'], system=CLASSIFY_SYS, user=user, tokens=600, temp=0.25)
    cats = data.get('categories',[])
    tags = data.get('tags',[])
    ents = data.get('entities',{})
    relevance = data.get('relevance_score', 0.5)
    
    return cats, tags, ents
