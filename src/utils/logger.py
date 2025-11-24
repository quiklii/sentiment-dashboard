# src/utils/logger.py

import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

def _configure_root_logger():
    """Configure the root logger to log messages to a file with rotation."""
    logger = logging.getLogger('sentiment_dashboard')
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # --- FILE HANDLER ---
    file_handler = RotatingFileHandler(
        LOG_DIR / 'app.log',
        maxBytes=5_000_000, # 5 MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s | %(filename)s | %(levelname)s] : %(message)s",
        "%Y-%m-%d %H:%M:%S"
    ))
    
    # --- STREAM HANDLER (console) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "[%(asctime)s | %(levelname)s] : %(message)s",
        "%Y-%m-%d %H:%M:%S"
    ))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# --- public function ---
def get_logger(name: str = 'None'):
    root_logger = _configure_root_logger()
    return root_logger.getChild(name) if name else root_logger
        