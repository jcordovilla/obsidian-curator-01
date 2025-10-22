# Technical Specification for Obsidian Curator

## Overview

Obsidian Curator is a specialized AI-powered knowledge curation system designed for infrastructure investment professionals. It transforms raw notes, documents, and web clippings into a publication-ready research database optimized for academic papers, industry reports, and professional presentations. The system uses advanced local AI models and provides three main pipelines: analysis, preprocessing, and curation.

### Key Features
- **Incremental Processing**: Smart processing that only handles new or changed notes, dramatically reducing costs and processing time
- **Note Register System**: SQLite-based tracking system that monitors notes across all processing stages
- **Comprehensive Attachment Handling**: Full pipeline attachment copying from raw→preprocessed→curated
- **Performance Optimization**: Significant cost and time savings for subsequent processing runs

## Architecture

### Core Design Principles
- **Unified Configuration**: Single source of truth in `config.py`
- **Modular Design**: Separate concerns (analysis, preprocessing, curation)
- **Path Abstraction**: Consistent use of `pathlib.Path` throughout
- **Error Handling**: Comprehensive validation and recovery
- **Safety First**: Automatic backups and dry-run capabilities
- **Incremental Processing**: Default behavior to only process new/changed notes
- **Register-Based Tracking**: SQLite database for comprehensive note state management

### AI Models & Performance

#### Core Models
- **Llama 3.1:8B**: Primary model for classification, analysis, and summarization with strong multilingual support (especially Spanish/English)
- **Mistral**: Specialized model for image OCR analysis
- **Whisper (dimavz/whisper-tiny:latest)**: Audio transcription via Ollama
- **nomic-embed-text**: Embedding model for semantic similarity and content discovery

#### Model Usage by Process
| Process | Model | Purpose | Token Limit | Notes |
|---------|-------|---------|-------------|-------|
| Classification | Llama 3.1:8B | Content categorization | 600 | Multilingual support |
| Relevance Analysis | Llama 3.1:8B | Professional scoring | 400 | No credibility scoring |
| PDF Summarization | Llama 3.1:8B | Technical summaries | 900 | ~3s per PDF |
| Image Analysis | Mistral | OCR interpretation | 800 | Auto-resizes large images |
| Audio Transcription | Whisper (tiny) | Speech-to-text | N/A | ~10-30s per minute |
| Audio Analysis | Llama 3.1:8B | Content analysis | 800 | ~2s per audio |
| Embeddings | nomic-embed-text | Similarity search | N/A | ~0.5s per note |

#### Key Features
- **Multilingual Support**: Superior performance on Spanish and English content
- **Publication-focused prompts**: Optimized for professional content curation
- **Local Processing**: All models run locally via Ollama for privacy and control
- **Anti-fabrication measures**: Strict rules to prevent content hallucination

### Audio Processing System

#### Supported Formats
- **WAV, MP3, M4A, AAC, FLAC, OGG, WMA** - Comprehensive audio format support
- **Automatic Detection** - Intelligent classification based on file extensions
- **Metadata Extraction** - File size, format, creation time, and duration tracking

#### Transcription Pipeline
1. **File Validation** - Format verification and size checking
2. **Whisper Processing** - Speech-to-text conversion via Ollama
3. **Text Cleaning** - Whitespace normalization and formatting
4. **LLM Analysis** - Comprehensive content analysis and extraction

#### Analysis Framework
- **Content Type Identification** - Meeting, presentation, interview classification
- **Speaker Recognition** - Multi-speaker detection and identification
- **Professional Content Extraction** - Quotes, statistics, data points
- **Technical Substance Assessment** - Quantitative data and frameworks
- **Publication Utility Evaluation** - Citation-ready content identification

#### Integration Points
- **Preprocessing Pipeline** - Audio annotation classification and cleaning
- **Curation Pipeline** - Full content analysis and scoring
- **Quality Validation** - Anti-fabrication measures and source attribution

### Configuration System

#### Primary Configuration (`config.py`)
```python
# Main vault paths (single source of truth)
RAW_VAULT_PATH = "/Users/jose/Documents/Obsidian/Evermd"
PREPROCESSED_VAULT_PATH = "/Users/jose/Documents/Obsidian/Ever-preprocessed"
CURATED_VAULT_PATH = "/Users/jose/Documents/Obsidian/Ever-curated"

# AI Models configuration
MODELS = {
    'fast': 'llama3.1:8b',  # Upgraded for multilingual support
    'main': 'llama3.1:8b', 
    'embed': 'nomic-embed-text'
}
```

