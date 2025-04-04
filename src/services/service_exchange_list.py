from typing import Union, List

import pandas as pd

from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import ExchangeList
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = ExchangeList


class ServiceExchangeList(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    def __init__(self):
        super().__init__(model)

    async def validate_insert_records(self, records: Union[pd.DataFrame, List[dict]]):
        """Bulk insert multiple trade records, skipping duplicates."""
        records = self.validate_clean_records(records)
        await self.bulk_insert_records(records=records, index_elements=["exchange"],
                                       update_on_conflict=False)

    @staticmethod
    def validate_clean_records(records):
        return records


service_exchange_list = ServiceExchangeList()
