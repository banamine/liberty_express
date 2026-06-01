"""
Data models for Liberty Express
"""

from enum import Enum
import hashlib

class ContentType(Enum):
    """Content category types"""
    ARTICLE = "article"
    LIVE_TV = "live_tv"
    NEWS = "news"
    VIDEO = "video"
    OTHER = "other"
    
    @classmethod
    def from_string(cls, value):
        """Create ContentType from string value"""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.OTHER

class LinkItem:
    """Represents a single extracted link with metadata"""
    
    def __init__(self, title, url, description=""):
        self.title = title
        self.url = url
        self.description = description
        self.content_type = ContentType.OTHER
        # Explicitly mark as not for security
        self.item_id = hashlib.md5(
            f"{title}{url}".encode(),
            usedforsecurity=False
        ).hexdigest()[:8]
        
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.item_id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'type': self.content_type.value
        }
        
    def __repr__(self):
        return f"LinkItem(title='{self.title}', url='{self.url}')"
