import asyncio

from models.order_history import Orders
from models.portfolio_holdings import PortfolioHoldings  # Import Holdings model
from models.position import Position
from models.trades import Trades
from utils.db_connection import DbConnection as db
from utils.logger import get_logger
from utils.zerodha_kite import ZerodhaKite

# Initialize Async Logger
logger = get_logger(__name__)


async def fetch_and_sync_trades():
    """Fetch trades from Kite API and insert missing ones into the database."""
    logger.log("Fetching trades from Kite API...", level="info")
    kite = ZerodhaKite.get_kite_conn()
    api_trades = await asyncio.to_thread(kite.trades)

    async with db.get_async_session() as session:
        existing_trades = await Trades.get_all_trades(session)
        existing_trade_ids = {trade.order_id for trade in existing_trades}

        new_trades = [Trades.from_api_data(trade) for trade in api_trades if
                      trade["order_id"] not in existing_trade_ids]

        if new_trades:
            session.add_all(new_trades)
            await session.commit()
            logger.log(f"Inserted {len(new_trades)} new trades.", level="info")
        else:
            logger.log("No new trades to insert.", level="info")


async def fetch_and_sync_orders():
    """Fetch orders from Kite API and insert missing ones into the database."""
    logger.log("Fetching orders from Kite API...", level="info")
    kite = ZerodhaKite.get_kite_conn()
    api_orders = await asyncio.to_thread(kite.orders)

    async with db.get_async_session() as session:
        existing_orders = await Orders.get_all_orders(session)
        existing_order_ids = {order.order_id for order in existing_orders}

        new_orders = [Orders.from_api_data(order) for order in api_orders if
                      order["order_id"] not in existing_order_ids]

        if new_orders:
            session.add_all(new_orders)
            await session.commit()
            logger.log(f"Inserted {len(new_orders)} new orders.", level="info")
        else:
            logger.log("No new orders to insert.", level="info")


async def fetch_and_sync_positions():
    """Fetch positions from Kite API and insert missing ones into the database."""
    logger.log("Fetching positions from Kite API...", level="info")
    kite = ZerodhaKite.get_kite_conn()
    api_positions = await asyncio.to_thread(lambda: kite.positions()["net"])

    async with db.get_async_session() as session:
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
            logger.log(f"Inserted {len(new_positions)} new positions.", level="info")
        else:
            logger.log("No new positions to insert.", level="info")


async def fetch_and_sync_holdings():
    """Fetch holdings from Kite API and insert missing ones into the database."""
    logger.log("Fetching holdings from Kite API...", level="info")
    kite = ZerodhaKite.get_kite_conn()
    api_holdings = await asyncio.to_thread(kite.holdings)

    async with db.get_async_session() as session:
        existing_holdings = await PortfolioHoldings.get_all_holdings(session)
        existing_holding_keys = {(h.trading_symbol, h.exchange) for h in existing_holdings}

        new_holdings = [
            PortfolioHoldings.from_api_data(h)
            for h in api_holdings
            if (h["tradingsymbol"], h["exchange"]) not in existing_holding_keys
        ]

        if new_holdings:
            session.add_all(new_holdings)
            await session.commit()
            logger.log(f"Inserted {len(new_holdings)} new holdings.", level="info")
        else:
            logger.log("No new holdings to insert.", level="info")


async def sync_all():
    """Run all sync tasks."""
    logger.log("Starting trade, order, position, and holdings synchronization...", level="info")
    await fetch_and_sync_trades()
    await fetch_and_sync_orders()
    await fetch_and_sync_positions()
    await fetch_and_sync_holdings()
    logger.log("Synchronization completed.", level="info")


# 🛠️ TEST CODE: Run sync_all() when executing this script directly
if __name__ == "__main__":
    logger.log("Running sync_data.py in standalone mode...", level="info")

    try:
        asyncio.run(sync_all())
    except KeyboardInterrupt:
        logger.log("Sync process interrupted.", level="warning")
