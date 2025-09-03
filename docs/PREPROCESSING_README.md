# Obsidian Vault Preprocessor

A comprehensive Python application for cleaning and preprocessing Obsidian notes converted from Evernote. This tool removes boilerplate content, standardizes metadata, and optimizes notes for knowledge management.

## 🚀 Quick Start

### 1. Analysis (Recommended First Step)
```bash
# Analyze your vault structure and content patterns
python main.py --sample --analyze --technical-analysis --sample-size 200

# This generates:
# - analysis_output/coding_agent_brief.md (technical specifications)
# - analysis_output/technical_characterization.json (detailed analysis)
# - analysis_output/analysis_report.md (summary)
```

### 2. Test Preprocessing
```bash
# Test with a small sample (dry run - no changes made)
python preprocess.py --sample 10 --dry-run

# Test specific content categories
python preprocess.py --sample 20 --categories web_clipping --dry-run
```

### 3. Full Vault Processing
```bash
# Process entire vault (outputs to /Users/jose/Documents/Obsidian/Ever-output)
python preprocess.py

# High-performance processing
python preprocess.py --batch-size 100 --workers 8

# Process only specific categories
python preprocess.py --categories web_clipping news_article

# Custom output directory (override default)
python preprocess.py --output /path/to/custom/output
```

## 📊 What It Does

Based on analysis of your 3,712-note vault, this system:

### Content Processing (By Category)
- **Web Clippings (60%)**: Removes navigation, social sharing, ads, subscription prompts
- **Personal Notes (11.5%)**: Gentle formatting cleanup, preserves all content  
- **PDF Annotations (9.5%)**: Validates attachments, preserves context
- **Unknown Content (14%)**: Minimal cleanup, flags for review
- **Business Cards (3%)**: Structures contact information
- **Technical Documents (2%)**: Preserves code blocks and technical structure

### Metadata Standardization
- Converts Evernote date formats to ISO standard (YYYY-MM-DD HH:MM:SS)
- Normalizes tags and language codes
- Ensures required fields: title, date created, date modified, language
- Validates and cleans source URLs

### Quality Assurance
- Validates processed content integrity
- Checks link and attachment references
- Ensures proper encoding and formatting
- Generates detailed quality reports

## 🏗️ Architecture

```
src/
├── analysis/           # Vault analysis and characterization
│   ├── note_sampler.py
│   ├── content_analyzer.py
│   └── technical_characterizer.py
├── preprocessing/      # Batch processing pipeline
│   ├── batch_processor.py       # Main pipeline orchestrator
│   ├── metadata_standardizer.py # Metadata cleanup
│   ├── web_clipping_cleaner.py  # Boilerplate removal
│   ├── content_classifier.py    # Note type detection
│   └── quality_validator.py     # Quality assurance
└── utils/
    └── file_handler.py          # Safe file operations
```

## 🔧 Processing Pipeline

1. **Validation & Backup**: Validates files and creates backups
2. **Attachment Copying**: Copies entire attachments folder (1,022+ files)
3. **Content Classification**: Identifies note types (web clipping, personal, etc.)
4. **Metadata Standardization**: Normalizes frontmatter fields
5. **Content Processing**: Applies category-specific cleaning rules
6. **Attachment Validation**: Verifies all attachment references exist
7. **Quality Validation**: Ensures processing integrity
8. **Output Generation**: Creates cleaned notes with reports

## 📈 Performance

- **Speed**: ~2-5 seconds per note
- **Parallel Processing**: Configurable worker threads
- **Memory Efficient**: Batch processing with configurable batch sizes
- **Safe**: Automatic backups and rollback capabilities

## 🎯 Key Features

### Smart Boilerplate Removal
Removes 23 identified boilerplate patterns including:
- Social sharing buttons (Facebook, Twitter, LinkedIn)
- Navigation elements (home, about, search, menu)
- Subscription prompts and registration forms
- Advertisement blocks and sponsored content

### Metadata Preservation
Maintains essential knowledge management metadata:
- **Required**: title, date created, date modified, language
- **Optional**: source URLs, tags
- **Custom**: Preserves any additional fields

### Quality Assurance
- **Excellent**: 68% of notes (minimal processing needed)
- **Good/Medium**: 32% of notes (cleanup applied)
- **Failed**: <1% (flagged for manual review)

## 📝 Usage Examples

### Basic Processing
```bash
# Process entire vault (outputs to /Users/jose/Documents/Obsidian/Ever-output)
python preprocess.py

# Dry run to see what would be changed (no files created)
python preprocess.py --dry-run
```

### Advanced Options
```bash
# High-performance batch processing
python preprocess.py --batch-size 100 --workers 8

# Process only web clippings (60% of your content)
python preprocess.py --categories web_clipping

# Custom output directory
python preprocess.py --output /path/to/cleaned_vault

# Disable backups (not recommended)
python preprocess.py --no-backup
```

### Analysis and Testing
```bash
# Complete analysis workflow
python main.py --sample --analyze --technical-analysis --sample-size 200

# Test preprocessing on sample
python preprocess.py --sample 50 --dry-run

# Quick preprocessing test
python main.py --preprocess
```

## 📊 Expected Results

After processing your vault:
- **15-20% reduction** in content volume (boilerplate removal)
- **Standardized metadata** across all 3,712 notes
- **Consistent formatting** and structure
- **Preserved valuable content** with enhanced readability
- **Detailed processing reports** and quality metrics

## 🔍 Output Files

### Processing Results (in /Users/jose/Documents/Obsidian/Ever-output/)
- `*/` - Cleaned notes (mirrors original vault folder structure)
- `backup/` - Original file backups with timestamps
- `reports/processing_summary_YYYYMMDD_HHMMSS.json` - Processing statistics
- `logs/processing_log_YYYYMMDD_HHMMSS.json` - Detailed processing log

### Analysis Results (from main.py)
- `analysis_output/coding_agent_brief.md` - Technical specifications
- `analysis_output/technical_characterization.json` - Detailed analysis data
- `analysis_output/sample_dataset.yaml` - Sample data for reference

## ⚠️ Important Notes

1. **Always run analysis first** to understand your vault's content patterns
2. **Test with samples** before processing the entire vault
3. **Backups are created automatically** but verify they exist
4. **Processing is irreversible** without backups
5. **Quality validation** ensures content integrity

## 🚨 Safety Features

- **Automatic backups** with timestamps
- **Dry run mode** for safe testing
- **Validation checks** at every stage
- **Error handling** with detailed logging
- **Rollback capability** using backups

## 🎉 Ready to Process!

Your vault shows excellent potential for optimization:
- **Minimal boilerplate** (only 1.5% of notes)
- **High-quality content** (68% excellent/good)
- **Clear content patterns** (86% classifiable)
- **Rich attachments** (1,022 files across 139 notes)

The preprocessing system is ready to transform your 3,712 notes into a clean, optimized knowledge management vault!
