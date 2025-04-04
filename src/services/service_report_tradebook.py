import pandas as pd

from src.core.singleton_base import SingletonBase
from src.helpers.date_time_utils import convert_to_timezone
from src.helpers.logger import get_logger
from src.models.report_tradebook import ReportTradebook
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = ReportTradebook


class ServiceReportTradebook(SingletonBase, ServiceBase):
    """Service class for handling ReportTradebook database operations."""
    model = ReportTradebook
    conflict_cols = ['schedule']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)

    async def validate_insert_records(self, records):
        """Bulk insert holdings data, skipping duplicates. Supports both DataFrame and list of dicts."""

        records = self.validate_clean_records(records)

        await self.bulk_insert_records(records=records, index_elements=["account", "trade_id"])

    @staticmethod
    def validate_clean_records(records: pd.DataFrame):
        """Cleans and validates trade records before inserting into the database."""

        # Convert list of dicts to DataFrame if needed
        records = pd.DataFrame(records) if isinstance(records, list) else records

        # Standardize column names
        records.columns = (
            records.columns.str.lower()
            .str.replace(r"[& ]+", "_", regex=True)
        )

        # Convert date columns with timezone
        for col, fmt, return_date in [
            ("trade_date", "%Y-%m-%d", True),
            ("order_execution_time", "%Y-%m-%dT%H:%M:%S", None),
            ("expiry_date", "%Y-%m-%d", True),
        ]:
            if col in records:
                records[col] = records[col].apply(
                    lambda x: convert_to_timezone(x, format=fmt, return_date=return_date) if pd.notna(x) else None
                )

        records = records.to_dict(orient="records")

        return records


service_report_tradebook = ServiceReportTradebook()
