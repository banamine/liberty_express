#!/usr/bin/env python3
"""
Liberty Express - Web Content Extractor and Organizer
Entry point for the application
"""

import sys
import os
import traceback

# Only add to path when running directly without installation
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from ui.dashboard import DashboardWindow
from utils.logging_setup import setup_logging
from utils.config import load_config


def check_write_permission(directory="."):
    """Check if the working directory is writable"""
    test_file = os.path.join(directory, ".write_test_temp")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except (IOError, OSError):
        return False


def show_fatal_error(error_details):
    """Display fatal error dialog before exiting"""
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Fatal Error")
        msg.setText("The application encountered a fatal error and must close.")
        msg.setInformativeText("Please check the logs for more information.")
        msg.setDetailedText(error_details)
        msg.exec()
    except Exception:
        print("FATAL ERROR:", file=sys.stderr)
        print(error_details, file=sys.stderr)


def main():
    """Main application entry point"""
    try:
        setup_logging()
        
        if not check_write_permission():
            print("ERROR: Current working directory is not writable.", file=sys.stderr)
            try:
                app = QApplication(sys.argv)
                QMessageBox.critical(
                    None,
                    "Permission Error",
                    "The application cannot write to the current directory."
                )
            except Exception:
                pass
            sys.exit(1)
        
        config = load_config()
        app = QApplication(sys.argv)
        app.setApplicationName("Liberty Express")
        app.setOrganizationName("ContentHub")
        app.setApplicationVersion("2.0.0")
        
        window = DashboardWindow(config)
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        error_details = traceback.format_exc()
        try:
            import logging
            logging.getLogger(__name__).critical(f"Fatal error: {error_details}")
        except Exception:
            print(f"FATAL ERROR: {error_details}", file=sys.stderr)
        
        show_fatal_error(error_details)
        sys.exit(1)


if __name__ == "__main__":
    main()
