import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from models import Trades
from threads.sync_data import logger
from utils.db_connection import DbConnection as Db
from utils.zerodha_kite import ZerodhaKite


def fetch_and_sync_trades_api():
    """Fetch trades from Kite API and insert missing ones into the database."""
    logger.info("Fetching trades from Kite API...")
    try:
        kite = ZerodhaKite.get_kite_conn()
        api_trades = kite.trades()
    except Exception as ex:
        logger.error(f"Failed to fetch trades: {ex}")
        return

    session = Db.get_sync_session()
    try:
        existing_trades = session.query(Trades).all()
        existing_trade_ids = {trade.order_id for trade in existing_trades}

        new_trades = [Trades.from_api_data(trade) for trade in api_trades if
                      trade["order_id"] not in existing_trade_ids]

        if new_trades:
            session.bulk_save_objects(new_trades)
            session.commit()
            logger.info(f"Inserted {len(new_trades)} new trades from API.")
        else:
            logger.info("No new trades to insert from API.")
    except SQLAlchemyError as ex:
        logger.error(f"Database error while syncing trades from API: {ex}")
    except Exception as ex:
        logger.error(f"Unexpected error while syncing trades from API: {ex}")
    finally:
        session.close()


def load_trades_from_csv_equity(file_path):
    """Load and sync equity trades from a CSV file."""
    logger.info(f"Loading equity trades from CSV: {file_path}")
    try:
        df = pd.read_csv(file_path)
    except Exception as ex:
        logger.error(f"Failed to read CSV file {file_path}: {ex}")
        return

    session = Db.sync_session()
    try:
        existing_trades = session.query(Trades).all()
        existing_trade_ids = {trade.order_id for trade in existing_trades}

        new_trades = [
            Trades(trade_id=row["trade_id"], order_id=row["order_id"], trading_symbol=row["symbol"], isin=row["isin"],
                   exchange=row["exchange"], segment=row["segment"], series=row["series"], trade_type=row["trade_type"],
                   auction=bool(row["auction"]), quantity=int(row["quantity"]), price=float(row["price"]),
                   trade_date=pd.to_datetime(row["trade_date"]),
                   order_execution_time=pd.to_datetime(row["order_execution_time"]), expiry_date=None,
                   # Not applicable for equity
                   instrument_type="Equity") for _, row in df.iterrows() if row["order_id"] not in existing_trade_ids]

        if new_trades:
            session.bulk_save_objects(new_trades)
            session.commit()
            logger.info(f"Inserted {len(new_trades)} new equity trades from CSV.")
        else:
            logger.info("No new equity trades to insert from CSV.")
    except SQLAlchemyError as ex:
        logger.error(f"Database error while syncing equity trades from CSV: {ex}")
    except Exception as ex:
        logger.error(f"Unexpected error while syncing equity trades from CSV: {ex}")
    finally:
        session.close()


def load_trades_from_csv_options(file_path):
    """Load and sync options trades from a CSV file."""
    logger.info(f"Loading options trades from CSV: {file_path}")
    try:
        df = pd.read_csv(file_path)
    except Exception as ex:
        logger.error(f"Failed to read CSV file {file_path}: {ex}")
        return

    session = Db.get_sync_session()
    try:
        existing_trades = session.query(Trades).all()
        existing_trade_ids = {trade.order_id for trade in existing_trades}

        new_trades = [
            Trades(trade_id=row["trade_id"], order_id=row["order_id"], trading_symbol=row["symbol"], isin=row["isin"],
                   exchange=row["exchange"], segment=row["segment"], series=row["series"], trade_type=row["trade_type"],
                   auction=bool(row["auction"]), quantity=int(row["quantity"]), price=float(row["price"]),
                   trade_date=pd.to_datetime(row["trade_date"]),
                   order_execution_time=pd.to_datetime(row["order_execution_time"]),
                   expiry_date=pd.to_datetime(row["expiry_date"]), instrument_type="Options") for _, row in
            df.iterrows() if row["order_id"] not in existing_trade_ids]

        if new_trades:
            session.bulk_save_objects(new_trades)
            session.commit()
            logger.info(f"Inserted {len(new_trades)} new options trades from CSV.")
        else:
            logger.info("No new options trades to insert from CSV.")
    except SQLAlchemyError as ex:
        logger.error(f"Database error while syncing options trades from CSV: {ex}")
    except Exception as ex:
        logger.error(f"Unexpected error while syncing options trades from CSV: {ex}")
    finally:
        session.close()


def sync_trades(csv_equity_path: str, csv_options_path: str):
    """Synchronize trades from Kite API and CSV files."""
    fetch_and_sync_trades_api()
    load_trades_from_csv_equity(csv_equity_path)
    load_trades_from_csv_options(csv_options_path)
