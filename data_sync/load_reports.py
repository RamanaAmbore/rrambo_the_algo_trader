import asyncio
import glob
import os
from json.decoder import NaN

import pandas as pd
import pytz

from models.ledger_entry import LedgerEntry
from models.profit_loss import ProfitLoss
from models.trades import Trades  # Removed TradeTypeEnum import
from utils.config_loader import Env, sc
from utils.db_connection import DbConnection as Db
from utils.logger import get_logger

logger = get_logger(__name__)  # Initialize logger
IST = pytz.timezone("Asia/Kolkata")


def return_model_for_prefix(report_prefix: str):
    """Return the correct model based on the file prefix."""
    model_mapping = {"tradebook": Trades, "pnl": ProfitLoss, "ledger": LedgerEntry}
    return model_mapping.get(report_prefix)


def to_ist(timestamp):
    """Convert a timestamp to IST (if it's not None)."""
    if pd.isna(timestamp) or timestamp is None:
        return None
    ts = pd.to_datetime(timestamp)
    return ts.tz_localize("UTC").tz_convert(IST) if ts.tzinfo is None else ts.astimezone(IST)


async def load_data(file_path: str, model, prefix):
    """Load data from CSV/Excel into the database efficiently."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    # Read file
    df = None
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)

    if prefix == 'pnl':
        # Step 1: Find the row index where a specific value (e.g., "ID") exists in column "A"
        header_row_idx = df[df["Unnamed: 1"] == "Symbol"].index[0]

        # Step 2: Set this row as the new header
        df.columns = df.iloc[header_row_idx]

        # Step 3: Remove all rows before the new header and reset index
        df = df.iloc[header_row_idx + 1:].reset_index(drop=True)

    if df is None or df.empty:
        logger.warning(f"No data in {file_path}")
        return

    # Replace NaN values with None (to avoid database errors)
    df = df.fillna("")

    async for session in Db.get_async_session():
        # Fetch existing records
        existing_records = await model.get_existing_records(session)

        # Prepare new records for bulk insert
        new_records = []
        for _, row in df.iterrows():
            if model == Trades and row["trade_id"] not in existing_records:
                print(row['symbol'])
                new_records.append(Trades(trade_id=row["trade_id"], order_id=row["order_id"],
                                          trading_symbol="" if row["symbol"] == NaN else row["symbol"],
                                          isin=row.get("isin"), exchange=row["exchange"], segment=row["segment"],
                                          series=row["series"], trade_type=row["trade_type"],  # Kept as a string
                                          auction=row.get("auction", False), quantity=row["quantity"],
                                          price=row["price"], trade_date=pd.to_datetime(row["trade_date"]).tz_localize(
                        sc.INDIAN_TIMEZONE) if row["trade_date"] else None,
                                          order_execution_time=pd.to_datetime(row["order_execution_time"]).tz_localize(
                                              sc.INDIAN_TIMEZONE) if row["order_execution_time"] else None,
                                          expiry_date=pd.to_datetime(row["expiry_date"]).tz_localize(
                                              sc.INDIAN_TIMEZONE) if row.get("expiry_date") else None,
                                          instrument_type="Options" if row.get("expiry_date") else "Equity", ))

            elif model == ProfitLoss and (row["Symbol"], row["ISIN"]) not in existing_records:
                new_records.append(ProfitLoss(symbol=row["Symbol"], isin=row["ISIN"], quantity=row["Quantity"],
                                              buy_value=row["Buy Value"], sell_value=row["Sell Value"],
                                              realized_pnl=row["Realized P&L"],
                                              realized_pnl_pct=row["Realized P&L Pct."],
                                              previous_closing_price=row.get("Previous Closing Price"),
                                              open_quantity=row["Open Quantity"],
                                              open_quantity_type=row["Open Quantity Type"],
                                              open_value=row["Open Value"], unrealized_pnl=row["Unrealized P&L"],
                                              unrealized_pnl_pct=row["Unrealized P&L Pct."], ))

            elif model == LedgerEntry and (
                    row['particulars'], row['posting_date'], row['cost_center'], row['voucher_type'], row['debit'],
                    row['credit'], row['net_balance']) not in existing_records:
                new_records.append(LedgerEntry(particulars=row['particulars'], posting_date=row['posting_date'],
                                               cost_center=row['cost_center'], voucher_type=row['voucher_type'],
                                               debit=0 if row['debit'] == '' else row['debit'],
                                               credit=0 if row['credit'] == '' else row['credit'],
                                               net_balance=row['net_balance'], ))

        # Bulk insert new records
        if new_records:
            await model.bulk_insert(session, new_records)
            logger.info(f"✅ Inserted {len(new_records)} new records into {model.__tablename__}")


async def process_directory(directory: str, prefix: str):
    """Process all matching files in a directory based on prefix."""

    if not os.path.exists(directory):
        logger.error(f"Directory not found: {directory}")
        return

    model = return_model_for_prefix(prefix)
    if not model:
        logger.error(f"No model found for prefix: {prefix}")
        return

    # Find all files matching the prefix
    files = glob.glob(os.path.join(directory, f"{prefix}*.*"))

    for file_path in files:
        logger.info(f"Processing {file_path} for {model.__name__}")
        await load_data(file_path, model, prefix)


async def main():
    """Loop through sc.DOWNLOAD_REPORTS and process each type."""
    for key, value in sc.DOWNLOAD_REPORTS.items():
        prefix = value.get("prefix")
        if prefix:
            await process_directory(Env.DOWNLOAD_DIR, prefix)
        else:
            logger.warning(f"Skipping {key}: Missing prefix.")


if __name__ == "__main__":
    asyncio.run(main())
