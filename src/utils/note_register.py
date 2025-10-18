#!/usr/bin/env python3
"""
Note Register System for tracking notes across all processing stages.

This module provides functionality to track notes through the pipeline:
- Raw notes (original source)
- Preprocessed notes (cleaned and standardized)
- Curated notes (AI-processed and enhanced)
- Triaged notes (flagged for manual review)

The register enables incremental processing by tracking which notes have
been processed at each stage.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple
import sqlite3

class NoteRegister:
    """Register for tracking notes across processing stages."""
    
    def __init__(self, register_path: str = ".metadata/note_register.db"):
        """Initialize the note register database."""
        self.register_path = register_path
        self.db_path = register_path if register_path.endswith('.db') else f"{register_path}.db"
        
        # Ensure metadata directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create main register table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS note_register (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_path TEXT UNIQUE NOT NULL,
                    note_hash TEXT NOT NULL,
                    note_name TEXT NOT NULL,
                    note_size INTEGER NOT NULL,
                    modified_time REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create processing stages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_stages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER NOT NULL,
                    stage TEXT NOT NULL,
                    status TEXT NOT NULL,
                    output_path TEXT,
                    processing_time REAL,
                    metadata TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (note_id) REFERENCES note_register (id),
                    UNIQUE(note_id, stage)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_note_path ON note_register (note_path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_note_hash ON note_register (note_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stage ON processing_stages (stage)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON processing_stages (status)')
            
            conn.commit()
    
    def _calculate_note_hash(self, note_path: str) -> str:
        """Calculate hash of note file for change detection."""
        try:
            with open(note_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def _get_file_stats(self, note_path: str) -> Tuple[int, float]:
        """Get file size and modification time."""
        try:
            stat = os.stat(note_path)
            return stat.st_size, stat.st_mtime
        except Exception:
            return 0, 0
    
    def register_note(self, note_path: str) -> int:
        """Register a note and return its ID."""
        note_hash = self._calculate_note_hash(note_path)
        note_name = os.path.basename(note_path)
        file_size, modified_time = self._get_file_stats(note_path)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Try to get existing note ID
            cursor.execute(
                'SELECT id FROM note_register WHERE note_path = ?',
                (note_path,)
            )
            result = cursor.fetchone()
            
            if result:
                note_id = result[0]
                # Update existing record
                cursor.execute('''
                    UPDATE note_register 
                    SET note_hash = ?, note_size = ?, modified_time = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (note_hash, file_size, modified_time, note_id))
            else:
                # Insert new record
                cursor.execute('''
                    INSERT INTO note_register (note_path, note_hash, note_name, note_size, modified_time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (note_path, note_hash, note_name, file_size, modified_time))
                note_id = cursor.lastrowid
            
            conn.commit()
            return note_id
    
    def record_stage(self, note_path: str, stage: str, status: str, 
                    output_path: str = None, processing_time: float = None, 
                    metadata: Dict = None) -> bool:
        """Record a processing stage for a note."""
        note_id = self.register_note(note_path)
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO processing_stages 
                (note_id, stage, status, output_path, processing_time, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (note_id, stage, status, output_path, processing_time, metadata_json))
            
            conn.commit()
            return True
    
    def get_note_status(self, note_path: str, stage: str = None) -> Dict:
        """Get processing status for a note."""
        note_id = self.register_note(note_path)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if stage:
                cursor.execute('''
                    SELECT stage, status, output_path, processing_time, metadata, processed_at
                    FROM processing_stages 
                    WHERE note_id = ? AND stage = ?
                ''', (note_id, stage))
            else:
                cursor.execute('''
                    SELECT stage, status, output_path, processing_time, metadata, processed_at
                    FROM processing_stages 
                    WHERE note_id = ?
                    ORDER BY processed_at
                ''', (note_id,))
            
            results = cursor.fetchall()
            
            if stage and results:
                stage_data = results[0]
                return {
                    'stage': stage_data[0],
                    'status': stage_data[1],
                    'output_path': stage_data[2],
                    'processing_time': stage_data[3],
                    'metadata': json.loads(stage_data[4]) if stage_data[4] else None,
                    'processed_at': stage_data[5]
                }
            elif not stage:
                return {
                    stage_data[0]: {
                        'status': stage_data[1],
                        'output_path': stage_data[2],
                        'processing_time': stage_data[3],
                        'metadata': json.loads(stage_data[4]) if stage_data[4] else None,
                        'processed_at': stage_data[5]
                    }
                    for stage_data in results
                }
            
            return {}
    
    def get_notes_needing_processing(self, stage: str, vault_path: str) -> List[str]:
        """Get list of notes that need processing at a specific stage."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all notes in vault
            vault_notes = []
            for root, dirs, files in os.walk(vault_path):
                for file in files:
                    if file.endswith('.md'):
                        vault_notes.append(os.path.join(root, file))
            
            # Get notes that haven't been processed at this stage or need reprocessing
            notes_needing_processing = []
            
            for note_path in vault_notes:
                note_id = self.register_note(note_path)
                
                cursor.execute('''
                    SELECT status, note_hash 
                    FROM processing_stages ps
                    JOIN note_register nr ON ps.note_id = nr.id
                    WHERE ps.note_id = ? AND ps.stage = ?
                ''', (note_id, stage))
                
                result = cursor.fetchone()
                
                if not result:
                    # Never processed at this stage
                    notes_needing_processing.append(note_path)
                elif result[0] == 'failed':
                    # Previously failed, needs reprocessing
                    notes_needing_processing.append(note_path)
                elif result[0] == 'completed':
                    # Check if file has changed
                    current_hash = self._calculate_note_hash(note_path)
                    if current_hash != result[1]:
                        # File changed, needs reprocessing
                        notes_needing_processing.append(note_path)
            
            return notes_needing_processing
    
    def get_processing_stats(self) -> Dict:
        """Get overall processing statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total notes registered
            cursor.execute('SELECT COUNT(*) FROM note_register')
            total_notes = cursor.fetchone()[0]
            
            # Notes by stage and status
            cursor.execute('''
                SELECT stage, status, COUNT(*) 
                FROM processing_stages 
                GROUP BY stage, status
            ''')
            stage_stats = cursor.fetchall()
            
            stats = {
                'total_notes': total_notes,
                'stages': {}
            }
            
            for stage, status, count in stage_stats:
                if stage not in stats['stages']:
                    stats['stages'][stage] = {}
                stats['stages'][stage][status] = count
            
            return stats
    
    def cleanup_orphaned_records(self, vault_path: str):
        """Remove records for notes that no longer exist in the vault."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all registered note paths
            cursor.execute('SELECT id, note_path FROM note_register')
            registered_notes = cursor.fetchall()
            
            orphaned_ids = []
            for note_id, note_path in registered_notes:
                if not os.path.exists(note_path):
                    orphaned_ids.append(note_id)
            
            # Remove orphaned records
            if orphaned_ids:
                placeholders = ','.join('?' * len(orphaned_ids))
                cursor.execute(f'DELETE FROM processing_stages WHERE note_id IN ({placeholders})', orphaned_ids)
                cursor.execute(f'DELETE FROM note_register WHERE id IN ({placeholders})', orphaned_ids)
                conn.commit()
                
                return len(orphaned_ids)
            
            return 0
    
    def export_register(self, output_path: str = None) -> str:
        """Export register data to JSON file."""
        if not output_path:
            output_path = f"note_register_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all notes with their processing stages
            cursor.execute('''
                SELECT nr.note_path, nr.note_name, nr.note_hash, nr.note_size, nr.modified_time,
                       ps.stage, ps.status, ps.output_path, ps.processing_time, ps.metadata, ps.processed_at
                FROM note_register nr
                LEFT JOIN processing_stages ps ON nr.id = ps.note_id
                ORDER BY nr.note_path, ps.processed_at
            ''')
            
            results = cursor.fetchall()
            
            # Organize data by note
            export_data = {}
            for row in results:
                note_path = row[0]
                if note_path not in export_data:
                    export_data[note_path] = {
                        'note_name': row[1],
                        'note_hash': row[2],
                        'note_size': row[3],
                        'modified_time': row[4],
                        'stages': {}
                    }
                
                if row[5]:  # stage
                    export_data[note_path]['stages'][row[5]] = {
                        'status': row[6],
                        'output_path': row[7],
                        'processing_time': row[8],
                        'metadata': json.loads(row[9]) if row[9] else None,
                        'processed_at': row[10]
                    }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return output_path


