#!/usr/bin/env python3
"""
Note Type Tester

Crawls the source vault to find one example of each note type,
then tests the complete pipeline performance on this diverse sample.
Provides comprehensive evaluation of system performance across different content types.
"""

import argparse
import json
import logging
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.preprocessing.web_clipping_cleaner import clean_html_like_clipping
from src.curation.obsidian_curator.main import run as curation_run
import config


class NoteTypeTester:
    """Crawls vault to find diverse note types and tests pipeline performance."""
    
    def __init__(self, source_vault: str):
        self.source_vault = Path(source_vault)
        self.note_types = {}
        self.test_results = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for the tester."""
        # Ensure logs directory exists
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        log_filename = logs_dir / f'note_type_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_filename)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def classify_note_type(self, note_path: Path) -> str:
        """Classify a note into one of the main types."""
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter
            frontmatter = None
            if content.startswith('---'):
                try:
                    import yaml
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        content_body = parts[2]
                    else:
                        content_body = content
                except:
                    content_body = content
            else:
                content_body = content
            
            # Check for attachments
            attachments_dir = self.source_vault / "attachments"
            attachment_folder = attachments_dir / f"{note_path.stem}.resources"
            has_pdf = attachment_folder.exists() and any(
                f.suffix.lower() == '.pdf' for f in attachment_folder.iterdir() if f.is_file()
            )
            has_audio = attachment_folder.exists() and any(
                f.suffix.lower() in ['.mp3', '.wav', '.m4a', '.ogg', '.flac'] 
                for f in attachment_folder.iterdir() if f.is_file()
            )
            
            # Classify based on content and structure
            content_lower = content_body.lower()
            
            # Web clipping indicators
            if any(indicator in content_lower for indicator in [
                'skip to', 'jump to', 'navigation', 'menu', 'footer',
                'subscribe', 'newsletter', 'cookie', 'privacy policy',
                'share on', 'follow us', 'social media'
            ]):
                return 'web_clipping'
            
            # PDF document indicators
            if has_pdf or 'pdf' in content_lower or 'document' in frontmatter.get('type', '').lower():
                return 'pdf_document'
            
            # Audio note indicators
            if has_audio or 'audio' in content_lower or 'transcription' in content_lower:
                return 'audio_note'
            
            # Image note indicators (OCR content)
            if any(indicator in content_lower for indicator in [
                'image', 'photo', 'screenshot', 'scan', 'ocr'
            ]) or len(content_body.strip()) < 200:
                return 'image_note'
            
            # Web reference indicators
            if content_body.count('http') > 3 or 'source:' in content_lower:
                return 'web_reference'
            
            # Structured note indicators
            if content_body.count('#') > 3 or '##' in content_body:
                return 'structured_note'
            
            # Short note indicators
            if len(content_body.strip()) < 100:
                return 'short_note'
            
            # Default to text note
            return 'text_note'
            
        except Exception as e:
            self.logger.warning(f"Error classifying {note_path.name}: {e}")
            return 'unknown'
    
    def crawl_for_note_types(self) -> Dict[str, Path]:
        """Crawl the vault to find one example of each note type."""
        self.logger.info(f"🔍 Crawling {self.source_vault} for diverse note types...")
        
        # Get all markdown files recursively (vault structure has files in subdirectories)
        all_notes = list(self.source_vault.rglob("*.md"))
        
        # Filter out files in .obsidian directory and other system directories
        all_notes = [
            note for note in all_notes 
            if not any(part.startswith('.') for part in note.parts)
        ]
        
        random.shuffle(all_notes)  # Randomize order
        
        found_types = {}
        type_counts = {}
        
        for note_path in all_notes:
            if len(found_types) >= 8:  # Stop when we have examples of main types
                break
                
            note_type = self.classify_note_type(note_path)
            
            if note_type not in type_counts:
                type_counts[note_type] = 0
            type_counts[note_type] += 1
            
            # Take first example of each type
            if note_type not in found_types:
                found_types[note_type] = note_path
                self.logger.info(f"  ✅ Found {note_type}: {note_path.name}")
        
        self.logger.info(f"\n📊 Note type distribution in sample:")
        for note_type, count in sorted(type_counts.items()):
            status = "✅" if note_type in found_types else "❌"
            self.logger.info(f"  {status} {note_type}: {count} notes")
        
        return found_types
    
    def test_preprocessing(self, note_path: Path) -> Dict:
        """Test preprocessing on a single note."""
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Extract frontmatter
            frontmatter = None
            if original_content.startswith('---'):
                try:
                    import yaml
                    parts = original_content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        content_body = parts[2]
                    else:
                        content_body = original_content
                except:
                    content_body = original_content
            else:
                content_body = original_content
            
            # Test preprocessing
            cleaned_content = clean_html_like_clipping(content_body, frontmatter)
            
            # Calculate metrics
            if frontmatter is not None:
                original_body_length = len(content_body)
                cleaned_length = len(cleaned_content)
                reduction_percentage = ((original_body_length - cleaned_length) / original_body_length * 100) if original_body_length > 0 else 0
                original_length = len(original_content)
            else:
                original_length = len(original_content)
                cleaned_length = len(cleaned_content)
                reduction_percentage = ((original_length - cleaned_length) / original_length * 100) if original_length > 0 else 0
            
            return {
                'success': True,
                'original_length': original_length,
                'cleaned_length': cleaned_length,
                'reduction_percentage': reduction_percentage,
                'note_type': self.classify_note_type(note_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'note_type': self.classify_note_type(note_path)
            }
    
    def test_full_pipeline(self, note_path: Path, test_raw_dir: Path, test_preprocessed_dir: Path, test_curated_dir: Path, note_index: int) -> Dict:
        """Test the complete pipeline (preprocessing + curation) on a single note."""
        note_type = self.classify_note_type(note_path)
        note_name = note_path.name
        
        result = {
            'note_type': note_type,
            'note_name': note_name,
            'preprocessing': {'success': False},
            'curation': {'success': False},
            'pipeline_success': False
        }
        
        try:
            # Step 1: Copy note to test directory (EXACT same structure as test_complete_pipeline.py)
            new_note_name = f"test_note_{note_index:02d}_{note_name}"
            test_raw_path = test_raw_dir / "notes" / new_note_name
            import shutil
            shutil.copy2(note_path, test_raw_path)
            
            # Copy associated attachments (EXACT same logic as test_complete_pipeline.py)
            note_stem = note_path.stem
            source_vault = note_path.parent.parent  # Go up to vault root
            
            # Build attachment mapping (same as test_complete_pipeline.py)
            attachments_dir = source_vault / "attachments"
            attachment_mapping = {}
            if attachments_dir.exists():
                for att_dir in attachments_dir.iterdir():
                    if att_dir.is_dir() and att_dir.name.endswith('.resources'):
                        # Remove .resources extension to get the base name
                        base_name = att_dir.name[:-10]
                        attachment_mapping[base_name] = att_dir
            
            def sanitize_filename(filename):
                """Sanitize filename the same way Obsidian/Evernote does for attachment directories."""
                # Convert multiple spaces to double underscores, single spaces to single underscores
                import re
                sanitized = re.sub(r'\s{2,}', '__', filename)  # Multiple spaces -> __
                sanitized = re.sub(r'\s', '_', sanitized)      # Single spaces -> _
                return sanitized
            
            real_attachments_dir = None
            
            # Try exact match first
            exact_att_dir = source_vault / "attachments" / f"{note_stem}.resources"
            if exact_att_dir.exists():
                real_attachments_dir = exact_att_dir
            else:
                # Try sanitized match
                sanitized_stem = sanitize_filename(note_stem)
                if sanitized_stem in attachment_mapping:
                    real_attachments_dir = attachment_mapping[sanitized_stem]
            
            if real_attachments_dir and real_attachments_dir.exists():
                try:
                    new_attachments_dir = test_raw_dir / "attachments" / f"{new_note_name}.resources"
                    shutil.copytree(real_attachments_dir, new_attachments_dir)
                    attachment_count = len(list(real_attachments_dir.iterdir()))
                    self.logger.info(f"    + attachments: {attachment_count} files")
                except Exception as e:
                    self.logger.warning(f"    + attachments: ERROR copying - {e}")
            else:
                # Try alternative attachment locations
                alt_locations = [
                    source_vault / "attachments" / note_stem,
                    source_vault / "attachments" / f"{note_stem}_files",
                    source_vault / "attachments" / f"{note_stem}_attachments"
                ]
                
                found_attachments = False
                for alt_dir in alt_locations:
                    if alt_dir.exists():
                        try:
                            new_attachments_dir = test_raw_dir / "attachments" / f"{new_note_name}.resources"
                            shutil.copytree(alt_dir, new_attachments_dir)
                            attachment_count = len(list(alt_dir.iterdir()))
                            self.logger.info(f"    + attachments: {attachment_count} files (from {alt_dir.name})")
                            found_attachments = True
                            break
                        except Exception as e:
                            self.logger.warning(f"    + attachments: ERROR copying from {alt_dir.name} - {e}")
                            continue
                
                # If still not found, try to find attachments by reading the note content
                if not found_attachments:
                    try:
                        with open(note_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Look for attachment references in the content
                        import re
                        attachment_refs = re.findall(r'!\[\[attachments/([^\]]+)\]\]', content)
                        if attachment_refs:
                            # Try to find the attachment folder by the referenced file
                            for ref in attachment_refs:
                                ref_stem = ref.split('/')[0]  # Get the folder name
                                potential_attachments_dir = source_vault / "attachments" / ref_stem
                                if potential_attachments_dir.exists():
                                    try:
                                        new_attachments_dir = test_raw_dir / "attachments" / f"{new_note_name}.resources"
                                        shutil.copytree(potential_attachments_dir, new_attachments_dir)
                                        attachment_count = len(list(potential_attachments_dir.iterdir()))
                                        self.logger.info(f"    + attachments: {attachment_count} files (found by content reference: {ref_stem})")
                                        found_attachments = True
                                        break
                                    except Exception as e:
                                        self.logger.warning(f"    + attachments: ERROR copying from {ref_stem} - {e}")
                                        continue
                    except Exception as e:
                        self.logger.warning(f"    + attachments: ERROR reading note content - {e}")
                
                if not found_attachments:
                    self.logger.info(f"    + attachments: none found")
            
            # Step 2: Test preprocessing (use the SAME pipeline as test_complete_pipeline.py)
            self.logger.info(f"    🧹 Preprocessing {note_type}: {note_name}")
            
            # Use the same preprocessing pipeline as test_complete_pipeline.py
            from src.preprocessing import BatchProcessor
            
            # Initialize batch processor with the same settings as test_complete_pipeline.py
            processor = BatchProcessor(
                vault_path=str(test_raw_dir),
                output_path=str(test_preprocessed_dir),
                backup=False,
                batch_size=10,
                max_workers=2
            )
            
            # Process the single note
            results = processor.process_vault()
            
            # Check if preprocessing was successful
            if results['summary']['processed_files'] > 0:
                # Find the preprocessed file
                test_preprocessed_path = test_preprocessed_dir / "notes" / new_note_name
                
                if test_preprocessed_path.exists():
                    # Read the preprocessed content to calculate metrics
                    with open(test_raw_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    with open(test_preprocessed_path, 'r', encoding='utf-8') as f:
                        preprocessed_content = f.read()
                    
                    # Calculate metrics
                    original_length = len(original_content)
                    cleaned_length = len(preprocessed_content)
                    reduction_percentage = ((original_length - cleaned_length) / original_length * 100) if original_length > 0 else 0
                else:
                    raise Exception("Preprocessed file not found")
            else:
                raise Exception("Preprocessing failed")
            
            result['preprocessing'] = {
                'success': True,
                'original_length': original_length,
                'cleaned_length': cleaned_length,
                'reduction_percentage': reduction_percentage
            }
            
            # Step 3: Test curation
            self.logger.info(f"    🎯 Curation {note_type}: {note_name}")
            
            try:
                # Set up curation paths (same structure as test_complete_pipeline.py)
                curation_output_dir = test_curated_dir / "notes"
                curation_output_dir.mkdir(parents=True, exist_ok=True)
                
                # Load curation configuration and override paths for testing
                from src.curation.obsidian_curator.main import load_cfg
                cfg = load_cfg("config.yaml")
                
                # Override output paths for testing (same as test_complete_pipeline.py)
                cfg['paths']['out_notes'] = str(curation_output_dir)
                cfg['paths']['out_assets'] = str(curation_output_dir.parent / "attachments")
                cfg['paths']['vault'] = str(test_preprocessed_dir)
                cfg['paths']['attachments'] = str(test_preprocessed_dir / "attachments")
                
                # Run curation on the preprocessed notes (same as test_complete_pipeline.py)
                curation_results = curation_run(
                    cfg=cfg,
                    vault=str(test_preprocessed_dir),
                    attachments=str(test_preprocessed_dir / "attachments"),
                    out_notes=str(curation_output_dir),
                    dry_run=False
                )
                
                # Extract results from curation output
                curated_files = list(curation_output_dir.glob("*.md"))
                triage_files = list((curation_output_dir.parent / "triage").glob("*.md")) if (curation_output_dir.parent / "triage").exists() else []
                
                # Determine decision based on output files
                if curated_files:
                    decision = "keep"
                    output_path = curated_files[0]
                elif triage_files:
                    decision = "triage"
                    output_path = triage_files[0]
                else:
                    decision = "discard"
                    output_path = None
                
                # Try to extract score and reasoning from the curated file
                score = 0.0
                reasoning = "No reasoning available"
                
                if output_path and output_path.exists():
                    try:
                        with open(output_path, 'r', encoding='utf-8') as f:
                            curated_content = f.read()
                        
                        # Extract score from frontmatter
                        if '---' in curated_content:
                            frontmatter_part = curated_content.split('---')[1]
                            
                            # Look for score in various formats
                            for line in frontmatter_part.split('\n'):
                                if 'score:' in line.lower():
                                    try:
                                        score_str = line.split(':')[1].strip()
                                        score = float(score_str)
                                        break
                                    except ValueError:
                                        continue
                            
                            # Look for reasoning in various formats
                            reasoning_lines = []
                            in_reasoning = False
                            for line in frontmatter_part.split('\n'):
                                line_lower = line.lower()
                                if 'reasoning:' in line_lower:
                                    in_reasoning = True
                                    reasoning_text = line.split(':', 1)[1].strip() if ':' in line else ""
                                    if reasoning_text:
                                        reasoning_lines.append(reasoning_text)
                                elif in_reasoning and line.strip() and not line.strip().startswith('-'):
                                    reasoning_lines.append(line.strip())
                                elif in_reasoning and not line.strip():
                                    break
                                elif in_reasoning and line.strip().startswith('-'):
                                    break
                            
                            if reasoning_lines:
                                reasoning = ' '.join(reasoning_lines)
                    except Exception as e:
                        self.logger.warning(f"Could not extract score/reasoning: {e}")
                
                # If we couldn't extract the score from the file, try to get it from the decision logic
                if score == 0.0 and decision != "discard":
                    # For kept/triaged notes, we should have a score
                    # This is a fallback - the actual scores are logged by the curation system
                    score = 0.5  # Default moderate score if we can't extract it
                
                result['curation'] = {
                    'success': True,
                    'decision': decision,
                    'score': score,
                    'reasoning': reasoning,
                    'output_path': str(output_path) if output_path else ''
                }
                
                result['pipeline_success'] = True
                
            except Exception as e:
                result['curation'] = {
                    'success': False,
                    'error': str(e)
                }
                self.logger.warning(f"      ⚠️ Curation failed: {e}")
            
        except Exception as e:
            result['preprocessing'] = {
                'success': False,
                'error': str(e)
            }
            self.logger.error(f"      ❌ Preprocessing failed: {e}")
        
        return result
    
    def analyze_by_content_type(self, pipeline_results: Dict) -> Dict:
        """Analyze results grouped by content type characteristics."""
        analysis = {
            'web_content': {
                'types': ['web_clipping', 'web_reference'],
                'preprocessing_success': 0,
                'curation_success': 0,
                'average_reduction': 0.0,
                'average_score': 0.0,
                'decisions': {'keep': 0, 'triage': 0, 'discard': 0}
            },
            'document_content': {
                'types': ['pdf_document', 'structured_note'],
                'preprocessing_success': 0,
                'curation_success': 0,
                'average_reduction': 0.0,
                'average_score': 0.0,
                'decisions': {'keep': 0, 'triage': 0, 'discard': 0}
            },
            'media_content': {
                'types': ['image_note', 'audio_note'],
                'preprocessing_success': 0,
                'curation_success': 0,
                'average_reduction': 0.0,
                'average_score': 0.0,
                'decisions': {'keep': 0, 'triage': 0, 'discard': 0}
            },
            'personal_content': {
                'types': ['text_note', 'short_note'],
                'preprocessing_success': 0,
                'curation_success': 0,
                'average_reduction': 0.0,
                'average_score': 0.0,
                'decisions': {'keep': 0, 'triage': 0, 'discard': 0}
            }
        }
        
        # Count results by content type
        for note_type, result in pipeline_results.items():
            for category, data in analysis.items():
                if note_type in data['types']:
                    # Preprocessing success
                    if result['preprocessing'].get('success', False):
                        data['preprocessing_success'] += 1
                        data['average_reduction'] += result['preprocessing'].get('reduction_percentage', 0)
                    
                    # Curation success
                    if result['curation'].get('success', False):
                        data['curation_success'] += 1
                        data['average_score'] += result['curation'].get('score', 0.0)
                        decision = result['curation'].get('decision', 'unknown').lower()
                        if decision in data['decisions']:
                            data['decisions'][decision] += 1
        
        # Calculate averages
        for category, data in analysis.items():
            if data['preprocessing_success'] > 0:
                data['average_reduction'] /= data['preprocessing_success']
            if data['curation_success'] > 0:
                data['average_score'] /= data['curation_success']
        
        return analysis
    
    def run_pipeline_test(self, note_types: Dict[str, Path]) -> Dict:
        """Run the complete pipeline test (preprocessing + curation) on the diverse sample."""
        self.logger.info(f"\n🚀 Running COMPLETE pipeline test on {len(note_types)} diverse notes...")
        
        # Use the same test directory structure as test_complete_pipeline.py
        test_cfg = config.get_test_config()
        test_raw_dir = Path(test_cfg['paths']['test_raw_vault'])
        test_preprocessed_dir = Path(test_cfg['paths']['test_preprocessed_vault'])
        test_curated_dir = Path(test_cfg['paths']['test_curated_vault'])
        
        # Clean and recreate directories (same as test_complete_pipeline.py)
        import shutil
        import os
        
        # Clean existing test folders
        if test_raw_dir.exists():
            shutil.rmtree(test_raw_dir)
        if test_preprocessed_dir.exists():
            shutil.rmtree(test_preprocessed_dir)
        if test_curated_dir.exists():
            shutil.rmtree(test_curated_dir)
        
        # Create directories with proper structure
        test_raw_dir.mkdir(parents=True, exist_ok=True)
        (test_raw_dir / "notes").mkdir(exist_ok=True)
        (test_raw_dir / "attachments").mkdir(exist_ok=True)
        test_preprocessed_dir.mkdir(parents=True, exist_ok=True)
        test_curated_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'note_types_tested': {},
            'pipeline_results': {},
            'summary': {},
            'content_type_analysis': {}
        }
        
        # Test each note type through the complete pipeline
        self.logger.info("🔄 Testing complete pipeline...")
        preprocessing_success = 0
        curation_success = 0
        pipeline_success = 0
        total_notes = len(note_types)
        
        for i, (note_type, note_path) in enumerate(note_types.items(), 1):
            self.logger.info(f"  Processing {note_type}: {note_path.name}")
            
            result = self.test_full_pipeline(note_path, test_raw_dir, test_preprocessed_dir, test_curated_dir, i)
            results['pipeline_results'][note_type] = result
            
            if result['preprocessing']['success']:
                preprocessing_success += 1
                self.logger.info(f"    ✅ Preprocessing: {result['preprocessing']['reduction_percentage']:.1f}% reduction")
            else:
                self.logger.error(f"    ❌ Preprocessing failed: {result['preprocessing'].get('error', 'Unknown error')}")
            
            if result['curation']['success']:
                curation_success += 1
                decision = result['curation'].get('decision', 'unknown')
                score = result['curation'].get('score', 0.0)
                self.logger.info(f"    ✅ Curation: {decision} (score: {score:.3f})")
            else:
                self.logger.error(f"    ❌ Curation failed: {result['curation'].get('error', 'Unknown error')}")
            
            if result['pipeline_success']:
                pipeline_success += 1
                self.logger.info(f"    🎉 Complete pipeline success!")
            
            results['note_types_tested'][note_type] = {
                'original_path': str(note_path),
                'note_name': note_path.name
            }
        
        # Analyze results by content type
        results['content_type_analysis'] = self.analyze_by_content_type(results['pipeline_results'])
        
        # Generate comprehensive summary
        results['summary'] = {
            'total_note_types': total_notes,
            'preprocessing_success_rate': (preprocessing_success / total_notes * 100) if total_notes > 0 else 0,
            'curation_success_rate': (curation_success / total_notes * 100) if total_notes > 0 else 0,
            'pipeline_success_rate': (pipeline_success / total_notes * 100) if total_notes > 0 else 0,
            'average_preprocessing_reduction': sum(
                r['preprocessing'].get('reduction_percentage', 0) 
                for r in results['pipeline_results'].values() 
                if r['preprocessing'].get('success', False)
            ) / max(1, preprocessing_success),
            'average_curation_score': sum(
                r['curation'].get('score', 0.0) 
                for r in results['pipeline_results'].values() 
                if r['curation'].get('success', False)
            ) / max(1, curation_success)
        }
        
        # Preserve test directories for inspection (same as test_complete_pipeline.py)
        self.logger.info(f"📁 Test directories preserved for inspection:")
        self.logger.info(f"  Raw: {test_raw_dir}")
        self.logger.info(f"  Preprocessed: {test_preprocessed_dir}")
        self.logger.info(f"  Curated: {test_curated_dir}")
        
        return results
    
    def print_results(self, results: Dict):
        """Print comprehensive test results."""
        print("\n" + "="*80)
        print("🎯 COMPLETE PIPELINE DIVERSITY TEST RESULTS")
        print("="*80)
        
        # Summary
        summary = results['summary']
        print(f"\n📊 OVERALL SUMMARY:")
        print(f"  Total Note Types Tested: {summary['total_note_types']}")
        print(f"  Preprocessing Success Rate: {summary['preprocessing_success_rate']:.1f}%")
        print(f"  Curation Success Rate: {summary['curation_success_rate']:.1f}%")
        print(f"  Complete Pipeline Success Rate: {summary['pipeline_success_rate']:.1f}%")
        print(f"  Average Content Reduction: {summary['average_preprocessing_reduction']:.1f}%")
        print(f"  Average Curation Score: {summary['average_curation_score']:.3f}")
        
        # Note Types Found
        print(f"\n📝 NOTE TYPES TESTED:")
        for note_type, info in results['note_types_tested'].items():
            print(f"  ✅ {note_type}: {info['note_name']}")
        
        # Complete Pipeline Results
        print(f"\n🔄 COMPLETE PIPELINE RESULTS:")
        for note_type, result in results['pipeline_results'].items():
            print(f"\n  📄 {note_type}: {result['note_name']}")
            
            # Preprocessing results
            if result['preprocessing']['success']:
                reduction = result['preprocessing']['reduction_percentage']
                print(f"    🧹 Preprocessing: ✅ {reduction:.1f}% reduction")
            else:
                print(f"    🧹 Preprocessing: ❌ {result['preprocessing'].get('error', 'Unknown error')}")
            
            # Curation results
            if result['curation']['success']:
                decision = result['curation']['decision']
                score = result['curation']['score']
                print(f"    🎯 Curation: ✅ {decision} (score: {score:.3f})")
                reasoning = result['curation']['reasoning'][:100] + "..." if len(result['curation']['reasoning']) > 100 else result['curation']['reasoning']
                print(f"      💭 Reasoning: {reasoning}")
            else:
                print(f"    🎯 Curation: ❌ {result['curation'].get('error', 'Unknown error')}")
            
            # Overall pipeline success
            status = "🎉 COMPLETE SUCCESS" if result['pipeline_success'] else "❌ PIPELINE FAILED"
            print(f"    📊 Pipeline: {status}")
        
        # Content Type Analysis
        print(f"\n📊 CONTENT TYPE ANALYSIS:")
        content_analysis = results['content_type_analysis']
        
        for category, data in content_analysis.items():
            if data['preprocessing_success'] > 0 or data['curation_success'] > 0:
                print(f"\n  📁 {category.upper().replace('_', ' ')} ({', '.join(data['types'])}):")
                print(f"    🧹 Preprocessing: {data['preprocessing_success']} success, {data['average_reduction']:.1f}% avg reduction")
                print(f"    🎯 Curation: {data['curation_success']} success, {data['average_score']:.3f} avg score")
                print(f"    📋 Decisions: Keep({data['decisions']['keep']}) Triage({data['decisions']['triage']}) Discard({data['decisions']['discard']})")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if summary['preprocessing_success_rate'] < 100:
            print(f"  ⚠️  Preprocessing issues detected - investigate failed note types")
        
        if summary['curation_success_rate'] < 100:
            print(f"  ⚠️  Curation issues detected - check LLM integration and scoring")
        
        if summary['pipeline_success_rate'] < 100:
            print(f"  ⚠️  Complete pipeline failures - review end-to-end integration")
        
        # Content type specific recommendations
        for category, data in content_analysis.items():
            if data['preprocessing_success'] > 0:
                if data['average_reduction'] > 40:
                    print(f"  ✅ {category}: Good clutter removal for web content")
                elif data['average_reduction'] < 5:
                    print(f"  ✅ {category}: Conservative cleaning preserving content")
                else:
                    print(f"  ✅ {category}: Balanced cleaning approach")
            
            if data['curation_success'] > 0:
                if data['average_score'] > 0.6:
                    print(f"  ✅ {category}: High curation scores - content highly valued")
                elif data['average_score'] < 0.3:
                    print(f"  ⚠️  {category}: Low curation scores - may need scoring adjustment")
                else:
                    print(f"  ✅ {category}: Moderate curation scores - appropriate valuation")
        
        print(f"\n📈 OVERALL ASSESSMENT:")
        if summary['pipeline_success_rate'] >= 90:
            print(f"  🎉 EXCELLENT: Complete pipeline handles diverse content types very well")
        elif summary['pipeline_success_rate'] >= 75:
            print(f"  ✅ GOOD: Pipeline generally handles diverse content well")
        elif summary['pipeline_success_rate'] >= 50:
            print(f"  ⚠️  FAIR: Pipeline has some issues with certain content types")
        else:
            print(f"  ❌ POOR: Pipeline needs significant improvements")
        
        print("\n" + "="*80)
    
    def run_full_test(self) -> Dict:
        """Run the complete note type diversity test."""
        self.logger.info("🚀 Starting Note Type Diversity Test")
        self.logger.info("="*60)
        
        # Step 1: Crawl for diverse note types
        note_types = self.crawl_for_note_types()
        
        if not note_types:
            raise ValueError("No note types found in the vault")
        
        # Step 2: Run pipeline test
        results = self.run_pipeline_test(note_types)
        
        # Step 3: Print results
        self.print_results(results)
        
        # Step 4: Save results
        output_file = f"analysis_output/note_type_test_{results['timestamp']}.json"
        Path("analysis_output").mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"\n💾 Results saved to: {output_file}")
        
        return results


def main():
    """Main entry point for the note type tester."""
    parser = argparse.ArgumentParser(
        description="Test pipeline performance across diverse note types"
    )
    parser.add_argument(
        '--source-vault',
        default=config.RAW_VAULT_PATH,
        help='Path to the source vault (default: from config.py)'
    )
    parser.add_argument(
        '--output',
        help='Custom output file for results'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize tester
        tester = NoteTypeTester(args.source_vault)
        
        # Run the test
        results = tester.run_full_test()
        
        # Save to custom output if specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Additional results saved to: {args.output}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
