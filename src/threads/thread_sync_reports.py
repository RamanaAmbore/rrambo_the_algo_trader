import asyncio
import threading
import time

from src.threads.report_uploader import ReportUploader


class SyncReportsThread(threading.Thread):
    """A worker thread that performs a task asynchronously."""

    def __init__(self, name, run_time=5):
        super().__init__()
        self.name = name
        self.run_time = run_time  # Duration to run the thread
        self._stop_event = threading.Event()

    def run(self):
        """Executes the thread's task asynchronously."""
        print(f"{self.name} started.")

        loop = asyncio.new_event_loop()  # Create a new event loop
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(ReportUploader.upload_reports())  # Run async function
        finally:
            loop.close()  # Ensure the loop is properly closed

        print(f"{self.name} has finished execution.")

    def stop(self):
        """Stops the thread."""
        self._stop_event.set()

