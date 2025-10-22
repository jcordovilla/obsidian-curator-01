#!/usr/bin/env python3
"""
Launcher script for the Triage GUI.

This script sets up the environment and launches the triage GUI application.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the GUI
from scripts.triage_gui import main

if __name__ == "__main__":
    main()
