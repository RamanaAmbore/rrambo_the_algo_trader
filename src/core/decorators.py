import threading
import time
from functools import wraps
from inspect import iscoroutinefunction

from src.helpers.logger import get_logger

logger = get_logger(__name__)


from functools import wraps

def singleton_init_guard(init_func):
    @wraps(init_func)
    def wrapper(self, *args, **kwargs):
        if getattr(self, '_singleton_initialized', False):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        init_func(self, *args, **kwargs)
        self._singleton_initialized = True
    return wrapper


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


def track_it():
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

def lock_it_for_update(method):
    def wrapper(self, *args, **kwargs):
        with self.lock:
            return method(self, *args, **kwargs)
    return wrapper



def update_lock(method):
    """
    Decorator that ensures method execution is thread-safe using global and per-element locks.
    The element key is assumed to be the first positional argument.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = args[0] if args else None  # get key if passed

        with self.lock:
            if key:
                if key not in self.element_locks:
                    self.element_locks[key] = threading.Lock()
                lock = self.element_locks[key]
            else:
                lock = self.lock

        with lock:
            return method(self, *args, **kwargs)

    return wrapper



