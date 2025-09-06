#!/usr/bin/env python3
"""
Compare original and curated notes to see the curation pipeline results.
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.curation.obsidian_curator.utils import parse_front_matter

def compare_notes():
    """Compare original and curated notes."""
    
    # Use absolute paths from tests folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    original_dir = os.path.join(base_dir, "test_data", "source")
    curated_dir = os.path.join(base_dir, "test_data", "curated")
    
    if not os.path.exists(original_dir) or not os.path.exists(curated_dir):
        print("❌ Test directories not found. Run test_curation_pipeline.py first.")
        return
    
    print("🔍 Comparing Original vs Curated Notes")
    print("=" * 60)
    
    original_files = {f.name: f for f in Path(original_dir).glob("*.md")}
    curated_files = {f.name: f for f in Path(curated_dir).glob("*.md")}
    
    for filename in sorted(original_files.keys()):
        if filename in curated_files:
            print(f"\n📄 {filename}")
            print("-" * 40)
            
            # Read both files
            original = original_files[filename].read_text(encoding='utf-8')
            curated = curated_files[filename].read_text(encoding='utf-8')
            
            # Extract metadata
            print("📊 ORIGINAL METADATA:")
            orig_lines = original.split('\n')
            for line in orig_lines[:15]:
                if line.startswith('---') or line.startswith('title:') or line.startswith('date') or line.startswith('tags:'):
                    print(f"   {line}")
            
            print("\n✨ CURATED METADATA:")
            cur_lines = curated.split('\n')
            for line in cur_lines[:15]:
                if line.startswith('---') or line.startswith('title:') or line.startswith('curated:') or line.startswith('categories:') or line.startswith('usefulness:'):
                    print(f"   {line}")
            
            # Show summary if present
            if "## Curator Summary" in curated:
                print("\n📝 CURATOR SUMMARY:")
                summary_start = curated.find("## Curator Summary")
                summary_end = curated.find("---", summary_start)
                if summary_end > summary_start:
                    summary = curated[summary_start:summary_end].strip()
                    print(f"   {summary}")
            
            # Show content length comparison
            orig_content = original.split('---', 2)[-1].strip() if '---' in original else original
            cur_content = curated.split('---', 2)[-1].strip() if '---' in curated else curated
            
            print(f"\n📏 CONTENT LENGTH:")
            print(f"   Original: {len(orig_content)} characters")
            print(f"   Curated:  {len(cur_content)} characters")
            print(f"   Difference: {len(cur_content) - len(orig_content):+d} characters")
            
            print("\n" + "="*60)
        else:
            print(f"⚠️  {filename} was not curated (likely discarded)")

if __name__ == "__main__":
    compare_notes()
