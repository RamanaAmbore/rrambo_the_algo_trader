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
                    x= func(*args, **kwargs)
                    return x
                except Exception as e:
                    logger.warning(f"{func.__name__}: Attempt {attempt + 1} of {max_attempts} failed: {e}...")
                    if attempt == max_attempts - 1:
                        logger.error(f"{func.__name__}: Operation failed after {max_attempts} attempts.")
                        raise

        return wrapper

    return decorator


# async def insert_thread_status(thread_name):
#     """Update the thread status in the database."""
#     # Define Indian timezone (IST)
#
#     record_id = await ThreadStatusTrackerServiceBase().insert_record(
#         {
#             "thread": thread_name,
#             "schedule": Schedule.PRE_MARKET,
#             "thread_status": ThreadStatus.IN_PROGRESS,
#             "run_count": 1,
#             "error_count": 0,
#             "source": Source.CODE,  # Assuming Source has API as a valid value
#             "timestamp": timestamp_indian,
#             "upd_timestamp": timestamp_indian,
#             "warning_error": False,
#             "notes": "Thread started successfully"
#         })
#     return record_id
#
#
# async def update_thread_status(record_id, thread_status=ThreadStatus.IN_PROGRESS, run_count=1, error_count=0):
#     """Update the thread status in the database."""
#     # Define Indian timezone (IST)
#
#     return await ThreadStatusTrackerServiceBase().update_record(record_id,
#                                                              {
#                                                                  "thread_status": thread_status,
#                                                                  "run_count": run_count,
#                                                                  "error_count": error_count,
#                                                                  "timestamp": timestamp_indian,
#                                                                  "upd_timestamp": timestamp_indian,
#                                                                  "notes": "Thread started successfully"
#                                                              })
#
#
# async def run_in_thread_with_status(thread_name, retries=parms.MAX_RETRIES, delay=parms.RETRY_DELAY):
#     """Decorator to run a function in a separate thread and update its status in the DB."""
#
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             async def target():
#                 attempt = 1
#                 await insert_thread_status(thread_name)
#
#                 while attempt <= retries:
#                     try:
#                         func(*args, **kwargs)
#                         await update_thread_status(thread_name, ThreadStatus.COMPLETED)
#                         return  # Exit if successful
#                     except Exception as e:
#                         attempt += 1
#                         print(f"[{thread_name}] Error: {e}. Retrying {attempt}/{retries}...")
#                         time.sleep(delay)
#
#                     await update_thread_status(thread_name, thread_status=ThreadStatus.FAILED, run_count=attempt,
#                                          error_count=attempt - 1)  # Mark as FAILED after retries
#
#             thread = threading.Thread(target=target, name=thread_name, daemon=True)
#             thread.start()
#             return thread  # Return thread if we need to join later
#
#         return wrapper
#
#     return decorator
#
#
# # Example Usage
# @run_in_thread_with_status('SYNC_REPORT_DATA', retries=3, delay=1)
# def unstable_function():
#     """Function that randomly fails."""
#     import random
#     if random.random() < 0.7:  # 70% chance to fail
#         raise ValueError("Simulated failure")
#     print("Function succeeded!")
#
#
# # Run the function in a separate thread
# thread = unstable_function()
#
# # Main thread continues execution
# print("Main thread continues while function runs in the background.")
#
# # Optionally wait for the thread to finish
# thread.join()
# print("Thread execution completed.")
