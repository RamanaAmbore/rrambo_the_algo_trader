from typing import Any, Dict, List

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.future import select

from src.core.database_manager import DatabaseManager as Db
from src.models.report_tradebook import ReportTradebook
from src.services.base_service import BaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReportTradebookService(BaseService):
    """Service class for handling ReportTradebook database operations."""

    model = ReportTradebook

    @classmethod
    async def insert_trade(cls, trade_data: pd.Series | Dict[str, Any]):
        """Insert a single trade record if the trade_id does not already exist."""
        trade_dict = trade_data.to_dict() if isinstance(trade_data, pd.Series) else trade_data
        trade_id = trade_dict["trade_id"]

        async with Db.get_async_session() as session:
            query = select(cls.model.trade_id).where(cls.model.trade_id == trade_id)
            existing_trade = await session.execute(query)
            existing_trade = existing_trade.scalar_one_or_none()

            if not existing_trade:
                trade_record = cls.model(**trade_dict)
                cls.validate_and_clean(trade_record)
                session.add(trade_record)
                await session.commit()
                logger.info(f"Inserted new trade record: {trade_id}")
            else:
                logger.info(f"Trade ID {trade_id} already exists. Skipping insert.")

    @classmethod
    async def bulk_insert_trades(cls, trade_records: pd.DataFrame | List[Dict[str, Any]]):
        """Bulk insert multiple trade records, skipping duplicates."""
        if isinstance(trade_records, pd.DataFrame):
            trade_records = trade_records.to_dict(orient="records")
        if not trade_records:
            logger.info("No records to insert.")
            return

        async with Db.get_async_session() as session:
            query = select(cls.model.trade_id)
            existing_trade_ids = {row[0] for row in (await session.execute(query)).all()}

            new_trades = [trade for trade in trade_records if trade["trade_id"] not in existing_trade_ids]

            if new_trades:
                stmt = insert(cls.model).values(new_trades)
                stmt = stmt.on_conflict_do_nothing(index_elements=["trade_id"])
                await session.execute(stmt)
                await session.commit()
                logger.info(f"Bulk inserted {len(new_trades)} trade records.")
            else:
                logger.info("No new trades to insert.")

    @classmethod
    def validate_and_clean(cls, record):
        """Validate and clean trade data before insertion."""
        warning_messages = []
        if not record.buy_value:
            record.buy_value = 0.0
            warning_messages.append("Buy value was empty, set to 0.0")
        if not record.sell_value:
            record.sell_value = 0.0
            warning_messages.append("Sell value was empty, set to 0.0")
        if not record.realized_pnl:
            record.realized_pnl = 0.0
            warning_messages.append("Realized P&L was empty, set to 0.0")
        if not record.timestamp:
            record.timestamp = None
            warning_messages.append("Timestamp was empty, set to None")

        if warning_messages:
            record.warning_error = True
            record.notes = "; ".join(warning_messages)
            logger.warning(f"Data corrections for record {record.trade_id}: {'; '.join(warning_messages)}")
