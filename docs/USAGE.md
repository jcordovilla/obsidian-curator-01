# Usage Guide

## Quick Start

### 1. Configure Paths
Edit `config.py` to set your vault path:
```python
VAULT_PATH = "/path/to/your/obsidian/vault"
```

### 2. Update Configuration
```bash
python scripts/update_config.py
```

### 3. Run Analysis (Optional)
```bash
python scripts/main.py --sample --analyze
```

### 4. Process Your Vault
```bash
# Test with sample
python scripts/preprocess.py --sample 10 --dry-run

# Process entire vault
python scripts/preprocess.py
```

## Available Commands

### Analysis
```bash
# Create sample dataset
python scripts/main.py --sample

# Analyze content
python scripts/main.py --analyze

# Technical characterization
python scripts/main.py --technical-analysis
```

### Preprocessing
```bash
# Dry run (test without changes)
python scripts/preprocess.py --dry-run

# Process sample
python scripts/preprocess.py --sample 50

# Process specific categories
python scripts/preprocess.py --categories web_clipping personal_note

# High performance
python scripts/preprocess.py --batch-size 100 --workers 8
```

### Curation
```bash
# Run curation pipeline
python -m src.curation.obsidian_curator.main

# With custom paths
python -m src.curation.obsidian_curator.main --vault /path/to/vault --out /path/to/output
```

## Configuration

The project uses a unified configuration system:

- **`config.py`** - Main configuration (single source of truth)
- **`config.yaml`** - Auto-generated for curation module
- **`scripts/update_config.py`** - Sync configuration files

### Key Settings
```python
# Main vault path
VAULT_PATH = "/path/to/your/vault"

# Output paths (automatically calculated)
PREPROCESSING_OUTPUT_PATH = "/path/to/processed/vault"
CURATION_OUTPUT_PATH = "/path/to/curated/vault"
```

## What Gets Processed

### Content Categories
- **Web Clipping** (60%) - Removes boilerplate, ads, navigation
- **Personal Notes** (11.5%) - Gentle formatting cleanup
- **PDF Annotations** (9.5%) - Validates attachments
- **Business Cards** (3%) - Structures contact info
- **Technical Documents** (2%) - Preserves code and structure
- **Unknown** (14%) - Minimal processing

### Processing Pipeline
1. **Validation** - File integrity checks
2. **Metadata** - Standardize dates and tags
3. **Classification** - Auto-categorize content
4. **Cleaning** - Remove boilerplate
5. **Formatting** - Standardize structure
6. **Validation** - Quality checks
7. **Output** - Generate clean notes

## Safety Features

- **Automatic Backups** - Original files backed up
- **Dry Run Mode** - Test without changes
- **Validation** - Quality and integrity checks
- **Error Handling** - Comprehensive error recovery

## Troubleshooting

### Common Issues
1. **Path not found** - Check `config.py` and run `python scripts/update_config.py`
2. **Permission errors** - Ensure write access to output directories
3. **Memory issues** - Reduce batch size: `--batch-size 25`

### Getting Help
- Check the main `README.md` for detailed information
- Review error messages in the console output
- Use `--dry-run` to test before processing
