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
    
    # Check for professional content indicators (MULTILINGUAL)
    professional_indicators_en = [
        'analysis', 'report', 'study', 'research', 'project', 'investment',
        'infrastructure', 'finance', 'governance', 'risk', 'management',
        'technology', 'development', 'strategy', 'policy', 'regulation',
        # Energy sector
        'energy', 'power', 'renewable', 'wind', 'solar', 'nuclear', 'tidal', 'grid',
        'turbine', 'offshore', 'onshore', 'generation', 'capacity', 'electricity',
        # Infrastructure sectors
        'transport', 'water', 'wastewater', 'highway', 'railway', 'port', 'airport',
        'hospital', 'school', 'telecommunications', 'broadband', 'digital',
        # Policy & legal
        'legislation', 'law', 'legal', 'regulatory', 'policy', 'government', 'budget',
        'concession', 'ppp', 'contract', 'procurement', 'tender', 'bid',
        # Economic & market
        'market', 'sector', 'industry', 'economic', 'fiscal', 'funding', 'financing'
    ]
    
    professional_indicators_es = [
        'análisis', 'informe', 'estudio', 'investigación', 'proyecto', 'inversión',
        'infraestructura', 'infraestructuras', 'financiación', 'concesión', 'concesiones',
        'licitación', 'millones', 'contrato', 'contratos', 'obra', 'obras',
        'ministerio', 'presupuesto', 'presupuestos', 'tarifa', 'tarifas', 'gestión',
        'política', 'regulación', 'desarrollo', 'estrategia', 'riesgo',
        # Energy sector (Spanish)
        'energía', 'eléctrica', 'renovable', 'eólica', 'solar', 'nuclear', 'mareomotriz',
        'turbina', 'aerogenerador', 'generación', 'capacidad', 'electricidad',
        # Infrastructure sectors (Spanish)
        'transporte', 'agua', 'carretera', 'autopista', 'ferrocarril', 'puerto', 'aeropuerto',
        'hospital', 'escuela', 'telecomunicaciones', 'digital',
        # Policy & legal (Spanish)
        'legislación', 'ley', 'legal', 'regulatorio', 'gobierno', 'público',
        'contratación', 'adjudicación', 'licitación',
        # Economic & market (Spanish)
        'mercado', 'sector', 'industria', 'económico', 'fiscal', 'financiero'
    ]
    
    # Combine based on language
    language = meta.get('language', 'en')
    # Support Spanish locale variants (es, es-ES, es-MX, etc.)
    if language.lower().startswith('es'):
        indicators = professional_indicators_es
        # Boost Spanish structured content recognition
        structure_multiplier = 1.3
    else:
        indicators = professional_indicators_en
        structure_multiplier = 1.0
    
    if any(indicator in text_lower for indicator in indicators):
        structure_score += 0.3 * structure_multiplier  # Increased from 0.2
    
    # Combine length and structure
    final_richness = min(1.0, length_richness + structure_score)
    return final_richness

