import threading
import time
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from market_ticker import MarketTicker  # Import MarketTicker
from sync_data import sync_all  # Import sync function
from utils.logger import get_logger  # Import Async Logger

# Initialize Logger
logger = get_logger(__name__)


class ThreadManager:
    def __init__(self, num_threads):
        """
        Initializes the thread manager.
        :param num_threads: Number of additional threads to run independently.
        """
        self.num_threads = num_threads
        self.market_ticker = MarketTicker()  # Initialize MarketTicker

    def worker(self, thread_id):
        """Function executed by each worker thread independently."""
        logger.info(f"Worker Thread-{thread_id} started execution at {datetime.now()}")

    def start_market_ticker(self):
        """Starts the MarketTicker WebSocket thread."""
        logger.info("Starting MarketTicker WebSocket...")
        self.market_ticker.start()

    def start_sync_process(self):
        """Starts the sync process in a separate thread."""
        logger.info("Starting sync process...")
        asyncio.run(sync_all())  # Run async sync function

    def start_threads(self):
        """Starts MarketTicker and multiple independent threads."""
        logger.info("Starting scheduled tasks...")

        # Start MarketTicker in a separate thread
        ticker_thread = threading.Thread(target=self.start_market_ticker, daemon=True)
        ticker_thread.start()

        # Start worker threads
        threads = []
        for i in range(self.num_threads):
            thread = threading.Thread(target=self.worker, args=(i,), daemon=True)
            threads.append(thread)
            thread.start()

        # Start the sync process in a separate thread
        sync_thread = threading.Thread(target=self.start_sync_process, daemon=True)
        sync_thread.start()

        # Optional: Wait for worker threads to complete
        for thread in threads:
            thread.join()


# Create an instance of the manager
manager = ThreadManager(num_threads=5)

# Create APScheduler
scheduler = BackgroundScheduler()

# Schedule MarketTicker and sync_data tasks
start_time = datetime.now() + timedelta(seconds=10)  # Start in 10 seconds
scheduler.add_job(manager.start_threads, 'date', run_date=start_time)

# Start the scheduler
scheduler.start()

logger.info(f"Scheduled MarketTicker and sync tasks to start at {start_time}")

# Keep the script running so the scheduler can execute
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    logger.info("Scheduler shutdown")
