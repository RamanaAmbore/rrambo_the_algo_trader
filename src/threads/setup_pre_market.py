import asyncio

from src.core.zerodha_kite_connect import ZerodhaKiteConnect
from src.helpers.logger import get_logger
from src.services.service_exchange_list import service_exchange_list
from src.services.service_instrument_list import service_instrument_list

logger = get_logger(__name__)  # Initialize logger

kite = ZerodhaKiteConnect.get_kite_conn()


async def sync_instrument_list():
    """Fetches stock list from Kite API without filtering and updates the database."""

    try:
        logger.info("Fetching complete stock list from Kite API...")
        records = await asyncio.to_thread(kite.instruments)  # Run in a separate thread
        exchange_set = {record["exchange"] for record in records}
        exchange_set = [{'exchange': record} for record in exchange_set]
        await service_exchange_list.pre_process_records(exchange_set)  # Async DB insert
        await service_instrument_list.pre_process_records(records)  # Async DB insert

        logger.info("Stock List successfully updated.")
    except Exception as e:
        logger.error(f"Error fetching stock list: {e}")
