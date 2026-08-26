"""
QThread workers for background processing
"""

from PySide6.QtCore import QThread, pyqtSignal
import threading
import logging
import json
import csv
import os
from datetime import datetime

from core.extractor import LinkExtractor
from core.content_manager import ContentManager
from utils.file_utils import safe_file_write, FileLock

logger = logging.getLogger(__name__)

class ExtractionWorker(QThread):
    """Worker thread for content extraction"""
    
    finished = pyqtSignal(list, str, dict, list)  # items, html, json, csv
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, url, content_manager, config):
        super().__init__()
        self.url = url
        self.content_manager = content_manager
        self.config = config
        self._stop_event = threading.Event()
        self.extractor = LinkExtractor(config)
        
    def stop(self):
        """Request worker to stop"""
        self._stop_event.set()
        
    @property
    def is_running(self):
        """Check if worker should continue running"""
        return not self._stop_event.is_set()
        
    def run(self):
        """Main extraction logic"""
        try:
            self.progress.emit(f"Fetching {self.url}...")
            
            # Fetch HTML content
            html_content = self.extractor.fetch_url(self.url)
            if not self.is_running:
                return
                
            # Extract links
            self.progress.emit("Extracting links...")
            items = self.extractor.extract_links(self.url, html_content)
            
            if not self.is_running:
                return
                
            # Classify items
            self.progress.emit("Classifying content...")
            self.content_manager.organize_items(items)
            
            # Generate outputs
            self.progress.emit("Generating outputs...")
            html_output = self._generate_html_output()
            json_output = self._generate_json_output(items)
            csv_output = self._generate_csv_output(items)
            
            self.finished.emit(items, html_output, json_output, csv_output)
            
        except Exception as e:
            logger.exception("Extraction failed")
            self.error.emit(str(e))
            
    def _generate_html_output(self):
        """Generate HTML output from classified content"""
        sections = self.content_manager.get_sections_snapshot()
        
        html_parts = ['<!DOCTYPE html><html><head><meta charset="UTF-8">']
        html_parts.append('<title>Content Hub</title>')
        html_parts.append('<style>body{font-family:Arial;margin:20px}')
        html_parts.append('.section{margin-bottom:30px}')
        html_parts.append('.item{margin:10px 0;padding:10px;background:#f5f5f5}')
        html_parts.append('</style></head><body>')
        html_parts.append('<h1>Content Hub</h1>')
        
        for content_type, items in sections.items():
            if items:
                html_parts.append(f'<div class="section">')
                html_parts.append(f'<h2>{content_type.value.title()}</h2>')
                for item in items:
                    html_parts.append(f'<div class="item">')
                    html_parts.append(f'<a href="{item.url}">{item.title}</a>')
                    if item.description:
                        html_parts.append(f'<p>{item.description}</p>')
                    html_parts.append('</div>')
                html_parts.append('</div>')
                
        html_parts.append('</body></html>')
        return '\n'.join(html_parts)
        
    def _generate_json_output(self, items):
        """Generate JSON output"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'source_url': self.url,
            'total_items': len(items),
            'items': [
                {
                    'title': item.title,
                    'url': item.url,
                    'description': item.description,
                    'type': item.content_type.value
                }
                for item in items
            ]
        }
        return output
        
    def _generate_csv_output(self, items):
        """Generate CSV data"""
        return [
            {
                'title': item.title,
                'url': item.url,
                'description': item.description,
                'type': item.content_type.value
            }
            for item in items
        ]

class FileSaveWorker(QThread):
    """Worker thread for saving files"""
    
    finished = pyqtSignal(bool, str)  # success, file_type
    
    def __init__(self, output_dir, file_type, data):
        super().__init__()
        self.output_dir = output_dir
        self.file_type = file_type
        self.data = data
        self._is_running = True
        
    def stop(self):
        """Stop the worker (non-blocking)"""
        self._is_running = False
        self.wait(5000)
        
    def run(self):
        """Save file based on type"""
        try:
            if not self._is_running:
                self.finished.emit(False, self.file_type)
                return
                
            os.makedirs(self.output_dir, exist_ok=True)
            
            if self.file_type == 'html':
                success = self._save_html()
            elif self.file_type == 'json':
                success = self._save_json()
            elif self.file_type == 'csv':
                success = self._save_csv()
            else:
                logger.error(f"Unknown file type: {self.file_type}")
                success = False
                
            self.finished.emit(success, self.file_type)
            
        except Exception as e:
            logger.exception(f"Failed to save {self.file_type}")
            self.finished.emit(False, self.file_type)
            
    def _save_html(self):
        """Save HTML file with locking"""
        filepath = os.path.join(self.output_dir, "content.html")
        return safe_file_write(filepath, self.data)
        
    def _save_json(self):
        """Save JSON file with locking"""
        filepath = os.path.join(self.output_dir, "content.json")
        content = json.dumps(self.data, indent=2, ensure_ascii=False)
        return safe_file_write(filepath, content)
        
    def _save_csv(self):
        """Save CSV file with locking"""
        filepath = os.path.join(self.output_dir, "content.csv")
        lock = FileLock(filepath + ".lock")
        
        try:
            with lock:
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    if self.data:
                        fieldnames = self.data[0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(self.data)
                return True
        except Exception as e:
            logger.error(f"Failed to write CSV: {e}")
            return False
