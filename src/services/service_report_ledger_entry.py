import pandas as pd

from src.helpers.date_time_utils import convert_to_timezone
from src.helpers.logger import get_logger
from src.models import ReportLedgerEntries
from src.services.service_base import ServiceBase

logger = get_logger(__name__)

model = ReportLedgerEntries


class ServiceBaseReportLedgerEntry(ServiceBase):
    """Service class for handling ReportTradebook database operations."""

    def __init__(self):
        super().__init__(model)

    async def insert_report_records(self, records_df: pd.DataFrame):
        """Bulk insert multiple trade records, skipping duplicates."""
        if records_df.empty:
            logger.info("No valid records to process.")
            return

        table_columns = {c.name for c in self.model.__table__.columns}
        valid_columns = [c for c in records_df.columns if c in table_columns]

        records = self.validate_clean_records(records_df)[list(valid_columns)].to_dict(orient="records")

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
    def validate_clean_records(data_records: pd.DataFrame) -> pd.DataFrame:
        """Cleans and validates trade records before inserting into the database."""

        # Convert date columns with timezone
        for col, fmt, return_date in [("posting_date", "%Y-%m-%d", True)]:
            if col in data_records:
                data_records[col] = data_records[col].apply(
                    lambda x: convert_to_timezone(x, format=fmt, return_date=return_date) if pd.notna(x) else None
                )

        return data_records


service_report_ledger_entry = ServiceBaseReportLedgerEntry()
