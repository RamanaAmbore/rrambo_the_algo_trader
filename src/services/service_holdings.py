from typing import Union, List

import pandas as pd
from src.helpers.logger import get_logger
from src.models import Holdings
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = Holdings


class ServiceHoldings(ServiceBase):
    """Service class for handling holdings database operations."""

    def __init__(self):
        super().__init__(model)

    async def bulk_insert_holdings(self, records: Union[pd.DataFrame, List[dict]]):
        """Bulk insert holdings data, skipping duplicates. Supports both DataFrame and list of dicts."""

        if not records or (isinstance(records, pd.DataFrame) and records.empty):
            logger.info("No valid holding records to process.")
            return

        # Convert list of dicts to DataFrame if needed
        if isinstance(records, list):
            records_df = pd.DataFrame(records)
        else:
            records_df = records

        await self.delete_all_records()

        table_columns = {c.name for c in self.model.__table__.columns}
        valid_columns = [c for c in records_df.columns if c in table_columns]
        records = self.validate_clean_records(records_df)[valid_columns].to_dict(orient="records")

        await self.bulk_insert_records(records=records, index_elements=[])

    @staticmethod
    def validate_clean_records(df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates holdings data before inserting into the database."""
        df["quantity"] = df["quantity"].astype(int)
        df["t1_quantity"] = df["t1_quantity"].fillna(0).astype(int)
        df["average_price"] = df["average_price"].astype(float)
        df["last_price"] = df["last_price"].astype(float)
        df["pnl"] = df["pnl"].fillna(0).astype(float)
        df["collateral_quantity"] = df["collateral_quantity"].fillna(0).astype(int)
        return df


service_holdings = ServiceHoldings()
