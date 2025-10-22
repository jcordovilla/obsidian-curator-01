#!/usr/bin/env python3
"""
Triage GUI for manually processing notes from the triage folder.

This GUI allows users to:
- View triage notes one by one with scrollable preview
- Accept notes (move to notes folder + copy attachments)
- Discard notes (move to discarded folder)
- Preview attachments using system default viewer
- Track progress and resume from where left off
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import shutil
import json
import subprocess
import sys
from pathlib import Path
import re
from typing import List, Dict, Optional

# Add src to path to import config
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from config import CURATED_VAULT_PATH, CURATED_NOTES_PATH, CURATED_ATTACHMENTS_PATH, PREPROCESSED_ATTACHMENTS_PATH

class TriageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Obsidian Curator - Triage Manager")
        self.root.geometry("1000x700")
        
        # Configuration
        self.triage_folder = os.path.join(CURATED_VAULT_PATH, "triage")
        self.notes_folder = CURATED_NOTES_PATH
        self.discarded_folder = os.path.join(CURATED_VAULT_PATH, "discarded")
        self.curated_attachments = CURATED_ATTACHMENTS_PATH
        self.preprocessed_attachments = PREPROCESSED_ATTACHMENTS_PATH
        
        # State
        self.current_note_index = 0
        self.triage_notes = []
        self.progress_file = os.path.join(CURATED_VAULT_PATH, ".triage_progress.json")
        
        # Statistics
        self.total_notes = 0
        self.accepted_count = 0
        self.discarded_count = 0
        
        # Create folders if they don't exist
        self._ensure_folders_exist()
        
        # Load progress and triage notes
        self._load_progress()
        self._load_triage_notes()
        
        # Setup GUI
        self._setup_gui()
        
        # Load first note if available
        if self.triage_notes:
            self._load_current_note()
        else:
            self._show_no_notes_message()
    
    def _ensure_folders_exist(self):
        """Create necessary folders if they don't exist."""
        for folder in [self.notes_folder, self.discarded_folder, self.curated_attachments]:
            os.makedirs(folder, exist_ok=True)
    
    def _load_progress(self):
        """Load progress from previous session."""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                    saved_index = progress.get('current_index', 0)
                    self.accepted_count = progress.get('accepted_count', 0)
                    self.discarded_count = progress.get('discarded_count', 0)
                    # Only use saved index if it's valid for current note list
                    if saved_index < len(self.triage_notes):
                        self.current_note_index = saved_index
                    else:
                        self.current_note_index = 0
            except (json.JSONDecodeError, KeyError):
                self.current_note_index = 0
                self.accepted_count = 0
                self.discarded_count = 0
        else:
            self.current_note_index = 0
            self.accepted_count = 0
            self.discarded_count = 0
    
    def _save_progress(self):
        """Save current progress."""
        progress = {
            'current_index': self.current_note_index,
            'total_notes': len(self.triage_notes),
            'accepted_count': self.accepted_count,
            'discarded_count': self.discarded_count,
            'timestamp': str(Path().cwd())
        }
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def _load_triage_notes(self):
        """Load all triage notes."""
        if not os.path.exists(self.triage_folder):
            self.triage_notes = []
            return
        
        self.triage_notes = []
        for file in os.listdir(self.triage_folder):
            if file.endswith('.md'):
                note_path = os.path.join(self.triage_folder, file)
                self.triage_notes.append(note_path)
        
        # Sort for consistent ordering
        self.triage_notes.sort()
        
        # Set total notes count
        self.total_notes = len(self.triage_notes)
        
        # Ensure current index is valid
        if self.current_note_index >= len(self.triage_notes):
            self.current_note_index = 0
    
    def _setup_gui(self):
        """Setup the GUI layout."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Progress info
        self.progress_label = ttk.Label(main_frame, text="")
        self.progress_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Status info
        self.status_label = ttk.Label(main_frame, text="", foreground="gray")
        self.status_label.grid(row=0, column=2, sticky=tk.E, pady=(0, 10))
        
        # Note content frame
        content_frame = ttk.LabelFrame(main_frame, text="Note Content", padding="5")
        content_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Text widget with scrollbar
        self.text_widget = scrolledtext.ScrolledText(
            content_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=25,
            font=('Consolas', 10)
        )
        self.text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Attachment frame
        attachment_frame = ttk.LabelFrame(main_frame, text="Attachments", padding="5")
        attachment_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        attachment_frame.columnconfigure(0, weight=1)
        
        # Attachment listbox with scrollbar
        self.attachment_listbox = tk.Listbox(attachment_frame, height=4)
        self.attachment_scrollbar = ttk.Scrollbar(attachment_frame, orient=tk.VERTICAL, command=self.attachment_listbox.yview)
        self.attachment_listbox.configure(yscrollcommand=self.attachment_scrollbar.set)
        
        self.attachment_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.attachment_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click to preview attachment
        self.attachment_listbox.bind('<Double-1>', self._preview_attachment)
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        # Navigation buttons
        ttk.Button(button_frame, text="← Previous", command=self._previous_note).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Next →", command=self._next_note).pack(side=tk.LEFT, padx=(0, 10))
        
        # Action buttons
        ttk.Button(button_frame, text="Accept → Notes", command=self._accept_note, style="Success.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Discard", command=self._discard_note, style="Danger.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        # Exit button
        ttk.Button(button_frame, text="Exit", command=self._exit_application).pack(side=tk.RIGHT)
        
        # Reset progress button
        ttk.Button(button_frame, text="Reset Progress", command=self._reset_progress).pack(side=tk.RIGHT, padx=(0, 10))
        
        # Configure button styles
        style = ttk.Style()
        style.configure("Success.TButton", foreground="green")
        style.configure("Danger.TButton", foreground="red")
    
    def _update_progress_label(self):
        """Update the progress label."""
        if self.triage_notes:
            processed = self.accepted_count + self.discarded_count
            remaining = len(self.triage_notes)
            self.progress_label.config(
                text=f"Note {self.current_note_index + 1} of {len(self.triage_notes)} | "
                     f"Accepted: {self.accepted_count} | Discarded: {self.discarded_count} | "
                     f"Processed: {processed} | Remaining: {remaining}"
            )
        else:
            self.progress_label.config(text="No triage notes found")
    
    def _load_current_note(self):
        """Load the current note content."""
        if not self.triage_notes or self.current_note_index >= len(self.triage_notes):
            return
        
        note_path = self.triage_notes[self.current_note_index]
        
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Display content
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, content)
            
            # Extract and display attachments
            self._load_attachments(content, note_path)
            
            # Update progress and clear status
            self._update_progress_label()
            self.status_label.config(text="", foreground="gray")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load note: {str(e)}")
    
    def _load_attachments(self, content: str, note_path: str):
        """Load and display attachments for the current note."""
        # Clear existing attachments
        self.attachment_listbox.delete(0, tk.END)
        
        # Find attachment references in the content
        attachment_pattern = r'!\[\[attachments/([^\]]+)\]\]'
        attachments = re.findall(attachment_pattern, content)
        
        if attachments:
            for attachment in attachments:
                self.attachment_listbox.insert(tk.END, attachment)
        else:
            self.attachment_listbox.insert(tk.END, "No attachments found")
    
    def _preview_attachment(self, event):
        """Preview the selected attachment using system default viewer."""
        selection = self.attachment_listbox.curselection()
        if not selection:
            return
        
        attachment_name = self.attachment_listbox.get(selection[0])
        if attachment_name == "No attachments found":
            return
        
        # Try to find the attachment file
        attachment_path = self._find_attachment_file(attachment_name)
        
        if attachment_path and os.path.exists(attachment_path):
            try:
                # Open with system default viewer
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["open", attachment_path])
                elif sys.platform == "win32":  # Windows
                    os.startfile(attachment_path)
                else:  # Linux
                    subprocess.run(["xdg-open", attachment_path])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open attachment: {str(e)}")
        else:
            messagebox.showwarning("Warning", f"Attachment file not found: {attachment_name}")
    
    def _find_attachment_file(self, attachment_name: str) -> Optional[str]:
        """Find the full path to an attachment file."""
        # Get current note name
        current_note_path = self.triage_notes[self.current_note_index]
        note_filename = os.path.basename(current_note_path)
        note_stem = Path(note_filename).stem
        
        # Try different patterns to find the attachment folder
        # Handle various naming conventions used by the curation system
        attachment_patterns = [
            f"{note_filename.replace(' ', '_')}.resources",
            f"{note_stem.replace(' ', '_')}.resources", 
            f"{note_filename}.resources",
            f"{note_stem}.resources"
        ]
        
        # Also try to extract folder name from the attachment_name itself
        if '/' in attachment_name:
            folder_name = attachment_name.split('/')[0]
            attachment_patterns.append(folder_name)
        
        for pattern in attachment_patterns:
            # Try in preprocessed attachments first
            attachment_folder = os.path.join(self.preprocessed_attachments, pattern)
            attachment_file = os.path.join(attachment_folder, attachment_name)
            
            if os.path.exists(attachment_file):
                return attachment_file
            
            # Try in curated attachments
            attachment_folder = os.path.join(self.curated_attachments, pattern)
            attachment_file = os.path.join(attachment_folder, attachment_name)
            
            if os.path.exists(attachment_file):
                return attachment_file
        
        # If still not found, try to search for the attachment file directly
        for root, dirs, files in os.walk(self.preprocessed_attachments):
            for file in files:
                if file == os.path.basename(attachment_name):
                    return os.path.join(root, file)
        
        return None
    
    def _accept_note(self):
        """Accept the current note - move to notes folder and copy attachments."""
        if not self.triage_notes or self.current_note_index >= len(self.triage_notes):
            return
        
        current_note = self.triage_notes[self.current_note_index]
        note_filename = os.path.basename(current_note)
        destination_note = os.path.join(self.notes_folder, note_filename)
        
        try:
            # Move note to notes folder
            shutil.move(current_note, destination_note)
            
            # Copy attachments if they exist
            self._copy_attachments(note_filename)
            
            # Increment accepted count
            self.accepted_count += 1
            
            # Remove from triage list
            self.triage_notes.pop(self.current_note_index)
            
            # Adjust index if necessary
            if self.current_note_index >= len(self.triage_notes) and self.triage_notes:
                self.current_note_index = len(self.triage_notes) - 1
            elif not self.triage_notes:
                self.current_note_index = 0
            
            # Save progress
            self._save_progress()
            
            # Load next note or show completion message
            if self.triage_notes:
                self._load_current_note()
            else:
                self._show_no_notes_message()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to accept note: {str(e)}")
    
    def _discard_note(self):
        """Discard the current note - move to discarded folder."""
        if not self.triage_notes or self.current_note_index >= len(self.triage_notes):
            return
        
        current_note = self.triage_notes[self.current_note_index]
        note_filename = os.path.basename(current_note)
        destination_note = os.path.join(self.discarded_folder, note_filename)
        
        try:
            # Move note to discarded folder
            shutil.move(current_note, destination_note)
            
            # Increment discarded count
            self.discarded_count += 1
            
            # Remove from triage list
            self.triage_notes.pop(self.current_note_index)
            
            # Adjust index if necessary
            if self.current_note_index >= len(self.triage_notes) and self.triage_notes:
                self.current_note_index = len(self.triage_notes) - 1
            elif not self.triage_notes:
                self.current_note_index = 0
            
            # Save progress
            self._save_progress()
            
            # Load next note or show completion message
            if self.triage_notes:
                self._load_current_note()
            else:
                self._show_no_notes_message()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to discard note: {str(e)}")
    
    def _copy_attachments(self, note_filename: str):
        """Copy attachments for the given note from preprocessed to curated."""
        try:
            note_stem = Path(note_filename).stem
            
            # Try different patterns to find source attachments
            # Handle various naming conventions used by the curation system
            attachment_patterns = [
                f"{note_filename.replace(' ', '_')}.resources",
                f"{note_stem.replace(' ', '_')}.resources", 
                f"{note_filename}.resources",
                f"{note_stem}.resources"
            ]
            
            # Also try to find by searching for folders that contain the note name
            for folder_name in os.listdir(self.preprocessed_attachments):
                if folder_name.endswith('.resources') and note_stem in folder_name:
                    attachment_patterns.append(folder_name)
            
            # Remove duplicates while preserving order
            attachment_patterns = list(dict.fromkeys(attachment_patterns))
            
            for pattern in attachment_patterns:
                source_folder = os.path.join(self.preprocessed_attachments, pattern)
                
                if os.path.exists(source_folder):
                    # Create destination folder
                    dest_folder = os.path.join(self.curated_attachments, pattern)
                    
                    if os.path.exists(dest_folder):
                        shutil.rmtree(dest_folder)
                    
                    shutil.copytree(source_folder, dest_folder)
                    self.status_label.config(text="✓ Attachments copied", foreground="green")
                    print(f"✓ Copied attachments: {pattern}")
                    return
            
            self.status_label.config(text="⚠ No attachments found", foreground="orange")
            print(f"⚠ No attachments found for note: {note_filename}")
            print(f"   Searched patterns: {attachment_patterns}")
            print(f"   Available folders: {[f for f in os.listdir(self.preprocessed_attachments) if f.endswith('.resources')][:5]}...")
        
        except Exception as e:
            self.status_label.config(text="⚠ Copy failed", foreground="red")
            print(f"Error copying attachments: {str(e)}")
    
    def _previous_note(self):
        """Go to previous note."""
        if self.triage_notes and self.current_note_index > 0:
            self.current_note_index -= 1
            self._save_progress()
            self._load_current_note()
    
    def _next_note(self):
        """Go to next note."""
        if self.triage_notes and self.current_note_index < len(self.triage_notes) - 1:
            self.current_note_index += 1
            self._save_progress()
            self._load_current_note()
    
    def _show_no_notes_message(self):
        """Show message when no triage notes are available."""
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, "No triage notes available for processing.")
        self.attachment_listbox.delete(0, tk.END)
        self.attachment_listbox.insert(tk.END, "No attachments")
        self.progress_label.config(text="No triage notes found")
    
    def _reset_progress(self):
        """Reset progress to start from the beginning."""
        if messagebox.askyesno("Reset Progress", "Are you sure you want to reset progress and start from the first note?"):
            self.current_note_index = 0
            self.accepted_count = 0
            self.discarded_count = 0
            self._save_progress()
            self._load_current_note()
            messagebox.showinfo("Progress Reset", "Progress has been reset. Starting from the first note.")
    
    def _exit_application(self):
        """Exit the application."""
        self._save_progress()
        self.root.quit()


def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = TriageGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
