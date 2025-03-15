import pandas as pd
from sqlalchemy.exc import IntegrityError

from src.core.database_manager import DatabaseManager as Db
from src.models.report_profit_loss import ReportProfitLoss
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProfitLossService:
    """Service for managing ReportProfitLoss records."""

    @staticmethod
    def _validate_and_clean(record: ReportProfitLoss):
        """
        Validates and cleans record data before insertion.
        Modifies the record in place and sets warning flags if needed.
        """
        warning_messages = []

        for field in ["buy_value", "sell_value", "realized_pnl"]:
            if getattr(record, field) in ["", None]:
                setattr(record, field, 0.0)
                warning_messages.append(f"{field.replace('_', ' ').title()} was empty, set to 0.0")

        if record.timestamp in ["", None]:
            record.timestamp = None
            warning_messages.append("Timestamp was empty, set to None")

        if warning_messages:
            record.warning_error = True
            record.notes = "; ".join(warning_messages)

        return record

    @staticmethod
    def _record_exists(session, account: str, symbol: str, timestamp):
        """
        Checks if a record already exists in the table.
        :param session: Active SQLAlchemy session.
        :param account: Account to check.
        :param symbol: Symbol to check.
        :param timestamp: Timestamp to check.
        :return: Boolean indicating existence.
        """
        return session.query(ReportProfitLoss).filter_by(
            account=account, symbol=symbol, timestamp=timestamp
        ).first() is not None

    @staticmethod
    def insert_record(record_data: dict, async_mode: bool = False):
        """
        Inserts a single record if it does not already exist.
        :param record_data: Dictionary containing the record data.
        :param async_mode: Boolean flag to determine async or sync session.
        :return: Newly inserted record or None if skipped.
        """
        with Db.get_session(async_mode) as session:
            try:
                if ProfitLossService._record_exists(
                    session, record_data["account"], record_data["symbol"], record_data["timestamp"]
                ):
                    logger.info(f"Skipped duplicate record: {record_data}")
                    return None

                record = ProfitLossService._validate_and_clean(ReportProfitLoss(**record_data))
                session.add(record)
                session.commit()
                logger.info(f"Inserted record: {record}")
                return record
            except IntegrityError as e:
                session.rollback()
                logger.error(f"IntegrityError: {e.orig} - Data: {record_data}")
            except Exception as e:
                session.rollback()
                logger.error(f"Error inserting record: {e} - Data: {record_data}")
            return None

    @staticmethod
    def bulk_insert_dataframe(record_df: pd.DataFrame, async_mode: bool = False, chunk_size=1000):
        """
        Bulk inserts records if they do not already exist.
        :param record_df: Pandas DataFrame with columns matching ReportProfitLoss.
        :param async_mode: Boolean flag to determine async or sync session.
        :param chunk_size: Number of records per batch insert.
        :return: Number of records successfully inserted.
        """
        if not isinstance(record_df, pd.DataFrame):
            logger.error("Expected a Pandas DataFrame.")
            return 0

        records = record_df.to_dict(orient="records")
        total_inserted = 0

        with Db.get_session(async_mode) as session:
            try:
                for i in range(0, len(records), chunk_size):
                    batch = [
                        ProfitLossService._validate_and_clean(ReportProfitLoss(**record_data))
                        for record_data in records[i : i + chunk_size]
                        if not ProfitLossService._record_exists(
                            session, record_data["account"], record_data["symbol"], record_data["timestamp"]
                        )
                    ]

                    if batch:
                        session.bulk_save_objects(batch)
                        session.commit()
                        total_inserted += len(batch)
                        logger.info(f"Inserted batch {i // chunk_size + 1}: {len(batch)} records")
                return total_inserted
            except IntegrityError as e:
                session.rollback()
                logger.error(f"Bulk insert failed: {e.orig}")
            except Exception as e:
                session.rollback()
                logger.error(f"Unexpected error during bulk insert: {e}")
            return total_inserted

    @staticmethod
    def get_existing_records(account: str = None, symbol: str = None, async_mode: bool = False):
        """
        Retrieves existing records from the report_profit_loss table.

        :param account: (Optional) Filter by account.
        :param symbol: (Optional) Filter by symbol.
        :param async_mode: Boolean flag to determine async or sync session.
        :return: List of matching ReportProfitLoss records.
        """
        with Db.get_session(async_mode) as session:
            try:
                query = session.query(ReportProfitLoss)

                if account:
                    query = query.filter(ReportProfitLoss.account == account)
                if symbol:
                    query = query.filter(ReportProfitLoss.symbol == symbol)

                records = query.all()
                logger.info(f"Fetched {len(records)} records from report_profit_loss.")
                return records
            except Exception as e:
                logger.error(f"Error fetching records: {e}")
                return []
