import logging
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def setup_logger(name: str) -> logging.Logger:
    """Sets up a standardized logger for the project."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
