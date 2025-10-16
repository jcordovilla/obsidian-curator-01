# 🧹 Obsidian Curator

**AI-powered knowledge curation for infrastructure investment professionals**

Transform your raw Obsidian vault into a publication-ready research database with professional summaries, intelligent categorization, and citation-ready content.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 What It Does

Obsidian Curator transforms your raw notes into a professional knowledge base by:

- **🧹 Cleaning & Standardizing**: Removes boilerplate, fixes formatting, standardizes metadata
- **🤖 AI Analysis**: Uses OpenAI models to analyze content usefulness and relevance
- **📚 Professional Summaries**: Generates citation-ready abstracts and technical contributions
- **🏷️ Smart Classification**: Categorizes content by infrastructure sectors and themes
- **📊 Quality Scoring**: Ranks content for professional publication value

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Clone and setup
git clone <repository-url>
cd obsidian-curator-01
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Paths

Edit `config.py` to set your vault paths:

```python
RAW_VAULT_PATH = "/path/to/your/raw/obsidian/vault"
PREPROCESSED_VAULT_PATH = "/path/to/preprocessed/vault" 
CURATED_VAULT_PATH = "/path/to/curated/vault"
```

### 3. Test First (Recommended)

```bash
# Test with 10 random notes
python tests/test_complete_pipeline.py 10
```

### 4. Run the Pipeline

```bash
# Step 1: Preprocessing (cleans and standardizes)
python scripts/preprocess.py

# Step 2: Curation (AI analysis and summarization)
python -m src.curation.obsidian_curator.main
```

## 📁 Output Structure

Your curated vault will contain:

```
/Users/jose/Documents/Obsidian/Ever-curated/
├── notes/           # High-value notes (score ≥ 0.45)
├── triage/          # Medium-value notes (manual review)
└── attachments/     # Copied attachments
```

**Decision Logic:**
- **Keep**: Professional quality content ready for publication
- **Triage**: Good content requiring manual review
- **Discard**: Low-value or irrelevant content

## 💰 Cost Estimate

- **Cost per note**: ~$0.001-0.002 (less than 1 cent)
- **1,000 notes**: ~$1-2 total cost
- **Processing time**: ~2-4 hours for 1,000 notes

Uses GPT-4o-mini for cost efficiency while maintaining high quality.

## 🏗️ Project Structure

```
obsidian-curator-01/
├── src/
│   ├── preprocessing/    # Cleaning and standardization
│   ├── curation/        # AI analysis and summarization
│   └── utils/           # Helper functions
├── scripts/
│   ├── preprocess.py    # Main preprocessing script
│   └── update_config.py # Configuration sync
├── tests/               # Test framework
├── config.py           # Main configuration
└── requirements.txt    # Dependencies
```

## 🔧 Configuration

The system uses `config.py` as the single source of truth for all settings:

- **Vault paths**: Raw, preprocessed, and curated directories
- **AI models**: OpenAI model selection and parameters
- **Processing options**: Batch sizes, worker threads
- **Quality thresholds**: Keep/triage/discard scores

## 🧪 Testing

Comprehensive testing framework included:

```bash
# Basic test
python tests/test_complete_pipeline.py 10

# Reproducible test
python tests/test_complete_pipeline.py 10 --seed 42

# Incremental testing
python tests/test_complete_pipeline.py 15 --incremental

# Partial pipeline testing
python tests/test_complete_pipeline.py --stages preprocess
```

## 📊 What Gets Processed

### Content Types
- **Web Clippings**: Articles, reports, blog posts
- **PDF Annotations**: Technical documents with PDF attachments
- **News Articles**: Industry news and analysis
- **Technical Documents**: Research papers, presentations
- **Personal Notes**: Professional notes and observations

### Cleaning Process
- ❌ Removes: Social buttons, ads, navigation, cookie notices
- ✅ Preserves: Main content, images, links, structure
- 📅 Standardizes: Dates, metadata, formatting

## 🛡️ Safety Features

- **Automatic Backups**: Original files preserved
- **Dry Run Mode**: Test without changes
- **Rollback Capability**: Easy restoration
- **Validation**: Comprehensive quality checks
- **Error Handling**: Robust recovery and reporting

## 📚 Documentation

- **[Usage Guide](docs/USAGE.md)**: Detailed usage instructions
- **[Technical Spec](docs/TECHNICAL_SPECIFICATION.md)**: Developer documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the Obsidian community**