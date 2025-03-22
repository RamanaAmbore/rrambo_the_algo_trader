import asyncio
import pandas as pd

from src.core.zerodha_kite_connect import ZerodhaKiteConnect
from src.helpers.logger import get_logger
from src.services.service_holdings import service_holdings  # Ensure correct import

logger = get_logger(__name__)  # Initialize logger


class HoldingsUpdater:
    """Fetches holdings from Kite API and updates the database asynchronously."""

    def __init__(self):
        self.kite = ZerodhaKiteConnect.get_kite_conn()

    async def fetch_update_holdings(self):
        """Fetches holdings from Kite API and updates the database."""
        logger.info("Fetching holdings from Kite API...")
        kite = ZerodhaKiteConnect.get_kite_conn()

        try:
            holdings = kite.holdings()  # Fetch holdings from Kite API
            df = pd.DataFrame(holdings)

            if df.empty:
                logger.warning("No holdings data received from Kite API.")
                return

            # Asynchronous bulk insert
            await service_holdings.bulk_insert_holdings(df)
            logger.info("Holdings data successfully updated.")

        except Exception as e:
            logger.error(f"Error fetching holdings data: {e}")

    async def run(self):
        """Main execution function."""
        await self.fetch_update_holdings()


if __name__ == "__main__":
    updater = HoldingsUpdater()
    asyncio.run(updater.run())  # Proper way to call an async function
