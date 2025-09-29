"""
Main batch processing pipeline for Obsidian note preprocessing.
"""

import os
import re
import json
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..utils.file_handler import FileHandler
from .metadata_standardizer import MetadataStandardizer
from .web_clipping_cleaner import WebClippingCleaner
from .content_classifier import ContentClassifier
from .quality_validator import QualityValidator


class BatchProcessor:
    """Main batch processing pipeline for note preprocessing."""
    
    def __init__(self, 
                 vault_path: str,
                 output_path: str = None,
                 backup: bool = True,
                 batch_size: int = 50,
                 max_workers: int = 4):
        
        self.vault_path = Path(vault_path)
        self.output_path = Path(output_path) if output_path else self.vault_path / "processed"
        self.backup = backup
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        # Initialize components
        self.file_handler = FileHandler(backup_dir=self.output_path / "backup")
        self.metadata_standardizer = MetadataStandardizer()
        self.web_cleaner = WebClippingCleaner()
        self.classifier = ContentClassifier()
        self.validator = QualityValidator()
        
        # Processing statistics
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'processing_time': 0.0,
            'category_counts': {},
            'quality_distribution': {},
            'errors': []
        }
        
        # Create output directories
        self.output_path.mkdir(exist_ok=True)
        (self.output_path / "logs").mkdir(exist_ok=True)
        (self.output_path / "reports").mkdir(exist_ok=True)
        
        # Attachment handling
        self.vault_attachments_path = self.vault_path / "attachments"
        self.output_attachments_path = self.output_path / "attachments"
    
    def process_vault(self, 
                     file_pattern: str = "*.md",
                     dry_run: bool = False,
                     categories_to_process: Optional[List[str]] = None) -> Dict:
        """
        Process the entire vault or a subset of files.
        
        Args:
            file_pattern: Glob pattern for files to process
            dry_run: If True, analyze without making changes
            categories_to_process: List of categories to process (None = all)
            
        Returns:
            Dict with processing results and statistics
        """
        start_time = time.time()
        
        print(f"Starting batch processing of vault: {self.vault_path}")
        print(f"Output directory: {self.output_path}")
        print(f"Dry run: {dry_run}")
        print("-" * 60)
        
        # Handle attachments folder first
        if not dry_run:
            self._handle_attachments_folder()
        
        # Discover files
        files_to_process = list(self.vault_path.rglob(file_pattern))
        self.stats['total_files'] = len(files_to_process)
        
        print(f"Found {len(files_to_process)} files to process")
        
        if not files_to_process:
            return self._finalize_results(start_time)
        
        # Process files in batches
        batch_results = []
        for i in range(0, len(files_to_process), self.batch_size):
            batch = files_to_process[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(files_to_process) + self.batch_size - 1) // self.batch_size
            
            print(f"\nProcessing batch {batch_num}/{total_batches} ({len(batch)} files)")
            
            batch_result = self._process_batch(batch, dry_run, categories_to_process)
            batch_results.append(batch_result)
            
            # Update statistics
            self._update_stats(batch_result)
            
            # Progress report
            self._print_progress_report()
        
        # Finalize results
        results = self._finalize_results(start_time)
        
        # Generate reports
        self._generate_reports(results, batch_results)
        
        return results
    
    def _process_batch(self, 
                      files: List[Path], 
                      dry_run: bool,
                      categories_to_process: Optional[List[str]]) -> Dict:
        """Process a batch of files."""
        batch_results = {
            'processed': [],
            'failed': [],
            'skipped': [],
            'classifications': [],
            'validations': []
        }
        
        # Use thread pool for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all files for processing
            future_to_file = {
                executor.submit(self._process_single_file, file_path, dry_run, categories_to_process): file_path
                for file_path in files
            }
            
            # Collect results
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result['status'] == 'processed':
                        batch_results['processed'].append(result)
                    elif result['status'] == 'failed':
                        batch_results['failed'].append(result)
                    elif result['status'] == 'skipped':
                        batch_results['skipped'].append(result)
                    
                    # Collect classification and validation data
                    if 'classification' in result:
                        batch_results['classifications'].append(result['classification'])
                    if 'validation' in result:
                        batch_results['validations'].append(result['validation'])
                        
                except Exception as e:
                    batch_results['failed'].append({
                        'file': str(file_path),
                        'status': 'failed',
                        'error': str(e),
                        'stage': 'batch_processing'
                    })
        
        return batch_results
    
    def _process_single_file(self, 
                           file_path: Path, 
                           dry_run: bool,
                           categories_to_process: Optional[List[str]]) -> Dict:
        """Process a single file through the complete pipeline."""
        result = {
            'file': str(file_path),
            'status': 'unknown',
            'original_size': 0,
            'processed_size': 0,
            'processing_time': 0.0,
            'stages_completed': [],
            'classification': None,
            'validation': None,
            'changes_made': []
        }
        
        start_time = time.time()
        
        try:
            # Stage 1: Validation and Backup
            result['stages_completed'].append('validation')
            validation_check = self.file_handler.validate_file(file_path)
            if not validation_check['exists'] or not validation_check['readable']:
                result['status'] = 'failed'
                result['error'] = f"File validation failed: {validation_check['errors']}"
                return result
            
            # Stage 2: Read and parse file
            result['stages_completed'].append('reading')
            frontmatter, content = self.file_handler.read_note(file_path)
            result['original_size'] = len(content)
            
            # Stage 3: Content Classification
            result['stages_completed'].append('classification')
            classification = self.classifier.classify_note(content, frontmatter)
            result['classification'] = classification
            
            category = classification['category']
            
            # Skip if not in categories to process
            if categories_to_process and category not in categories_to_process:
                result['status'] = 'skipped'
                result['skip_reason'] = f'Category {category} not in processing list'
                return result
            
            # Stage 4: Metadata Standardization
            result['stages_completed'].append('metadata_standardization')
            original_frontmatter = frontmatter.copy()
            standardized_metadata = self.metadata_standardizer.standardize_metadata(
                frontmatter, file_path.name, str(file_path)
            )
            
            if standardized_metadata != original_frontmatter:
                result['changes_made'].append('metadata_standardized')
            
            # Stage 5: HTML Table Conversion (for all notes)
            result['stages_completed'].append('html_table_conversion')
            from src.preprocessing.web_clipping_cleaner import convert_html_tables_to_markdown
            content = convert_html_tables_to_markdown(content)
            
            # Stage 6: Content Processing based on classification
            result['stages_completed'].append('content_processing')
            original_content = content
            processed_content = content
            
            if category == 'web_clipping' and self.web_cleaner.is_web_clipping(content, frontmatter):
                try:
                    processed_content, cleaning_stats = self.web_cleaner.clean_web_clipping(content, frontmatter)
                    if cleaning_stats and cleaning_stats.get('removed_chars', 0) > 0:
                        result['changes_made'].append(f"removed_{cleaning_stats['removed_chars']}_chars_boilerplate")
                        result['cleaning_stats'] = cleaning_stats
                except Exception as e:
                    result['changes_made'].append('web_cleaning_failed')
                    result['cleaning_error'] = str(e)
                    # Continue with original content if cleaning fails
            
            elif category == 'pdf_annotation':
                # Minimal processing for PDF annotations
                processed_content = self._clean_pdf_annotation(content)
                if processed_content != original_content:
                    result['changes_made'].append('pdf_annotation_cleaned')
            
            elif category == 'personal_note':
                # Gentle formatting cleanup for personal notes
                processed_content = self._clean_personal_note(content)
                if processed_content != original_content:
                    result['changes_made'].append('personal_note_formatted')
            
            # Stage 6: Attachment Validation
            result['stages_completed'].append('attachment_validation')
            if not dry_run:  # Only validate if we have the attachments copied
                attachment_validation = self._validate_attachments(processed_content, file_path.name)
                result['attachment_validation'] = attachment_validation
                
                if not attachment_validation['all_valid']:
                    result['changes_made'].append(f"missing_{len(attachment_validation['missing_attachments'])}_attachments")
            
            # Stage 7: Quality Validation
            result['stages_completed'].append('quality_validation')
            try:
                validation = self.validator.validate_note(processed_content, standardized_metadata, file_path.name)
                result['validation'] = validation
                
                if validation and validation.get('overall_quality') == 'failed':
                    result['status'] = 'failed'
                    result['error'] = f"Quality validation failed: {validation.get('issues', 'Unknown issues')}"
                    return result
            except Exception as e:
                result['validation_error'] = str(e)
                # Continue processing even if validation fails
            
            # Stage 8: Write processed file (if not dry run)
            if not dry_run:
                result['stages_completed'].append('writing')
                
                # Determine output path
                relative_path = file_path.relative_to(self.vault_path)
                output_file_path = self.output_path / relative_path
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write the processed file
                success = self.file_handler.write_note(
                    output_file_path, 
                    standardized_metadata, 
                    processed_content,
                    backup=self.backup
                )
                
                if not success:
                    result['status'] = 'failed'
                    result['error'] = 'Failed to write processed file'
                    return result
                
                result['output_file'] = str(output_file_path)
            
            # Success!
            result['status'] = 'processed'
            result['processed_size'] = len(processed_content)
            result['processing_time'] = time.time() - start_time
            
            return result
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            result['processing_time'] = time.time() - start_time
            return result
    
    def _clean_pdf_annotation(self, content: str) -> str:
        """Minimal cleaning for PDF annotation notes."""
        # Just clean up excessive whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        cleaned = cleaned.strip()
        return cleaned
    
    def _clean_personal_note(self, content: str) -> str:
        """Gentle formatting cleanup for personal notes that preserves intentional structure."""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Preserve leading whitespace for indentation-sensitive structures
            if line.strip():  # Non-empty line
                # Only clean internal whitespace, preserve leading/trailing structure
                # Remove excessive internal spaces but keep single spaces and tabs/indentation
                cleaned_line = re.sub(r'[ \t]{2,}', ' ', line)  # Multiple spaces/tabs -> single space
                cleaned_line = re.sub(r' +$', '', cleaned_line)  # Trailing spaces only
                cleaned_lines.append(cleaned_line)
            else:
                # Keep empty lines as-is for structure
                cleaned_lines.append(line)
        
        # Only remove excessive consecutive empty lines (3+ -> 2)
        cleaned = '\n'.join(cleaned_lines)
        cleaned = re.sub(r'\n\s*\n\s*\n\s*\n+', '\n\n\n', cleaned)  # 4+ empty lines -> 3
        cleaned = re.sub(r'^\s+|\s+$', '', cleaned)  # Trim start/end only
        
        return cleaned
    
    def _handle_attachments_folder(self):
        """Copy the entire attachments folder to the output directory."""
        if not self.vault_attachments_path.exists():
            print(f"⚠️  Warning: Attachments folder not found at {self.vault_attachments_path}")
            return
        
        print(f"📎 Copying attachments folder...")
        print(f"   From: {self.vault_attachments_path}")
        print(f"   To: {self.output_attachments_path}")
        
        try:
            if self.output_attachments_path.exists():
                # Remove existing attachments folder to avoid conflicts
                shutil.rmtree(self.output_attachments_path)
            
            # Copy the entire attachments folder
            shutil.copytree(self.vault_attachments_path, self.output_attachments_path)
            
            # Count attachments
            attachment_count = sum(1 for _ in self.output_attachments_path.rglob("*") if _.is_file())
            print(f"✅ Successfully copied {attachment_count} attachment files")
            
        except Exception as e:
            print(f"❌ Error copying attachments: {e}")
            self.stats['errors'].append({
                'stage': 'attachment_copy',
                'error': str(e),
                'file': str(self.vault_attachments_path)
            })
    
    def _validate_attachments(self, content: str, filename: str) -> Dict:
        """Validate that all attachment references in content exist."""
        validation = {
            'total_references': 0,
            'valid_references': 0,
            'missing_attachments': [],
            'all_valid': True
        }
        
        # Find all attachment references
        import re
        attachment_pattern = re.compile(r'!\[\[attachments/([^\]]+)\]\]')
        references = attachment_pattern.findall(content)
        
        validation['total_references'] = len(references)
        
        for ref in references:
            attachment_path = self.output_attachments_path / ref
            if attachment_path.exists():
                validation['valid_references'] += 1
            else:
                validation['missing_attachments'].append(ref)
                validation['all_valid'] = False
        
        return validation
    
    def _update_stats(self, batch_result: Dict):
        """Update processing statistics with batch results."""
        self.stats['processed_files'] += len(batch_result['processed'])
        self.stats['failed_files'] += len(batch_result['failed'])
        self.stats['skipped_files'] += len(batch_result['skipped'])
        
        # Update category counts
        for classification in batch_result['classifications']:
            category = classification['category']
            self.stats['category_counts'][category] = self.stats['category_counts'].get(category, 0) + 1
        
        # Update quality distribution
        for validation in batch_result['validations']:
            quality = validation['overall_quality']
            self.stats['quality_distribution'][quality] = self.stats['quality_distribution'].get(quality, 0) + 1
        
        # Collect errors
        for failed in batch_result['failed']:
            self.stats['errors'].append({
                'file': failed['file'],
                'error': failed.get('error', 'Unknown error'),
                'stage': failed.get('stage', 'unknown')
            })
    
    def _print_progress_report(self):
        """Print progress report."""
        total = self.stats['total_files']
        processed = self.stats['processed_files']
        failed = self.stats['failed_files']
        skipped = self.stats['skipped_files']
        completed = processed + failed + skipped
        
        progress_pct = (completed / total * 100) if total > 0 else 0
        success_pct = (processed / completed * 100) if completed > 0 else 0
        
        print(f"  Progress: {completed}/{total} files ({progress_pct:.1f}%)")
        print(f"  Success rate: {processed}/{completed} ({success_pct:.1f}%)")
        print(f"  Failed: {failed}, Skipped: {skipped}")
    
    def _finalize_results(self, start_time: float) -> Dict:
        """Finalize processing results."""
        self.stats['processing_time'] = time.time() - start_time
        
        results = {
            'summary': {
                'total_files': self.stats['total_files'],
                'processed_files': self.stats['processed_files'],
                'failed_files': self.stats['failed_files'],
                'skipped_files': self.stats['skipped_files'],
                'success_rate': (self.stats['processed_files'] / self.stats['total_files']) if self.stats['total_files'] > 0 else 0,
                'processing_time': self.stats['processing_time'],
                'files_per_second': self.stats['total_files'] / self.stats['processing_time'] if self.stats['processing_time'] > 0 else 0
            },
            'categories': self.stats['category_counts'],
            'quality_distribution': self.stats['quality_distribution'],
            'errors': self.stats['errors'][:50],  # Limit error list
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n{'='*60}")
        print("PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"Total files: {results['summary']['total_files']}")
        print(f"Processed: {results['summary']['processed_files']}")
        print(f"Failed: {results['summary']['failed_files']}")
        print(f"Skipped: {results['summary']['skipped_files']}")
        print(f"Success rate: {results['summary']['success_rate']:.1%}")
        print(f"Processing time: {results['summary']['processing_time']:.1f}s")
        print(f"Speed: {results['summary']['files_per_second']:.1f} files/sec")
        
        return results
    
    def _generate_reports(self, results: Dict, batch_results: List[Dict]):
        """Generate detailed processing reports."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Summary report
        summary_path = self.output_path / "reports" / f"processing_summary_{timestamp}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Detailed log
        log_path = self.output_path / "logs" / f"processing_log_{timestamp}.json"
        detailed_log = {
            'results': results,
            'batch_details': batch_results,
            'configuration': {
                'vault_path': str(self.vault_path),
                'output_path': str(self.output_path),
                'batch_size': self.batch_size,
                'max_workers': self.max_workers,
                'backup_enabled': self.backup
            }
        }
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_log, f, indent=2, ensure_ascii=False)
        
        print(f"\nReports generated:")
        print(f"  Summary: {summary_path}")
        print(f"  Detailed log: {log_path}")
    
    def process_sample(self, sample_size: int = 10, dry_run: bool = True) -> Dict:
        """Process a small sample for testing."""
        import random
        
        all_files = list(self.vault_path.rglob("*.md"))
        if len(all_files) <= sample_size:
            files = all_files
            print(f"Warning: Only {len(all_files)} files available, processing all of them")
        else:
            files = random.sample(all_files, sample_size)
            print(f"Randomly sampled {sample_size} files from {len(all_files)} available")
        
        print(f"Processing sample of {len(files)} files (dry_run={dry_run})")
        
        # Handle attachments for sample processing too
        if not dry_run:
            self._handle_attachments_folder()
        
        results = []
        for file_path in files:
            result = self._process_single_file(file_path, dry_run, None)
            results.append(result)
            print(f"  {file_path.name}: {result['status']}")
        
        return {
            'sample_size': len(files),
            'results': results,
            'success_count': sum(1 for r in results if r['status'] == 'processed'),
            'failure_count': sum(1 for r in results if r['status'] == 'failed')
        }
