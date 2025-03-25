from typing import Union, List

import pandas as pd

from src.helpers.date_time_utils import convert_to_timezone
from src.helpers.logger import get_logger
from src.models import ReportLedgerEntries
from src.services.service_base import ServiceBase, check_for_empty_input

logger = get_logger(__name__)

model = ReportLedgerEntries


class ServiceBaseReportLedgerEntry(ServiceBase):
    """Service class for handling ReportTradebook database operations."""

    def __init__(self):
        super().__init__(model)

    @check_for_empty_input
    async def validate_insert_records(self, records: Union[pd.DataFrame, List[dict]]):
        """Bulk insert holdings data, skipping duplicates. Supports both DataFrame and list of dicts."""

        await self.bulk_insert_records(records=records, index_elements=['account',
                                                                        'particulars',
                                                                        'posting_date',
                                                                        'cost_center',
                                                                        'voucher_type',
                                                                        'debit',
                                                                        'credit',
                                                                        'net_balance'])

        logger.info(f"Bulk processed {len(records)} records.")

    @staticmethod
    def validate_clean_records(records):
        """Cleans and validates trade records before inserting into the database."""
        # Convert list of dicts to DataFrame if needed
        records = pd.DataFrame(records) if isinstance(records, list) else records

        # Convert date columns with timezone
        for col, fmt, return_date in [("posting_date", "%Y-%m-%d", True)]:
            if col in records:
                records[col] = records[col].apply(
                    lambda x: convert_to_timezone(x, format=fmt, return_date=return_date) if pd.notna(x) else None
                )
        records = records.to_dict(orient="records")
        return records


service_report_ledger_entry = ServiceBaseReportLedgerEntry()
