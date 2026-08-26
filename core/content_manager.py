"""
Content classification and organization logic
"""

from enum import Enum
from PySide6.QtCore import QReadWriteLock, QWriteLocker, QReadLocker
import logging

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content category types"""
    ARTICLE = "article"
    LIVE_TV = "live_tv"
    NEWS = "news"
    VIDEO = "video"
    OTHER = "other"

class LinkItem:
    """Represents a single extracted link with metadata"""
    
    def __init__(self, title, url, description=""):
        self.title = title
        self.url = url
        self.description = description
        self.content_type = ContentType.OTHER
        
class ContentManager:
    """Manages content classification and organization with thread safety"""
    
    def __init__(self, config):
        self.config = config
        self.lock = QReadWriteLock()
        self._sections = {}
        self.classification_rules = self._build_priority_rules()
        self._init_sections()
        
    def _build_priority_rules(self):
        """Build rules with explicit priority order"""
        rules = []
        categories = self.config.get('classification', {}).get('categories', {})
        priorities = self.config.get('classification', {}).get('priority', {})
        
        for content_type, keywords in categories.items():
            try:
                ct = ContentType[content_type.upper()]
                priority = priorities.get(content_type, 50)
                rules.append((ct, keywords, priority))
            except KeyError:
                logger.warning(f"Unknown content type: {content_type}")
                
        # Sort by priority (lower number = higher priority)
        rules.sort(key=lambda x: x[2])
        return [(ct, keywords) for ct, keywords, _ in rules]
        
    def _init_sections(self):
        """Initialize sections under write lock"""
        with QWriteLocker(self.lock):
            self._sections = {
                ContentType.ARTICLE: [],
                ContentType.LIVE_TV: [],
                ContentType.NEWS: [],
                ContentType.VIDEO: [],
                ContentType.OTHER: []
            }
            
    def classify_item(self, item):
        """Classify a single item using priority rules"""
        combined = f"{item.title} {item.description}".lower()
        
        for content_type, keywords in self.classification_rules:
            for keyword in keywords:
                if keyword.lower() in combined:
                    item.content_type = content_type
                    return content_type
                    
        item.content_type = ContentType.OTHER
        return ContentType.OTHER
        
    def organize_items(self, items):
        """Thread-safe organization of items into sections"""
        with QWriteLocker(self.lock):
            # Reset sections
            for key in self._sections:
                self._sections[key] = []
                
            # Classify and organize
            for item in items:
                category = self.classify_item(item)
                self._sections[category].append(item)
                
    def get_sections_snapshot(self):
        """Return a thread-safe copy of current sections"""
        with QReadLocker(self.lock):
            return {k: v.copy() for k, v in self._sections.items()}
            
    def get_items_by_type(self, content_type):
        """Get items of a specific type"""
        with QReadLocker(self.lock):
            return self._sections.get(content_type, []).copy()
