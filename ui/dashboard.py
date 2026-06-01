"""
Main dashboard window for Liberty Express
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTextEdit, QStatusBar,
    QProgressBar, QMessageBox, QFileDialog, QDialog, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from core.workers import ExtractionWorker, FileSaveWorker
from core.content_manager import ContentManager
from core.models import LinkItem
from utils.config import load_config

class DashboardWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or load_config()
        self.content_manager = ContentManager(self.config)
        self.workers = []
        self.output_dir = self.config.get('output_directory', 'output')
        
        # Export tracking
        self.pending_exports = 0
        self.export_success = 0
        
        # HTML data storage
        self.html_data = ""
        self.json_data = {}
        self.csv_data = []
        
        self.setup_ui()
        self.setup_timers()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Liberty Express - Content Extractor")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # URL input section
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Target URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        url_layout.addWidget(self.url_input)
        
        self.fetch_btn = QPushButton("Fetch & Extract")
        self.fetch_btn.clicked.connect(self.generate_content_hub)
        url_layout.addWidget(self.fetch_btn)
        
        main_layout.addLayout(url_layout)
        
        # Progress section
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        # Export buttons
        export_layout = QHBoxLayout()
        self.export_html_btn = QPushButton("Export HTML")
        self.export_html_btn.clicked.connect(lambda: self.export_format('html'))
        self.export_html_btn.setEnabled(False)
        
        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.clicked.connect(lambda: self.export_format('json'))
        self.export_json_btn.setEnabled(False)
        
        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(lambda: self.export_format('csv'))
        self.export_csv_btn.setEnabled(False)
        
        self.export_all_btn = QPushButton("Export All Formats")
        self.export_all_btn.clicked.connect(self.export_all_formats)
        self.export_all_btn.setEnabled(False)
        
        export_layout.addWidget(self.export_html_btn)
        export_layout.addWidget(self.export_json_btn)
        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.export_all_btn)
        main_layout.addLayout(export_layout)
        
        # View content button
        view_btn = QPushButton("View Content Library")
        view_btn.clicked.connect(self.view_content_library)
        main_layout.addWidget(view_btn)
        
        # Stop button
        self.stop_btn = QPushButton("Stop Processing")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        main_layout.addWidget(self.stop_btn)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
    def setup_timers(self):
        """Setup UI timers for updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(500)
        
    def generate_content_hub(self):
        """Start content extraction"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL")
            return
            
        # Disable controls during extraction
        self.fetch_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Create and start worker
        worker = ExtractionWorker(url, self.content_manager, self.config)
        worker.finished.connect(self.on_extraction_finished)
        worker.progress.connect(self.on_extraction_progress)
        worker.error.connect(self.on_extraction_error)
        
        self.workers.append(worker)
        worker.start()
        
    def on_extraction_finished(self, items, html_content, json_data, csv_data):
        """Handle extraction completion"""
        self.html_data = html_content
        self.json_data = json_data
        self.csv_data = csv_data
        
        # Enable export buttons
        self.export_html_btn.setEnabled(True)
        self.export_json_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)
        self.export_all_btn.setEnabled(True)
        
        self.statusBar.showMessage(f"Extracted {len(items)} items", 3000)
        self.reset_ui_state()
        
    def on_extraction_progress(self, message):
        """Handle extraction progress updates"""
        self.status_label.setText(message)
        
    def on_extraction_error(self, error_msg):
        """Handle extraction errors"""
        QMessageBox.critical(self, "Extraction Error", error_msg)
        self.reset_ui_state()
        
    def export_format(self, format_type):
        """Export a single format"""
        worker = FileSaveWorker(self.output_dir, format_type, 
                               self._get_format_data(format_type))
        worker.finished.connect(self.on_export_finished)
        self.workers.append(worker)
        worker.start()
        
    def export_all_formats(self):
        """Export all formats with proper tracking"""
        self.pending_exports = 3
        self.export_success = 0
        self.statusBar.showMessage("Exporting all formats...")
        
        formats = ['html', 'json', 'csv']
        for fmt in formats:
            worker = FileSaveWorker(self.output_dir, fmt, 
                                   self._get_format_data(fmt))
            worker.finished.connect(self.on_export_finished)
            self.workers.append(worker)
            worker.start()
            
    def on_export_finished(self, success, file_type):
        """Handle individual export completion"""
        self.pending_exports -= 1
        if success:
            self.export_success += 1
            self.statusBar.showMessage(f"Exported {file_type} successfully", 2000)
        else:
            self.statusBar.showMessage(f"Failed to export {file_type}", 2000)
            
        if self.pending_exports == 0:
            if self.export_success == 3:
                QMessageBox.information(self, "Export Complete", 
                    "All exports completed successfully!")
            else:
                QMessageBox.warning(self, "Export Partial", 
                    f"Exported {self.export_success}/3 formats successfully.\n"
                    "Check logs for details.")
                    
    def view_content_library(self):
        """Display content library in proper multi-line widget"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Content Library")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        json_path = os.path.join(self.output_dir, "content.json")
        try:
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                formatted = json.dumps(data, indent=2)
                text_edit.setPlainText(formatted)
        except Exception as e:
            text_edit.setPlainText(f"Error loading content: {e}")
            
        layout.addWidget(text_edit)
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(text_edit.toPlainText()))
        layout.addWidget(copy_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def stop_processing(self):
        """Stop all running workers"""
        for worker in self.workers:
            if worker.isRunning():
                if hasattr(worker, 'stop'):
                    worker.stop()
                else:
                    worker.wait(5000)
        self.statusBar.showMessage("Stopping...", 2000)
        self.reset_ui_state()
        
    def reset_ui_state(self):
        """Reset UI controls after operation"""
        self.fetch_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        
    def update_status(self):
        """Update status bar with worker info"""
        if self.workers:
            running = sum(1 for w in self.workers if w.isRunning())
            if running > 0:
                self.statusBar.showMessage(f"Active workers: {running}")
                
    def _get_format_data(self, format_type):
        """Get data for specific export format"""
        if format_type == 'html':
            return self.html_data
        elif format_type == 'json':
            return self.json_data
        elif format_type == 'csv':
            return self.csv_data
        return None
