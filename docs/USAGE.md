# Usage Guide

## Quick Start

### 1. Configure Paths
Edit `config.py` to set your vault paths:
```python
RAW_VAULT_PATH = "/path/to/your/raw/obsidian/vault"
PREPROCESSED_VAULT_PATH = "/path/to/preprocessed/vault"
CURATED_VAULT_PATH = "/path/to/curated/vault"
```

### 2. Update Configuration
```bash
python scripts/update_config.py
```

### 3. Test the System (Recommended)
```bash
# Test with 10 random notes
python tests/test_complete_pipeline.py 10

# Test with specific seed for reproducibility
python tests/test_complete_pipeline.py 10 --seed 42

# Incremental testing (preserves previous results)
python tests/test_complete_pipeline.py 15 --incremental
```

### 4. Process Your Vault
```bash
# Preprocessing (raw → preprocessed)
python scripts/preprocess.py

# Curation (preprocessed → curated)
python -m src.curation.obsidian_curator.main
```

## Advanced Usage

### Preprocessing Options
```bash
# Full vault processing
python scripts/preprocess.py

# Sample processing
python scripts/preprocess.py --sample 50

# Dry run (no changes)
python scripts/preprocess.py --dry-run

# Custom batch size and workers
python scripts/preprocess.py --batch-size 100 --workers 8

# Process specific categories
python scripts/preprocess.py --categories web_clipping personal_note
```

### Curation Module
```bash
# Run the curation pipeline
python -m src.curation.obsidian_curator.main

# With custom paths
python -m src.curation.obsidian_curator.main --vault /path/to/vault --out /path/to/output
```

### Testing Options
```bash
# Run complete pipeline test
python tests/test_complete_pipeline.py

# Test folder structure and configuration
python tests/test_folder_structure.py

# Test preprocessing pipeline only
python tests/test_preprocessing_pipeline.py

# Partial pipeline testing
python tests/test_complete_pipeline.py --stages random preprocess
python tests/test_complete_pipeline.py --stages curate
```

## Configuration Management

```bash
# Update config.yaml after changing config.py
python scripts/update_config.py

# View current configuration
python scripts/update_config.py
```

## Output Structure

The system creates a three-stage workflow:

```
Raw → Preprocessed → Curated
```

### Raw Vault
- Original notes and attachments
- Unprocessed content

### Preprocessed Vault
- Cleaned and standardized notes
- Metadata normalized
- Boilerplate removed
- Attachments organized

### Curated Vault
- AI-analyzed content
- Professional summaries
- Quality scoring
- Three outputs:
  - `notes/`: High-value content (score ≥ 0.45)
  - `triage/`: Medium-value content (manual review)
  - `attachments/`: Curated attachments

## Cost and Performance

### Cost Estimates
- **Per note**: ~$0.001-0.002 (less than 1 cent)
- **1,000 notes**: ~$1-2 total
- Uses GPT-4o-mini for cost efficiency

### Performance
- **Processing speed**: ~0.4 files/second
- **Memory usage**: Optimized for large vaults
- **Quality**: 99.9% success rate

## Troubleshooting

### Common Issues

**Configuration errors**: Run `python scripts/update_config.py` after changing `config.py`

**Path issues**: Ensure all paths in `config.py` are absolute and exist

**Memory issues**: Reduce batch size in preprocessing: `--batch-size 25`

**API errors**: Check OpenAI API key and rate limits

### Getting Help

1. Check the logs in the `logs/` directory
2. Run tests to verify setup: `python tests/test_complete_pipeline.py 5`
3. Use dry-run mode: `python scripts/preprocess.py --dry-run`
4. Review the technical specification in `docs/TECHNICAL_SPECIFICATION.md`