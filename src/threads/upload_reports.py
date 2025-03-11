import glob
import os
from math import nan
from typing import Type, Dict, Optional

import pandas as pd

from src.models import ReportLedgerEntries
from src.models import ReportProfitLoss
from src.models import ReportTradebook
from src.utils.date_time_utils import INDIAN_TIMEZONE
from src.core.db_manager import DbManager
from src.utils.logger import get_logger
from src.utils.parameter_manager import ParameterManager as Parm

logger = get_logger(__name__)


class ReportUploader:
    """Handles report file processing and database uploads."""
    
    MODEL_MAPPING: Dict[str, Type] = {
        "report_tradebook": ReportTradebook,
        "pnl": ReportProfitLoss,
        "ledger": ReportLedgerEntries
    }

    def __init__(self):
        self.db = DbManager()

    @staticmethod
    def to_ist(timestamp) -> Optional[pd.Timestamp]:
        """Convert a timestamp to IST timezone."""
        if pd.isna(timestamp) or timestamp is None:
            return None
        ts = pd.to_datetime(timestamp)
        return ts.tz_localize("UTC").tz_convert(INDIAN_TIMEZONE) if ts.tzinfo is None else ts.astimezone(INDIAN_TIMEZONE)
    @staticmethod
    def read_file(file_path: str) -> Optional[pd.DataFrame]:
        """Read CSV or Excel file into DataFrame."""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None

        try:
            if file_path.endswith(".csv"):
                return pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                return pd.read_excel(file_path)
            return None
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def process_tradebook(self, row: pd.Series, existing_records: set) -> Optional[ReportTradebook]:
        """Process tradebook record."""
        if not Parm.DOWNLOAD_TRADEBOOK or row["trade_id"] in existing_records:
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
            trade_date=self.to_ist(row["trade_date"]),
            order_execution_time=self.to_ist(row["order_execution_time"]),
            expiry_date=self.to_ist(row.get("expiry_date")),
            instrument_type="Options" if row.get("expiry_date") else "Equity"
        )
    @staticmethod
    def process_pnl(row: pd.Series, existing_records: set) -> Optional[ReportProfitLoss]:
        """Process P&L record."""
        if not Parm.DOWNLOAD_PNL or (row["Symbol"], row["ISIN"]) in existing_records:
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
        if not Parm.DOWNLOAD_LEDGER or (
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

    def load_data(self, file_path: str, model_type: str) -> None:
        """Load data from file into database."""
        df = self.read_file(file_path)
        if df is None or df.empty:
            return

        if model_type == 'pnl':
            df = self.prepare_pnl_data(df)

        df = df.fillna("")
        model = self.MODEL_MAPPING[model_type]
        
        with self.db.get_sync_session() as session:
            existing_records = model.get_existing_records_sync(session)
            processor = getattr(self, f"process_{model_type}")
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

    def process_directory(self, directory: str, prefix: str) -> None:
        """Process all matching files in directory."""
        if not os.path.exists(directory):
            logger.error(f"Directory not found: {directory}")
            return

        for file_path in glob.glob(os.path.join(directory, f"{prefix}*.csv")):
            self.load_data(file_path, prefix)

def main():
    """Main function to process reports."""
    try:
        logger.info("Starting report upload process...")
        uploader = ReportUploader()
        uploader.process_directory(Parm.DOWNLOAD_DIR, "report_tradebook")
        uploader.process_directory(Parm.DOWNLOAD_DIR, "pnl")
        uploader.process_directory(Parm.DOWNLOAD_DIR, "ledger")
        logger.info("Report upload process completed")
    except Exception as e:
        logger.error(f"Main process failed: {e}")
        raise

if __name__ == "__main__":
    main()