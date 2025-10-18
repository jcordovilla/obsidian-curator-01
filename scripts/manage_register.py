#!/usr/bin/env python3
"""
Comprehensive note register management tool.
Handles register population, querying, and reporting.
"""

import os
import sys
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.note_register import get_register
from config import VAULT_PATH, PREPROCESSING_OUTPUT_PATH

def populate_register():
    """Populate the register with existing processed notes from the last run."""
    print("=== POPULATING NOTE REGISTER ===")
    
    # Initialize register
    register = get_register(".metadata/note_register.db")
    
    # Get paths
    raw_vault = Path(VAULT_PATH)
    preprocessed_vault = Path(PREPROCESSING_OUTPUT_PATH)
    
    print(f"Raw vault: {raw_vault}")
    print(f"Preprocessed vault: {preprocessed_vault}")
    
    if not raw_vault.exists():
        print(f"Error: Raw vault path does not exist: {raw_vault}")
        return False
    
    if not preprocessed_vault.exists():
        print(f"Error: Preprocessed vault path does not exist: {preprocessed_vault}")
        return False
    
    # Find all raw notes
    raw_notes = list(raw_vault.rglob("*.md"))
    print(f"Found {len(raw_notes)} raw notes")
    
    # Find all preprocessed notes
    preprocessed_notes = list(preprocessed_vault.rglob("*.md"))
    print(f"Found {len(preprocessed_notes)} preprocessed notes")
    
    # Create mapping of note names to paths
    preprocessed_map = {}
    for note in preprocessed_notes:
        note_name = note.name
        preprocessed_map[note_name] = note
    
    # Find all curated notes
    curated_path = Path("/Users/jose/Documents/Obsidian/Ever-curated/notes")
    curated_notes = []
    if curated_path.exists():
        curated_notes = list(curated_path.rglob("*.md"))
        print(f"Found {len(curated_notes)} curated notes")
    
    curated_map = {}
    for note in curated_notes:
        note_name = note.name
        curated_map[note_name] = note
    
    # Find all triaged notes
    triage_path = Path("/Users/jose/Documents/Obsidian/Ever-curated/triage")
    triaged_notes = []
    if triage_path.exists():
        triaged_notes = list(triage_path.rglob("*.md"))
        print(f"Found {len(triaged_notes)} triaged notes")
    
    triaged_map = {}
    for note in triaged_notes:
        note_name = note.name
        triaged_map[note_name] = note
    
    # Process each raw note
    processed_count = 0
    preprocessed_count = 0
    curated_count = 0
    triaged_count = 0
    
    for raw_note in raw_notes:
        note_name = raw_note.name
        raw_path = str(raw_note)
        
        # Determine processing status
        status = "raw"
        output_path = None
        stage = "raw"
        
        if note_name in preprocessed_map:
            preprocessed_path = str(preprocessed_map[note_name])
            status = "completed"
            output_path = preprocessed_path
            stage = "preprocessed"
            preprocessed_count += 1
            
            # Check if also curated
            if note_name in curated_map:
                curated_path = str(curated_map[note_name])
                status = "completed"
                output_path = curated_path
                stage = "curated"
                curated_count += 1
            
            # Check if also triaged
            elif note_name in triaged_map:
                triaged_path = str(triaged_map[note_name])
                status = "completed"
                output_path = triaged_path
                stage = "triaged"
                triaged_count += 1
        
        # Record in register
        try:
            register.record_stage(
                note_path=raw_path,
                stage=stage,
                status=status,
                output_path=output_path
            )
            processed_count += 1
            
            if processed_count % 100 == 0:
                print(f"Processed {processed_count} notes...")
                
        except Exception as e:
            print(f"Error recording {raw_path}: {e}")
    
    print(f"\n=== REGISTER POPULATION COMPLETE ===")
    print(f"Total notes processed: {processed_count}")
    print(f"Preprocessed notes: {preprocessed_count}")
    print(f"Curated notes: {curated_count}")
    print(f"Triaged notes: {triaged_count}")
    
    return True

