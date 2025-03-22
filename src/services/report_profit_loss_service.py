import pandas as pd

from src.helpers.logger import get_logger
from src.models import ReportProfitLoss
from src.services.base_service import BaseService

logger = get_logger(__name__)

model = ReportProfitLoss


class ReportProfitLossService(BaseService):
    """Service class for handling ReportProfitLoss database operations."""

    def __init__(self):
        super().__init__(model)

    async def insert_report_records(self, records_df: pd.DataFrame):
        """Bulk insert multiple trade records, skipping duplicates."""
        if records_df.empty:
            logger.info("No valid records to process.")
            return

        table_columns = {c.name for c in self.model.__table__.columns}
        valid_columns = [c for c in records_df.columns if c in table_columns]
        records = self.validate_clean_records(records_df)[list(valid_columns)].to_dict(orient="records")

        await self.bulk_insert_records(records=records, index_elements=["account",
                                                                        "symbol",
                                                                        "isin",
                                                                        "quantity",
                                                                        "buy_value",
                                                                        "sell_value"])

    @staticmethod
    def validate_clean_records(data_records: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates trade records before inserting into the database."""
        return data_records


report_profitLoss_service = ReportProfitLossService()
