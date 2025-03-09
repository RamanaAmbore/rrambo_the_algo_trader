from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import ReportProfitLoss
from utils.db_connect import DbConnection as Db


async def exists(symbol: str, isin: str):
    """Check if a profit-loss record exists for a symbol & ISIN."""
    with Db.get_session(sync) as session:
        result = await session.execute(
            select(ReportProfitLoss).where(ReportProfitLoss.symbol.is_(symbol), ReportProfitLoss.isin.is_(isin)))
        return result.scalars().first() is not None


async def get_existing_records(sync=False):
    """Fetch all existing (symbol, ISIN) pairs from the table."""
    with Db.get_session(sync) as session:
        result = await session.execute(select(ReportProfitLoss.symbol, ReportProfitLoss.isin))
        return {(row[0], row[1]) for row in result.fetchall()}


async def get_all_results(account, sync=False):
    """Fetch all backtest results asynchronously."""
    with Db.get_session(sync) as session:
        result = await session.execute(select(ReportProfitLoss).where(ReportProfitLoss.account.is_(account)))
        return result.scalars().all()


async def bulk_insert(records, sync=False):
    """Insert multiple profit/loss records in bulk."""
    for record in records:
        warning_messages = []

        # Validate and clean data
        if record.buy_value == "":
            record.buy_value = 0.0
            warning_messages.append("Buy value was empty, set to 0.0")
        if record.sell_value == "":
            record.sell_value = 0.0
            warning_messages.append("Sell value was empty, set to 0.0")
        if record.realized_pnl == "":
            record.realized_pnl = 0.0
            warning_messages.append("Realized P&L was empty, set to 0.0")
        if record.timestamp == "":
            record.timestamp = None
            warning_messages.append("Timestamp was empty, set to None")

        if warning_messages:
            record.warning = True
            record.notes = "; ".join(warning_messages)
    with Db.get_session(sync) as session:
        session.add_all(records)
        await session.commit()
