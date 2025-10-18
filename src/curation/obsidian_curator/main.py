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
from .writer import write_curated_note, write_triage_note
from .store import EmbeddingIndex, Manifest
from .utils import iter_markdown_notes, parse_front_matter
from .llm import get_token_usage, reset_token_usage
from ...utils.note_register import get_register

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

def run(cfg, vault=None, attachments=None, out_notes=None, dry_run=False, register_path=".metadata/note_register.db", incremental=True):
    # Set up logging with run ID
    os.makedirs("logs", exist_ok=True)
    run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    logger.add(f"logs/curation-{run_id}.log", level="INFO", encoding="utf-8", enqueue=True)
    
    vault = vault or cfg['paths']['vault']
    attachments = attachments or cfg['paths']['attachments']
    out_notes = out_notes or cfg['paths']['out_notes']
    
    # Initialize note register
    register = get_register(register_path)

    if not dry_run:
        os.makedirs(out_notes, exist_ok=True)
        embed_dims = cfg['models'].get('embed_dims', 1536)  # Default to OpenAI dims
        EmbeddingIndex.init('.metadata/faiss.index', model=cfg['models']['embed'], embed_dims=embed_dims)
        Manifest.init('.metadata/manifest.jsonl')

    # Get notes to process (incremental or full)
    if incremental:
        notes_to_process = register.get_notes_for_curation(Path(vault))
        logger.info(f"Found {len(notes_to_process)} notes needing curation (incremental mode - default)")
    else:
        notes_to_process = list(iter_markdown_notes(vault))
        logger.info(f"Found {len(notes_to_process)} notes to process (full mode - override)")
    
    total_notes = len(notes_to_process)
    processed_count = 0
    kept_count = 0
    triage_count = 0
    discard_count = 0
    
    for note_path in notes_to_process:
        try:
            meta, body = parse_front_matter(note_path)
            assets = detect_assets(body, attachments)
            primary = choose_primary(assets, body, cfg['priorities'])
            
            # Skip audio files for now (placeholder transcription not useful)
            if primary['kind'] == 'audio':
                logger.info(f'SKIP: Audio file not yet supported: {note_path}')
                continue
            
            content = extract_content(primary, assets, body, meta.get('language'), attachments, note_path)
            
            # Let the LLM decide on content quality - no early filtering
            text = content.get('text', '').strip()
            
            # Early classification for categories/tags/entities
            cats, tags, ents, pub_readiness = classify_json(content, meta, cfg)
            
            # Single-pass LLM usefulness assessment
            feats = analyze_features(content, meta, cfg)
            score = score_usefulness(feats, cfg)
            decision = decide(score, cfg['decision'])
            
            # Log LLM reasoning for transparency
            reasoning = feats.get('reasoning', 'No reasoning available')
            logger.debug(f'Usefulness Assessment for {note_path}: {reasoning}')
            
            if decision == 'triage':
                if not dry_run:
                    enqueue_triage(note_path, feats, score)
                    # Copy triaged notes to triage folder with rich metadata for manual review
                    import shutil
                    triage_dir = cfg['paths']['out_notes'].replace('/notes', '/triage')
                    os.makedirs(triage_dir, exist_ok=True)
                    triage_path = os.path.join(triage_dir, os.path.basename(note_path))
                    
                    # Create enhanced triage note with rich metadata
                    write_triage_note(note_path, meta, cats, tags, ents, content, score, cfg, attachments)
                    
                    # Record triage in register
                    register.record_note_status(str(note_path), 'triaged', triage_path=str(triage_path))
                logger.info(f'TRIAGE: {note_path} (score={score:.3f})')
                triage_count += 1
                processed_count += 1
                print(f"Progress: {processed_count}/{total_notes} | Kept: {kept_count}, Triage: {triage_count}, Discard: {discard_count}")
                continue
                
            if decision == 'discard':
                if not dry_run:
                    # Record discard in register
                    register.record_note_status(str(note_path), 'discarded')
                logger.info(f'DISCARD: {note_path} (score={score:.3f})')
                discard_count += 1
                processed_count += 1
                print(f"Progress: {processed_count}/{total_notes} | Kept: {kept_count}, Triage: {triage_count}, Discard: {discard_count}")
                continue
                
            # Generate summary for kept notes
            summary = summarize_content(content, meta, cats, cfg)
            if not summary or len(summary.strip()) < 10:
                logger.warning(f'Empty or minimal summary generated for {note_path}: {len(summary)} chars')
            
            if not dry_run:
                curated_path = write_curated_note(note_path, meta, cats, tags, ents, summary, content, score, cfg, attachments)
                # Use the embedding from features analysis (not content dict)
                EmbeddingIndex.add(note_path, feats.get('embedding'))
                # Enhanced manifest with instrumentation
                Manifest.update(note_path, score, decision, primary, features=feats, categories=cats)
                
                # Record curation in register
                register.record_note_status(str(note_path), 'curated', curated_path=str(curated_path))
            logger.success(f'KEPT{ " (dry-run)" if dry_run else "" }: {note_path} (score={score:.3f})')
            kept_count += 1
            processed_count += 1
            print(f"Progress: {processed_count}/{total_notes} | Kept: {kept_count}, Triage: {triage_count}, Discard: {discard_count}")
        except Exception as e:
            logger.exception(f'Error processing {note_path}: {e}')
    
    # Report token usage at the end
    usage = get_token_usage()
    if usage['total_tokens'] > 0:
        logger.info(f"📊 TOKEN USAGE SUMMARY:")
        logger.info(f"  Total tokens: {usage['total_tokens']:,}")
        logger.info(f"  Prompt tokens: {usage['total_prompt_tokens']:,}")
        logger.info(f"  Completion tokens: {usage['total_completion_tokens']:,}")
        
        # Cost estimation (approximate OpenAI pricing)
        # gpt-4o-mini: $0.150/1M input, $0.600/1M output
        # gpt-5: $2.50/1M input, $10.00/1M output
        for model, stats in usage['calls_by_model'].items():
            if 'gpt-5' in model or 'o3' in model or 'o4' in model:
                input_cost = stats['prompt_tokens'] * 2.50 / 1_000_000
                output_cost = stats['completion_tokens'] * 10.00 / 1_000_000
            elif 'gpt-4o-mini' in model:
                input_cost = stats['prompt_tokens'] * 0.150 / 1_000_000
                output_cost = stats['completion_tokens'] * 0.600 / 1_000_000
            else:
                input_cost = stats['prompt_tokens'] * 0.30 / 1_000_000  # Generic estimate
                output_cost = stats['completion_tokens'] * 1.20 / 1_000_000
            
            total_cost = input_cost + output_cost
            logger.info(f"  {model}: {stats['calls']} calls, {stats['total_tokens']:,} tokens, ~${total_cost:.3f}")

def cli():
    p = argparse.ArgumentParser()
    p.add_argument('--vault', default=None)
    p.add_argument('--attachments', default=None)
    p.add_argument('--out', dest='out_notes', default=None)
    p.add_argument('--config', default='config.yaml')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--full', action='store_true', help='Process all notes (full mode) - normally only new/changed notes are processed')
    p.add_argument('--register-path', default='.metadata/note_register.db', help='Path to note register database')
    args = p.parse_args()
    cfg = load_cfg(args.config)
    run(cfg, args.vault, args.attachments, args.out_notes, dry_run=args.dry_run, register_path=args.register_path, incremental=not args.full)

if __name__ == '__main__':
    cli()
