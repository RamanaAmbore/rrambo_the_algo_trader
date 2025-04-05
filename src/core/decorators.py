import time
from functools import wraps
from inspect import iscoroutinefunction

from src.helpers.logger import get_logger

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
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    logger.warning(f"{func.__name__}: Attempt {attempt + 1} of {max_attempts} failed: {e}...")
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__}: Operation failed after {max_attempts} attempts.")
                        raise

        return wrapper

    return decorator


def track_exec_time():
    def decorator(func):
        if iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    raise e
                finally:
                    elapsed = time.perf_counter() - start_time
                    logger.info(f"Async function {func.__name__} executed in {elapsed:.4f} seconds")

            return async_wrapper

        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    raise e
                finally:
                    elapsed = time.perf_counter() - start_time
                    logger.info(f"Function {func.__name__} executed in {elapsed:.4f} seconds")

            return sync_wrapper

    return decorator
