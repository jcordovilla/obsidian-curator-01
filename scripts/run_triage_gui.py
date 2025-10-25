#!/usr/bin/env python3
"""
Launcher script for the Triage GUI.

This script sets up the environment and launches the triage GUI application.
"""

import sys
import os

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get project root (parent of scripts/)
project_root = os.path.dirname(script_dir)

# Get venv Python path
venv_python = os.path.join(project_root, 'venv', 'bin', 'python3')

# Check if venv exists
if not os.path.exists(venv_python):
    print("ERROR: Virtual environment not found!")
    print(f"Expected venv at: {os.path.join(project_root, 'venv')}")
    print("\nPlease create the virtual environment first:")
    print("  python3 -m venv venv")
    print("  source venv/bin/activate")
    print("  pip install -r requirements.txt")
    sys.exit(1)

# If we're not already using venv Python, restart with venv Python
current_python = sys.executable
if not venv_python in current_python and not project_root in current_python:
    print(f"Activating venv Python: {venv_python}")
    os.execv(venv_python, [venv_python] + sys.argv)

# Add the project root to Python path
sys.path.insert(0, project_root)

# Print environment info
print(f"✓ Python: {sys.executable}")
print(f"✓ Working in venv: {project_root}/venv")

# Import and run the GUI
from scripts.triage_gui import main

if __name__ == "__main__":
    main()
