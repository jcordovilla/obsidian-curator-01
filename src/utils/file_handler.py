"""
File handling utilities for safe note processing.
"""

import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime


class FileHandler:
    """Handles safe file operations with backup and validation."""
    
    def __init__(self, backup_dir: str = "backup"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def read_note(self, file_path: Path) -> Tuple[Dict, str]:
        """
        Read a note file and separate frontmatter from content.
        
        Returns:
            Tuple of (frontmatter_dict, content_string)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            frontmatter = {}
            body = content
            
            if content.startswith('---\n'):
                parts = content.split('---\n', 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        body = parts[2]
                    except yaml.YAMLError as e:
                        print(f"Warning: YAML parsing error in {file_path}: {e}")
                        # Keep empty frontmatter if parsing fails
            
            return frontmatter, body
            
        except Exception as e:
            raise IOError(f"Failed to read {file_path}: {e}")
    
    def write_note(self, file_path: Path, frontmatter: Dict, content: str, backup: bool = True) -> bool:
        """
        Write a note file with frontmatter and content.
        
        Args:
            file_path: Path to write the file
            frontmatter: Metadata dictionary
            content: Note content
            backup: Whether to create backup of original
            
        Returns:
            True if successful
        """
        try:
            # Create backup if requested and file exists
            if backup and file_path.exists():
                self.create_backup(file_path)
            
            # Prepare content
            if frontmatter:
                yaml_content = yaml.dump(frontmatter, default_flow_style=False, 
                                       allow_unicode=True, sort_keys=False)
                full_content = f"---\n{yaml_content}---\n\n{content}"
            else:
                full_content = content
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            return True
            
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
    
    def create_backup(self, file_path: Path) -> Path:
        """Create a timestamped backup of the file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def validate_file(self, file_path: Path) -> Dict:
        """Validate a note file and return status."""
        validation = {
            'exists': file_path.exists(),
            'readable': False,
            'valid_yaml': False,
            'has_content': False,
            'encoding_ok': True,
            'errors': []
        }
        
        if not validation['exists']:
            validation['errors'].append('File does not exist')
            return validation
        
        try:
            frontmatter, content = self.read_note(file_path)
            validation['readable'] = True
            validation['valid_yaml'] = True
            validation['has_content'] = bool(content.strip())
            
        except UnicodeDecodeError:
            validation['encoding_ok'] = False
            validation['errors'].append('Encoding error')
        except yaml.YAMLError:
            validation['valid_yaml'] = False
            validation['errors'].append('Invalid YAML frontmatter')
        except Exception as e:
            validation['errors'].append(str(e))
        
        return validation
