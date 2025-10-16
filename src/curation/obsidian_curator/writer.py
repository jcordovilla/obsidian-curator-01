import os, pathlib, datetime, shutil

def write_curated_note(note_path, meta, cats, tags, ents, summary, content, score, cfg, preprocessed_attachments=None):
    out_notes = cfg['paths']['out_notes']
    # Use the passed preprocessed_attachments or fall back to cfg
    if preprocessed_attachments is None:
        preprocessed_attachments = cfg['paths']['attachments']
    rel = pathlib.Path(note_path).name
    out = os.path.join(out_notes, rel)
    fm = []
    fm.append("---")
    fm.append(f'title: {meta.get("title","")}')
    fm.append(f'curated: true')
    fm.append(f'curated_at: {datetime.date.today().isoformat()}')
    fm.append(f'content_type: {content.get("kind")}')
    fm.append(f'categories: {cats}')
    fm.append(f'tags: {tags}')
    fm.append(f'usefulness: {score:.3f}')
    
    # Add extracted entities
    if ents:
        if ents.get('organizations'):
            fm.append(f'organizations: {ents["organizations"]}')
        if ents.get('projects'):
            fm.append(f'projects: {ents["projects"]}')
        if ents.get('technologies'):
            fm.append(f'technologies: {ents["technologies"]}')
        if ents.get('locations'):
            fm.append(f'locations: {ents["locations"]}')
    
    # Preserve important source metadata
    if meta.get('source'):
        fm.append(f'source: {meta.get("source")}')
    if meta.get('date created'):
        fm.append(f'date created: {meta.get("date created")}')
    if meta.get('date modified'):
        fm.append(f'date modified: {meta.get("date modified")}')
    if meta.get('language'):
        fm.append(f'language: {meta.get("language")}')
    
    fm.append("---")
    body = f"## Curator Summary\n\n{summary}\n\n---\n\n"
    
    # For PDFs, add attachment reference instead of full text
    if content.get('kind') in ['pdf', 'pdf_note']:
        # Add reference to original PDF attachment
        note_stem = pathlib.Path(note_path).stem
        body += f"**Source Document**: See attached PDF: `{note_stem}.pdf`\n\n"
        body += f"**Pages**: {content.get('pages', 'Unknown')} pages\n\n"
        body += "**Note**: Full PDF content available in attachments folder.\n"
    else:
        # For non-PDF content, include the full text without truncation
        text = content.get('text','')
        body += text
    os.makedirs(out_notes, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write("\n".join(fm) + "\n" + body)
    
    # Copy attachments to curated folder
    copy_attachments_to_curated(note_path, cfg, preprocessed_attachments)


def copy_attachments_to_curated(note_path, cfg, preprocessed_attachments):
    """Copy attachments from preprocessed to curated folder."""
    try:
        # Get paths from passed parameter
        curated_notes = cfg['paths']['out_notes']
        curated_attachments = os.path.join(os.path.dirname(curated_notes), 'attachments')
        
        # Get note name with extension (attachment folders use full filename)
        note_filename = pathlib.Path(note_path).name
        
        # Look for attachment folder in preprocessed
        attachment_folder = os.path.join(preprocessed_attachments, f"{note_filename}.resources")
        
        if os.path.exists(attachment_folder):
            # Create curated attachments directory
            os.makedirs(curated_attachments, exist_ok=True)
            
            # Copy the attachment folder
            curated_attachment_folder = os.path.join(curated_attachments, f"{note_filename}.resources")
            if os.path.exists(curated_attachment_folder):
                shutil.rmtree(curated_attachment_folder)
            
            shutil.copytree(attachment_folder, curated_attachment_folder)
            print(f"✓ Copied attachments for {note_filename}")
        else:
            # Check for alternative attachment locations
            alt_locations = [
                os.path.join(preprocessed_attachments, note_filename),
                os.path.join(preprocessed_attachments, f"{note_filename}_files"),
                os.path.join(preprocessed_attachments, f"{note_filename}_attachments")
            ]
            
            for alt_location in alt_locations:
                if os.path.exists(alt_location):
                    os.makedirs(curated_attachments, exist_ok=True)
                    curated_attachment_folder = os.path.join(curated_attachments, f"{note_filename}.resources")
                    if os.path.exists(curated_attachment_folder):
                        shutil.rmtree(curated_attachment_folder)
                    
                    shutil.copytree(alt_location, curated_attachment_folder)
                    print(f"✓ Copied attachments for {note_filename} from {os.path.basename(alt_location)}")
                    break
    
    except Exception as e:
        print(f"Warning: Failed to copy attachments for {note_filename}: {e}")

def write_triage_note(note_path, meta, cats, tags, ents, content, score, cfg, preprocessed_attachments=None):
    """Write triage note with rich metadata for manual review."""
    triage_dir = cfg['paths']['out_notes'].replace('/notes', '/triage')
    os.makedirs(triage_dir, exist_ok=True)
    
    # Use the passed preprocessed_attachments or fall back to cfg
    if preprocessed_attachments is None:
        preprocessed_attachments = cfg['paths']['attachments']
    
    rel = pathlib.Path(note_path).name
    out = os.path.join(triage_dir, rel)
    
    fm = []
    fm.append("---")
    fm.append(f'title: {meta.get("title","")}')
    fm.append(f'triaged: true')
    fm.append(f'triaged_at: {datetime.date.today().isoformat()}')
    fm.append(f'content_type: {content.get("kind")}')
    fm.append(f'categories: {cats}')
    fm.append(f'tags: {tags}')
    fm.append(f'usefulness: {score:.3f}')
    
    # Add extracted entities
    if ents:
        if ents.get('organizations'):
            fm.append(f'organizations: {ents["organizations"]}')
        if ents.get('projects'):
            fm.append(f'projects: {ents["projects"]}')
        if ents.get('technologies'):
            fm.append(f'technologies: {ents["technologies"]}')
        if ents.get('locations'):
            fm.append(f'locations: {ents["locations"]}')
    
    # Add original metadata
    if meta.get('source'):
        fm.append(f'source: {meta["source"]}')
    if meta.get('date created'):
        fm.append(f'date created: {meta["date created"]}')
    if meta.get('date modified'):
        fm.append(f'date modified: {meta["date modified"]}')
    if meta.get('language'):
        fm.append(f'language: {meta["language"]}')
    
    fm.append("---")
    fm.append("## Triage Note")
    fm.append("")
    fm.append(f"**Score**: {score:.3f} (below curation threshold)")
    fm.append("")
    fm.append("**Reason for Triage**: This note was automatically triaged for manual review.")
    fm.append("")
    fm.append("**Content**:")
    fm.append("")
    
    # Add the original content
    body = content.get('text', '').strip()
    if body:
        fm.append(body)
    else:
        fm.append("*No content extracted*")
    
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fm))
    
    # Copy attachments if they exist
    copy_attachments_to_curated(note_path, cfg, preprocessed_attachments)
