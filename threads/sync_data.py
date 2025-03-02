import asyncio

from sqlalchemy.exc import SQLAlchemyError

from data_sync.sync_Trades import fetch_and_sync_trades_api
from models.holdings import Holdings
from models.orders import Orders
from models.positions import Positions
from utils.db_connection import DbConnection as Db
from utils.logger import get_logger
from utils.zerodha_kite import ZerodhaKite

# Initialize Async Logger
logger = get_logger(__name__)


async def fetch_and_sync_orders():
    """Fetch orders from Kite API and insert missing ones into the database."""
    logger.info("Fetching orders from Kite API...")
    try:
        kite = ZerodhaKite.get_kite_conn()
        api_orders = await asyncio.to_thread(kite.orders)
    except Exception as ex:
        logger.error(f"Failed to fetch orders: {ex}")
        return

    async for session in Db.get_async_session():
        try:
            existing_orders = await Orders.get_all_orders(session)
            existing_order_ids = {order.order_id for order in existing_orders}

            new_orders = [Orders.from_api_data(order) for order in api_orders if
                          order["order_id"] not in existing_order_ids]

            if new_orders:
                session.bulk_save_objects(new_orders)
                await session.commit()
                logger.info(f"Inserted {len(new_orders)} new orders.")
            else:
                logger.info("No new orders to insert.")

        except SQLAlchemyError as ex:
            logger.error(f"Database error while syncing orders: {ex}")
        except Exception as ex:
            logger.error(f"Unexpected error while syncing orders: {ex}")


async def fetch_and_sync_positions():
    """Fetch positions from Kite API and insert missing ones into the database."""
    logger.info("Fetching positions from Kite API...")
    try:
        kite = ZerodhaKite.get_kite_conn()
        api_positions = await asyncio.to_thread(lambda: kite.positions()["net"])
    except Exception as ex:
        logger.error(f"Failed to fetch positions: {ex}")
        return

    async for session in Db.get_async_session():
        try:
            existing_positions = await Positions.get_all_positions(session)
            existing_position_keys = {(pos.trading_symbol, pos.exchange) for pos in existing_positions}

            new_positions = [Positions.from_api_data(pos) for pos in api_positions if
                             (pos["tradingsymbol"], pos["exchange"]) not in existing_position_keys]

            if new_positions:
                session.bulk_save_objects(new_positions)
                await session.commit()
                logger.info(f"Inserted {len(new_positions)} new positions.")
            else:
                logger.info("No new positions to insert.")

        except SQLAlchemyError as ex:
            logger.error(f"Database error while syncing positions: {ex}")
        except Exception as ex:
            logger.error(f"Unexpected error while syncing positions: {ex}")


async def fetch_and_sync_holdings():
    """Fetch holdings from Kite API and insert missing ones into the database."""
    logger.info("Fetching holdings from Kite API...")
    try:
        kite = ZerodhaKite.get_kite_conn()
        api_holdings = await asyncio.to_thread(kite.holdings)
    except Exception as ex:
        logger.error(f"Failed to fetch holdings: {ex}")
        return

    async for session in Db.get_async_session():
        try:
            existing_holdings = await Holdings.get_all_holdings(session)
            existing_holding_keys = {(h.trading_symbol, h.exchange) for h in existing_holdings}

            new_holdings = [Holdings.from_api_data(h) for h in api_holdings if
                            (h["tradingsymbol"], h["exchange"]) not in existing_holding_keys]

            if new_holdings:
                session.bulk_save_objects(new_holdings)
                await session.commit()
                logger.info(f"Inserted {len(new_holdings)} new holdings.")
            else:
                logger.info("No new holdings to insert.")

        except SQLAlchemyError as ex:
            logger.error(f"Database error while syncing holdings: {ex}")
        except Exception as ex:
            logger.error(f"Unexpected error while syncing holdings: {ex}")





async def sync_all():
    """Run all sync tasks in parallel."""
    logger.info("Starting trade, order, position, and holdings synchronization...")

    # Run all fetch tasks concurrently
    await asyncio.gather(fetch_and_sync_trades_api(), fetch_and_sync_orders(), fetch_and_sync_positions(),
                         fetch_and_sync_holdings(), )

    logger.info("Synchronization completed.")


# 🛠️ TEST CODE: Run sync_all() when executing this script directly
if __name__ == "__main__":
    logger.info("Running sync_data.py in standalone mode...")

    try:
        asyncio.run(sync_all())
    except KeyboardInterrupt:
        logger.info("Sync process interrupted.")
    except Exception as e:
        logger.error(f"Unexpected error in sync process: {e}")
