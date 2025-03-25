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

    async def validate_insert_records(self, records: Union[pd.DataFrame, List[dict]]):
        """Bulk insert holdings data, skipping duplicates. Supports both DataFrame and list of dicts."""

        await self.delete_all_records()

        # records = self.validate_clean_records(records).to_dict(orient="records")
        await self.bulk_insert_records(records=records, index_elements=[])

    @staticmethod
    def validate_clean_records(records):
        """Cleans and validates holdings data before inserting into the database."""

        return records


service_holdings = ServiceHoldings()
