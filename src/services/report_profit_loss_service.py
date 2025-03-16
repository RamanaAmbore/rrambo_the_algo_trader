from typing import Any, Dict, List, Union

import pandas as pd

from src.models import ReportProfitLoss
from src.services.base_service import BaseService
from src.utils.date_time_utils import convert_to_timezone


class ReportProfitLossService(BaseService):
    """Service class for handling ReportTradebook database operations."""

    model = ReportProfitLoss

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

        pass
