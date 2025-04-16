import time

from apscheduler.schedulers.background import BackgroundScheduler


def scheduled_task():
    """Function to run the report downloader."""
    try:
        ReportDownloader.setup_driver()
        ReportDownloader.login_kite()
        # Add other necessary calls if required
    except Exception as e:
        logger.error(f"Scheduled task failed: {e}")


# Initialize APScheduler
scheduler = BackgroundScheduler()

# Schedule `scheduled_task` at a specific time (e.g., every day at 9:15 AM)
scheduler.add_job(scheduled_task, 'cron', hour=9, minute=15)

# Start the scheduler
scheduler.start()

# Keep the script running to allow scheduled execution
try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
