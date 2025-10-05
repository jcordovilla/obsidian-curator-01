# Documentation

This folder contains comprehensive documentation for the Obsidian Curator project.

## Core Documentation

- **[TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md)** - Complete technical specification including architecture, AI models, module structure, and API reference
- **[USAGE.md](USAGE.md)** - Detailed usage guide with examples and troubleshooting
- **[FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md)** - Vault structure and folder organization
- **[SCORING_SYSTEM.md](SCORING_SYSTEM.md)** - Detailed explanation of the simplified scoring system

## Analysis Output

The `analysis_output/` directory contains sample analysis results:
- `analysis_report.md` - Human-readable analysis summary
- `content_analysis.json` - Detailed analysis data
- `technical_characterization.json` - Technical specifications
- `sample_dataset.yaml` - Sample dataset for testing
- `coding_agent_brief.md` - Technical brief for AI coding assistants

## Quick Reference

### Configuration
- Primary config: `../config.py` (single source of truth)
- Auto-generated: `../config.yaml` (synced from config.py)
- Models: Llama 3.1:8B (main), Mistral (image), Whisper (audio)

### Decision Thresholds
- **Keep**: Score ≥ 0.45
- **Triage**: Score 0.25-0.45 (manual review)
- **Discard**: Score < 0.25

### Scoring System
- **Single-Pass LLM Assessment**: Focuses on knowledge reusability for professional writing
- **Scoring Range**: 0.00-1.00 with 4 tiers (High, Medium, Low, No Value)
- **Context-Aware**: Considers content types (personal logs, web clips, technical guides, etc.)
- **Anti-Hallucination**: Prevents over-interpretation of business cards and contact info

## Additional Resources

For the most up-to-date information, always refer to:
- Main README: `../README.md`
- Configuration: `../config.py`
- Test examples: `../tests/test_data/`
