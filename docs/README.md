# Obsidian Curator

A Python application for analyzing and preprocessing Obsidian notes converted from Evernote, designed to identify content types, remove boilerplate, and extract useful content for knowledge management.

## Features

- **Smart Sampling**: Extracts representative samples from large note collections using stratified sampling
- **Content Classification**: Automatically categorizes notes into types (web clippings, PDFs, typed notes, etc.)
- **Boilerplate Detection**: Identifies and quantifies conversion artifacts and web boilerplate
- **Quality Assessment**: Evaluates note usefulness and content quality
- **Comprehensive Analysis**: Provides detailed statistics and reports

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

1. **Create a sample dataset** (100 notes from your vault):
   ```bash
   python main.py --sample
   ```

2. **Analyze the sample**:
   ```bash
   python main.py --analyze
   ```

3. **Do both in one command**:
   ```bash
   python main.py --sample --analyze
   ```

### Advanced Usage

- **Custom sample size**:
  ```bash
  python main.py --sample --sample-size 200
  ```

- **Different vault path**:
  ```bash
  python main.py --vault-path "/path/to/your/vault" --sample --analyze
  ```

- **Custom output directory**:
  ```bash
  python main.py --output-dir "my_analysis" --sample --analyze
  ```

## Output Files

The analysis generates several output files in the `analysis_output/` directory:

- `sample_dataset.yaml`: Raw data from sampled notes
- `content_analysis.json`: Detailed analysis results
- `analysis_report.md`: Human-readable summary report

## Content Categories

The tool automatically classifies notes into these categories:

- **Web Clipping**: Articles and content scraped from websites
- **PDF Annotation**: Notes with attached PDF documents
- **Business Card**: Contact information and business cards
- **News Article**: News content and articles
- **Technical Document**: Technical documentation and guides
- **Personal Note**: Short personal notes and observations
- **Unknown**: Content that doesn't fit other categories

## Analysis Features

### Content Indicators
- Attachment detection (PDFs, images)
- URL and email extraction
- Structural analysis (headers, lists, tables)
- Formatting assessment

### Boilerplate Detection
- Web navigation elements
- Social media buttons
- Cookie/privacy notices
- Advertisement content
- Subscription prompts

### Quality Assessment
- Content structure evaluation
- Meaningful content ratio
- Boilerplate percentage
- Overall usefulness scoring

## Configuration

Edit `config.py` to customize:
- Vault path
- Sample size
- Analysis categories
- Boilerplate patterns
- Output settings

## Requirements

- Python 3.7+
- PyYAML
- requests

## Example Output

```
ANALYSIS SUMMARY
========================================
Total notes analyzed: 100
Average word count: 342.5
High boilerplate notes: 23

Content categories:
  Web Clipping        :  45 ( 45.0%)
  Personal Note       :  18 ( 18.0%)
  Technical Document  :  15 ( 15.0%)
  News Article        :  12 ( 12.0%)
  Business Card       :   6 (  6.0%)
  PDF Annotation      :   3 (  3.0%)
  Unknown             :   1 (  1.0%)

Quality distribution:
  Medium              :  52 ( 52.0%)
  Low                 :  31 ( 31.0%)
  High                :  17 ( 17.0%)
```

## Next Steps

This analysis provides the foundation for:
1. **Automated preprocessing** based on content categories
2. **Boilerplate removal** using identified patterns
3. **Content prioritization** based on quality scores
4. **Batch processing** of the full vault (4000+ notes)

The insights from this sample analysis can be used to develop targeted preprocessing rules for each content type.
