"""
UI resources (styles, icons, etc.)
"""

def get_default_stylesheet():
    """Return default application stylesheet"""
    return """
    QMainWindow {
        background-color: #2b2b2b;
    }
    QPushButton {
        background-color: #3c3c3c;
        color: #ffffff;
        border: 1px solid #555;
        padding: 5px;
        border-radius: 3px;
    }
    QPushButton:hover {
        background-color: #4a4a4a;
    }
    QPushButton:pressed {
        background-color: #2a2a2a;
    }
    QPushButton:disabled {
        background-color: #2a2a2a;
        color: #666;
    }
    QLineEdit {
        background-color: #3c3c3c;
        color: #ffffff;
        border: 1px solid #555;
        padding: 4px;
        border-radius: 3px;
    }
    QLabel {
        color: #ffffff;
    }
    QProgressBar {
        border: 1px solid #555;
        border-radius: 3px;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: #4c9c4c;
        border-radius: 2px;
    }
    """
