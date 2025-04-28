import pandas as pd

from src.core.decorators import singleton_init_guard
from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import Orders
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = Orders


class ServiceOrders(SingletonBase, ServiceBase):
    """Service class for handling orders database operations."""

    @singleton_init_guard
    def __init__(self):
        super().__init__(model)

    async def bulk_insert_orders(self, records_df: pd.DataFrame):
        """Bulk insert orders data, skipping duplicates."""
        if records_df.empty:
            logger.info("No valid order records to process.")
            return

        await self.delete_all_records()
        table_columns = {c.name for c in self.model.__table__.columns}
        valid_columns = [c for c in records_df.columns if c in table_columns]
        records = self.validate_clean_records(records_df)[valid_columns].to_dict(orient="records")

        await self.bulk_insert_records(records=records, index_elements=["order_id"])

    @staticmethod
    def validate_clean_records(df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates order data before inserting into the database."""
        df["quantity"] = df["quantity"].astype(int)
        df["price"] = df["price"].astype(float)
        df["filled_quantity"] = df["filled_quantity"].fillna(0).astype(int)
        df["pending_quantity"] = df["pending_quantity"].fillna(0).astype(int)
        df["modified"] = df["modified"].astype(bool)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df


service_orders = ServiceOrders()