#### Configuration Management
- `get_curation_config()`: Generates YAML config from Python constants
- `update_curation_yaml()`: Syncs YAML file with Python config
- `scripts/update_config.py`: CLI tool for configuration synchronization

## Module Structure

### 1. Analysis Module (`src/analysis/`)

#### `content_analyzer.py`
**Purpose**: Core content analysis and statistics
**Key Classes**:
- `ContentAnalyzer`: Main analysis engine
**Key Methods**:
- `analyze_note()`: Comprehensive note analysis
- `calculate_quality_score()`: Quality assessment
- `detect_boilerplate()`: Boilerplate pattern detection
- `extract_metadata()`: Metadata extraction and validation

#### `note_sampler.py`
**Purpose**: Stratified sampling for representative analysis
**Key Classes**:
- `NoteSampler`: Sampling engine
**Key Methods**:
- `create_sample_dataset()`: Generate representative samples
- `stratified_sample()`: Category-based sampling
- `extract_note_info()`: Extract note metadata

#### `technical_characterizer.py`
**Purpose**: Technical characterization for coding agents
**Key Classes**:
- `TechnicalCharacterizer`: Inherits from ContentAnalyzer
**Key Methods**:
- `characterize_vault()`: Comprehensive vault analysis
- `generate_technical_brief()`: Technical specifications
- `analyze_content_patterns()`: Pattern recognition

### 2. Preprocessing Module (`src/preprocessing/`)

#### `batch_processor.py`
**Purpose**: Main processing pipeline orchestrator
**Key Classes**:
- `BatchProcessor`: Main pipeline controller
**Key Methods**:
- `process_vault()`: Full vault processing
- `_process_single_file()`: Individual file processing
- `_handle_attachments_folder()`: Attachment management
**Processing Pipeline**:
1. Validation & Backup
2. Metadata Standardization
3. Content Classification
4. Boilerplate Removal
5. Content Processing
6. Formatting Standardization
7. Quality Validation
8. Output Generation

#### `content_classifier.py`
**Purpose**: Automatic note categorization
**Key Classes**:
- `ContentClassifier`: Classification engine
**Key Methods**:
- `classify_note()`: Categorize note content
- `detect_content_type()`: Type detection logic
**Categories**:
- `web_clipping`: Web-scraped content
- `pdf_annotation`: PDF-based notes
- `personal_note`: Personal observations
- `business_card`: Contact information
- `technical_document`: Technical content
- `news_article`: News content
- `unknown`: Unclassified content

#### `metadata_standardizer.py`
**Purpose**: Evernote → ISO format conversion
**Key Classes**:
- `MetadataStandardizer`: Metadata processing
**Key Methods**:
- `standardize_metadata()`: Convert date formats
- `normalize_tags()`: Tag standardization
- `validate_metadata()`: Metadata validation

#### `web_clipping_cleaner.py`
**Purpose**: Boilerplate removal and content cleaning
**Key Classes**:
- `WebClippingCleaner`: Content cleaning engine
**Key Methods**:
- `clean_content()`: Main cleaning pipeline
- `remove_boilerplate()`: Pattern-based removal
- `preserve_meaningful_content()`: Content preservation

#### `quality_validator.py`
**Purpose**: Quality assessment and validation
**Key Classes**:
- `QualityValidator`: Quality assessment engine
**Key Methods**:
- `validate_note()`: Comprehensive validation
- `assess_content_quality()`: Quality scoring
- `check_attachments()`: Attachment validation

### 3. Curation Module (`src/curation/obsidian_curator/`)

#### `main.py`
**Purpose**: Main curation pipeline entry point
**Key Functions**:
- `load_cfg()`: Configuration loading (prefers config.py)
- `run()`: Main curation pipeline
- `cli()`: Command-line interface

#### `analyze.py`
**Purpose**: Content analysis and scoring
**Key Functions**:
- `analyze_features()`: Feature extraction
- `score_usefulness()`: Usefulness scoring
- `decide()`: Keep/triage/discard decisions

