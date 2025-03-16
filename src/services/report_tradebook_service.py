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
    async def bulk_insert_report_records(cls, trade_records: pd.DataFrame | List[Dict[str, Any]]):
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


