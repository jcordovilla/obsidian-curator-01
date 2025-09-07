"""
Module for sampling notes from the Obsidian vault for analysis.
"""

import os
import random
import yaml
from pathlib import Path
from typing import List, Dict, Tuple
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import RAW_VAULT_PATH, SAMPLE_SIZE, OUTPUT_DIR


class NoteSampler:
    """Handles sampling of notes from the Obsidian vault."""
    
    def __init__(self, vault_path: str = RAW_VAULT_PATH):
        self.vault_path = Path(vault_path)
        self.all_notes = []
        self._discover_notes()
    
    def _discover_notes(self) -> None:
        """Discover all markdown files in the vault."""
        self.all_notes = list(self.vault_path.rglob("*.md"))
        print(f"Discovered {len(self.all_notes)} notes in vault")
    
    def get_stratified_sample(self, sample_size: int = SAMPLE_SIZE) -> List[Path]:
        """
        Get a stratified sample of notes from different folders to ensure diversity.
        """
        # Group notes by their parent folder
        folder_groups = {}
        for note in self.all_notes:
            folder = note.parent.name
            if folder not in folder_groups:
                folder_groups[folder] = []
            folder_groups[folder].append(note)
        
        print(f"Found notes in {len(folder_groups)} different folders")
        
        # Calculate samples per folder (proportional to folder size)
        total_notes = len(self.all_notes)
        samples = []
        
        for folder, notes in folder_groups.items():
            folder_proportion = len(notes) / total_notes
            folder_sample_size = max(1, int(sample_size * folder_proportion))
            folder_sample_size = min(folder_sample_size, len(notes))  # Don't exceed available notes
            
            folder_samples = random.sample(notes, folder_sample_size)
            samples.extend(folder_samples)
            print(f"  {folder}: {len(notes)} notes, sampling {len(folder_samples)}")
        
        # If we don't have enough samples yet, add more randomly
        if len(samples) < sample_size:
            remaining_notes = [n for n in self.all_notes if n not in samples]
            additional_needed = sample_size - len(samples)
            additional_samples = random.sample(remaining_notes, 
                                             min(additional_needed, len(remaining_notes)))
            samples.extend(additional_samples)
        
        # If we have too many, randomly reduce
        if len(samples) > sample_size:
            samples = random.sample(samples, sample_size)
        
        print(f"Final sample size: {len(samples)} notes")
        return samples
    
    def extract_note_info(self, note_path: Path) -> Dict:
        """Extract basic information from a note."""
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split frontmatter and content
            frontmatter = {}
            body = content
            
            if content.startswith('---\n'):
                parts = content.split('---\n', 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        body = parts[2]
                    except yaml.YAMLError:
                        pass  # Keep empty frontmatter if parsing fails
            
            return {
                'path': str(note_path),
                'filename': note_path.name,
                'folder': note_path.parent.name,
                'size_bytes': len(content),
                'line_count': len(content.split('\n')),
                'frontmatter': frontmatter,
                'body': body,
                'has_attachments': '![[attachments/' in content,
                'has_urls': 'http' in content.lower(),
                'has_source': 'source:' in str(frontmatter),
                'language': frontmatter.get('language', 'unknown'),
                'tags': frontmatter.get('tags', [])
            }
            
        except Exception as e:
            print(f"Error reading {note_path}: {e}")
            return {
                'path': str(note_path),
                'filename': note_path.name,
                'folder': note_path.parent.name,
                'error': str(e)
            }
    
    def create_sample_dataset(self, sample_size: int = SAMPLE_SIZE) -> List[Dict]:
        """Create a comprehensive sample dataset for analysis."""
        print(f"Creating sample dataset of {sample_size} notes...")
        
        # Get stratified sample
        sample_notes = self.get_stratified_sample(sample_size)
        
        # Extract information from each note
        dataset = []
        for i, note_path in enumerate(sample_notes, 1):
            print(f"Processing note {i}/{len(sample_notes)}: {note_path.name}")
            note_info = self.extract_note_info(note_path)
            dataset.append(note_info)
        
        return dataset
    
    def save_sample_dataset(self, dataset: List[Dict], filename: str = "sample_dataset.yaml") -> str:
        """Save the sample dataset to a file."""
        output_path = Path(OUTPUT_DIR) / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(dataset, f, default_flow_style=False, allow_unicode=True)
        
        print(f"Sample dataset saved to: {output_path}")
        return str(output_path)


if __name__ == "__main__":
    # Set random seed for reproducible sampling
    random.seed(42)
    
    sampler = NoteSampler()
    dataset = sampler.create_sample_dataset()
    sampler.save_sample_dataset(dataset)
    
    print(f"\nSample dataset created with {len(dataset)} notes")
    print("Next step: Run the content analyzer to characterize the notes")
