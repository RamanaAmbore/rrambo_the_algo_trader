import asyncio
import os
import threading

from dash import Dash, html
from dash.dependencies import Input, Output
from flask import jsonify  # Still using Flask for backend routes

from src.backend.app_initializer import AppInitializer
from src.helpers.logger import get_logger
from src.ticks.tick_queue_manager import TickQueueManager
from src.settings.constants_manager import load_env

load_env()

logger = get_logger(__name__)

# Initialize Dash app (with Flask server under the hood)
app = Dash(__name__)
server = app.server  # Access Flask server for backend routes

# We will store the single instance of TickQueueManager here after initialization
app.tick_manager_instance = None


# Backend process (app_initializer setup and TickQueueManager initialization)
async def backend_process():
    logger.info("Starting backend process...")

    # Start the app initializer (Ticker, and other background threads)
    logger.info("Running app_initializer setup...")
    await AppInitializer().setup()  # This starts background tasks/threads

    logger.info("app_initializer setup complete.")

    # --- Create the TickQueueManager instance ONCE after setup ---
    try:
        app.tick_manager_instance = TickQueueManager()
        logger.info("TickQueueManager instance successfully created and attached to app.")
    except Exception as e:
        logger.critical(f"Failed to create TickQueueManager instance: {e}", exc_info=True)

    # Start Dash server in a separate thread so it can run alongside other background tasks
    logger.info("Starting Dash server thread...")
    dash_thread = threading.Thread(
        target=lambda: app.run_server(debug=False, host="0.0.0.0", port=5000),
        daemon=True,  # Daemon threads exit when the main thread exits
        name="DashServerThread"
    )
    dash_thread.start()

    logger.info("Dash server thread started. (Daemon: True, Name: DashServerThread)")

    # Keep the async loop alive until all non-main threads finish
    main_thread = threading.current_thread()
    logger.info(f"Main thread: {main_thread.name}")
    try:
        while True:
            alive_threads = [t for t in threading.enumerate() if t is not main_thread and t.is_alive()]
            thread_names = [t.name for t in alive_threads]

            if not dash_thread.is_alive():
                logger.error("Dash server thread has stopped unexpectedly!")
                break

            if not alive_threads:
                logger.info("No non-main threads are alive. Exiting main loop.")
                break

            logger.debug(f"Alive non-main threads: {thread_names}")
            await asyncio.sleep(5)

    except KeyboardInterrupt:
        logger.info("Main loop interrupted by user (Ctrl+C).")
    finally:
        logger.info("Main thread exiting.")


# Dash layout (UI)
app.layout = html.Div([
    html.H1("Backend Service Dashboard"),
    html.Button("Get Ticks", id="get-ticks-button", n_clicks=0, className="m-2"),
    html.Div(id="ticks-output", style={"whiteSpace": "pre-wrap"}),

    html.Button("Get Logs", id="get-logs-button", n_clicks=0, className="m-2"),
    html.Div(id="logs-output", style={"whiteSpace": "pre-wrap"}),
])


# Dash callback for /get_ticks
@app.callback(
    Output('ticks-output', 'children'),
    Input('get-ticks-button', 'n_clicks')
)
def get_ticks(n_clicks):
    if n_clicks == 0:
        return "Click to get ticks."

    logger.debug("Request received for /get_ticks")
    tick_queue_manager = app.tick_manager_instance  # Access the shared instance

    if tick_queue_manager is None:
        logger.error("TickQueueManager instance is not initialized yet!")
        return "Service not fully initialized."

    try:
        logger.debug("Attempting to get all ticks from manager...")
        ticks_map = tick_queue_manager.get_all_ticks()
        logger.debug(f"Successfully fetched {len(ticks_map)} ticks.")

        ticks_data = [
            {'instrument_token': tick.instrument_token,
             'last_price': tick.last_price,
             'timestamp': tick.exchange_timestamp}
            for tick in ticks_map.values()
        ]
        return str(ticks_data)

    except Exception as e:
        logger.error(f"An error occurred while processing /get_ticks: {e}", exc_info=True)
        return "An internal error occurred."


# Dash callback for /get_logs
@app.callback(
    Output('logs-output', 'children'),
    Input('get-logs-button', 'n_clicks')
)
def get_logs(n_clicks):
    if n_clicks == 0:
        return "Click to get logs."

    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.getenv('FILE_LOG_LEVEL')))
    try:
        with open(log_path, 'r') as f:
            log_content = f.read()
        return log_content
    except Exception as e:
        logger.error(f"Failed to read log file: {e}", exc_info=True)
        return "Could not read log file."


if __name__ == "__main__":
    logger.info("Application entry point reached.")
    try:
        # Run the backend process (with Dash server and background tasks)
        asyncio.run(backend_process())
    except Exception as e:
        logger.critical(f"An unhandled exception occurred during application execution: {e}", exc_info=True)

    logger.info("Application finished.")
