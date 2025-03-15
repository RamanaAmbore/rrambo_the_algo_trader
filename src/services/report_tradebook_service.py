from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from win32comext.shell.demos.IActiveDesktop import existing_item

from src.core.database_manager import DatabaseManager as Db
from src.models.report_tradebook import ReportTradebook
from src.services.base_service import BaseService
from src.services.parm_table import fetch_all_records
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReportTradebookService(BaseService):
    """Service class for handling ReportTradebook database operations."""

    def __init__(self):
        super().__init__(ReportTradebook)

    @classmethod
    async def insert_trade(cls, trade_data):
        """Insert a single trade record if the trade_id does not already exist."""
        existing_records = fetch_all_records()
        trade_dict = trade_data.to_dict()  # Convert Pandas Series to dict
        trade_id = trade_dict["trade_id"]

        with Db.get_session() as session:
            existing_trade_ids = {record[0] for record in existing_records}  # Extract trade_id from records

            if trade_id not in existing_trade_ids:
                trade_record = ReportTradebook(**trade_dict)
                cls.validate_and_clean(trade_record)
                session.add(trade_record)
                session.commit()
                logger.info(f"Inserted new trade record: {trade_id}")
            else:
                logger.info(f"Trade ID {trade_id} already exists. Skipping insert.")

    @classmethod
    def bulk_insert_trades(cls, trade_records):
        """Bulk insert multiple trade records, skipping duplicates."""
        trade_list = trade_records.to_dict(orient="records")  # Convert DataFrame to list of dicts
        if not trade_list:
            logger.info("No records to insert.")
            return

        with Db.get_session() as session:
            existing_records = cls.get_existing_records()
            existing_trade_ids = {record[0] for record in existing_records}  # Extract trade_id from records

            # Filter out duplicates
            new_trades = [trade for trade in trade_list if trade["trade_id"] not in existing_trade_ids]

            if new_trades:
                stmt = insert(ReportTradebook).values(new_trades)
                stmt = stmt.on_conflict_do_nothing(index_elements=["trade_id"])  # Avoid duplicate inserts
                session.execute(stmt)
                session.commit()
                logger.info(f"Bulk inserted {len(new_trades)} trade records.")
            else:
                logger.info("No new trades to insert.")

    @classmethod
    def validate_and_clean(cls, record):
        """Validate and clean trade data before insertion."""
        warning_messages = []
        if record.buy_value == "":
            record.buy_value = 0.0
            warning_messages.append("Buy value was empty, set to 0.0")
        if record.sell_value == "":
            record.sell_value = 0.0
            warning_messages.append("Sell value was empty, set to 0.0")
        if record.realized_pnl == "":
            record.realized_pnl = 0.0
            warning_messages.append("Realized P&L was empty, set to 0.0")
        if record.timestamp == "":
            record.timestamp = None
            warning_messages.append("Timestamp was empty, set to None")

        if warning_messages:
            record.warning_error = True
            record.notes = "; ".join(warning_messages)
            logger.warning(f"Data corrections for record {record.trade_id}: {'; '.join(warning_messages)}")
