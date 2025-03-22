import asyncio
import pandas as pd
from datetime import datetime, timedelta

from src.core.zerodha_kite_connect import ZerodhaKiteConnect
from src.helpers.logger import get_logger
from src.services.service_historical_data import service_historical_data  # Ensure correct import

logger = get_logger(__name__)  # Initialize logger


class HistoricalDataUpdater:
    """Fetches historical data from Kite API and updates the database asynchronously."""

    def __init__(self, instruments):
        self.kite = ZerodhaKiteConnect.get_kite_conn()
        self.instruments = instruments  # List of instrument tokens

    async def fetch_historical_data(self, instrument_token, interval):
        """Fetches historical data for a given instrument and interval."""
        logger.info(f"Fetching {interval} historical data for {instrument_token}...")

        # Define the date range based on Kite API limits
        end_date = datetime.today()
        start_date = end_date - timedelta(days=730) if interval == "5minute" else end_date - timedelta(days=3650)

        try:
            data = self.kite.historical_data(instrument_token, start_date, end_date, interval)
            df = pd.DataFrame(data)

            if df.empty:
                logger.warning(f"No {interval} data received for {instrument_token}.")
                return

            # Asynchronous bulk insert
            await service_historical_data.bulk_insert_historical_data(df, instrument_token, interval)
            logger.info(f"{interval} historical data for {instrument_token} successfully updated.")

        except Exception as e:
            logger.error(f"Error fetching {interval} historical data for {instrument_token}: {e}")

    async def fetch_update_all(self):
        """Fetches and updates historical data for all instruments."""
        tasks = []
        for instrument in self.instruments:
            for interval in ["5minute", "day"]:  # Fetch both 5-min and 1-day data
                tasks.append(self.fetch_historical_data(instrument, interval))

        await asyncio.gather(*tasks)  # Run all tasks concurrently

    async def run(self):
        """Main execution function."""
        await self.fetch_update_all()


if __name__ == "__main__":
    instrument_tokens = [738561, 5633, 256265, 408065]  # Example instrument tokens (NIFTY, BANKNIFTY, etc.)

    updater = HistoricalDataUpdater(instrument_tokens)
    asyncio.run(updater.run())  # Proper way to call an async function
