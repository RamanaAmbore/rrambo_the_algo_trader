from typing import Union, List

import pandas as pd

from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import Positions
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = Positions


class ServicePositions(SingletonBase, ServiceBase):
    """Service class for managing trading positions."""

    model = Positions
    conflict_cols = ['schedule']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)

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
