from sqlalchemy.ext.asyncio import AsyncSession
from models.order_history import Trades, OrderHistory
from models.portfolio_holdings import PortfolioHoldings
from models.market_hours import MarketData

async def get_active_instruments(db_session: AsyncSession):
    """Fetch all instruments that need live tick updates."""
    holdings = await db_session.execute("SELECT trading_symbol FROM portfolio_holdings")
    positions = await db_session.execute("SELECT trading_symbol FROM trades")
    orders = await db_session.execute("SELECT trading_symbol FROM order_history WHERE status = 'OPEN'")

    symbols = set([row[0] for row in holdings.fetchall() + positions.fetchall() + orders.fetchall()])
    return list(symbols)
