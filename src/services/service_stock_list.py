from typing import Union, List

import pandas as pd

from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import StockList
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = StockList


class ServiceStockList(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = StockList
    conflict_cols = ['account']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)

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
