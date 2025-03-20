import logging
import os
import queue
from logging.handlers import QueueHandler, QueueListener
from src.settings.parameter_manager import parms as Parm

# Ensure log directory exists
os.makedirs(os.path.dirname(Parm.DEBUG_LOG_FILE), exist_ok=True)

# Global log queue
log_queue = queue.Queue()

# Formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# File Handlers
debug_file_handler = logging.FileHandler(Parm.DEBUG_LOG_FILE)
debug_file_handler.setLevel(getattr(logging, Parm.FILE_LOG_LEVEL.upper(), Parm.FILE_LOG_LEVEL))
debug_file_handler.setFormatter(formatter)

error_file_handler = logging.FileHandler(Parm.ERROR_LOG_FILE)
error_file_handler.setLevel(getattr(logging, Parm.ERROR_LOG_LEVEL.upper(), Parm.ERROR_LOG_FILE))
error_file_handler.setFormatter(formatter)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, Parm.CONSOLE_LOG_LEVEL.upper(), Parm.CONSOLE_LOG_LEVEL))
console_handler.setFormatter(formatter)

# Queue Listener (Processes Logs from Queue)
queue_listener = QueueListener(log_queue, console_handler, debug_file_handler, error_file_handler,
                               respect_handler_level=True)
queue_listener.start()


def get_logger(name="app_logger"):
    """Returns a configured logger instance with a queue handler."""
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Prevent duplicate handlers
        logger.setLevel(logging.DEBUG)
        queue_handler = QueueHandler(log_queue)
        logger.addHandler(queue_handler)
    return logger


# Graceful shutdown of the queue listener
def shutdown_logger():
    queue_listener.stop()


# Example usage
if __name__ == "__main__":
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")

    logger1.debug("Module 1 - Debug message")
    logger2.info("Module 2 - Info message")
    logger1.warning("Module 1 - Warning message")
    logger2.error("Module 2 - Error message")

    shutdown_logger()
