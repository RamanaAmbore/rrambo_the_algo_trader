import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.logger import get_logger
from utils.db_connection import get_async_session
from zerodha_kite import ZerodhaKite
from models.trades import Trades
from models.order_history import Orders
from models.position import Position

logger = get_logger(__name__)
INDIAN_TZ = ZoneInfo("Asia/Kolkata")


async def fetch_and_sync_trades():
    """Fetch trades from Kite API and insert missing ones into the database."""
    logger.info("Fetching trades from Kite API...")
    kite = ZerodhaKite.get_kite_conn()
    api_trades = await asyncio.to_thread(kite.trades)

    async with get_async_session() as session:
        existing_trades = await Trades.get_all_trades(session)
        existing_trade_ids = {trade.order_id for trade in existing_trades}

        new_trades = [Trades.from_api_data(trade) for trade in api_trades if trade["order_id"] not in existing_trade_ids]

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

    async with get_async_session() as session:
        existing_orders = await Orders.get_all_orders(session)
        existing_order_ids = {order.order_id for order in existing_orders}

        new_orders = [Orders.from_api_data(order) for order in api_orders if order["order_id"] not in existing_order_ids]

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

    async with get_async_session() as session:
        existing_positions = await Position.get_all_positions(session)
        existing_position_keys = {(pos.trading_symbol, pos.exchange) for pos in existing_positions}

        new_positions = [
            Position.from_api_data(pos)
            for pos in api_positions
            if (pos["tradingsymbol"], pos["exchange"]) not in existing_position_keys
        ]

        if new_positions:
            session.add_all(new_positions)
            await session.commit()
            logger.info(f"Inserted {len(new_positions)} new positions.")
        else:
            logger.info("No new positions to insert.")


async def sync_all():
    """Run all sync tasks."""
    logger.info("Starting daily trade, order, and position synchronization...")
    await fetch_and_sync_trades()
    await fetch_and_sync_orders()
    await fetch_and_sync_positions()
    logger.info("Daily synchronization completed.")


def schedule_sync():
    """Schedule daily synchronization at 8:00 AM IST."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(sync_all, "cron", hour=8, minute=0, timezone=INDIAN_TZ)
    scheduler.start()
    logger.info("Scheduled daily sync at 08:00 AM IST.")

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down daily sync scheduler.")


if __name__ == "__main__":
    schedule_sync()