#### `classify.py`
**Purpose**: Content classification
**Key Functions**:
- `classify_json()`: JSON-based classification
- `extract_categories()`: Category extraction
- `generate_tags()`: Tag generation

#### `extractors.py`
**Purpose**: Content extraction from various sources
**Key Functions**:
- `extract_pdf()`: PDF content extraction
- `extract_image()`: Image text extraction (OCR)
- `extract_content()`: Multi-source extraction

#### `llm.py`
**Purpose**: LLM integration
**Key Functions**:
- `generate_embedding()`: Text embedding generation
- `classify_with_llm()`: LLM-based classification
- `summarize_content()`: Content summarization

#### `store.py`
**Purpose**: Embedding storage and retrieval
**Key Classes**:
- `EmbeddingIndex`: FAISS-based storage
- `Manifest`: Processing manifest
**Key Methods**:
- `add()`: Add embeddings
- `search()`: Similarity search
- `update()`: Update manifest

#### `summarize.py`
**Purpose**: Content summarization
**Key Functions**:
- `summarize_content()`: Main summarization
- `generate_bullets()`: Bullet point generation
- `extract_key_points()`: Key point extraction

#### `writer.py`
**Purpose**: Output generation
**Key Functions**:
- `write_curated_note()`: Write processed notes
- `format_metadata()`: Metadata formatting
- `generate_frontmatter()`: YAML frontmatter

#### `utils.py`
**Purpose**: Utility functions
**Key Functions**:
- `iter_markdown_notes()`: Recursive markdown discovery
- `parse_front_matter()`: Frontmatter parsing
- `clean_markdown_to_text()`: Content cleaning

### 4. Utilities Module (`src/utils/`)

#### `file_handler.py`
**Purpose**: Safe file operations
**Key Classes**:
- `FileHandler`: File operation manager
**Key Methods**:
- `read_note()`: Safe note reading
- `write_note()`: Safe note writing
- `create_backup()`: Backup creation
- `validate_file()`: File validation

#### `note_register.py`
**Purpose**: Note Register System for tracking notes across all processing stages
**Key Classes**:
- `NoteRegister`: Main register management class
**Key Methods**:
- `register_note()`: Register a note and return its ID
- `record_stage()`: Record a processing stage for a note
- `get_note_status()`: Get processing status for a note
- `get_notes_needing_processing()`: Get list of notes that need processing at a specific stage
- `get_processing_stats()`: Get overall processing statistics
- `cleanup_orphaned_records()`: Remove records for notes that no longer exist
- `export_register()`: Export register data to JSON file

**Register System Features**:
- **SQLite Database**: Persistent storage in `.metadata/note_register.db`
- **Hash-Based Change Detection**: MD5 hashing for efficient change detection
- **Multi-Stage Tracking**: Tracks notes through raw→preprocessed→curated→triaged stages
- **Incremental Processing**: Identifies notes that need reprocessing
- **Comprehensive Reporting**: Export capabilities for analysis and monitoring
- **Performance Optimization**: Indexed queries for fast lookups

**Database Schema**:
- `note_register`: Main table with note metadata and hashes
- `processing_stages`: Stage-specific processing records with status and metadata
- Indexes on note paths, hashes, stages, and status for optimal performance

## Scripts

### `scripts/main.py`
**Purpose**: Analysis and characterization entry point
**Key Features**:
- Command-line argument parsing
- Vault path validation
- Sample dataset creation
- Content analysis
- Technical characterization

### `scripts/preprocess.py`
**Purpose**: Main preprocessing script with incremental processing support
**Key Features**:
- **Incremental Processing**: Default mode processes only new/changed notes
- **Full Processing Mode**: `--full` flag to override incremental behavior
- Batch processing options
- Category filtering
- Performance tuning
- Dry-run mode
- Progress reporting
- Register integration for state tracking

### `scripts/manage_register.py`
**Purpose**: Comprehensive note register management tool
**Key Features**:
- **Register Population**: Populate register with existing processed notes
- **Query Interface**: Query notes by status, stage, or processing history
- **Statistics Reporting**: Generate comprehensive processing statistics
- **Export Capabilities**: Export register data to CSV and Markdown formats
- **Cleanup Operations**: Remove orphaned records and maintain database integrity
- **Performance Monitoring**: Track processing efficiency and success rates

