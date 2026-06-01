#!/usr/bin/env python3
"""
Liberty Express - Web Content Extractor and Organizer
Entry point for the application
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add parent directory to path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.dashboard import DashboardWindow
from utils.logging_setup import setup_logging
from utils.config import load_config

def main():
    """Main application entry point"""
    # Setup logging first
    setup_logging()
    
    # Load configuration
    config = load_config()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    # Set application metadata
    app.setApplicationName("Liberty Express")
    app.setOrganizationName("ContentHub")
    
    # Create and show main window
    window = DashboardWindow(config)
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
