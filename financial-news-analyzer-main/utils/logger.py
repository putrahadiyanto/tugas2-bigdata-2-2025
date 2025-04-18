import logging
import sys
from config import LOG_LEVEL, LOG_FORMAT

def setup_logger(name="financial_news_analyzer"):
    logger = logging.getLogger(name)
    
    # Set log level from config
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Create handler for console output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    
    # Avoid duplicate log messages
    logger.propagate = False
    
    return logger

# Application-wide logger instance
logger = setup_logger()