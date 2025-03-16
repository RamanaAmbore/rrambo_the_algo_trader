from typing import Any, Dict, List, Union
import pandas as pd
from src.models.report_tradebook import ReportTradebook
from src.services.base_service import BaseService
from src.utils.date_time_utils import convert_to_timezone


class ReportTradebookService(BaseService):
    """Service class for handling ReportTradebook database operations."""

    model = ReportTradebook

    @classmethod
    async def bulk_insert_report_records(cls, data_records: Union[pd.DataFrame, List[Dict[str, Any]]]):
        """Bulk insert multiple trade records, skipping duplicates."""

        # Convert list of dicts to DataFrame if necessary
        if isinstance(data_records, list):
            data_records = pd.DataFrame(data_records)

        data_records = cls.validate_clean_records(data_records)

        # Call the parent's bulk insert method correctly
        await super().bulk_insert_report_records(cls.model, data_records)

    @classmethod
    def validate_clean_records(cls, data_records: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates trade records before inserting into the database."""

        # # Replace NaN values with None
        # for col in ["isin", "series"]:
        #     if col in data_records:
        #         data_records[col] = data_records[col].apply(lambda x: None if pd.isna(x) else x)

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

