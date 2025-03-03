import pandas as pd
import os
from sqlalchemy.ext.asyncio import AsyncSession
from utils.db_session import async_session
from models.trades import Trades
from models.profit_loss import ProfitLoss
from models.ledger_entry import Ledger


async def load_data(file_path: str):
    """Load data from CSV/Excel into the database efficiently."""

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    # Determine model from filename prefix
    model = None
    if file_path.startswith("tradebook"):
        model = Trades
    elif file_path.startswith("pnl"):
        model = ProfitLoss
    elif file_path.startswith("ledger"):
        model = Ledger
    else:
        print("❌ Unsupported file format!")
        return

    # Read file
    df = None
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)

    if df is None or df.empty:
        print(f"❌ No data in {file_path}")
        return

    async with async_session() as session:
        # Fetch existing records
        existing_records = await model.get_existing_records(session)

        # Prepare new records for bulk insert
        new_records = []
        for _, row in df.iterrows():
            if model == Trades and row["trade_id"] not in existing_records:
                new_records.append(Trades(
                    trade_id=row["trade_id"],
                    order_id=row["order_id"],
                    trading_symbol=row["symbol"],
                    isin=row.get("isin"),
                    exchange=row["exchange"],
                    segment=row["segment"],
                    series=row["series"],
                    trade_type=row["trade_type"],
                    auction=row.get("auction", False),
                    quantity=row["quantity"],
                    price=row["price"],
                    trade_date=pd.to_datetime(row["trade_date"]),
                    order_execution_time=pd.to_datetime(row["order_execution_time"]),
                    expiry_date=pd.to_datetime(row["expiry_date"]) if "expiry_date" in row else None,
                    instrument_type="Options" if "expiry_date" in row else "Equity"
                ))

            elif model == ProfitLoss and (row["symbol"], row["isin"]) not in existing_records:
                new_records.append(ProfitLoss(
                    symbol=row["symbol"],
                    isin=row["isin"],
                    quantity=row["quantity"],
                    buy_value=row["buy_value"],
                    sell_value=row["sell_value"],
                    realized_pnl=row["realized_pnl"],
                    realized_pnl_pct=row["realized_pnl_pct"],
                    previous_closing_price=row.get("previous_closing_price"),
                    open_quantity=row["open_quantity"],
                    open_quantity_type=row["open_quantity_type"],
                    open_value=row["open_value"],
                    unrealized_pnl=row["unrealized_pnl"],
                    unrealized_pnl_pct=row["unrealized_pnl_pct"]
                ))

            elif model == Ledger and row["entry_id"] not in existing_records:
                new_records.append(Ledger(
                    entry_id=row["entry_id"],
                    date=pd.to_datetime(row["date"]),
                    transaction_type=row["transaction_type"],
                    amount=row["amount"],
                    balance=row["balance"],
                    reference=row.get("reference"),
                    remarks=row.get("remarks")
                ))

        # Bulk insert new records
        if new_records:
            await model.bulk_insert(session, new_records)
            print(f"✅ Inserted {len(new_records)} new records into {model.__tablename__}")


async def main():
    """Load all datasets."""
    await load_data("tradebook_2024.csv")
    await load_data("pnl_2024.csv")
    await load_data("ledger_2024.csv")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
