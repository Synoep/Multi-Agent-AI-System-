import logging
import sys
import os
from datetime import datetime

def setup_logger(name=None, level=logging.INFO):
    """
    Set up a logger with the specified name and level.
    
    Args:
        name (str, optional): The logger name
        level (int, optional): The logging level
        
    Returns:
        logging.Logger: The configured logger
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Get logger
    logger_name = name if name else "main"
    logger = logging.getLogger(logger_name)
    
    # Only configure if it hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(level)
        
        # Create formatters
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        
        # Create file handler
        log_filename = f"logs/{logger_name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)
        
        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger