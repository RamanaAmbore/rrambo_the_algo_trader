from typing import Union, List

import pandas as pd

from src.helpers.logger import get_logger
from src.models import Positions
from src.services.service_base import ServiceBase, check_for_empty_input

logger = get_logger(__name__)

model = Positions


class ServicePositions(ServiceBase):
    """Service class for managing trading positions."""

    def __init__(self):
        super().__init__(model)

    @check_for_empty_input
    async def validate_insert_records(self, records: Union[pd.DataFrame, List[dict]]):
        """Bulk insert holdings data, skipping duplicates. Supports both DataFrame and list of dicts."""

        await self.delete_all_records()

        # records = self.validate_clean_records(records).to_dict(orient="records")
        await self.bulk_insert_records(records=records, index_elements=[])

    @staticmethod
    def validate_clean_records(records):
        """Cleans and validates positions data before inserting into DB."""

        return records


service_positions = ServicePositions()
