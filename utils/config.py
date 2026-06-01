"""
Configuration management with validation
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "output_directory": "output",
    "timeout": 10,
    "retries": 3,
    "max_items": 100,
    "extraction": {
        "main_ul_selector": "ul:has(> li > a)",
        "max_links_per_page": 50
    },
    "classification": {
        "priority": {
            "live_tv": 10,
            "news": 20,
            "video": 30,
            "article": 40
        },
        "categories": {
            "live_tv": ["live", "tv", "stream", "watch now"],
            "news": ["news", "breaking", "headline", "update"],
            "video": ["video", "watch", "play", "episode"],
            "article": ["article", "blog", "post", "story"]
        }
    }
}

def validate_config(config):
    """Validate config values with type checking"""
    # Required numeric fields
    validations = {
        'timeout': (int, lambda x: x > 0),
        'retries': (int, lambda x: x >= 0),
        'max_items': (int, lambda x: x > 0),
    }
    
    for key, (type_func, validator) in validations.items():
        if key in config:
            if not isinstance(config[key], type_func):
                logger.warning(f"Config '{key}' must be {type_func.__name__}, "
                             f"got {type(config[key]).__name__}, using default")
                config.pop(key)
            elif not validator(config[key]):
                logger.warning(f"Config '{key}' value {config[key]} invalid, using default")
                config.pop(key)
    
    return config

def merge_configs(default_config, user_config):
    """Deep merge user config into default config"""
    merged = default_config.copy()
    
    for key, value in user_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key].update(value)
        else:
            merged[key] = value
            
    return merged

def load_config(config_path="config.json"):
    """Load configuration from file with validation"""
    config = DEFAULT_CONFIG.copy()
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                config = merge_configs(config, user_config)
                config = validate_config(config)
                logger.info(f"Loaded config from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
    else:
        logger.info(f"No config file found at {config_path}, using defaults")
        
    # Ensure output directory exists
    os.makedirs(config['output_directory'], exist_ok=True)
    
    return config
