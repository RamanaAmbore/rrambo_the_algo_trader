import asyncio
import pandas as pd

from src.core.zerodha_kite_connect import ZerodhaKiteConnect
from src.helpers.logger import get_logger
from src.services.service_positions import service_positions  # Ensure correct import

logger = get_logger(__name__)  # Initialize logger


class PositionsUpdater:
    """Fetches positions from Kite API and updates the database asynchronously."""

    def __init__(self):
        self.kite = ZerodhaKiteConnect.get_kite_conn()

    async def fetch_positions(self):
        """Fetches positions from Kite API and updates the database."""
        logger.info("Fetching positions from Kite API...")

        try:
            positions = self.kite.positions()  # Fetch positions

            # Combine day and overnight positions into a single DataFrame
            all_positions = positions.get("day", []) + positions.get("net", [])
            df = pd.DataFrame(all_positions)

            if df.empty:
                logger.info("No open positions found.")
                return

            # Asynchronous bulk insert
            await service_positions.bulk_insert_positions(df)
            logger.info("Positions successfully updated.")

        except Exception as e:
            logger.error(f"Error fetching positions: {e}")

    async def run(self):
        """Main execution function."""
        await self.fetch_positions()


if __name__ == "__main__":
    updater = PositionsUpdater()
    asyncio.run(updater.run())  # Proper way to call an async function
