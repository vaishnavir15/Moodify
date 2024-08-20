import logging
import sys
import os

def configure_logging():
    # Create a logger
    logger = logging.getLogger(__name__)
    
    # Check if the logger already has handlers to avoid duplicate logs
    if not logger.hasHandlers():
        # Set the logging level from an environment variable (default to DEBUG)
        log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
        logger.setLevel(log_level)

        # Create a console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(log_level)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        # Add the console handler to the logger
        logger.addHandler(ch)

    return logger

# Configure the logger
logger = configure_logging()

# Example usage
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")


def get_logger():
    return logger
