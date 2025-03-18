from typing import List, Set, Tuple, Any, Dict, Union

import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from src.core.database_manager import DatabaseManager as Db
from src.helpers.logger import get_logger

logger = get_logger(__name__)


class BaseService:
    """Generic service class providing common database operations for both async and sync modes."""

    def __init__(self, model):
        self.model = model
        self.validate_model_name()

    def validate_model_name(self) -> None:
        """Ensure that the model is provided."""
        if self.model is None:
            raise ValueError("Model is required but not provided")

    async def get_all_records(self):
        """Fetch all records from the model."""
        async with Db.get_async_session() as session:
            result = await session.execute(select(self.model))
            return result.scalars().all()

    async def get_by_id(self, record_id: Any):
        """Fetch a record by its primary key."""
        async with Db.get_async_session() as session:
            query = select(self.model).where(self.model.id == record_id)
            result = await session.execute(query)
            return result.scalars().first()

    async def insert_record(self, record: Union[Dict[str, Any], pd.Series]):
        """Insert a single record and return its ID."""
        if isinstance(record, pd.Series):
            record = record.to_dict()

        async with Db.get_async_session() as session:
            try:
                stmt = insert(self.model).values(record).returning(self.model.id)  # Fetch ID
                result = await session.execute(stmt)
                inserted_id = result.scalar_one()  # Extract inserted ID
                await session.commit()

                logger.info(f"Inserted record with ID: {inserted_id}")
                return inserted_id  # Return the ID instead of the whole object

            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Integrity error inserting record: {e}")

            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error inserting record: {e}")

        return None  # Return None if insert fails

    async def get_existing_records(self, unique_fields: List[str]) -> Set[Tuple[Any, ...]]:
        """Fetch existing records as a set of tuples based on unique fields."""
        async with Db.get_async_session() as session:
            query = select(*[getattr(self.model, field) for field in unique_fields])
            result = await session.execute(query)
            return {tuple(row) for row in result.scalars().all()}

    async def update_record(self, record_id: Any, update_data: Dict[str, Any]) -> None:
        """Update a record with new values."""
        async with Db.get_async_session() as session:
            record = await self.get_by_id(record_id)
            if not record:
                logger.warning(f"Record with id {record_id} not found.")
                return

            for key, value in update_data.items():
                setattr(record, key, value)
            try:
                await session.commit()
                logger.info(f"Updated record {record_id} with {update_data}.")
            except Exception as e:
                await session.rollback()
                logger.error(f"Error updating record {record_id}: {e}")

    async def insert_report_records(self, query, data_records: pd.DataFrame):
        """Bulk insert multiple trade records, skipping duplicates."""
        if isinstance(data_records, pd.DataFrame):
            data_records = data_records.to_dict(orient="records")
        if not data_records:
            logger.info("No records to insert.")
            return

        async with Db.get_async_session() as session:
            existing_trade_ids = {row[0] for row in (await session.execute(query)).all()}
            new_trades = [trade for trade in data_records if trade["trade_id"] not in existing_trade_ids]

            if new_trades:
                stmt = insert(self.model).values(new_trades)
                stmt = stmt.on_conflict_do_nothing(index_elements=["trade_id"])
                await session.execute(stmt)
                await session.commit()
                logger.info(f"Bulk inserted {len(new_trades)} trade records.")
            else:
                logger.info("No new trades to insert.")