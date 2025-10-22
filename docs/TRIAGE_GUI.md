# Triage GUI

A graphical user interface for manually processing notes from the triage folder in the Obsidian Curator system.

## Features

- **Note Preview**: View triage notes with full content and scrollable text
- **Attachment Management**: Preview attachments using system default viewer
- **Accept/Discard Actions**: 
  - Accept: Move note to curated notes folder and copy attachments
  - Discard: Move note to discarded folder
- **Progress Tracking**: Remembers where you left off between sessions
- **Navigation**: Previous/Next buttons to browse through notes

## Usage

### Running the GUI

```bash
# From the project root
python scripts/run_triage_gui.py

# Or run the GUI directly
python scripts/triage_gui.py
```

### GUI Controls

1. **Note Content**: The main text area shows the full content of the current triage note
2. **Attachments**: List of attachments referenced in the note
   - Double-click an attachment to preview it using your system's default viewer
3. **Navigation**:
   - **← Previous**: Go to the previous note
   - **Next →**: Go to the next note
4. **Actions**:
   - **Accept → Notes**: Move the note to the curated notes folder and copy its attachments
   - **Discard**: Move the note to the discarded folder
   - **Exit**: Save progress and close the application

### Progress Tracking

The GUI automatically saves your progress in `.triage_progress.json` in the curated vault folder. When you restart the application, it will resume from where you left off.

### Folder Structure

The GUI works with the following folder structure:

```
Ever-curated/
├── triage/          # Notes awaiting manual review
├── notes/           # Accepted notes (high-value content)
├── discarded/       # Discarded notes
└── attachments/     # Copied attachments for curated notes
```

### Attachment Handling

- Attachments are automatically copied from the preprocessed vault when you accept a note
- The GUI supports various attachment naming patterns used by the curation system
- Double-click any attachment in the list to preview it with your system's default application

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- Access to the Obsidian vault folders as configured in `config.py`

## Troubleshooting

### No Triage Notes Found
- Ensure the triage folder exists: `/Users/jose/obsidian/Ever-curated/triage`
- Run the curation pipeline to generate triage notes: `python -m src.curation.obsidian_curator.main`

### Attachment Preview Not Working
- Check that the attachment files exist in the preprocessed attachments folder
- Ensure your system has default applications configured for the file types

### Permission Errors
- Ensure you have read/write permissions to the curated vault folders
- Check that the folders exist and are accessible

## Integration with Curation Pipeline

This GUI is designed to work with the existing Obsidian Curator pipeline:

1. **Preprocessing**: `python scripts/preprocess.py` - cleans and standardizes notes
2. **Curation**: `python -m src.curation.obsidian_curator.main` - AI analysis and scoring
3. **Manual Triage**: `python run_triage_gui.py` - manual review of medium-value notes

The triage GUI processes notes that received scores between 0.25-0.45 (the "gray zone" requiring manual review).
