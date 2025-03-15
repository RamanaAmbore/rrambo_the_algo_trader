from math import nan
from typing import Optional

import pandas as pd

from src.core.database_manager import DatabaseManager as Db
from src.services.report_profit_loss_service import ReportProfitLossService
from src.services.report_tradebook_service import ReportTradebookService
from src.services.report_profit_loss_service import ReportProfitLossService
from src.utils.date_time_utils import INDIAN_TIMEZONE
from src.utils.logger import get_logger
from src.utils.parameter_manager import ParameterManager as Parms, sc
from src.utils.utils import read_files_by_regex_patterns

logger = get_logger(__name__)


class ReportUploader:
    _initialized = False
    _refresh_reports = None
    file_xref = None

    @classmethod
    def __initialize(cls, refresh=False):
        """Handles report file processing and database uploads."""

        if cls._initialized and not refresh:
            return

        cls.refresh_reports = {"tradebook": Parms.REFRESH_TRADEBOOK,
                               "pnl": Parms.REFRESH_PNL,
                               "ledger": Parms.REFRESH_LEDGER}

        file_regex_pattern = {"tradebook": sc.REPORTS_PARM['TRADEBOOK']['file_regex'],
                              "pnl": sc.REPORTS_PARM['PNL']['file_regex'],
                              "ledger": sc.REPORTS_PARM['LEDGER']['file_regex']}
        regex_xref = {}
        for key, val in file_regex_pattern.items():
            if cls.refresh_reports[key]:
                regex_xref[key] = file_regex_pattern[key]

        cls.file_xref = read_files_by_regex_patterns(Parms.DOWNLOAD_DIR, regex_xref)

    @staticmethod
    def to_ist(timestamp) -> Optional[pd.Timestamp]:
        """Convert a timestamp to IST timezone."""
        if pd.isna(timestamp) or timestamp is None:
            return None
        ts = pd.to_datetime(timestamp)
        return ts.tz_localize("UTC").tz_convert(INDIAN_TIMEZONE) if ts.tzinfo is None else ts.astimezone(
            INDIAN_TIMEZONE)

    @classmethod
    def process_tradebook(cls, row: pd.Series, existing_records: set) -> Optional[ReportTradebook]:
        """Process tradebook record."""
        if not Parms.TRADEBOOK or row["trade_id"] in existing_records:
            return None

        return ReportTradebook(
            trade_id=row["trade_id"],
            order_id=row["order_id"],
            trading_symbol="" if row["symbol"] == nan else row["symbol"],
            isin=row.get("isin"),
            exchange=row["exchange"],
            segment=row["segment"],
            series=row["series"],
            trade_type=row["trade_type"],
            auction=row.get("auction", False),
            quantity=row["quantity"],
            price=row["price"],
            trade_date=cls.to_ist(row["trade_date"]),
            order_execution_time=cls.to_ist(row["order_execution_time"]),
            expiry_date=cls.to_ist(row.get("expiry_date")),
            instrument_type="Options" if row.get("expiry_date") else "Equity"
        )

    @staticmethod
    def process_pnl(row: pd.Series, existing_records: set) -> Optional[ReportProfitLoss]:
        """Process P&L record."""
        if not Parms.PNL or (row["Symbol"], row["ISIN"]) in existing_records:
            return None

        return ReportProfitLoss(
            symbol=row["Symbol"],
            isin=row["ISIN"],
            quantity=row["Quantity"],
            buy_value=row["Buy Value"],
            sell_value=row["Sell Value"],
            realized_pnl=row["Realized P&L"],
            realized_pnl_pct=row["Realized P&L Pct."],
            previous_closing_price=row.get("Previous Closing Price"),
            open_quantity=row["Open Quantity"],
            open_quantity_type=row["Open Quantity Type"],
            open_value=row["Open Value"],
            unrealized_pnl=row["Unrealized P&L"],
            unrealized_pnl_pct=row["Unrealized P&L Pct."]
        )

    @staticmethod
    def process_ledger(row: pd.Series, existing_records: set) -> Optional[ReportLedgerEntries]:
        """Process ledger record."""
        if not Parms.LEDGER or (
                row['particulars'], row['posting_date'], row['cost_center'],
                row['voucher_type'], row['debit'], row['credit'], row['net_balance']
        ) in existing_records:
            return None

        return ReportLedgerEntries(
            particulars=row['particulars'],
            posting_date=None if row['posting_date'] == '' else row['posting_date'],
            cost_center=row['cost_center'],
            voucher_type=row['voucher_type'],
            debit=0 if row['debit'] == '' else row['debit'],
            credit=0 if row['credit'] == '' else row['credit'],
            net_balance=row['net_balance'],
            source="BATCH"
        )

    @classmethod
    def upload_reports(cls):
        """Main function to process reports."""
        cls.__initialize()
        try:
            logger.info("Starting report upload process...")
            for report, files in cls.file_xref.items():
                if report == 'TRADEBOOK':
                    existing_records = ReportTradebookService.bulk_insert_records()
                elif report == 'PNL':
                    existing_records = ReportProfitLossService.bulk_insert_records()
                elif report == 'LEDGER':
                    existing_records = ReportProfitLossService.get_existing_records()

                for file_details in files:
                    match_groups = file_details['match_groups']
                    df = file_details['content']
                    if df is None or df.empty:
                        return

                    if report == 'pnl':
                        header_row_idx = df[df["Unnamed: 1"] == "Symbol"].index[0]
                        df.columns = df.iloc[header_row_idx]
                        df = df.iloc[header_row_idx + 1:].reset_index(drop=True)

                    df = df.fillna("")

                    with Db.get_sync_session() as session:
                        existing_records = model.get_existing_records_sync(session)
                        processor = getattr(cls, f"process_{model_type}")
                        new_records = [
                            record for record in (
                                processor(row, existing_records)
                                for _, row in df.iterrows()
                            )
                            if record is not None
                        ]

                        if new_records:
                            model.bulk_insert_sync(session, new_records)
                            logger.info(f"✅ Inserted {len(new_records)} new records into {model.__tablename__}")
            uploader.process_directory(Parms.DOWNLOAD_DIR, "report_tradebook")
            logger.info("Report upload process completed")
        except Exception as e:
            logger.error(f"Main process failed: {e}")
            raise


if __name__ == "__main__":
    ReportUploader.upload_reports()
