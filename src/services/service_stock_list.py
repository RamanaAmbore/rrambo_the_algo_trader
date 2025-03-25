from typing import Union, List

import pandas as pd

from src.helpers.logger import get_logger
from src.models import StockList
from src.services.service_base import ServiceBase, check_for_empty_input

logger = get_logger(__name__)

model = StockList


class ServiceStockList(ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    def __init__(self):
        super().__init__(model)

    @check_for_empty_input
    async def validate_insert_records(self, records: Union[pd.DataFrame, List[dict]]):
        """Bulk insert multiple trade records, skipping duplicates."""
        records = self.validate_clean_records(records)
        await self.bulk_insert_records(records=records, index_elements=["tradingsymbol", 'exchange'],
                                       update_on_conflict=True)

    @staticmethod
    def validate_clean_records(records):
        """Cleans and validates trade records before inserting into the database."""
        # Ensure expiry column is handled properly
        for record in records:
            if record['expiry'] == '':
                record['expiry'] = None
        return records


service_stock_list = ServiceStockList()
