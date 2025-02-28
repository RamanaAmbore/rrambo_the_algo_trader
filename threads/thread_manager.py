import threading
import time
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from market_ticker import MarketTicker  # Import MarketTicker
from utils.logger import get_logger  # Import Async Logger

# Initialize Async Logger
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

    def start_threads(self):
        """Starts MarketTicker and multiple independent threads."""
        logger.info("Starting scheduled tasks...")

        # Start MarketTicker separately
        ticker_thread = threading.Thread(target=self.start_market_ticker)
        ticker_thread.start()

        # Start worker threads
        threads = []
        for i in range(self.num_threads):
            thread = threading.Thread(target=self.worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Optional: Wait for all threads to complete
        for thread in threads:
            thread.join()


# Create an instance of the manager
manager = ThreadManager(num_threads=5)

# Create APScheduler
scheduler = BackgroundScheduler()

# Schedule the job at a specific time
start_time = datetime.now() + timedelta(seconds=10)  # Example: Start in 10 seconds
scheduler.add_job(manager.start_threads, 'date', run_date=start_time)

# Start the scheduler
scheduler.start()

logger.info(f"Scheduled threads to start at {start_time}")

# Keep the script running so the scheduler can execute
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    logger.info("Scheduler shutdown")
