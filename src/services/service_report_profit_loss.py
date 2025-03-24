from typing import Union, List

import pandas as pd

from src.helpers.logger import get_logger
from src.models import ReportProfitLoss
from src.services.service_base import ServiceBase, validate_cast_parameter

logger = get_logger(__name__)

model = ReportProfitLoss


class ServiceReportProfitLoss(ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    def __init__(self):
        super().__init__(model)

    @validate_cast_parameter
    async def validate_insert_holdings(self, records: Union[pd.DataFrame, List[dict]]):
        """Bulk insert holdings data, skipping duplicates. Supports both DataFrame and list of dicts."""



        records = self.validate_clean_records(records).to_dict(orient="records")

        await self.bulk_insert_records(records=records, index_elements=["account",
                                                                        "tradingsymbol",
                                                                        "isin",
                                                                        "quantity",
                                                                        "buy_value",
                                                                        "sell_value"])

    @staticmethod
    def validate_clean_records(data_records: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates trade records before inserting into the database."""
        return data_records


service_report_profit_loss = ServiceReportProfitLoss()
