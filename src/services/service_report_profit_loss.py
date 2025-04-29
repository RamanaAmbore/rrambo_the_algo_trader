from typing import Union, List

import pandas as pd

from src.helpers.decorators import singleton_init_guard
from src.helpers.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import ReportProfitLoss
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = ReportProfitLoss


class ServiceReportProfitLoss(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = ReportProfitLoss
    conflict_cols = ["account",
                     "symbol",
                     "isin",
                     "quantity",
                     "buy_value",
                     "sell_value"]

    @singleton_init_guard
    def __init__(self):
        """Ensure __init__ is only called once."""

        super().__init__(self.model, self.conflict_cols)

    async def validate_insert_records(self, records: Union[pd.DataFrame, List[dict]]):
        """Bulk insert holdings data, skipping duplicates. Supports both DataFrame and list of dicts."""
        records = records.iloc[:, 1:]
        await self.bulk_insert_records(records=records, index_elements=self.conflict_cols)

    @staticmethod
    def validate_clean_records(records):
        """Cleans and validates trade records before inserting into the database."""

        return records


service_report_profit_loss = ServiceReportProfitLoss()
