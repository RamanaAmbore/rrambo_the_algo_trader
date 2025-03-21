import pandas as pd
from src.helpers.logger import get_logger
from src.models import Positions
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = Positions


class ServicePositions(ServiceBase):
    """Service class for managing trading positions."""

    def __init__(self):
        super().__init__(model)

    async def bulk_insert_positions(self, records_df: pd.DataFrame):
        """Bulk insert positions data after validation."""
        if records_df.empty:
            logger.info("No positions data to insert.")
            return

        await self.delete_all_records()
        table_columns = {c.name for c in self.model.__table__.columns}
        valid_columns = [c for c in records_df.columns if c in table_columns]
        records = self.validate_clean_records(records_df)[valid_columns].to_dict(orient="records")

        await self.bulk_insert_records(records=records, index_elements=["account", "tradingsymbol"])

    @staticmethod
    def validate_clean_records(df: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates positions data before inserting into DB."""
        df["quantity"] = df["quantity"].astype(int)
        df["overnight_quantity"] = df["overnight_quantity"].astype(int)
        df["buy_quantity"] = df["buy_quantity"].astype(int)
        df["sell_quantity"] = df["sell_quantity"].astype(int)
        df["buy_price"] = df["buy_price"].astype(float)
        df["sell_price"] = df["sell_price"].astype(float)
        df["buy_value"] = df["buy_value"].astype(float)
        df["sell_value"] = df["sell_value"].astype(float)
        df["pnl"] = df["pnl"].fillna(0).astype(float)
        df["realised"] = df["realised"].fillna(0).astype(float)
        df["unrealised"] = df["unrealised"].fillna(0).astype(float)
        df["last_price"] = df["last_price"].astype(float)
        df["close_price"] = df["close_price"].fillna(0).astype(float)
        df["multiplier"] = df["multiplier"].astype(float)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df


service_positions = ServicePositions()
