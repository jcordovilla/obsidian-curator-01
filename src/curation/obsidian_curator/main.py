from loguru import logger
import argparse, os, yaml, datetime, json
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

def enqueue_triage(note_path, feats, score):
    os.makedirs(".metadata", exist_ok=True)
    with open(".metadata/triage.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"note":note_path,"score":score,"reason":"gray-zone"})+"\n")

def run(cfg, vault=None, attachments=None, out_notes=None, dry_run=False):
    # Set up logging with run ID
    os.makedirs("logs", exist_ok=True)
    run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    logger.add(f"logs/curation-{run_id}.log", level="INFO", encoding="utf-8", enqueue=True)
    
    vault = vault or cfg['paths']['vault']
    attachments = attachments or cfg['paths']['attachments']
    out_notes = out_notes or cfg['paths']['out_notes']

    if not dry_run:
        os.makedirs(out_notes, exist_ok=True)
        EmbeddingIndex.init('.metadata/faiss.index', model=cfg['models']['embed'])
        Manifest.init('.metadata/manifest.jsonl')

    for note_path in iter_markdown_notes(vault):
        try:
            meta, body = parse_front_matter(note_path)
            assets = detect_assets(body, attachments)
            primary = choose_primary(assets, body, cfg['priorities'])
            content = extract_content(primary, assets, body, meta.get('language'), attachments, note_path)
            
            # CRITICAL: Validate content before any scoring
            text = content.get('text', '').strip()
            if not text or len(text) < 50:
                logger.info(f'DISCARD: {note_path} (insufficient content: {len(text)} chars)')
                continue
            
            # Early classification to get relevance score for better filtering
            cats, tags, ents = classify_json(content, meta, cfg)
            
            # Use LLM-powered analysis for professional relevance
            feats = analyze_features(content, meta, cfg)
            score = score_usefulness(feats, cfg)
            decision = decide(score, cfg['decision'])
            
            # Log LLM reasoning for transparency
            llm_reasoning = feats.get('llm_reasoning', 'No reasoning available')
            logger.debug(f'LLM Assessment for {note_path}: {llm_reasoning}')
            
            if decision == 'triage':
                if not dry_run:
                    enqueue_triage(note_path, feats, score)
                    # Copy triaged notes to triage folder for manual review
                    import shutil
                    triage_dir = cfg['paths']['out_notes'].replace('/notes', '/triage')
                    os.makedirs(triage_dir, exist_ok=True)
                    triage_path = os.path.join(triage_dir, os.path.basename(note_path))
                    shutil.copy2(note_path, triage_path)
                logger.info(f'TRIAGE: {note_path} (score={score:.3f})'); continue
            if decision == 'discard':
                logger.info(f'DISCARD: {note_path} (score={score:.3f})'); continue
                
            # Generate summary for kept notes
            summary = summarize_content(content, meta, cats, cfg)
            
            if not dry_run:
                write_curated_note(note_path, meta, cats, tags, ents, summary, content, score, cfg)
                EmbeddingIndex.add(note_path, content.get('embedding'))
                Manifest.update(note_path, score, decision, primary)
            logger.success(f'KEPT{ " (dry-run)" if dry_run else "" }: {note_path} (score={score:.3f})')
        except Exception as e:
            logger.exception(f'Error processing {note_path}: {e}')

def cli():
    p = argparse.ArgumentParser()
    p.add_argument('--vault', default=None)
    p.add_argument('--attachments', default=None)
    p.add_argument('--out', dest='out_notes', default=None)
    p.add_argument('--config', default='config.yaml')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    cfg = load_cfg(args.config)
    run(cfg, args.vault, args.attachments, args.out_notes, dry_run=args.dry_run)

if __name__ == '__main__':
    cli()
