import threading
import time
from functools import wraps

from src.helpers.date_time_utils import timestamp_indian
from src.helpers.logger import get_logger
from src.services.service_thread_status_tracker import ThreadStatusTrackerServiceBase
from src.settings.constants_manager import ThreadStatus, Schedule, Source
from src.settings.parameter_manager import parms

logger = get_logger(__name__)


def retry_kite_conn(max_attempts):
    """
    Decorator to retry a function on failure.

    :param max_attempts: Maximum retry attempts.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    result= func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.warning(f"{func.__name__}: Attempt {attempt + 1} of {max_attempts} failed: {e}...")
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__}: Operation failed after {max_attempts} attempts.")
                        raise

        return wrapper

    return decorator