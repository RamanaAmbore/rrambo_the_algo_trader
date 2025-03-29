import asyncio

from src.core.report_downloader import ReportDownloader
from src.core.report_uploader import ReportUploader
from src.core.zerodha_kite_connect import ZerodhaKiteConnect
from src.helpers.logger import get_logger
from src.services.service_exchange_list import service_exchange_list
from src.services.service_holdings import service_holdings
from src.services.service_positions import service_positions
from src.services.service_stock_list import service_stock_list

logger = get_logger(__name__)  # Initialize logger

kite = ZerodhaKiteConnect.get_kite_conn()


async def sync_stock_list():
    """Fetches stock list from Kite API without filtering and updates the database."""
    try:
        logger.info("Fetching complete stock list from Kite API...")
        records = await asyncio.to_thread(kite.instruments)  # Run in a separate thread
        exchange_set = {record["exchange"] for record in records}
        exchange_set = [{'exchange':record} for record in exchange_set]
        await service_exchange_list.validate_insert_records(exchange_set)  # Async DB insert
        await service_stock_list.validate_insert_records(records)  # Async DB insert
        logger.info("Stock list successfully updated.")
    except Exception as e:
        logger.error(f"Error fetching stock list: {e}")


async def sync_stock_reports():
    """Downloads reports and updates the database."""
    try:
        logger.info("Fetching reports from Zerodha Console...")
        await asyncio.to_thread(ReportDownloader.login_download_reports)  # Run in a separate thread

        await ReportUploader.upload_reports()  # Async upload
        logger.info("Reports successfully updated.")
    except Exception as e:
        logger.error(f"Error syncing stock reports: {e}")


async def sync_positions():
    """Fetches positions from Kite API and updates the database."""
    try:
        logger.info("Fetching positions from Kite API...")
        positions = await asyncio.to_thread(kite.positions)  # Fetch in a separate thread
        records = positions.get("day", []) + positions.get("net", [])

        await service_positions.validate_insert_records(records)  # Async DB insert
        logger.info("Positions successfully updated.")
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")


async def sync_holdings():
    """Fetches holdings from Kite API and updates the database."""
    try:
        logger.info("Fetching holdings from Kite API...")
        records = await asyncio.to_thread(kite.holdings)  # Fetch in a separate thread
        master_rec = {'mtf_average_price': None, 'mtf_initial_margin': None, 'mtf_quantity': None,
                      'mtf_used_quantity': None, 'mtf_value': None}
        for record in records:
            mtf = record.pop('mtf')
            if mtf is None:
                mtf = master_rec

            for k, v in mtf.items():
                record[f'mtf_{k}'] = v

        await service_holdings.validate_insert_records(records)  # Async DB insert
        logger.info("Holdings successfully updated.")
    except Exception as e:
        logger.error(f"Error fetching holdings: {e}")


async def run():
    """Main execution function, running all tasks in parallel."""
    await asyncio.gather(
        # sync_stock_reports(),
        sync_stock_list(),
        # sync_holdings(),
        # sync_positions()
    )


if __name__ == "__main__":
    asyncio.run(run())  # Proper way to call an async function