def get_llm_usefulness_score(text, title, meta, cfg):
    """Single-pass LLM assessment of content usefulness for knowledge base."""
    
    # Truncate text for LLM processing
    text_sample = text[:3500] if len(text) > 3500 else text
    
    # Extract metadata
    source = meta.get('source', 'Not specified')
    language = meta.get('language', 'Unknown')
    date_created = meta.get('date created', 'Unknown')
    
    prompt = f"""You are evaluating content for an infrastructure investment consultant's knowledge base.

INPUT TYPES YOU'LL RECEIVE:
- Personal work logs, timesheets, meeting notes, administrative tasks
- Web-clipped industry articles, news, and reports (may have residual boilerplate)
- Conference/event promotional emails and announcements
- Technical guides, research papers, and methodologies
- User's own professional notes, analysis, and reflections
- PDFs, images with OCR text, and transcribed audio

DOCUMENT METADATA:
Title: {title}
Source: {source}
Language: {language}
Date: {date_created}

CONTENT SAMPLE:
{text_sample}

EVALUATION PURPOSE:
Score this content based on its REUSABILITY as knowledge material for a professional who:
- Writes articles and reports on infrastructure investment, PPPs, and sector developments
- Conducts due diligence and market analysis
- Needs broad knowledge across energy, transport, water, legal, policy, and economic domains
- Works internationally (any geography is relevant for benchmarking)

SCORING RUBRIC (0-1):

🟢 HIGH VALUE (0.70-1.00) - Reusable knowledge about infrastructure sectors/markets/policy:
• Industry news, sector analysis, market trends, company strategies
• Policy documents, regulatory changes, legal cases, economic data
• Technical guides, methodologies, engineering developments
• Project announcements, case studies, expert commentary
• Energy developments (ANY energy source), infrastructure projects
• Government budgets, fiscal policy, public investment programs
Examples: "Spain toll revenue impact", "Indonesia credit rating upgrade", "Energy access strategies", "Water tariff regulations"

🟡 MEDIUM VALUE (0.45-0.69) - Background knowledge, context, frameworks:
• General sector overviews, educational content, conceptual frameworks
• Conference announcements with relevant topics
• Comparative examples, basic policy information
• Industry news with limited analysis
Examples: "Overview of PPP models", "Introduction to infrastructure finance", "Wind turbine market news"

🟠 LOW VALUE (0.25-0.44) - Minimal reusable knowledge:
• Very general content weakly connected to infrastructure
• Promotional material with little substance
• Incomplete information, mostly navigation/boilerplate
Examples: "Generic project management tips", "Software vendor marketing"

🔴 NO VALUE (0.00-0.24) - Discard, not reusable knowledge:
• Personal timesheets: "Met with X", "Reviewed Y document", "Sent email to Z"
• Administrative logs: daily activity lists, task tracking, meeting schedules WITHOUT insights
• Old project-specific meeting notes (>5 years) with only logistics/scheduling, no sector insights
• Personal receipts, invoices, bills, travel bookings
• Software installation guides (unless infrastructure-specific tools)
• Corrupted content, empty files, pure navigation elements
• Unclear OCR text with garbled characters, random symbols, or nonsensical content
Examples: "April 3rd - Finished PASTAS letter, emailed Brett, reviewed memo", "ai ail aD 4 ap ay i 12SDP KICK -oEE Me ERTNG", "Land acquisition expected to start February 2015"

IMPORTANT: Industry news about energy, transport, water, policy, etc. should score AT LEAST 0.45 (medium value). Only administrative/personal content should score below 0.25.

CRITICAL: Personal notes WITH professional analysis/insights ARE valuable. Only discard administrative/logistical tracking.

ANTI-HALLUCINATION: Base score ONLY on provided content. Do NOT assume value from title alone. Do NOT infer professional expertise or project involvement from names, titles, or locations. Business cards, contact info, and personal details score LOW unless they contain substantial professional insights.

Return JSON: {{"usefulness": 0.xx, "reasoning": "2-3 sentences explaining score based on knowledge reusability"}}"""

    try:
        result = chat_json(cfg['models']['main'], 
                          system="You evaluate infrastructure consultant's content. Return strict JSON only.",
                          user=prompt, 
                          tokens=300, 
                          temp=0.15)
        
        return {
            'usefulness': min(1.0, max(0.0, result.get('usefulness', 0.4))),
            'reasoning': result.get('reasoning', 'No reasoning provided')
        }
    except Exception as e:
        print(f"Warning: LLM scoring failed: {e}")
        return {
            'usefulness': 0.3,
            'reasoning': 'LLM scoring failed, using conservative fallback'
        }

def analyze_features(content, meta, cfg):
    """Simplified single-pass content analysis."""
    text = content.get('text','')
    title = meta.get('title', '')
    
    embedding = embed_text(text, cfg['models']['embed']) if text else None
    
    # Single LLM call for usefulness assessment - trust the LLM
    llm_result = get_llm_usefulness_score(text, title, meta, cfg)
    
    features = {
        'length_chars': len(text),
        'has_numbers': any(ch.isdigit() for ch in text),
        'sections': text.count('\n## '),
        'embedding': embedding,
        'usefulness': llm_result['usefulness'],  # Pure LLM score
        'reasoning': llm_result['reasoning']
    }
    return features

def score_usefulness(feats, cfg):
    """Return the LLM-assessed usefulness score."""
    # Simplified: LLM score is the final score (already capped by richness in analyze_features)
    return feats['usefulness']

def decide(score, decision_cfg):
    th = decision_cfg['keep_threshold']
    m  = decision_cfg['gray_margin']
    if score >= th: return 'keep'
    if score <= th - m: return 'discard'
    return 'triage'
