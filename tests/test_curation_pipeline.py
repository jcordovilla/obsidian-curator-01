#!/usr/bin/env python3
"""
Real curation pipeline test - runs the actual system on a small sample.
This bypasses test mode to show the real behavior.
"""

import os
import sys
from pathlib import Path

# Add project root to path (parent of tests folder)
sys.path.append(str(Path(__file__).parent.parent))

def get_sample_notes_from_vault():
    """Get a small sample of real notes from the actual vault."""
    vault_path = "/Users/jose/Documents/Obsidian/Evermd"
    sample_notes = []
    
    # Find some real markdown files from the vault
    import glob
    import random
    md_files = glob.glob(f"{vault_path}/**/*.md", recursive=True)
    
    # Filter files by size first
    suitable_files = []
    for file_path in md_files:
        try:
            if os.path.getsize(file_path) < 50000:  # Less than 50KB
                suitable_files.append(file_path)
        except:
            continue
    
    # Randomly sample 20 files from all suitable files
    if len(suitable_files) >= 20:
        selected_files = random.sample(suitable_files, 20)
    else:
        selected_files = suitable_files
    
    return selected_files[:20]  # Return max 20 files

def run_real_curation_test():
    """Run the real curation pipeline on a small test sample."""
    
    print("🚀 Real Curation Pipeline Test")
    print("=" * 50)
    print("⚠️  This will make real LLM calls and process actual content")
    print("📁 Using small test sample for safety")
    print()
    
    # Create a smaller test sample (3-4 notes) for real testing
    test_sample_dir = "/Users/jose/Documents/apps/obsidian-curator-01/test_data/source"
    test_output_dir = "/Users/jose/Documents/apps/obsidian-curator-01/test_data/curated"
    
    # Create both test directories
    os.makedirs(test_sample_dir, exist_ok=True)
    os.makedirs(test_output_dir, exist_ok=True)
    
    # Always recreate test sample for fresh testing
    print("📋 Creating fresh test sample from real vault...")
    
    # Remove existing test data
    if os.path.exists(test_sample_dir):
        import shutil
        shutil.rmtree(test_sample_dir)
    if os.path.exists(test_output_dir):
        import shutil
        shutil.rmtree(test_output_dir)
    
    # Recreate clean directories
    os.makedirs(test_sample_dir, exist_ok=True)
    os.makedirs(test_output_dir, exist_ok=True)
    
    # Get real notes from the actual vault
    real_notes = get_sample_notes_from_vault()
    
    if not real_notes:
        print("❌ No suitable notes found in vault for testing")
        return False
    
    # Copy real notes to test directory
    import shutil
    import re
    
    # Create attachments directory
    test_attachments = f"{test_sample_dir}/attachments"
    os.makedirs(test_attachments, exist_ok=True)
    
    # Track which attachments we need to copy
    needed_attachments = set()
    
    for i, real_note_path in enumerate(real_notes, 1):
        filename = f"real_note_{i}_{Path(real_note_path).name}"
        dest_path = f"{test_sample_dir}/{filename}"
        shutil.copy2(real_note_path, dest_path)
        print(f"   ✓ Copied: {filename}")
        
        # Extract attachment references from the note
        with open(real_note_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find all ![[attachments/...]] references
            attachment_refs = re.findall(r'!\[\[attachments/([^\]]+)\]\]', content)
            for ref in attachment_refs:
                needed_attachments.add(ref)
    
    # Copy only the needed attachments
    vault_attachments = "/Users/jose/Documents/Obsidian/Evermd/attachments"
    if os.path.exists(vault_attachments) and needed_attachments:
        print(f"   📎 Copying {len(needed_attachments)} specific attachments...")
        for attachment in needed_attachments:
            src_path = os.path.join(vault_attachments, attachment)
            if os.path.exists(src_path):
                # Create subdirectories if needed
                dest_path = os.path.join(test_attachments, attachment)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(src_path, dest_path)
                print(f"     ✓ {attachment}")
            else:
                print(f"     ⚠️  Missing: {attachment}")
    else:
        print(f"   📎 No attachments needed")
    
    print(f"\n📁 Test sample: {test_sample_dir}")
    print(f"📁 Output: {test_output_dir}")
    print()
    
    # Check if Ollama is running
    print("🔍 Checking Ollama availability...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"   ✅ Ollama is running with {len(models)} models")
            if models:
                print(f"   📋 Available models: {[m['name'] for m in models[:3]]}...")
        else:
            print("   ❌ Ollama not responding properly")
            return False
    except Exception as e:
        print(f"   ❌ Ollama not available: {e}")
        print("   💡 Please start Ollama with: ollama serve")
        return False
    
    print()
    
    # Run the real curation pipeline
    try:
        from src.curation.obsidian_curator.main import run
        from config import get_curation_config
        
        # Get configuration
        cfg = get_curation_config()
        
        # Update paths for test
        cfg["paths"]["vault"] = test_sample_dir
        cfg["paths"]["out_notes"] = test_output_dir
        cfg["paths"]["attachments"] = f"{test_sample_dir}/attachments"
        
        # Use production thresholds
        cfg["decision"]["keep_threshold"] = 0.68
        cfg["decision"]["gray_margin"] = 0.05
        
        print("🔄 Running real curation pipeline...")
        print("   (This may take a few minutes for LLM processing)")
        print()
        
        # Run the pipeline
        run(cfg, 
            vault=cfg["paths"]["vault"],
            attachments=cfg["paths"]["attachments"], 
            out_notes=cfg["paths"]["out_notes"])
        
        print("\n✅ Real curation pipeline completed!")
        
        # Show results
        if os.path.exists(test_output_dir):
            output_files = list(Path(test_output_dir).glob("*.md"))
            print(f"\n📊 Generated {len(output_files)} curated notes:")
            
            for file in sorted(output_files):
                print(f"\n📄 {file.name}:")
                content = file.read_text(encoding='utf-8')
                
                # Extract key metadata
                lines = content.split('\n')
                for line in lines[:10]:  # First 10 lines
                    if line.startswith('title:') or line.startswith('categories:') or line.startswith('usefulness:'):
                        print(f"   {line}")
                
                # Show summary preview
                if "## Curator Summary" in content:
                    summary_start = content.find("## Curator Summary")
                    summary_end = content.find("---", summary_start)
                    if summary_end > summary_start:
                        summary = content[summary_start:summary_end].strip()
                        print(f"   Summary: {summary[:100]}...")
        
        # Check triage
        triage_file = Path(".metadata/triage.jsonl")
        if triage_file.exists():
            with open(triage_file, 'r') as f:
                triage_lines = f.readlines()
            if triage_lines:
                print(f"\n📋 Triage queue: {len(triage_lines)} items")
                for line in triage_lines[-2:]:  # Show last 2 items
                    import json
                    item = json.loads(line.strip())
                    print(f"   - {Path(item['note']).name}: {item['score']:.3f}")
        
        # Show latest log
        logs_dir = Path("logs")
        if logs_dir.exists():
            log_files = list(logs_dir.glob("curation-*.log"))
            if log_files:
                latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                print(f"\n📝 Latest log: {latest_log}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error running real curation pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_real_curation_test()
    if success:
        print("\n🎉 Real curation test completed successfully!")
        print("💡 Run: python tests/compare_results.py to compare original vs curated notes")
    else:
        print("\n❌ Real curation test failed!")
        sys.exit(1)
