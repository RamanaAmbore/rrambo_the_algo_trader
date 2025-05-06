# src/backend/stock_charts/__init__.py
from flask import Flask

from src.backend.api import register_api_endpoints
from src.backend.stock_charts.historical_data_service import HistoricalDataService
from src.backend.stock_charts.intraday_data_service import IntradayDataService
from src.helpers.logger import get_logger

logger = get_logger(__name__)


def initialize_stock_charts(app: Flask) -> None:
    """
    Initialize stock chart services and attach them to the Flask app

    Args:
        app: Flask application instance
    """
    logger.info("Initializing stock chart services...")

    try:
        # Initialize historical data service
        app.historical_data_service = HistoricalDataService()
        logger.info("Historical data service initialized")

        # Initialize intraday data service
        app.intraday_data_service = IntradayDataService()
        logger.info("Intraday data service initialized")

        # Register API endpoints
        register_api_endpoints(app)
        logger.info("Stock chart API endpoints registered")

        logger.info("Stock chart services initialization complete")
    except Exception as e:
        logger.error(f"Error initializing stock chart services: {e}", exc_info=True)
        # Don't re-raise - allow application to start even if this fails
        # Services will return appropriate errors when accessed