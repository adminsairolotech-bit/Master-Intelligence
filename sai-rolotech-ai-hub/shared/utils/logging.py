"""
Shared Logging Utility
"""

import logging
import os
from datetime import datetime

LOG_DIR = "./logs"
LOG_FILE = os.path.join(LOG_DIR, "ai-hub.log")


def setup_logger(name: str = "sairolotech") -> logging.Logger:
    """Setup logger with file and console output"""
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    # File handler
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def log_action(user_id: int, action: str, tool: str, payload: str = ""):
    """Log user action"""
    logger = setup_logger()
    logger.info(f"USER:{user_id} | ACTION:{action} | TOOL:{tool} | {payload}")


def log_error(user_id: int, error: str, context: str = ""):
    """Log error"""
    logger = setup_logger()
    logger.error(f"USER:{user_id} | ERROR:{error} | CONTEXT:{context}")


# Default logger
log = setup_logger()
