import logging
from datetime import datetime
import os

def setup_logger():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')
    except Exception as e:
        print(f"Warning: Could not create logs directory: {str(e)}")
        return logging.getLogger('crypto_bot')

    # Create logger
    logger = logging.getLogger('crypto_bot')
    logger.setLevel(logging.INFO)

    # Create file handler
    try:
        log_file = f"logs/crypto_bot_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {str(e)}")
        # Add only console handler if file handling fails
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger