import asyncio
import json

from sqlalchemy.exc import SQLAlchemyError

from src.models.holdings import Holdings
from src.models.orders import Orders
from src.models.positions import Positions
from src.core.db_connect import DbConnect as Db
from src.utils.logger import get_logger
from src.core.kite_api_login import ZerodhaKite

logger = get_logger(__name__)

from datetime import datetime

def parse_datetime(value):
    """Convert string to datetime if needed."""
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    return value
def parse_json(value):
    """Convert string to JSON if needed."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}  # Return empty JSON if parsing fails
    return value


def parse_date(value):
    """Convert string to date if needed."""
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    return value

async def fetch_and_sync_orders():
    """Fetch orders from Kite API and insert missing ones into the database."""
    logger.info("Fetching orders from Kite API...")

    try:
        kite = ZerodhaKite.get_kite_conn()
        api_orders = await asyncio.to_thread(kite.orders)  # Fetch orders in a thread-safe way
    except Exception as ex:
        logger.error(f"Failed to fetch orders: {ex}")
        return

    logger.info(f"Fetched {len(api_orders)} orders from API.")
    logger.info(f'orders: {api_orders[0]}')

    async for session in Db.get_async_session():
        try:
            # Get existing orders from the database
            result = await session.execute(Orders.__table__.select())
            existing_orders = result.fetchall()
            existing_order_ids = {order.order_id for order in existing_orders}

            # Identify new orders and ensure datetime fields are properly converted
            new_orders = []
            for order in api_orders:
                if order["order_id"] not in existing_order_ids:
                    order["exchange_update_timestamp"] = parse_datetime(order.get("exchange_update_timestamp"))
                    order["order_timestamp"] = parse_datetime(order.get("order_timestamp"))
                    order["exchange_timestamp"] = parse_datetime(order.get("exchange_timestamp"))
                    new_orders.append(Orders.from_api_data(order))

            if new_orders:
                session.add_all(new_orders)
                await session.commit()
                logger.info(f"Inserted {len(new_orders)} new orders.")
            else:
                logger.info("No new orders to insert.")

        except SQLAlchemyError as ex:
            logger.error(f"Database error while syncing orders: {ex}")
            await session.rollback()
        except Exception as ex:
            logger.error(f"Unexpected error while syncing orders: {ex}")
        finally:
            await session.close()


async def fetch_and_sync_positions():
    """Fetch positions from Kite API and insert missing ones into the database."""
    logger.info("Fetching positions from Kite API...")
    try:
        kite = ZerodhaKite.get_kite_conn()
        api_positions = await asyncio.to_thread(lambda: kite.positions()["net"])
    except Exception as ex:
        logger.error(f"Failed to fetch positions: {ex}")
        return

    logger.info(f'Positions: {api_positions[0]}')

    async for session in Db.get_async_session():
        try:
            existing_positions = await Positions.get_all_results(session)
            existing_instrument_tokens = {pos.instrument_token for pos in existing_positions}

            new_positions = [Positions.from_api_data(pos) for pos in api_positions if
                pos["instrument_token"] not in existing_instrument_tokens]

            if new_positions:
                session.add_all(new_positions)
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
    logger.info(f"Fetched {len(api_holdings)} holding records from API.")
    if not api_holdings:
        logger.info("No holdings found in API response.")
        return
    logger.info(f'Holdings: {api_holdings[0]}')
    async for session in Db.get_async_session():
        try:
            existing_holdings = await Holdings.get_all_holdings(session)
            existing_holding_keys = {(h.tradingsymbol, h.exchange) for h in existing_holdings}

            new_holdings = []
            for h in api_holdings:
                h["authorised_date"] = parse_datetime(h.get("authorised_date")).date()  # Ensure correct date format
                h["mtf"] = parse_json(h.get("mtf", "{}"))  # Ensure MTF is stored as JSON
                if (h["tradingsymbol"], h["exchange"]) not in existing_holding_keys:
                    new_holdings.append(Holdings.from_api_data(h))

            if new_holdings:
                print(new_holdings[0])
                session.add_all(new_holdings)
                await session.commit()
                logger.info(f"Inserted {len(new_holdings)} new holdings.")
            else:
                logger.info("No new holdings to insert.")

        except SQLAlchemyError as ex:
            logger.error(f"Database error while syncing holdings: {ex}")
            await session.rollback()
        except Exception as ex:
            logger.error(f"Unexpected error while syncing holdings: {ex}")
        finally:
            await session.close()



async def sync_all():
    """Run all sync tasks in parallel."""
    logger.info("Starting order, position, and holdings synchronization...")

    # Run all fetch tasks concurrently
    await asyncio.gather(fetch_and_sync_orders(), fetch_and_sync_positions(), fetch_and_sync_holdings(), )

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
