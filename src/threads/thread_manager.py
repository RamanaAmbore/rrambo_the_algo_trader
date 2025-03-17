import importlib
import threading
import time
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.database import engine
from src.models.algo_thread_status import AlgoThreadStatus
from src.models.algo_thread_schedule_xref import AlgoThreadScheduleXref
from src.utils.logger import get_logger

logger = get_logger(__name__)
Session = sessionmaker(bind=engine)


class ThreadManager:
    """Manages the lifecycle of dynamically imported and scheduled threads."""

    def __init__(self):
        self.running_threads = {}
        self.lock = threading.Lock()

    def get_active_threads(self):
        """Fetch active threads based on their schedule and status."""
        session = Session()
        now = datetime.now()
        active_threads = []
        try:
            query = (
                session.query(AlgoThreadStatus)
                .join(AlgoThreadScheduleXref, AlgoThreadStatus.thread == AlgoThreadScheduleXref.thread)
                .filter(AlgoThreadStatus.is_active == True)
                .filter(AlgoThreadStatus.next_run <= now)
                .distinct()
            )
            active_threads = query.all()
        except Exception as e:
            logger.error(f"Error fetching active threads: {e}")
        finally:
            session.close()
        return active_threads

    def start_thread(self, thread_status):
        """Dynamically imports and starts a thread if not already running."""
        thread_name = thread_status.thread
        with self.lock:
            if thread_name in self.running_threads:
                logger.info(f"Thread {thread_name} is already running.")
                return
            try:
                module = importlib.import_module(f"threads.{thread_name}")
                thread_class = getattr(module, thread_name)
                thread_instance = thread_class()
                thread_instance.start()
                self.running_threads[thread_name] = thread_instance
                logger.info(f"Started thread: {thread_name}")
                self.update_thread_status(thread_status, "RUNNING")
            except Exception as e:
                logger.error(f"Failed to start thread {thread_name}: {e}")
                self.update_thread_status(thread_status, "FAILED")

    def stop_thread(self, thread_name):
        """Stops a running thread gracefully."""
        with self.lock:
            thread = self.running_threads.pop(thread_name, None)
            if thread:
                thread.stop()
                logger.info(f"Stopped thread: {thread_name}")
            else:
                logger.info(f"Thread {thread_name} was not running.")

    def update_thread_status(self, thread_status, status):
        """Updates the status of a thread in the database."""
        session = Session()
        try:
            thread_status.is_active = status == "RUNNING"
            if status == "FAILED":
                thread_status.error_count += 1
            elif status == "COMPLETED":
                thread_status.run_count += 1
            thread_status.last_run = datetime.now()
            session.commit()
        except Exception as e:
            logger.error(f"Error updating thread status: {e}")
            session.rollback()
        finally:
            session.close()

    def stop_market_threads(self):
        """Stops all market schedule threads."""
        session = Session()
        try:
            market_threads = session.query(AlgoThreadStatus).filter_by(schedule="MARKET").all()
            for thread in market_threads:
                self.stop_thread(thread.thread)
        except Exception as e:
            logger.error(f"Error stopping market threads: {e}")
        finally:
            session.close()

    def manage_threads(self):
        """Continuously checks for threads that should start or stop."""
        while True:
            active_threads = self.get_active_threads()
            running_threads = set(self.running_threads.keys())

            for thread_status in active_threads:
                if thread_status.is_active and thread_status.thread not in running_threads:
                    self.start_thread(thread_status)
                elif thread_status.is_active == "REFRESH":
                    self.stop_market_threads()
                    logger.info("Stopping all market threads due to REFRESH status.")

            time.sleep(10)  # Check every 10 seconds


if __name__ == "__main__":
    manager = ThreadManager()
    manager.manage_threads()

