import pandas as pd

from src.helpers.logger import get_logger
from src.models import StockList
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = StockList


class ServiceStockList(ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    def __init__(self):
        super().__init__(model)

    async def bulk_insert_stocks(self, records_df: pd.DataFrame):
        """Bulk insert multiple trade records, skipping duplicates."""

        if records_df.empty:
            logger.info("No valid records to process.")
            return
        await self.delete_all_records()
        table_columns = {c.name for c in self.model.__table__.columns}
        valid_columns = [c for c in records_df.columns if c in table_columns]
        records = self.validate_clean_records(records_df)[list(valid_columns)].to_dict(orient="records")

        await self.bulk_insert_records(records=records, index_elements=["tradingsymbol"])

    @staticmethod
    def validate_clean_records(df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates trade records before inserting into the database."""
        # Ensure expiry column is handled properly
        df["expiry"] = df["expiry"].astype(str).replace("NaT", "")
        df["lot_size"] = df["lot_size"].astype(int)
        df["tick_size"] = df["tick_size"].astype(float)  # Decimal-compatible type
        df["last_price"] = df["tick_size"].astype(float)  # Decimal-compatible type
        df["strike"] = df["strike"].astype(float)  # Decimal-compatible type
        return df


service_stock_list = ServiceStockList()