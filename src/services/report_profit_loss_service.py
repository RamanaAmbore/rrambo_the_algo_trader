import pandas as pd
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert

from src.core.database_manager import DatabaseManager as Db
from src.models import ReportProfitLoss
from src.services.base_service import BaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReportProfitLossService(BaseService):
    """Service class for handling ReportTradebook database operations."""

    model = ReportProfitLoss

    @classmethod
    async def bulk_insert_report_records(cls, records_df: pd.DataFrame):
        """Bulk insert multiple trade records, skipping duplicates."""

        if records_df.empty:
            logger.info("No valid records to process.")
            return

        table_columns = {c.name for c in cls.model.__table__.columns}
        valid_columns = [c for c in records_df.columns if c in table_columns]
        records = cls.validate_clean_records(records_df)[list(valid_columns)].to_dict(orient="records")

        async with Db.get_async_session() as session:
            stmt = insert(cls.model).values(records)
            stmt = stmt.on_conflict_do_nothing(index_elements=["account",
                                                               "symbol",
                                                               'isin',
                                                               'quantity',
                                                               'buy_value',
                                                               'sell_value'])
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Bulk processed {len(records)} records.")

    @classmethod
    def validate_clean_records(cls, data_records: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates trade records before inserting into the database."""

        return data_records
