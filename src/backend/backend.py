import asyncio
import os
import threading

from flask import Flask, jsonify  # Import current_app for accessing app context

from src.backend.app_initializer import app_initializer
from src.helpers.logger import get_logger
# Assuming TickQueueManager might be populated by app_initializer
from src.ticks.tick_queue_manager import TickQueueManager

logger = get_logger(__name__)

# Flask application to expose the /get_ticks endpoint
app = Flask(__name__)

# We will store the single instance of TickQueueManager here after initialization
# Using an attribute on the app object is a clean way to share resources
app.tick_manager_instance = None


@app.route('/get_ticks', methods=['GET'])
def get_ticks():
    logger.debug("Request received for /get_ticks")
    tick_queue_manager = app.tick_manager_instance  # Access the shared instance

    if tick_queue_manager is None:
        logger.error("TickQueueManager instance is not initialized yet!")
        return jsonify({"error": "Service not fully initialized"}), 503

    try:
        logger.debug("Attempting to get all ticks from manager...")
        ticks_map = tick_queue_manager.get_all_ticks()
        logger.debug(f"Successfully fetched {len(ticks_map)} ticks.")

        # Corrected line: Use tick.exchange_timestamp
        ticks_data = [
            {'instrument_token': tick.instrument_token,
             'last_price': tick.last_price,
             'timestamp': tick.exchange_timestamp}  # <-- CHANGED THIS LINE
            for tick in ticks_map.values()
        ]

        logger.debug(f"Returning {len(ticks_data)} ticks data.")
        return jsonify(ticks_data)

    except Exception as e:
        logger.error(f"An error occurred while processing /get_ticks: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred"}), 500

@app.route('/get_logs', methods=['GET'])
def get_logs():
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs/log.log"))
    try:
        with open(log_path, 'r') as f:
            log_content = f.read()
        return jsonify({"logs": log_content})
    except Exception as e:
        logger.error(f"Failed to read log file: {e}", exc_info=True)
        return jsonify({"error": "Could not read log file"}), 500

# Backend process, including Flask server
async def backend_process():
    logger.info("Starting backend process...")

    # Start the app initializer (Ticker, and other background threads)
    logger.info("Running app_initializer setup...")
    # app_initializer.setup() might return the manager or populate internal state.
    # Assuming TickQueueManager() can be safely instantiated *after* setup completes.
    await app_initializer.setup()  # This starts background tasks/threads

    logger.info("app_initializer setup complete.")

    # --- Create the TickQueueManager instance ONCE after setup ---
    # This is crucial. Create the instance here and store it.
    # If app_initializer.setup() returns the instance, get it from there.
    # For now, assuming we instantiate it here after setup.
    try:
        app.tick_manager_instance = TickQueueManager()
        logger.info("TickQueueManager instance successfully created and attached to app.")
    except Exception as e:
        logger.critical(f"Failed to create TickQueueManager instance: {e}", exc_info=True)
        # Depending on severity, you might want to exit here.
        # raise e # Uncomment to stop execution if manager is critical

    # Start Flask server in a separate thread so it can run alongside other background tasks
    logger.info("Starting Flask server thread...")
    # app.run is a blocking call, hence it needs its own thread.
    flask_thread = threading.Thread(target=app.run,
                                    kwargs={'debug': False, 'use_reloader': False, 'host': '0.0.0.0', 'port': 5000},
                                    daemon=True,  # Daemon threads exit when the main thread exits
                                    name="FlaskServerThread")  # Give it a name for easier debugging

    flask_thread.start()
    logger.info(f"Flask server thread started. (Daemon: {flask_thread.daemon}, Name: {flask_thread.name})")
    logger.info("Flask server should be listening on http://0.0.0.0:5000")

    # Keep the async loop alive until all non-main threads finish
    # This prevents asyncio.run from exiting immediately.
    main_thread = threading.current_thread()
    logger.info(f"Main thread: {main_thread.name}")
    try:
        while True:
            # Check status of all non-main threads, especially the Flask one
            alive_threads = [t for t in threading.enumerate() if t is not main_thread and t.is_alive()]
            thread_names = [t.name for t in alive_threads]

            # Check specifically if the Flask thread is still alive
            if not flask_thread.is_alive():
                logger.error("Flask server thread has stopped unexpectedly!")
                # Depending on your application logic, you might want to:
                # 1. Attempt to restart it (complex)
                # 2. Shut down the entire application
                # For now, we'll log and let the loop potentially break if no other threads remain.
                pass  # Continue checking other threads

            if not alive_threads:
                logger.info("No non-main threads are alive. Exiting main loop.")
                break  # Exit the loop if all background threads are done

            logger.debug(f"Alive non-main threads: {thread_names}")  # Use debug for frequent checks

            # Use asyncio.sleep within the async function
            await asyncio.sleep(5)  # Yield control and avoid CPU hogging

    except KeyboardInterrupt:
        logger.info("Main loop interrupted by user (Ctrl+C).")
    finally:
        logger.info("Main thread exiting.")
        # Any cleanup logic can go here


if __name__ == "__main__":
    logger.info("Application entry point reached.")
    try:
        # Run the backend process (with Flask server and background tasks)
        asyncio.run(backend_process())
    except Exception as e:
        logger.critical(f"An unhandled exception occurred during application execution: {e}", exc_info=True)

    logger.info("Application finished.")
