from typing import Union, List

import pandas as pd

from src.helpers.date_time_utils import convert_to_timezone
from src.helpers.logger import get_logger
from src.models.report_tradebook import ReportTradebook
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = ReportTradebook


class ServiceReportTradebook(ServiceBase):
    """Service class for handling ReportTradebook database operations."""

    def __init__(self):
        super().__init__(model)

    async def validate_insert_holdings(self, records: Union[pd.DataFrame, List[dict]]):
        """Bulk insert holdings data, skipping duplicates. Supports both DataFrame and list of dicts."""

        if not records or (isinstance(records, pd.DataFrame) and records.empty):
            logger.info("No valid holding records to process.")
            return

        # Convert list of dicts to DataFrame if needed
        if isinstance(records, list):
            records_df = pd.DataFrame(records)
        else:
            records_df = records

        table_columns = {c.name for c in self.model.__table__.columns}
        valid_columns = [c for c in records_df.columns if c in table_columns]
        records = self.validate_clean_records(records_df)[list(valid_columns)].to_dict(orient="records")
        await self.bulk_insert_records(records=records, index_elements=["account", "trade_id"])


    @staticmethod
    def validate_clean_records(data_records: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates trade records before inserting into the database."""

        # Standardize column names
        data_records.columns = (
            data_records.columns.str.lower()
            .str.replace(r"[& ]+", "_", regex=True)
        )

        # Convert date columns with timezone
        for col, fmt, return_date in [
            ("trade_date", "%Y-%m-%d", True),
            ("order_execution_time", "%Y-%m-%dT%H:%M:%S", None),
            ("expiry_date", "%Y-%m-%d", True),
        ]:
            if col in data_records:
                data_records[col] = data_records[col].apply(
                    lambda x: convert_to_timezone(x, format=fmt, return_date=return_date) if pd.notna(x) else None
                )

        return data_records


service_report_tradebook = ServiceReportTradebook()
