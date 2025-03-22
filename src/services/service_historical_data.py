import pandas as pd
from src.helpers.logger import get_logger
from src.models import HistoricalData
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = HistoricalData


class ServiceHistoricalData(ServiceBase):
    """Service class for handling historical market data database operations."""

    def __init__(self):
        super().__init__(model)

    async def bulk_insert_historical_data(self, records_df: pd.DataFrame):
        """Bulk insert historical data, skipping duplicates."""
        if records_df.empty:
            logger.info("No valid historical records to process.")
            return

        await self.delete_all_records()
        table_columns = {c.name for c in self.model.__table__.columns}
        valid_columns = [c for c in records_df.columns if c in table_columns]
        records = self.validate_clean_records(records_df)[list(valid_columns)].to_dict(orient="records")

        await self.bulk_insert_records(records=records, index_elements=["instrument_token", "timestamp"])

    @staticmethod
    def validate_clean_records(df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates historical data before inserting into the database."""
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(int)
        df["interval"] = df["interval"].astype(str)
        return df


service_historical_data = ServiceHistoricalData()
