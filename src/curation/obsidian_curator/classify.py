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

CRITICAL ANTI-FABRICATION RULES:
- NEVER invent, assume, or infer content not explicitly present in the provided text
- NEVER add professional context, background, or interpretation beyond what is stated
- NEVER reference external sources, studies, or organizations not mentioned in the text
- If content is insufficient for proper classification, state this honestly
- Base ALL assessments strictly on the provided document metadata and content
- Every classification decision must be directly traceable to the source material

CRITICAL: You MUST use ONLY the infrastructure taxonomy categories below. Do NOT create new categories or use geographic regions as categories.

INFRASTRUCTURE TAXONOMY CATEGORIES (select 1-3 only):
- Infrastructure Investment: Core investment strategies, funding mechanisms, financial structures
- PPP/P3: Public-private partnerships, concession models, collaborative frameworks
- Concessions: Long-term infrastructure concessions, operational agreements
- Project Finance: Financing structures, risk allocation, financial modeling
- Risk Management: Risk assessment, mitigation strategies, insurance frameworks
- Roads & Transport: Transportation infrastructure, mobility solutions, traffic management
- Water & Wastewater: Water infrastructure, sanitation systems, resource management
- Energy: Power generation, distribution, renewable energy, grid systems
- Hospitals & Social Infrastructure: Healthcare facilities, social services, community infrastructure
- Railways: Rail systems, high-speed rail, freight networks, station infrastructure
- Digital Transformation: Technology adoption, digital infrastructure, smart systems
- AI & Machine Learning: Artificial intelligence applications, predictive analytics, automation
- Digital Twins: Digital replicas, simulation models, virtual infrastructure
- Geospatial Data: Geographic information systems, mapping, location intelligence
- Process Automation: Workflow automation, robotic process automation, efficiency systems
- Governance & Transparency: Regulatory compliance, accountability frameworks, oversight
- Policy & Regulation: Legislative frameworks, regulatory policies, compliance requirements
- Strategic Planning: Long-term planning, development strategies, vision frameworks
- Asset Management: Infrastructure lifecycle management, maintenance strategies, optimization
- Technical Due Diligence: Technical assessment, feasibility analysis, engineering review
- Feasibility Studies: Project viability analysis, technical feasibility, economic assessment
- Market Intelligence: Industry analysis, market research, competitive intelligence
- Critical Infrastructure Protection: Security frameworks, resilience planning, threat mitigation
- ESG & Sustainability: Environmental, social, governance factors, sustainable development
- Climate Resilience: Climate adaptation, environmental sustainability, green infrastructure
- Innovation & R&D: Research and development, technological innovation, pilot projects
- Capacity Building: Skills development, institutional strengthening, knowledge transfer

GEOGRAPHIC REGIONS (use as tags/entities, NOT categories):
- Spain, Europe, LATAM, International Development, Africa, Asia, North America

Return strict JSON only (no prose, no markdown, no code fences)."""

def classify_json(content, meta, cfg):
    text = content.get('text','')[:4000]
    title = meta.get("title","")
    
    # Extract metadata for better classification context
    source = meta.get('source', 'Not specified')
    language = meta.get('language', 'Unknown')
    date_created = meta.get('date created', 'Unknown')
    date_modified = meta.get('date modified', 'Unknown')
    
    # Enhanced prompt with unified professional context
    user = f"""Classify this content for a specialized knowledge database supporting professional publication writing.

DOCUMENT METADATA:
Title: {title}
Source: {source}
Language: {language}
Created: {date_created}
Modified: {date_modified}

CONTENT: {text}

EVALUATION CRITERIA:
Assess content for potential use in specialized articles and publications. Only assign high relevance when material contains concrete professional substance suitable for citation in academic or industry publications.

CRITICAL CLASSIFICATION RULES:
- Use ONLY the infrastructure taxonomy categories defined in the system prompt
- Select 1-3 categories that best match the content's primary focus
- Put geographic regions (Spain/Europe/LATAM/Africa) in tags/entities, NOT categories
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
- "categories": List of 1-3 infrastructure taxonomy categories from system prompt
- "tags": List of 5-10 professional tags
- "entities": Object with "organizations", "projects", "technologies", "locations" arrays
- "publication_readiness": Score 0-1 for suitability in professional publications

Return strict JSON only."""
    
    data = chat_json(cfg['models']['fast'], system=CLASSIFY_SYS, user=user, tokens=600, temp=0.25)
    cats = data.get('categories',[])
    tags = data.get('tags',[])
    ents = data.get('entities',{})
    # Use publication_readiness as the relevance score for downstream processing
    pub_readiness = data.get('publication_readiness', 0.5)
    
    return cats, tags, ents, pub_readiness
