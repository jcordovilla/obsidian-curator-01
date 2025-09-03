# 🧹 Obsidian Curator

**A comprehensive Python application for preprocessing and cleaning Obsidian vaults converted from Evernote.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

Obsidian Curator is a powerful tool designed to clean and standardize Obsidian vaults that have been converted from Evernote. It removes boilerplate content, standardizes metadata, preserves attachments, and ensures high-quality output suitable for knowledge management.

### ✨ Key Features

- **🧹 Boilerplate Removal**: Intelligently removes web clipping trash, social sharing buttons, ads
- **📊 Content Classification**: Automatically categorizes notes (web clipping, personal, technical, etc.)
- **📎 Attachment Preservation**: Complete handling of 15,000+ attachment files with validation
- **📅 Metadata Standardization**: Converts Evernote dates to ISO format, normalizes tags
- **🔍 Quality Validation**: Comprehensive quality assessment and reporting
- **⚡ Batch Processing**: Efficient parallel processing with configurable workers
- **🛡️ Safety First**: Automatic backups and rollback capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Obsidian vault with Evernote-converted notes

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd obsidian-curator-01
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

1. **Configure your vault path** in `config.py`:
   ```python
   VAULT_PATH = "/path/to/your/obsidian/vault"
   PREPROCESSING_OUTPUT_PATH = "/path/to/output/vault"
   ```

2. **Run preprocessing**
   ```bash
   python scripts/preprocess.py
   ```

3. **View results** in your output directory

## 📁 Project Structure

```
obsidian-curator-01/
├── src/                          # Core application code
│   ├── analysis/                 # Note analysis modules
│   │   ├── content_analyzer.py   # Content analysis and statistics
│   │   ├── note_sampler.py       # Stratified sampling
│   │   └── technical_characterizer.py  # Technical characterization
│   ├── preprocessing/            # Preprocessing pipeline
│   │   ├── batch_processor.py    # Main processing pipeline
│   │   ├── content_classifier.py # Note classification
│   │   ├── metadata_standardizer.py  # Metadata normalization
│   │   ├── quality_validator.py  # Quality assessment
│   │   └── web_clipping_cleaner.py  # Boilerplate removal
│   └── utils/                    # Utility functions
│       └── file_handler.py       # File operations
├── scripts/                      # Executable scripts
│   ├── main.py                   # Analysis and characterization
│   └── preprocess.py             # Main preprocessing script
├── tests/                        # Test files
│   └── test_performance.py       # Performance comparison tests
├── docs/                         # Documentation and reports
│   ├── analysis_output/          # Analysis results
│   ├── performance_test_results_*.json  # Test results
│   ├── PERFORMANCE_TEST_SUMMARY.md      # Performance analysis
│   ├── PREPROCESSING_README.md          # Detailed preprocessing guide
│   └── PROJECT_SUMMARY.md               # Project overview
├── config.py                     # Configuration settings
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🔧 Configuration

Edit `config.py` to customize:

- **Vault paths**: Input and output directories
- **Sample sizes**: For analysis and testing
- **Processing parameters**: Batch sizes, worker threads
- **Boilerplate patterns**: Custom patterns for content cleaning
- **Metadata fields**: Standardization rules

## 📊 Performance Results

### ✅ **Outstanding Performance Achieved**

- **Processing Success**: 100% (3,662/3,662 notes)
- **Attachment Preservation**: 100% (15,017/15,017 files)
- **Quality Score**: 99.9% excellent quality
- **Data Loss**: 0 files
- **Processing Speed**: 0.4 files/second

### 📈 **Content Categories Processed**

| Category | Count | Percentage |
|----------|-------|------------|
| Web Clipping | 1,382 | 37.7% |
| Business Card | 603 | 16.5% |
| Technical Document | 573 | 15.7% |
| PDF Annotation | 563 | 15.4% |
| Unknown | 306 | 8.4% |
| News Article | 184 | 5.0% |
| Personal Note | 51 | 1.4% |

## 🛠️ Advanced Usage

### Analysis and Characterization

```bash
# Analyze vault content
python scripts/main.py --analyze

# Generate technical characterization
python scripts/main.py --technical-analysis

# Sample analysis
python scripts/main.py --sample 100
```

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

### Performance Testing

```bash
# Run performance comparison test
python tests/test_performance.py --sample-size 50
```

## 🔍 What Gets Cleaned

### Web Clippings
- ❌ Social sharing buttons
- ❌ Navigation menus
- ❌ Advertisement content
- ❌ Cookie notices
- ❌ Newsletter signups
- ✅ Preserves main content
- ✅ Preserves images and links

### Metadata Standardization
- 📅 **Dates**: `"Created: Monday, April 15, 2016 at 6:27:24 PM"` → `"2026-04-15T18:27:24"`
- 🏷️ **Tags**: Normalized formatting and ordering
- 📋 **Fields**: Consistent field ordering and structure
- 🌐 **Language**: Proper language detection and tagging

### Content Quality
- 📝 **Structure**: Improved formatting and organization
- 🔗 **Links**: Validated attachment references
- 📊 **Statistics**: Content analysis and quality scoring
- 🎯 **Classification**: Automatic content categorization

## 🛡️ Safety Features

- **Automatic Backups**: Original files backed up before processing
- **Rollback Capability**: Easy restoration from backups
- **Dry Run Mode**: Test processing without making changes
- **Validation**: Comprehensive quality and integrity checks
- **Error Handling**: Robust error recovery and reporting

## 📚 Documentation

- **[Preprocessing Guide](docs/PREPROCESSING_README.md)**: Detailed preprocessing instructions
- **[Performance Analysis](docs/PERFORMANCE_TEST_SUMMARY.md)**: Comprehensive performance results
- **[Project Summary](docs/PROJECT_SUMMARY.md)**: Complete project overview
- **[Analysis Results](docs/analysis_output/)**: Technical characterization and analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for cleaning Evernote-converted Obsidian vaults
- Designed for knowledge management workflows
- Optimized for large-scale content processing

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the repository
- Check the documentation in the `docs/` directory
- Review the performance test results for examples

---

**Made with ❤️ for the Obsidian community**
