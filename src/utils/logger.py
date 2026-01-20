"""Logging configuration utilities"""

import logging


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Setup and configure a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)