# Convenience functions for common operations
def get_register(register_path: str = ".metadata/note_register.db") -> NoteRegister:
    """Get or create a note register instance."""
    return NoteRegister(register_path)

def register_raw_note(note_path: str, register_path: str = ".metadata/note_register.db") -> int:
    """Register a raw note."""
    register = get_register(register_path)
    return register.register_note(note_path)

def record_preprocessing(note_path: str, status: str, output_path: str = None, 
                        processing_time: float = None, metadata: Dict = None,
                        register_path: str = ".metadata/note_register.db") -> bool:
    """Record preprocessing stage."""
    register = get_register(register_path)
    return register.record_stage(note_path, 'preprocessing', status, output_path, processing_time, metadata)

def record_curation(note_path: str, status: str, output_path: str = None, 
                   processing_time: float = None, metadata: Dict = None,
                   register_path: str = ".metadata/note_register.db") -> bool:
    """Record curation stage."""
    register = get_register(register_path)
    return register.record_stage(note_path, 'curation', status, output_path, processing_time, metadata)

def get_notes_needing_preprocessing(vault_path: str, register_path: str = ".metadata/note_register.db") -> List[str]:
    """Get notes that need preprocessing."""
    register = get_register(register_path)
    return register.get_notes_needing_processing('preprocessing', vault_path)

def get_notes_needing_curation(vault_path: str, register_path: str = ".metadata/note_register.db") -> List[str]:
    """Get notes that need curation."""
    register = get_register(register_path)
    return register.get_notes_needing_processing('curation', vault_path)
