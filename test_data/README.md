# Test Data

This directory contains test data for the Obsidian Curator pipeline.

## Structure

- `source/` - Original test notes (input to the curation pipeline)
- `curated/` - Curated notes (output from the curation pipeline)

## Test Scripts

- `test_curation_pipeline.py` - Run curation pipeline with production thresholds
- `test_curation_pipeline_lenient.py` - Run curation pipeline with lenient thresholds (ensures notes are kept)
- `compare_results.py` - Compare original vs curated notes

## Usage

```bash
# Run with production thresholds (some notes may be discarded)
python test_curation_pipeline.py

# Run with lenient thresholds (all notes kept for testing)
python test_curation_pipeline_lenient.py

# Compare results
python compare_results.py
```

## Notes

- All test scripts use real LLM calls (no test mode stubs)
- Ensure Ollama is running before executing tests
- Test data is automatically created if not present
