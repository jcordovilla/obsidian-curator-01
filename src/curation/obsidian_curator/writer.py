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
    fm.append("---")
    body = f"## Curator Summary\n\n{summary}\n\n---\n\n"
    text = content.get('text','')
    body += text
    os.makedirs(out_notes, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write("\\n".join(fm) + "\\n" + body)
