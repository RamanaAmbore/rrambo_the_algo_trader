import logging
import os

from utils.config_loader import Env

# Create logs directory if not exists
os.makedirs(os.path.dirname(Env.DEBUG_LOG_FILE), exist_ok=True)

logger = None


def get_logger(name="app_logger"):
    """Returns a configured logger instance."""
    global logger
    if logger is not None:
        return logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture all logs, control output using handlers

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Console Handler (prints logs to console)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, Env.CONSOLE_LOG_LEVEL.upper(), logging.DEBUG))
    console_handler.setFormatter(formatter)

    # Debug Log File Handler (stores DEBUG and above logs)
    debug_file_handler = logging.FileHandler(Env.DEBUG_LOG_FILE)
    debug_file_handler.setLevel(getattr(logging, Env.FILE_LOG_LEVEL.upper(), logging.DEBUG))
    debug_file_handler.setFormatter(formatter)

    # Error Log File Handler (stores only ERROR logs)
    error_file_handler = logging.FileHandler(Env.ERROR_LOG_FILE)
    error_file_handler.setLevel(getattr(logging, Env.ERROR_LOG_LEVEL.upper(), logging.ERROR))
    error_file_handler.setFormatter(formatter)

    # Add handlers to logger
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(debug_file_handler)
        logger.addHandler(error_file_handler)

    return logger


# Example usage
if __name__ == "__main__":
    logger = get_logger("test_logger")
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