def generate_full_register():
    """Generate a comprehensive register showing all notes and their processing status."""
    print("=== GENERATING FULL NOTE REGISTER ===")
    
    # Initialize register
    register = get_register(".metadata/note_register.db")
    
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Create detailed register file
    register_path = reports_dir / "note_register.md"
    
    with open(register_path, 'w', encoding='utf-8') as f:
        f.write("# Full Note Register\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("This register shows the complete processing status of all notes.\n\n")
        
        # Get all notes from database
        with sqlite3.connect(".metadata/note_register.db") as conn:
            cursor = conn.cursor()
            
            # Get all notes with their processing stages
            cursor.execute("""
                SELECT 
                    n.note_path,
                    n.note_name,
                    n.note_hash,
                    n.note_size,
                    n.modified_time,
                    GROUP_CONCAT(
                        CASE 
                            WHEN s.stage = 'preprocessed' THEN '✓ Preprocessed'
                            WHEN s.stage = 'curated' THEN '✓ Curated' 
                            WHEN s.stage = 'triaged' THEN '✓ Triaged'
                            WHEN s.stage = 'discarded' THEN '✗ Discarded'
                            ELSE s.stage
                        END, ' | '
                    ) as stages,
                    GROUP_CONCAT(s.output_path, ' | ') as output_paths,
                    GROUP_CONCAT(s.status, ' | ') as statuses,
                    GROUP_CONCAT(s.processed_at, ' | ') as processed_dates
                FROM note_register n
                LEFT JOIN processing_stages s ON n.id = s.note_id
                GROUP BY n.id, n.note_path, n.note_name, n.note_hash, n.note_size, n.modified_time
                ORDER BY n.note_path
            """)
            
            rows = cursor.fetchall()
            
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Notes**: {len(rows)}\n\n")
            
            # Count by stage
            stage_counts = {}
            for row in rows:
                stages = row[5] if row[5] else "Raw only"
                if 'Preprocessed' in stages:
                    stage_counts['Preprocessed'] = stage_counts.get('Preprocessed', 0) + 1
                if 'Curated' in stages:
                    stage_counts['Curated'] = stage_counts.get('Curated', 0) + 1
                if 'Triaged' in stages:
                    stage_counts['Triaged'] = stage_counts.get('Triaged', 0) + 1
                if 'Discarded' in stages:
                    stage_counts['Discarded'] = stage_counts.get('Discarded', 0) + 1
            
            for stage, count in sorted(stage_counts.items()):
                f.write(f"- **{stage}**: {count}\n")
            
            f.write(f"\n## Detailed Register\n\n")
            f.write("| Note Name | Status | Output Path | Processed Date | Size | Hash |\n")
            f.write("|-----------|--------|-------------|----------------|------|------|\n")
            
            for row in rows:
                note_path = row[0]
                note_name = row[1]
                note_hash = row[2]
                note_size = row[3]
                modified_time = row[4]
                stages = row[5] if row[5] else "Raw only"
                output_paths = row[6] if row[6] else ""
                processed_dates = row[7] if row[7] else ""
                
                # Format file size
                if note_size:
                    if note_size < 1024:
                        size_str = f"{note_size} B"
                    elif note_size < 1024*1024:
                        size_str = f"{note_size/1024:.1f} KB"
                    else:
                        size_str = f"{note_size/(1024*1024):.1f} MB"
                else:
                    size_str = "Unknown"
                
                # Truncate long paths
                display_name = note_name if len(note_name) <= 50 else note_name[:47] + "..."
                display_output = output_paths.split(' | ')[0] if output_paths else ""
                if len(display_output) > 50:
                    display_output = display_output[:47] + "..."
                
                f.write(f"| {display_name} | {stages} | {display_output} | {processed_dates.split(' | ')[0] if processed_dates else ''} | {size_str} | {note_hash[:8] if note_hash else ''} |\n")
    
    print(f"Full register generated: {register_path}")
    
    # Also create a CSV version for easier analysis
    csv_path = reports_dir / "note_register.csv"
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("note_path,note_name,note_hash,note_size,modified_time,stages,output_paths,statuses,processed_dates\n")
        
        with sqlite3.connect(".metadata/note_register.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    n.note_path,
                    n.note_name,
                    n.note_hash,
                    n.note_size,
                    n.modified_time,
                    GROUP_CONCAT(s.stage, ' | ') as stages,
                    GROUP_CONCAT(s.output_path, ' | ') as output_paths,
                    GROUP_CONCAT(s.status, ' | ') as statuses,
                    GROUP_CONCAT(s.processed_at, ' | ') as processed_dates
                FROM note_register n
                LEFT JOIN processing_stages s ON n.id = s.note_id
                GROUP BY n.id, n.note_path, n.note_name, n.note_hash, n.note_size, n.modified_time
                ORDER BY n.note_path
            """)
            
            rows = cursor.fetchall()
            for row in rows:
                # Escape CSV values
                escaped_row = []
                for value in row:
                    if value is None:
                        escaped_row.append("")
                    else:
                        # Escape quotes and wrap in quotes if contains comma
                        value_str = str(value).replace('"', '""')
                        if ',' in value_str or '"' in value_str or '\n' in value_str:
                            escaped_row.append(f'"{value_str}"')
                        else:
                            escaped_row.append(value_str)
                
                f.write(",".join(escaped_row) + "\n")
    
    print(f"CSV register generated: {csv_path}")
    
    return register_path, csv_path

def query_notes(stage=None, search_term=None, limit=50):
    """Query notes from the register."""
    with sqlite3.connect(".metadata/note_register.db") as conn:
        cursor = conn.cursor()
        
        if stage:
            cursor.execute("""
                SELECT n.note_name, s.output_path, s.processed_at
                FROM note_register n
                JOIN processing_stages s ON n.id = s.note_id
                WHERE s.stage = ?
                ORDER BY n.note_name
                LIMIT ?
            """, (stage, limit))
        elif search_term:
            cursor.execute("""
                SELECT n.note_name, GROUP_CONCAT(s.stage, ' | ') as stages
                FROM note_register n
                LEFT JOIN processing_stages s ON n.id = s.note_id
                WHERE n.note_name LIKE ?
                GROUP BY n.id
                ORDER BY n.note_name
                LIMIT ?
            """, (f'%{search_term}%', limit))
        else:
            cursor.execute("""
                SELECT n.note_name, GROUP_CONCAT(s.stage, ' | ') as stages
                FROM note_register n
                LEFT JOIN processing_stages s ON n.id = s.note_id
                GROUP BY n.id
                ORDER BY n.note_name
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        return rows

def get_summary():
    """Get processing summary."""
    with sqlite3.connect(".metadata/note_register.db") as conn:
        cursor = conn.cursor()
        
        # Total notes
        cursor.execute("SELECT COUNT(*) FROM note_register")
        total_notes = cursor.fetchone()[0]
        
        # Notes by stage
        cursor.execute("""
            SELECT stage, COUNT(*) as count
            FROM processing_stages
            GROUP BY stage
            ORDER BY count DESC
        """)
        
        stages = cursor.fetchall()
        return total_notes, stages

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_register.py populate                    # Populate register with existing notes")
        print("  python manage_register.py generate                   # Generate full register report")
        print("  python manage_register.py summary                    # Show summary statistics")
        print("  python manage_register.py curated [limit]            # Show curated notes")
        print("  python manage_register.py triaged [limit]            # Show triaged notes")
        print("  python manage_register.py preprocessed [limit]       # Show preprocessed notes")
        print("  python manage_register.py search <term> [limit]      # Search notes by name")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "populate":
        success = populate_register()
        if success:
            print("✅ Register populated successfully!")
        else:
            print("❌ Failed to populate register")
            sys.exit(1)
    
    elif command == "generate":
        register_path, csv_path = generate_full_register()
        print(f"✅ Full register generated:")
        print(f"   📊 Markdown: {register_path}")
        print(f"   📊 CSV: {csv_path}")
    
    elif command == "summary":
        total_notes, stages = get_summary()
        print(f"=== PROCESSING SUMMARY ===")
        print(f"Total notes in register: {total_notes}")
        print("\nNotes by processing stage:")
        for stage, count in stages:
            percentage = (count / total_notes) * 100
            print(f"  {stage.title()}: {count} ({percentage:.1f}%)")
    
    elif command in ["curated", "triaged", "preprocessed"]:
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        rows = query_notes(stage=command, limit=limit)
        
        print(f"=== {command.upper()} NOTES (showing {len(rows)} of {limit}) ===")
        for i, row in enumerate(rows, 1):
            print(f"{i:4d}. {row[0]}")
            if len(row) > 1:
                print(f"      Output: {row[1]}")
                if len(row) > 2:
                    print(f"      Processed: {row[2]}")
            print()
    
    elif command == "search" and len(sys.argv) > 2:
        search_term = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        rows = query_notes(search_term=search_term, limit=limit)
        
        print(f"=== SEARCH RESULTS FOR '{search_term}' (showing {len(rows)}) ===")
        for i, row in enumerate(rows, 1):
            stages = row[1] if row[1] else "Raw only"
            print(f"{i:4d}. {row[0]}")
            print(f"      Stages: {stages}")
            print()
    
    else:
        print("Invalid command. Use 'populate', 'generate', 'summary', 'curated', 'triaged', 'preprocessed', or 'search <term>'")
        sys.exit(1)

if __name__ == "__main__":
    main()
