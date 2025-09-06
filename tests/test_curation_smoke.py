import os, tempfile, shutil
from pathlib import Path
from src.curation.obsidian_curator.main import run
from config import VAULT_PATH, CURATION_ATTACHMENTS_PATH

def test_smoke_curate(tmp_path, monkeypatch):
    # Force test mode
    monkeypatch.setenv("OC_TEST_MODE", "1")

    out_notes = tmp_path / "curated_notes"
    out_notes.mkdir(parents=True, exist_ok=True)

    cfg = {
      "paths": {
        "vault": str(VAULT_PATH),
        "attachments": str(CURATION_ATTACHMENTS_PATH),
        "out_notes": str(out_notes)
      },
      "models": {"fast":"phi3:mini","main":"llama3.1:8b","embed":"nomic-embed-text"},
      "decision": {"keep_threshold":0.68,"gray_margin":0.05},
      "taxonomy": {"categories":["PPP","Governance","Finance"]}
    }

    run(cfg, vault=cfg["paths"]["vault"],
             attachments=cfg["paths"]["attachments"],
             out_notes=cfg["paths"]["out_notes"])

    curated = list(out_notes.glob("*.md"))
    assert len(curated) >= 1, "At least one curated note expected"
    txt = curated[0].read_text(encoding="utf-8")
    assert "curated: true" in txt
    assert "## Curator Summary" in txt
