import os, pathlib, datetime

def write_curated_note(note_path, meta, cats, tags, ents, summary, content, score, cfg):
    out_notes = cfg['paths']['out_notes']
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
    if content.get('kind') == 'pdf':
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
