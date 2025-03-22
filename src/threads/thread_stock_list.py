import asyncio

import pandas as pd

from src.core.zerodha_kite_connect import ZerodhaKiteConnect
from src.helpers.logger import get_logger
from src.services.service_stock_list import service_stock_list  # Ensure this is the correct import

logger = get_logger(__name__)  # Initialize logger


class StockListUpdater:
    """Fetches stock list from Kite API and updates the database asynchronously."""

    def __init__(self):
        self.kite = ZerodhaKiteConnect.get_kite_conn()

    async def fetch_update_stock_list(self):
        """Fetches stock list from Kite API without filtering and updates the database."""
        logger.info("Fetching complete stock list from Kite API...")
        kite = ZerodhaKiteConnect.get_kite_conn()
        instruments = kite.instruments()
        df = pd.DataFrame(instruments)

        # Asynchronous bulk insert
        await service_stock_list.bulk_insert_stocks(df)

    async def run(self):
        """Main execution function."""
        await self.fetch_update_stock_list()


if __name__ == "__main__":
    updater = StockListUpdater()
    asyncio.run(updater.run())  # Proper way to call an async function
