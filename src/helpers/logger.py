import logging
import os
import queue
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from src.settings.parameter_manager import parms as parm
from twilio.rest import Client

def send_twilio_alert(message):
    """Sends an alert via Twilio if an error occurs and TWILIO_ALERT is enabled."""
    if not parm.TWILIO_ALERT:
        return
    try:
        client = Client(parm.TWILIO_ACCOUNT_SID, parm.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=f'{parm.TWILIO_FROM_NUMBER}',
            to=f'{parm.TWILIO_TO_NUMBER}'
        )
    except Exception as e:
        print(f"Failed to send Twilio alert: {e}")

# Ensure log directory exists
os.makedirs(os.path.dirname(parm.FILE_LOG_FILE), exist_ok=True)

# Global log queue
log_queue = queue.Queue()

# Formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Rotating File Handlers
log_file_handler = RotatingFileHandler(
    parm.FILE_LOG_FILE,
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=5
)
log_file_handler.setLevel(getattr(logging, parm.FILE_LOG_LEVEL.upper(), parm.FILE_LOG_LEVEL))
log_file_handler.setFormatter(formatter)

error_file_handler = RotatingFileHandler(
    parm.ERROR_LOG_FILE,
    maxBytes=5 * 1024 * 1024,
    backupCount=5
)
error_file_handler.setLevel(getattr(logging, parm.ERROR_LOG_LEVEL.upper(), parm.ERROR_LOG_LEVEL))
error_file_handler.setFormatter(formatter)

# --- Short Handlers for 100 lines ---

class LineLimitedFileHandler(logging.FileHandler):
    """Custom FileHandler that keeps only last N lines."""
    def __init__(self, filename, mode='a', max_lines=100, encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
        self.max_lines = max_lines
        self.filename = filename

    def emit(self, record):
        super().emit(record)
        self._trim_file()

    def _trim_file(self):
        try:
            with open(self.filename, 'r', encoding=self.encoding or 'utf-8') as f:
                lines = f.readlines()
            if len(lines) > self.max_lines:
                with open(self.filename, 'w', encoding=self.encoding or 'utf-8') as f:
                    f.writelines(lines[-self.max_lines:])
        except Exception as e:
            print(f"Failed to trim log file {self.filename}: {e}")

short_log_file_handler = LineLimitedFileHandler(
    parm.SHORT_FILE_LOG_FILE,  # you will need to define this in parms
    max_lines=100
)
short_log_file_handler.setLevel(getattr(logging, parm.FILE_LOG_LEVEL.upper(), parm.FILE_LOG_LEVEL))
short_log_file_handler.setFormatter(formatter)

short_error_file_handler = LineLimitedFileHandler(
    parm.SHORT_ERROR_LOG_FILE,  # you will need to define this in parms
    max_lines=100
)
short_error_file_handler.setLevel(getattr(logging, parm.ERROR_LOG_LEVEL.upper(), parm.ERROR_LOG_LEVEL))
short_error_file_handler.setFormatter(formatter)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, parm.CONSOLE_LOG_LEVEL.upper(), parm.CONSOLE_LOG_LEVEL))
console_handler.setFormatter(formatter)

# Twilio Handler
class TwilioHandler(logging.Handler):
    """Custom logging handler to send Twilio alerts for errors when enabled."""
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            send_twilio_alert(self.format(record))

twilio_handler = TwilioHandler()
twilio_handler.setLevel(logging.ERROR)
twilio_handler.setFormatter(formatter)

# Queue Listener (Processes Logs from Queue)
queue_listener = QueueListener(
    log_queue,
    console_handler,
    log_file_handler,
    error_file_handler,
    short_log_file_handler,
    short_error_file_handler,
    twilio_handler,
    respect_handler_level=True
)
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
    logger2.error("Module 2 - Error message")  # This will trigger a Twilio alert if TWILIO_ALERT is True

    shutdown_logger()



