import threading
import time

from src.helpers.date_time_utils import timestamp_indian
from src.services.algo_thread_status_service import AlgoThreadStatusService
from src.settings.parameter_loader import ThreadStatus, Schedule, Source
from src.settings.parameter_manager import ParameterManager as Parms

update_record = {
    "thread": "market_data_fetcher",
    "account": "ACC12345",
    "schedule": "daily_run",
    "thread_status": "FAILED",  # Updating status after multiple failures
    "last_run": "2025-03-18 12:00:00",
    "next_run": "2025-03-18 16:00:00",
    "run_count": 3,
    "error_count": 3,  # Increased due to retries
    "source": "API",
    "upd_timestamp": "2025-03-18 12:15:00",
    "warning_error": True,
    "notes": "Thread failed after 3 retries"
}


async def insert_thread_status(thread_name):
    """Update the thread status in the database."""
    # Define Indian timezone (IST)

    record_id = await AlgoThreadStatusService().insert_record(
        {
            "thread": thread_name,
            "schedule": Schedule.PRE_MARKET,
            "thread_status": ThreadStatus.IN_PROGRESS,
            "run_count": 1,
            "error_count": 0,
            "source": Source.CODE,  # Assuming Source has API as a valid value
            "timestamp": timestamp_indian,
            "upd_timestamp": timestamp_indian,
            "warning_error": False,
            "notes": "Thread started successfully"
        })
    return record_id


async def update_thread_status(record_id, thread_status=ThreadStatus.IN_PROGRESS, run_count=1, error_count=0):
    """Update the thread status in the database."""
    # Define Indian timezone (IST)

    return await AlgoThreadStatusService().update_record(record_id,
                                                         {
                                                             "thread_status": thread_status,
                                                             "run_count": run_count,
                                                             "error_count": error_count,
                                                             "timestamp": timestamp_indian,
                                                             "upd_timestamp": timestamp_indian,
                                                             "notes": "Thread started successfully"
                                                         })


def run_in_thread_with_status(thread_name, retries=Parms.MAX_RETRIES, delay=Parms.RETRY_DELAY):
    """Decorator to run a function in a separate thread and update its status in the DB."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            def target():
                attempt = 1
                insert_thread_status(thread_name)

                while attempt <= retries:
                    try:
                        func(*args, **kwargs)
                        update_thread_status(thread_name, ThreadStatus.COMPLETED)
                        return  # Exit if successful
                    except Exception as e:
                        attempt += 1
                        print(f"[{thread_name}] Error: {e}. Retrying {attempt}/{retries}...")
                        time.sleep(delay)

                    update_thread_status(thread_name, thread_status=ThreadStatus.FAILED, run_count=attempt,
                                         error_count=attempt - 1)  # Mark as FAILED after retries

            thread = threading.Thread(target=target, name=thread_name, daemon=True)
            thread.start()
            return thread  # Return thread if we need to join later

        return wrapper

    return decorator


# Example Usage
@run_in_thread_with_status('SYNC_REPORT_DATA', retries=3, delay=1)
def unstable_function():
    """Function that randomly fails."""
    import random
    if random.random() < 0.7:  # 70% chance to fail
        raise ValueError("Simulated failure")
    print("Function succeeded!")


# Run the function in a separate thread
thread = unstable_function()

# Main thread continues execution
print("Main thread continues while function runs in the background.")

# Optionally wait for the thread to finish
thread.join()
print("Thread execution completed.")
