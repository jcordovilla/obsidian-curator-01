# Folder Structure

This document explains the clear separation between different stages of note processing in the Obsidian Curator system, including the advanced testing framework.

## Overview

The system uses three distinct vaults for production processing and a comprehensive testing framework for evaluation and development:

### Production Vaults
```
/Users/jose/Documents/Obsidian/
├── Evermd/                          # RAW VAULT
├── Ever-preprocessed/               # PREPROCESSED VAULT  
└── Ever-curated/                   # CURATED VAULT
```

### Testing Framework
```
tests/test_data/
├── archive/                         # Historical test results
│   ├── 20250928_235500_raw/        # Timestamped archives
│   ├── 20250928_235500_preprocessed/
│   └── 20250928_235500_curated/
├── curated/
│   ├── notes/                      # Successfully curated notes
│   └── triage/                     # Notes requiring manual review
├── preprocessed/                   # Cleaned test notes
└── raw/                           # Fresh test notes
```

## Vault Descriptions

### 1. Raw Vault (`Evermd/`)
- **Purpose**: Contains the original, unprocessed notes and attachments
- **Source**: Direct export from Evernote or other note-taking systems
- **Contents**: 
  - Raw markdown files with original formatting
  - Original attachments in their native format
  - May contain boilerplate, poor formatting, or incomplete metadata

### 2. Preprocessed Vault (`Ever-preprocessed/`)
- **Purpose**: Contains cleaned and standardized notes and attachments
- **Source**: Processed from raw vault using preprocessing pipeline
- **Contents**:
  - Cleaned markdown files with standardized formatting
  - Web boilerplate removed
  - Metadata standardized
  - Attachments cleaned and organized

### 3. Curated Vault (`Ever-curated/`)
- **Purpose**: Contains enhanced, professionally curated notes and attachments
- **Source**: Processed from preprocessed vault using curation pipeline
- **Contents**:
  - Enhanced markdown files with professional metadata
  - LLM-generated summaries and classifications
  - Relevance scores and professional tags
  - Curated attachments (only relevant ones)

## Testing Framework

### Test Data Structure (`tests/test_data/`)

#### Archive System (`archive/`)
- **Purpose**: Preserves historical test results for comparison and analysis
- **Structure**: Timestamped folders (e.g., `20250928_235500_raw/`)
- **Contents**: Complete snapshots of test runs including raw, preprocessed, and curated results
- **Benefits**: Enables performance tracking and regression testing

#### Curated Test Results (`curated/`)
- **`notes/`**: Successfully curated notes that passed all quality thresholds
- **`triage/`**: Notes requiring manual review (scored in gray zone)
- **Purpose**: Review curation decisions and quality of AI analysis

#### Preprocessed Test Results (`preprocessed/`)
- **Purpose**: Cleaned and standardized test notes
- **Contents**: Boilerplate-removed content with enhanced formatting
- **Use**: Validate preprocessing effectiveness and content preservation

#### Raw Test Data (`raw/`)
- **Purpose**: Fresh test notes selected randomly from production vault
- **Contents**: Original notes and attachments for testing
- **Selection**: Prioritizes notes with attachments for comprehensive testing

### Testing Capabilities

#### Reproducible Testing
- **Seed-based selection**: Consistent test sets using `--seed` parameter
- **Performance comparison**: Track improvements across model updates
- **Regression testing**: Detect quality degradation over time

#### Preservation System
- **Automatic archiving**: Previous results moved to timestamped folders
- **Work preservation**: Triage decisions and manual reviews maintained
- **Historical analysis**: Compare performance across different configurations

#### Incremental Testing
- **New note testing**: Test additional notes without losing previous work
- **Efficient evaluation**: Avoid re-testing already processed content
- **Continuous improvement**: Build knowledge base of test results over time

## Configuration

The new structure is configured in `config.py` with clear variable names:

```python
# Main vault paths
RAW_VAULT_PATH = "/Users/jose/Documents/Obsidian/Evermd"
PREPROCESSED_VAULT_PATH = "/Users/jose/Documents/Obsidian/Ever-preprocessed"
CURATED_VAULT_PATH = "/Users/jose/Documents/Obsidian/Ever-curated"

# Specific paths within each vault
RAW_NOTES_PATH = os.path.join(RAW_VAULT_PATH, "notes")
RAW_ATTACHMENTS_PATH = os.path.join(RAW_VAULT_PATH, "attachments")

PREPROCESSED_NOTES_PATH = os.path.join(PREPROCESSED_VAULT_PATH, "notes")
PREPROCESSED_ATTACHMENTS_PATH = os.path.join(PREPROCESSED_VAULT_PATH, "attachments")

CURATED_NOTES_PATH = os.path.join(CURATED_VAULT_PATH, "notes")
CURATED_ATTACHMENTS_PATH = os.path.join(CURATED_VAULT_PATH, "attachments")
```

## Backward Compatibility

Legacy aliases are maintained for existing code:

```python
# Legacy aliases
VAULT_PATH = RAW_VAULT_PATH
PREPROCESSING_OUTPUT_PATH = PREPROCESSED_VAULT_PATH
CURATION_OUTPUT_PATH = CURATED_VAULT_PATH
CURATION_NOTES_PATH = CURATED_NOTES_PATH
CURATION_ASSETS_PATH = CURATED_ATTACHMENTS_PATH
CURATION_ATTACHMENTS_PATH = RAW_ATTACHMENTS_PATH
```

## Usage

### For Preprocessing
- **Input**: Raw vault (`Evermd/`)
- **Output**: Preprocessed vault (`Ever-preprocessed/`)

### For Curation
- **Input**: Preprocessed vault (`Ever-preprocessed/`) or Raw vault (`Evermd/`)
- **Output**: Curated vault (`Ever-curated/`)

### For Analysis
- **Input**: Any vault depending on analysis needs
- **Output**: Analysis results in `analysis_output/`

## Test Structure

The same clear separation principle applies to test data within the `tests/` folder:

```
tests/
├── test_data/
│   ├── raw/                         # Test raw notes + attachments
│   │   ├── notes/
│   │   └── attachments/
│   ├── preprocessed/                # Test preprocessed notes + attachments
│   │   ├── notes/
│   │   └── attachments/
│   └── curated/                     # Test curated notes + attachments
│       ├── notes/
│       └── attachments/
└── test_*.py                        # Test scripts
```

### Test Configuration

Test-specific configuration is available through `config.get_test_config()`:

```python
# Get test configuration
test_cfg = config.get_test_config()

# Test paths are automatically set
test_cfg['paths']['raw_vault']      # tests/test_data/raw
test_cfg['paths']['preprocessed_vault']  # tests/test_data/preprocessed
test_cfg['paths']['curated_vault']  # tests/test_data/curated
```

### Running Tests

```python
# Use test configuration for tests
from config import get_test_config
from src.curation.obsidian_curator.main import run

test_cfg = get_test_config()
# test_cfg automatically uses preprocessed data as input for curation
run(test_cfg, dry_run=True)  # Test run
```

**Note**: The test configuration automatically uses preprocessed data as input for the curation pipeline, ensuring the complete workflow: `raw -> preprocessed -> curated`.

## Benefits

1. **Clear Separation**: Each stage has its own dedicated space
2. **No Confusion**: Easy to understand what each folder contains
3. **Safe Processing**: Original data is never modified
4. **Flexible Workflow**: Can process from any stage to any stage
5. **Easy Cleanup**: Can safely delete intermediate stages if needed
6. **Consistent Testing**: Test data follows the same structure as production data
7. **Isolated Testing**: Test runs don't interfere with production data
