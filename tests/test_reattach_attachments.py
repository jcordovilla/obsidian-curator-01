import importlib.util
import os
import tempfile
from pathlib import Path


def load_script_module(path: Path):
    spec = importlib.util.spec_from_file_location("reattach", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_find_and_detect_pdf_tmp_sample():
    # Prepare a tiny temp directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        notes_root = tmp / "notes"
        att_root = tmp / "attachments_src"
        dest_root = tmp / "attachments_dst"
        notes_root.mkdir()
        att_root.mkdir()

        # create a note with the exact snippet
        note = notes_root / "Test Note.md"
        note.write_text("This is a test.\n**Note**: Full PDF content available in attachments folder.\nEnd.", encoding="utf-8")

        # create attachments folder matching basename and a PDF inside
        folder = att_root / "Test Note.resources"
        folder.mkdir()
        pdf = folder / "document.pdf"
        pdf.write_bytes(b"%PDF-1.4 test pdf content")

        # load module
        # repository root is the parent of the tests directory
        repo_root = Path(__file__).resolve().parents[1]
        script_path = repo_root / "scripts" / "reattach_attachments.py"
        mod = load_script_module(script_path)

        # use find_notes_with_snippet
        notes = mod.find_notes_with_snippet(notes_root)
        assert len(notes) == 1

        # find pdfs for the note
        found = mod.find_pdfs_for_note(att_root, notes[0])
        assert len(found) == 1

        # process_notes in dry-run mode
        results = mod.process_notes(notes_root, att_root, dest_root, sample=None, dry_run=True)
        assert len(results) == 1
