"""
Custom dialog windows for Liberty Express
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QApplication
from PyQt6.QtCore import Qt

class ContentViewerDialog(QDialog):
    """Dialog for viewing content with copy capability"""
    
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(content)
        layout.addWidget(self.text_edit)
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(copy_btn)
        
        self.setLayout(layout)
        
    def copy_to_clipboard(self):
        """Copy content to clipboard"""
        QApplication.clipboard().setText(self.text_edit.toPlainText())
        
class ProgressDialog(QDialog):
    """Dialog showing long operation progress"""
    
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing")
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.addWidget(QTextEdit(message))
        self.setLayout(layout)
