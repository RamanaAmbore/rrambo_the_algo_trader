# src/backend/stock_charts/api.py
from typing import cast

from flask import Flask, jsonify, request, current_app, Blueprint, g

from src.backend.stock_charts.analysis_utils import generate_market_analysis_report
from src.backend.stock_charts.historical_data_service import HistoricalDataService
from src.backend.stock_charts.intraday_data_service import IntradayDataService
from src.helpers.logger import get_logger

logger = get_logger(__name__)

stock_blueprint = Blueprint('stock', __name__)


def get_historical_service() -> HistoricalDataService:
    """Get the historical data service from the app context"""
    if not hasattr(g, 'historical_data_service'):
        g.historical_data_service = getattr(current_app, 'historical_data_service', None)
        if g.historical_data_service is None:
            raise RuntimeError("Historical data service not initialized")
    return cast(HistoricalDataService, g.historical_data_service)


def get_intraday_service() -> IntradayDataService:
    """Get the intraday data service from the app context"""
    if not hasattr(g, 'intraday_data_service'):
        g.intraday_data_service = getattr(current_app, 'intraday_data_service', None)
        if g.intraday_data_service is None:
            raise RuntimeError("Intraday data service not initialized")
    return cast(IntradayDataService, g.intraday_data_service)


@stock_blueprint.route('/api/stocks/<symbol>/historical', methods=['GET'])
def get_historical_data(symbol: str):
    """
    Get historical stock data for a given symbol

    Args:
        symbol: Stock symbol to fetch data for

    Query parameters:
        start_date: Start date for historical data (YYYY-MM-DD)
        end_date: End date for historical data (YYYY-MM-DD)
        interval: Data interval (daily, weekly, monthly)
    """
    try:
        # Get query parameters
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        interval = request.args.get('interval', 'daily')

        # Get historical data service
        historical_service = get_historical_service()

        # Get historical data
        historical_data = historical_service.get_historical_data(
            symbol, start_date, end_date, interval
        )

        return jsonify(historical_data)
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@stock_blueprint.route('/api/stocks/<symbol>/intraday', methods=['GET'])
def get_intraday_data(symbol: str):
    """
    Get intraday stock data for a given symbol

    Args:
        symbol: Stock symbol to fetch data for

    Query parameters:
        interval: Data interval in minutes (1, 5, 15, 30, 60)
    """
    try:
        # Get query parameters
        interval = request.args.get('interval', '5')

        # Get intraday service
        intraday_service = get_intraday_service()

        # Get intraday data
        intraday_data = intraday_service.get_intraday_data(
            symbol, interval
        )

        return jsonify(intraday_data)
    except Exception as e:
        logger.error(f"Error fetching intraday data for {symbol}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@stock_blueprint.route('/api/stocks/<symbol>/analysis', methods=['GET'])
def get_stock_analysis(symbol: str):
    """
    Get comprehensive technical analysis for a stock

    Args:
        symbol: Stock symbol to analyze

    Query parameters:
        days: Number of days of data to analyze (default: 180)
    """
    try:
        # Get query parameters
        days = int(request.args.get('days', 180))

        # Get historical service
        historical_service = get_historical_service()

        # Get historical data
        historical_data = historical_service.get_historical_data(
            symbol, days=days
        )

        if not historical_data or 'data' not in historical_data or not historical_data['data']:
            return jsonify({'error': 'No data available for analysis'}), 404

        # Convert to DataFrame
        df = historical_service.to_dataframe(historical_data['data'])

        # Generate analysis report
        analysis_report = generate_market_analysis_report(df)

        # Add symbol to report
        analysis_report['symbol'] = symbol

        return jsonify(analysis_report)
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def register_api_endpoints(app: Flask) -> None:
    """
    Register stock API endpoints with Flask app

    Args:
        app: Flask application instance
    """
    app.register_blueprint(stock_blueprint)
    logger.info("Stock API endpoints registered")


