import asyncio
import threading
import time

from apscheduler.schedulers.background import BackgroundScheduler

# Import existing thread functions
from market_ticker import MarketTicker
from src.models.algo_schedule import AlgoScheduleTime
from sync_data import sync_all
from src.utils.date_time_utils import current_time_indian
from src.core.database_manager import DbManager as Db
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ThreadManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.running_threads = {}  # Tracks running threads
        self.lock = threading.Lock()  # Prevents race conditions

    @staticmethod
    def fetch_schedules():
        """Fetch active schedules from algo_schedule using sync session."""

        with Db.get_sync_session() as session:
            try:
                schedules = [AlgoScheduleTime.get_market_hours_for_today(session)]
                return schedules
            except Exception as e:
                logger.error(f"Error fetching schedules: {e}")
                return []


    @staticmethod
    def start_market_ticker():
        """Start MarketTicker WebSocket."""
        logger.info("Starting MarketTicker WebSocket...")
        ticker = MarketTicker()
        ticker.start()

    @staticmethod
    def start_sync_process():
        """Start sync process asynchronously."""
        logger.info("Starting sync process...")
        asyncio.run(sync_all())

    def start_thread(self, thread_name):
        """Start a new thread only if it's not already running."""
        with self.lock:
            if thread_name in self.running_threads and self.running_threads[thread_name].is_alive():
                logger.info(f"Thread {thread_name} is already running. Skipping restart.")
                return

            logger.info(f"Starting new thread: {thread_name}")

            if thread_name == "MARKET":
                thread = threading.Thread(target=self.start_market_ticker, daemon=True)
            elif thread_name == "BATCH":
                thread = threading.Thread(target=self.start_sync_process, daemon=True)
            else:
                logger.warning(f"Unknown thread type: {thread_name}. Skipping.")
                return

            thread.start()
            self.running_threads[thread_name] = thread  # Store thread instance

    def stop_thread(self, thread_name):
        """Stop a thread by marking it as stopped."""
        with self.lock:
            if thread_name in self.running_threads:
                logger.info(f"Stopping thread {thread_name}...")
                del self.running_threads[thread_name]  # Remove thread from tracking

    def manage_threads(self):
        """Fetch schedules, start/stop threads dynamically, and handle updates."""
        schedules = self.fetch_schedules()
        now = current_time_indian()

        with self.lock:
            for schedule in schedules:
                thread_name = schedule.thread
                start_time = schedule.start_time
                end_time = schedule.end_time

                # Start thread if within start time
                if now >= start_time and thread_name not in self.running_threads:
                    self.start_thread(thread_name)

                # Stop thread if end_time is set and passed
                if end_time and now >= end_time and thread_name in self.running_threads:
                    self.stop_thread(thread_name)

    def schedule_tasks(self):
        """Schedule periodic checks to manage threads dynamically."""
        self.scheduler.add_job(self.manage_threads, "interval", seconds=30)
        self.scheduler.start()
        logger.info("Scheduler started. Checking for thread updates every 30 seconds.")

    def run(self):
        """Start the manager and keep it running."""
        logger.info("Running initial thread check before scheduling...")
        self.manage_threads()  # 🔥 Immediate execution to avoid delay

        self.schedule_tasks()

        logger.info("ThreadManager is running...")

        try:
            while True:
                time.sleep(1)  # Keep the script alive
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            logger.info("Scheduler shut down. Stopping all threads.")
            with self.lock:
                self.running_threads.clear()  # Mark all threads as stopped


# Run the Thread Manager
if __name__ == "__main__":
    manager = ThreadManager()
    manager.run()
