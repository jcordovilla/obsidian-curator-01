import os
from pathlib import Path
from src.curation.obsidian_curator.main import run
from config import VAULT_PATH, CURATION_ATTACHMENTS_PATH

def test_integration_basic(tmp_path, monkeypatch):
    monkeypatch.setenv("OC_TEST_MODE", "1")

    # Use a tiny subset of the vault if you have a sample folder;
    # otherwise reuse VAULT_PATH; test mode stubs make it safe.
    out_notes = tmp_path / "out"
    out_notes.mkdir(parents=True, exist_ok=True)

    cfg = {
      "paths": {
        "vault": str(VAULT_PATH),
        "attachments": str(CURATION_ATTACHMENTS_PATH),
        "out_notes": str(out_notes)
      },
      "models": {"fast":"phi3:mini","main":"llama3.1:8b","embed":"nomic-embed-text"},
      "decision": {"keep_threshold":0.68,"gray_margin":0.05},
      "taxonomy": {"categories":["PPP","Governance","Finance","ESG"]}
    }

    run(cfg, vault=cfg["paths"]["vault"], attachments=cfg["paths"]["attachments"], out_notes=str(out_notes))

    for md in out_notes.glob("*.md"):
        t = md.read_text(encoding="utf-8")
        assert "content_type:" in t
        assert "usefulness:" in t
        assert "categories:" in t
