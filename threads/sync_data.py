import asyncio

from models.orders import Orders
from models.holdings import Holdings  # Import Holdings model
from models.positions import Positions
from models.trades import Trades
from utils.db_connection import DbConnection as db
from utils.logger import get_logger
from utils.zerodha_kite import ZerodhaKite

# Initialize Async Logger
logger = get_logger(__name__)


async def fetch_and_sync_trades():
    """Fetch trades from Kite API and insert missing ones into the database."""
    logger.info("Fetching trades from Kite API...")
    kite = ZerodhaKite.get_kite_conn()
    api_trades = await asyncio.to_thread(kite.trades)

    async for session in db.get_async_session():
        existing_trades = await Trades.get_all_trades(session)
        existing_trade_ids = {trade.order_id for trade in existing_trades}

        new_trades = [Trades.from_api_data(trade) for trade in api_trades if
                      trade["order_id"] not in existing_trade_ids]

        if new_trades:
            session.add_all(new_trades)
            await session.commit()
            logger.info(f"Inserted {len(new_trades)} new trades.")
        else:
            logger.info("No new trades to insert.")


async def fetch_and_sync_orders():
    """Fetch orders from Kite API and insert missing ones into the database."""
    logger.info("Fetching orders from Kite API...")
    kite = ZerodhaKite.get_kite_conn()
    api_orders = await asyncio.to_thread(kite.orders)

    async for session in db.get_async_session():
        existing_orders = await Orders.get_all_orders(session)
        existing_order_ids = {order.order_id for order in existing_orders}

        new_orders = [Orders.from_api_data(order) for order in api_orders if
                      order["order_id"] not in existing_order_ids]

        if new_orders:
            session.add_all(new_orders)
            await session.commit()
            logger.info(f"Inserted {len(new_orders)} new orders.")
        else:
            logger.info("No new orders to insert.")


async def fetch_and_sync_positions():
    """Fetch positions from Kite API and insert missing ones into the database."""
    logger.info("Fetching positions from Kite API...")
    kite = ZerodhaKite.get_kite_conn()
    api_positions = await asyncio.to_thread(lambda: kite.positions()["net"])

    async for session in db.get_async_session():
        existing_positions = await Positions.get_all_positions(session)
        existing_position_keys = {(pos.trading_symbol, pos.exchange) for pos in existing_positions}

        new_positions = [
            Positions.from_api_data(pos)
            for pos in api_positions
            if (pos["tradingsymbol"], pos["exchange"]) not in existing_position_keys
        ]

        if new_positions:
            session.add_all(new_positions)
            await session.commit()
            logger.info(f"Inserted {len(new_positions)} new positions.")
        else:
            logger.info("No new positions to insert.")


async def fetch_and_sync_holdings():
    """Fetch holdings from Kite API and insert missing ones into the database."""
    logger.info("Fetching holdings from Kite API...")
    kite = ZerodhaKite.get_kite_conn()
    api_holdings = await asyncio.to_thread(kite.holdings)

    async for session in db.get_async_session():
        existing_holdings = await Holdings.get_all_holdings(session)
        existing_holding_keys = {(h.trading_symbol, h.exchange) for h in existing_holdings}

        new_holdings = [
            Holdings.from_api_data(h)
            for h in api_holdings
            if (h["tradingsymbol"], h["exchange"]) not in existing_holding_keys
        ]

        if new_holdings:
            session.add_all(new_holdings)
            await session.commit()
            logger.info(f"Inserted {len(new_holdings)} new holdings.")
        else:
            logger.info("No new holdings to insert.")


async def sync_all():
    """Run all sync tasks."""
    logger.info("Starting trade, order, position, and holdings synchronization...")
    await fetch_and_sync_trades()
    await fetch_and_sync_orders()
    await fetch_and_sync_positions()
    await fetch_and_sync_holdings()
    logger.info("Synchronization completed.")


# 🛠️ TEST CODE: Run sync_all() when executing this script directly
if __name__ == "__main__":
    logger.info("Running sync_data.py in standalone mode...")

    try:
        asyncio.run(sync_all())
    except KeyboardInterrupt:
        logger.info("Sync process interrupted.")
