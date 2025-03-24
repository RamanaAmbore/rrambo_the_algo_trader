from typing import Union, List

import pandas as pd

from src.helpers.logger import get_logger
from src.models import StockList
from src.services.service_base import ServiceBase, validate_cast_parameter

logger = get_logger(__name__)

model = StockList


class ServiceStockList(ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    def __init__(self):
        super().__init__(model)

    @validate_cast_parameter
    async def validate_insert_records(self, records: Union[pd.DataFrame, List[dict]]):
        """Bulk insert multiple trade records, skipping duplicates."""

        records = self.validate_clean_records(records).to_dict(orient="records")

        await self.bulk_insert_records(records=records, index_elements=["tradingsymbol", 'exchange'], update_on_conflict=True)

    @staticmethod
    def validate_clean_records(df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates trade records before inserting into the database."""
        # Ensure expiry column is handled properly
        df["expiry"] = df["expiry"].astype(str).replace("NaT", "")
        df["lot_size"] = df["lot_size"].astype(int)
        df["tick_size"] = df["tick_size"].astype(float)  # Decimal-compatible type
        df["last_price"] = df["last_price"].astype(float)  # Decimal-compatible type
        df["strike"] = df["strike"].astype(float)  # Decimal-compatible type
        return df


service_stock_list = ServiceStockList()
