#!/usr/bin/env python3
"""
Script to relocate PDF attachments for moved Obsidian notes and insert markdown links.

Behavior:
- Scan notes under a notes root for the exact snippet:
  "**Note**: Full PDF content available in attachments folder."
- For each matching note, try to locate PDF(s) in the preprocessed attachments root
  usually under a folder with the note basename and a ".resources" suffix.
- Copy matched PDF(s) into a destination attachments folder.
- Insert a markdown link to the copied file right after the snippet occurrence.

Safety features:
- --dry-run (default): no files are copied or modified; prints planned actions.
- --apply: perform the copy and file edits.
- --sample N: operate on a random sample of N matching notes (for testing smaller set).

Do NOT run this script automatically; it's prepared for manual invocation.
"""

from __future__ import annotations

import argparse
import os
import random
import re
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

SNIPPET = "**Note**: Full PDF content available in attachments folder."
PDF_EXTS = {".pdf", ".PDF"}
DEFAULT_BACKUP_FOLDER = "/Users/jose/obsidian/JC/Attachments/.backups"


def find_notes_with_snippet(notes_root: Path, snippet: str = SNIPPET) -> List[Path]:
    notes = []
    for p in notes_root.rglob("*.md"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            # skip unreadable files
            continue
        if snippet in text:
            notes.append(p)
    return notes


def find_pdfs_for_note(attachments_root: Path, note_path: Path) -> List[Path]:
    """
    Heuristic search for PDFs related to a note.

    Strategy:
    - Look for folders under attachments_root matching <basename>*.resources and search inside
      for PDF files.
    - If none found, look for any PDFs whose filenames contain the basename.
    - Return full paths to PDF files (can be empty list).
    """
    basename = note_path.stem
    results: List[Path] = []

    # 1) search for <basename>*.resources directories
    for folder in attachments_root.rglob(f"{basename}*.resources"):
        if folder.is_dir():
            for f in folder.rglob("*"):
                if f.suffix in PDF_EXTS and f.is_file():
                    results.append(f)

    # 2) if none found, look for PDFs with basename in filename
    if not results:
        for f in attachments_root.rglob("*.*"):
            if f.suffix in PDF_EXTS and basename in f.name:
                results.append(f)

    # 3) de-dupe
    uniq = []
    seen = set()
    for p in results:
        if str(p) not in seen:
            uniq.append(p)
            seen.add(str(p))
    return uniq


def copy_attachment(src: Path, dest_dir: Path, dry_run: bool = True) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    # if target exists, add numeric suffix
    if dest.exists():
        base = src.stem
        ext = src.suffix
        i = 1
        while True:
            candidate = dest_dir / f"{base}-{i}{ext}"
            if not candidate.exists():
                dest = candidate
                break
            i += 1

    if dry_run:
        print(f"[dry-run] Would copy: {src} -> {dest}")
    else:
        shutil.copy2(src, dest)
        print(f"Copied: {src} -> {dest}")
    return dest


def insert_link_after_snippet(note_path: Path, snippet: str, link_text: str, link_path: str, dry_run: bool = True) -> bool:
    """Insert a markdown link right after the first occurrence of snippet in the note.

    Returns True if modification was (or would be) made, False otherwise.
    """
    text = note_path.read_text(encoding="utf-8")
    idx = text.find(snippet)
    if idx == -1:
        return False

    # find location to insert: after the snippet's line
    # we'll insert a newline + markdown link if not already present
    insert_pos = idx + len(snippet)

    # see if a link to the target already exists right after snippet
    remainder = text[insert_pos: insert_pos + 200]  # look ahead
    if link_path in remainder:
        print(f"Link already present in {note_path}")
        return False

    # construct markdown link. To avoid absolute paths, we'll insert the provided link_path as-is.
    md_link = f"\n\n[PDF Attachment]({link_path})\n"

    new_text = text[:insert_pos] + md_link + text[insert_pos:]

    if dry_run:
        print(f"[dry-run] Would insert link into {note_path}: {md_link.strip()}")
    else:
        # make a simple backup
        bak = note_path.with_suffix(note_path.suffix + ".bak")
        note_path.replace(note_path)  # touch, avoid flake
        shutil.copy2(note_path, bak)
        note_path.write_text(new_text, encoding="utf-8")
        print(f"Inserted link into {note_path}; backup at {bak}")
    return True


def process_notes(notes_root: Path, attachments_root: Path, dest_attachments: Path, backup_folder: Optional[Path] = None, sample: Optional[int] = None, dry_run: bool = True) -> List[Tuple[Path, List[Path], Path]]:
    """
    Process notes and return a list of tuples: (note_path, pdf_sources, copied_dest)
    For notes with multiple PDFs, returns the first copied dest for the tuple; adjust if needed.
    
    Also handles:
    - Moving .md.bak backup files to backup_folder
    - Renaming notes without PDFs to add ACTION- prefix and copying their backups
    """
    if backup_folder is None:
        backup_folder = Path(DEFAULT_BACKUP_FOLDER)
    
    notes = find_notes_with_snippet(notes_root)
    print(f"Found {len(notes)} notes containing the snippet under {notes_root}")

    if sample and sample > 0 and sample < len(notes):
        notes = random.sample(notes, sample)
        print(f"Sampling {len(notes)} notes for processing")

    results = []
    notes_without_attachments = []
    
    for note in notes:
        pdfs = find_pdfs_for_note(attachments_root, note)
        if not pdfs:
            notes_without_attachments.append(note)
            print(f"No PDFs found for note: {note}")
            continue

        copied_paths = []
        for pdf in pdfs:
            dest = copy_attachment(pdf, dest_attachments, dry_run=dry_run)
            copied_paths.append(dest)

        # choose first copied path for linking (if multiple, you could add all)
        first_dest = copied_paths[0] if copied_paths else None
        if first_dest:
            # compute relative path from note to destination file for nicer markdown link
            rel = os.path.relpath(str(first_dest), start=str(note.parent))
            inserted = insert_link_after_snippet(note, SNIPPET, "PDF Attachment", rel, dry_run=dry_run)
            if inserted:
                results.append((note, pdfs, first_dest))
                # move the backup file created by insert_link_after_snippet
                bak = note.with_suffix(note.suffix + ".bak")
                move_backup_file(bak, backup_folder, dry_run=dry_run)

    # Handle notes without attachments: rename and copy backup
    for note in notes_without_attachments:
        rename_note_to_action(note, dry_run=dry_run)
        # if there's a backup from a previous run, copy it
        bak = note.with_suffix(note.suffix + ".bak")
        if bak.exists():
            move_backup_file(bak, backup_folder, dry_run=dry_run)

    return results


def move_backup_file(backup_path: Path, backup_folder: Path, dry_run: bool = True) -> bool:
    """Move a .md.bak file to the backup folder. Returns True if moved (or would be moved)."""
    if not backup_path.exists():
        return False
    
    backup_folder.mkdir(parents=True, exist_ok=True)
    dest = backup_folder / backup_path.name
    
    # handle collision
    if dest.exists():
        base = backup_path.stem.replace(".md", "")  # remove .md from stem
        ext = backup_path.suffix  # .bak
        i = 1
        while True:
            candidate = backup_folder / f"{base}-{i}{ext}"
            if not candidate.exists():
                dest = candidate
                break
            i += 1
    
    if dry_run:
        print(f"[dry-run] Would move backup: {backup_path} -> {dest}")
    else:
        shutil.move(str(backup_path), str(dest))
        print(f"Moved backup: {backup_path} -> {dest}")
    
    return True


def rename_note_to_action(note_path: Path, dry_run: bool = True) -> bool:
    """Rename a note file to add ACTION- prefix. Returns True if renamed (or would be renamed)."""
    if note_path.name.startswith("ACTION-"):
        return False  # already renamed
    
    new_name = f"ACTION-{note_path.name}"
    new_path = note_path.parent / new_name
    
    if dry_run:
        print(f"[dry-run] Would rename: {note_path.name} -> {new_name}")
    else:
        note_path.rename(new_path)
        print(f"Renamed: {note_path.name} -> {new_name}")
    
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description="Reattach PDFs for moved notes and insert links")
    parser.add_argument("--notes-root", type=Path, default=Path("/Users/jose/obsidian/JC/4.ARCHIVO/Evernote"),
                        help="Root folder containing notes to scan")
    parser.add_argument("--attachments-root", type=Path, default=Path("/Users/jose/obsidian/Ever-preprocessed/attachments"),
                        help="Root folder where original attachments live")
    parser.add_argument("--dest-attachments", type=Path, default=Path("/Users/jose/obsidian/JC/Attachments"),
                        help="Destination folder for copied attachments")
    parser.add_argument("--backup-folder", type=Path, default=Path(DEFAULT_BACKUP_FOLDER),
                        help="Folder where backup .md.bak files and ACTION- notes will be stored")
    parser.add_argument("--sample", type=int, default=0, help="Process a random sample of N matching notes (0 = all)")
    parser.add_argument("--apply", action="store_true", help="Actually copy files and modify notes (default is dry-run)")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args(argv)

    dry_run = not args.apply
    results = process_notes(args.notes_root, args.attachments_root, args.dest_attachments,
                            backup_folder=args.backup_folder, sample=(args.sample or None), dry_run=dry_run)

    print(f"Processed {len(results)} notes (dry_run={dry_run})")


if __name__ == "__main__":
    main()
