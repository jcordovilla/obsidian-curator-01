# Documentation

This folder contains comprehensive documentation for the Obsidian Curator project.

## Core Documentation

- **[TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md)** - Complete technical specification including architecture, AI models, module structure, and API reference
- **[USAGE.md](USAGE.md)** - Detailed usage guide with examples and troubleshooting
- **[FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md)** - Vault structure and folder organization

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
- **Keep**: Score ≥ 0.55
- **Triage**: Score 0.45-0.55 (manual review)
- **Discard**: Score < 0.45

### Scoring Components
- **Relevance**: 50% (professional value for infrastructure writing)
- **Depth**: 30% (technical substance and detail)
- **Richness**: 20% (content structure and indicators)
- **Credibility**: 0% (disabled due to multilingual issues)

## Additional Resources

For the most up-to-date information, always refer to:
- Main README: `../README.md`
- Configuration: `../config.py`
- Test examples: `../tests/test_data/`
