"""
Logging configuration with fallback
"""

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_dir="logs", log_file="liberty_express.log"):
    """Setup logging with file rotation and console output"""
    
    # Create log directory if possible
    try:
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, log_file)
        
        # Configure file handler
        file_handler = RotatingFileHandler(
            log_path, 
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        # Configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(
            logging.Formatter('%(levelname)s: %(message)s')
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        logging.info("Logging initialized successfully")
        
    except Exception as e:
        # Fallback to console-only logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s'
        )
        logging.warning(f"Could not set up file logging: {e