### `scripts/update_config.py`
**Purpose**: Configuration synchronization
**Key Features**:
- Updates config.yaml from config.py
- Displays current configuration
- Validates path settings

## Testing System

### `tests/test_complete_pipeline.py`
**Purpose**: End-to-end pipeline testing with advanced capabilities
**Key Features**:
- **Reproducible Testing**: Optional seed for consistent results
- **Preservation System**: Timestamped archives of previous test results
- **Incremental Testing**: Test new notes without losing previous work
- **Targeted Testing**: Test specific notes by filename
- **Partial Pipeline Testing**: Run individual stages (random, preprocess, curate)
- **Performance Monitoring**: Track processing speed and quality metrics
- **Flexible Configuration**: Command-line options for different testing scenarios

#### Test Command Options
```bash
# Basic testing
python tests/test_complete_pipeline.py 10

# Reproducible testing with seed
python tests/test_complete_pipeline.py 10 --seed 42

# Incremental testing (preserves previous work)
python tests/test_complete_pipeline.py 15 --incremental

# Clean slate testing (delete previous results)
python tests/test_complete_pipeline.py 10 --no-preserve

# Targeted testing on specific notes
python tests/test_complete_pipeline.py --notes "Note1.md" "Note2.md"

# Partial pipeline testing (preprocessing only)
python tests/test_complete_pipeline.py --stages random preprocess

# Curation only (requires existing preprocessed notes)
python tests/test_complete_pipeline.py --stages curate
```

#### Test Output Structure
```
tests/test_data/
├── archive/                          # Historical test results
│   ├── 20250928_235500_raw/         # Timestamped archives
│   ├── 20250928_235500_preprocessed/
│   └── 20250928_235500_curated/
├── curated/
│   ├── notes/                       # Successfully curated notes
│   └── triage/                      # Notes requiring manual review
├── preprocessed/                    # Cleaned test notes
└── raw/                            # Fresh test notes
```

#### Performance Metrics
- **Processing Speed**: Track improvements across model updates
- **Quality Metrics**: Monitor curation accuracy and consistency
- **Resource Usage**: Memory and processing time optimization
- **Decision Analysis**: Review keep/triage/discard patterns

### `src/utils/preprocessing_analyzer.py`
**Purpose**: Comprehensive preprocessing effectiveness analysis
**Key Features**:
- **Large Sample Analysis**: Analyze 100+ random notes from source vault
- **Note Type Diversity**: Categorize notes (web clipping, PDF, image, text, etc.)
- **Clutter Pattern Analysis**: Identify common boilerplate and navigation elements
- **Preprocessing Effectiveness**: Test cleaning on sample and measure reduction
- **Recommendation Generation**: Propose improvements based on remaining clutter
- **Statistical Reporting**: Detailed metrics on preprocessing performance

#### Usage
```bash
# Analyze 100 random notes
python src/utils/preprocessing_analyzer.py --sample-size 100

# Custom output file
python src/utils/preprocessing_analyzer.py --output my_analysis.json

# Help and options
python src/utils/preprocessing_analyzer.py --help
```

## Data Flow

### Analysis Pipeline
1. **Sampling**: `NoteSampler` creates representative dataset
2. **Analysis**: `ContentAnalyzer` processes samples
3. **Characterization**: `TechnicalCharacterizer` generates specs
4. **Reporting**: Results saved to `docs/analysis_output/`

### Preprocessing Pipeline
1. **Discovery**: Recursive markdown file discovery
2. **Validation**: File integrity and encoding checks
3. **Classification**: Automatic content categorization
4. **Processing**: Category-specific content cleaning
5. **Standardization**: Metadata and formatting normalization
6. **Validation**: Quality and integrity verification
7. **Output**: Clean notes with preserved attachments

### Curation Pipeline
1. **Analysis**: Content feature extraction and scoring
2. **Classification**: AI-powered content categorization
3. **Decision**: Keep/triage/discard based on scores
4. **Processing**: Content extraction and summarization
5. **Storage**: Embedding generation and storage
6. **Output**: Curated notes with enhanced metadata

