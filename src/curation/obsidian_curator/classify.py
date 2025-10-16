from .llm import chat_json

# Import Pydantic schemas for validation
from .schemas import ClassificationResponse

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

CLASSIFY_SYS = """Classify infrastructure content for a professional knowledge base.

Use ONLY these categories (select 1-3):
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
- Capacity Building

Tags: 5-10 professional terms (lowercase, hyphenated).
Entities: Extract organizations, projects, technologies, locations (max 6 each).
Publication_readiness: Score 0-1 for citation quality.

Return JSON with: categories (array), tags (array), entities (object), publication_readiness (number)."""

def classify_json(content, meta, cfg):
    text = content.get('text','')[:2000]  # Reduced for cost optimization (~500 tokens)
    title = meta.get("title","")
    
    # Extract metadata for better classification context
    source = meta.get('source', 'Not specified')
    language = meta.get('language', 'Unknown')
    date_created = meta.get('date created', 'Unknown')
    date_modified = meta.get('date modified', 'Unknown')
    
    # Streamlined prompt for GPT-5 compatibility
    user = f"""Title: {title}
Source: {source}
Language: {language}

Content: {text}

Classify for infrastructure knowledge base. Return JSON with:
- categories: 1-3 from taxonomy
- tags: 5-10 professional terms  
- entities: {{organizations, projects, technologies, locations}}
- publication_readiness: 0-1 score

Readiness scoring:
- 0.8+: Primary sources, research, legislation
- 0.6-0.8: Professional analysis, case studies
- 0.4-0.6: Background material
- <0.4: Personal notes, marketing

Return JSON only."""
    
    provider = cfg['models'].get('provider', 'openai')
    data = chat_json(
        cfg['models']['fast'], 
        system=CLASSIFY_SYS, 
        user=user, 
        tokens=600, 
        temp=0.25,
        provider=provider
    )
    
    # Validate with Pydantic schema
    try:
        validated = ClassificationResponse(**data)
        return (
            validated.categories,
            validated.tags,
            validated.entities.model_dump(),
            validated.publication_readiness
        )
    except Exception as validation_error:
        print(f"Warning: Classification schema validation failed: {validation_error}")
        # Fall back to manual parsing
        cats = data.get('categories',[])
        tags = data.get('tags',[])
        ents = data.get('entities',{})
        pub_readiness = data.get('publication_readiness', 0.5)
        return cats, tags, ents, pub_readiness
