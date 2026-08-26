"""
File handling utilities with locking
"""

import os
import logging
from PySide6.QtCore import QLockFile

logger = logging.getLogger(__name__)

class FileLock:
    """Context manager for file locking using QLockFile"""
    
    def __init__(self, lock_path):
        self.lock_path = lock_path
        self.lock_file = QLockFile(lock_path)
        
    def __enter__(self):
        """Acquire the lock"""
        if not self.lock_file.tryLock(5000):  # 5 second timeout
            raise IOError(f"Could not acquire lock for {self.lock_path}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release the lock"""
        self.lock_file.unlock()

def safe_file_write(filepath, content, encoding='utf-8'):
    """Safely write content to file with locking"""
    lock_path = filepath + ".lock"
    temp_path = filepath + ".tmp"
    
    try:
        with FileLock(lock_path):
            # Write to temporary file first
            with open(temp_path, 'w', encoding=encoding) as f:
                f.write(content)
                
            # Atomic rename (works on Unix, may not be atomic on Windows)
            os.replace(temp_path, filepath)
            
        logger.info(f"Successfully wrote {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write {filepath}: {e}")
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return False
        
def ensure_directory(directory):
    """Ensure directory exists, create if needed"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False
        
def is_writable(directory):
    """Check if directory is writable"""
    try:
        test_file = os.path.join(directory, ".write_test")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except:
        return False
