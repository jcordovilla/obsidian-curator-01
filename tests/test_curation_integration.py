import os
import pytest
from pathlib import Path
from src.curation.obsidian_curator.main import run

def test_integration_basic(tmp_path):
    """Integration test for curation pipeline - requires Ollama to be running."""
    out_notes = tmp_path / "out"
    out_notes.mkdir(parents=True, exist_ok=True)
    
    # Use test data if available, otherwise skip
    test_source = Path("test_data/source")
    if not test_source.exists() or not any(test_source.glob("*.md")):
        pytest.skip("No test data available - run test_curation_pipeline.py first")
    
    cfg = {
      "paths": {
        "vault": str(test_source),
        "attachments": str(test_source),
        "out_notes": str(out_notes)
      },
      "models": {"fast":"phi3:mini","main":"llama3.1:8b","embed":"nomic-embed-text"},
      "decision": {"keep_threshold":0.3,"gray_margin":0.05},  # Lenient for testing
      "taxonomy": {"categories":["PPP","Governance","Finance","ESG"]}
    }
    
    # Check if Ollama is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            pytest.skip("Ollama not available")
    except:
        pytest.skip("Ollama not available")
    
    run(cfg, vault=cfg["paths"]["vault"], attachments=cfg["paths"]["attachments"], out_notes=str(out_notes))
    
    for md in out_notes.glob("*.md"):
        t = md.read_text(encoding="utf-8")
        assert "content_type:" in t
        assert "usefulness:" in t
        assert "categories:" in t
