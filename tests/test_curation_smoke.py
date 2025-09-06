import os, tempfile, shutil
import pytest
from pathlib import Path
from src.curation.obsidian_curator.main import run

def test_smoke_curate(tmp_path):
    """Smoke test for curation pipeline - requires Ollama to be running."""
    out_notes = tmp_path / "curated_notes"
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
      "taxonomy": {"categories":["PPP","Governance","Finance"]}
    }
    
    # Check if Ollama is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            pytest.skip("Ollama not available")
    except:
        pytest.skip("Ollama not available")
    
    run(cfg, vault=cfg["paths"]["vault"],
             attachments=cfg["paths"]["attachments"],
             out_notes=cfg["paths"]["out_notes"])
    curated = list(out_notes.glob("*.md"))
    assert len(curated) >= 1, "At least one curated note expected"
    txt = curated[0].read_text(encoding="utf-8")
    assert "curated: true" in txt
    assert "## Curator Summary" in txt
