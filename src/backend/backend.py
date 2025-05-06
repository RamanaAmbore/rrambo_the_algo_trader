import asyncio
import os
import threading

from flask import Flask, jsonify

from src.backend.app_initializer import AppInitializer
from src.backend.ticks.tick_queue_manager import TickQueueManager
from src.helpers.app_state_manager import app_state, AppState
from src.helpers.logger import get_logger
from src.settings.constants_manager import load_env
from src.backend.stock_charts import initialize_stock_charts  # Add this import
from src.backend.api import register_api_endpoints

load_env()

logger = get_logger(__name__)

# Flask application to expose the /get_ticks endpoint
app = Flask(__name__)

# We will store the single instance of TickQueueManager here after initialization
# Using an attribute on the app object is a clean way to share resources
app.tick_manager_instance = None


@app.route('/get_ticks', methods=['GET'])
def get_ticks():
    # Existing code...
    # No changes needed here
    # ...
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

        instr_symbol_xref = app_state.get(key=AppState.TOKEN_SYMBOL_MAP)
        ticks_data = {instr_symbol_xref[tick.instrument_token]: (tick.last_price, tick.change)
                      for tick in ticks_map.values()}

        logger.info(f"Returning {len(ticks_data)} ticks data.")
        return jsonify(ticks_data)

    except Exception as e:
        logger.error(f"An error occurred while processing /get_ticks: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred"}), 500


@app.route('/get_logs', methods=['GET'])
def get_logs():
    # Existing code...
    # No changes needed here
    # ...
    log_path = os.path.abspath(os.getenv('ERROR_LOG_FILE'))
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
    await AppInitializer().setup()  # This starts background tasks/threads

    logger.info("app_initializer setup complete.")

    # Create the TickQueueManager instance
    try:
        xref = app_state.get(AppState.TRACK_TOKEN_SYMBOL_MAP)
        app.tick_manager_instance = TickQueueManager()
        logger.info("TickQueueManager instance successfully created and attached to app.")
    except Exception as e:
        logger.critical(f"Failed to create TickQueueManager instance: {e}", exc_info=True)

    # Initialize stock charts module
    try:
        logger.info("Initializing stock charts module...")
        initialize_stock_charts(app)
        logger.info("Stock charts module successfully initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize stock charts module: {e}", exc_info=True)
        # Continue even if this fails - it's not critical for core functionality

    # Inside the backend_process function, after initializing stock charts:
    # Register API endpoints
    # try:
    #     logger.info("Registering API endpoints...")
    #     register_api_endpoints(app)
    # except Exception as e:
    #     logger.error(f"Failed to register API endpoints: {e}", exc_info=True)

    # Start Flask server in a separate thread
    logger.info("Starting Flask server thread...")
    flask_thread = threading.Thread(target=app.run,
                                   kwargs={'debug': False, 'use_reloader': False, 'host': '0.0.0.0', 'port': 5000},
                                   daemon=True,
                                   name="FlaskServerThread")

    flask_thread.start()
    logger.info(f"Flask server thread started. (Daemon: {flask_thread.daemon}, Name: {flask_thread.name})")
    logger.info("Flask server should be listening on http://0.0.0.0:5000")

    # Rest of the function remains unchanged
    # ...
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