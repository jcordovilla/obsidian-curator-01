from loguru import logger
import argparse, os, yaml
import sys
from pathlib import Path

# Add project root to path for config import
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from .detector import detect_assets, choose_primary
from .extractors import extract_content
from .analyze import analyze_features, score_usefulness, decide
from .classify import classify_json
from .summarize import summarize_content
from .writer import write_curated_note
from .store import EmbeddingIndex, Manifest
from .utils import iter_markdown_notes, parse_front_matter

def load_cfg(path='config.yaml'):
    """Load configuration, preferring config.py over YAML file."""
    try:
        # First try to use the unified config from config.py
        from config import get_curation_config
        return get_curation_config()
    except ImportError:
        # Fallback to YAML file if config.py not available
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

def run(cfg, vault=None, attachments=None, out_notes=None):
    vault = vault or cfg['paths']['vault']
    attachments = attachments or cfg['paths']['attachments']
    out_notes = out_notes or cfg['paths']['out_notes']

    os.makedirs(out_notes, exist_ok=True)
    EmbeddingIndex.init('.metadata/faiss.index', model=cfg['models']['embed'])
    Manifest.init('.metadata/manifest.jsonl')

    for note_path in iter_markdown_notes(vault):
        try:
            meta, body = parse_front_matter(note_path)
            assets = detect_assets(body, attachments)
            primary = choose_primary(assets, body, cfg['priorities'])
            content = extract_content(primary, assets, body, meta.get('language'))
            feats = analyze_features(content, meta, cfg)
            score = score_usefulness(feats, cfg)
            decision = decide(score, cfg['decision'])
            if decision == 'triage':
                logger.info(f'TRIAGE: {note_path} (score={score:.3f})'); continue
            if decision == 'discard':
                logger.info(f'DISCARD: {note_path} (score={score:.3f})'); continue
            cats, tags, ents = classify_json(content, meta, cfg)
            summary = summarize_content(content, meta, cats, cfg)
            write_curated_note(note_path, meta, cats, tags, ents, summary, content, score, cfg)
            EmbeddingIndex.add(note_path, content.get('embedding'))
            Manifest.update(note_path, score, decision, primary)
            logger.success(f'KEPT: {note_path} (score={score:.3f})')
        except Exception as e:
            logger.exception(f'Error processing {note_path}: {e}')

def cli():
    p = argparse.ArgumentParser()
    p.add_argument('--vault', default=None)
    p.add_argument('--attachments', default=None)
    p.add_argument('--out', dest='out_notes', default=None)
    p.add_argument('--config', default='config.yaml')
    args = p.parse_args()
    cfg = load_cfg(args.config)
    run(cfg, args.vault, args.attachments, args.out_notes)

if __name__ == '__main__':
    cli()