### Incremental Processing Pipeline
1. **Register Check**: Query note register for processing status
2. **Change Detection**: Compare file hashes to detect modifications
3. **Stage Identification**: Determine which processing stage is needed
4. **Selective Processing**: Process only notes requiring updates
5. **Register Update**: Record processing results and update status
6. **Attachment Synchronization**: Ensure attachments are copied through pipeline
7. **Statistics Update**: Update processing statistics and reports

#### Incremental Processing Benefits
- **Cost Reduction**: 80-90% reduction in processing costs for subsequent runs
- **Time Savings**: Significant speed improvements for large vaults
- **Resource Efficiency**: Reduced memory and CPU usage
- **Smart Detection**: Only processes notes that have changed or failed previously

## Configuration Management

### Path Resolution
```python
# All paths are absolute and derived from VAULT_PATH
vault_path = Path(VAULT_PATH)
output_path = Path(PREPROCESSING_OUTPUT_PATH)
curation_path = Path(CURATION_OUTPUT_PATH)
```

### Configuration Loading Priority
1. `config.py` (primary source)
2. `config.yaml` (fallback)
3. Command-line arguments (override)

## Error Handling

### Validation Points
- Vault path existence
- File readability
- Encoding compatibility
- Metadata validity
- Content integrity

### Recovery Mechanisms
- Automatic backups
- Dry-run mode
- Detailed error logging
- Graceful degradation

## Performance Considerations

### Parallel Processing
- Configurable worker threads
- Batch processing
- Memory-efficient file handling

### Optimization Strategies
- Lazy loading
- Caching mechanisms
- Incremental processing
- Resource cleanup

## Dependencies

### Core Dependencies
- `pathlib`: Path handling
- `yaml`: Configuration management
- `json`: Data serialization
- `re`: Pattern matching
- `os`: System operations

### Analysis Dependencies
- `collections`: Data structures
- `datetime`: Date handling
- `statistics`: Statistical analysis

### Processing Dependencies
- `concurrent.futures`: Parallel processing
- `shutil`: File operations
- `time`: Performance timing

### Curation Dependencies
- `fitz` (PyMuPDF): PDF processing
- `PIL` (Pillow): Image processing
- `pytesseract`: OCR functionality
- `loguru`: Logging

## File Patterns

### Input Files
- `*.md`: Markdown notes
- `attachments/*`: Media files
- `config.py`: Configuration
- `config.yaml`: Curation config

### Output Files
- `processed/*.md`: Cleaned notes
- `curated/notes/*.md`: Curated notes
- `backup/*.md`: Backup files
- `logs/*.log`: Processing logs

### Data Files
- `analysis_output/*.json`: Analysis results
- `analysis_output/*.yaml`: Sample datasets
- `.metadata/faiss.index`: Embedding index
- `.metadata/manifest.jsonl`: Processing manifest
- `.metadata/note_register.db`: Note register SQLite database
- `reports/note_register.csv`: Register export in CSV format
- `reports/note_register.md`: Register export in Markdown format

## API Surface

### Public Classes
- `ContentAnalyzer`: Content analysis
- `NoteSampler`: Dataset sampling
- `BatchProcessor`: Preprocessing pipeline with incremental processing
- `FileHandler`: File operations
- `ContentClassifier`: Note classification
- `MetadataStandardizer`: Metadata processing
- `WebClippingCleaner`: Content cleaning
- `QualityValidator`: Quality assessment
- `NoteRegister`: Note register system for tracking processing stages

### Public Functions
- `get_curation_config()`: Configuration generation
- `update_curation_yaml()`: Config synchronization
- `iter_markdown_notes()`: File discovery
- `parse_front_matter()`: Frontmatter parsing

### Command-Line Interface
- `python scripts/main.py`: Analysis pipeline
- `python scripts/preprocess.py`: Preprocessing pipeline (incremental by default)
- `python -m src.curation.obsidian_curator.main`: Curation pipeline (incremental by default)
- `python scripts/update_config.py`: Configuration management
- `python scripts/manage_register.py`: Register management and reporting

## Extension Points

### Custom Classifiers
Implement custom classification logic by extending `ContentClassifier`

### Custom Cleaners
Add new cleaning patterns by extending `WebClippingCleaner`

### Custom Validators
Implement custom quality checks by extending `QualityValidator`

### Custom Extractors
Add new content sources by extending `extractors.py`

This technical specification provides comprehensive information for coding LLMs to understand, modify, and extend the Obsidian Curator codebase.
