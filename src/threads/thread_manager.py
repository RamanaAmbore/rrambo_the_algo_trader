import time

from src.threads.thread_sync_reports import SyncReportsThread


class ThreadManager:
    """Manages multiple worker threads."""

    def __init__(self):
        self.threads = []

    def start_thread(self, name="Worker", run_time=5):
        """Starts a new worker thread."""
        worker = SyncReportsThread(name, run_time)
        worker.start()
        self.threads.append(worker)
        print(f"Thread '{name}' started.")

    def stop_all_threads(self):
        """Stops all running threads."""
        for thread in self.threads:
            thread.stop()
            thread.join()  # Wait for threads to finish
        self.threads.clear()
        print("All threads stopped.")


if __name__ == "__main__":
    manager = ThreadManager()

    # Start two worker threads
    manager.start_thread("Worker-1", 3)

    # Allow them to run before stopping
    time.sleep(6)

    # Stop all threads
    manager.stop_all_threads()




