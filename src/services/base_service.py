from typing import List, Set, Tuple, Any, Dict, Union

import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

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


    async def bulk_insert_records(self, query=None, records=None, index_elements=None, batch_size=500):
        """
        Performs bulk insert while ignoring duplicates.

        :param query: SQLAlchemy query to fetch records if records are not provided.
        :param records: List of dictionaries representing records to insert.
        :param index_elements: List of columns for conflict resolution.
        :param batch_size: Number of records to insert per batch (default: 100).
        """

        if (query is None) == (records is None):
            logger.info("Either provide `query` or `records`, not both or neither.")
            return

        if isinstance(records, pd.DataFrame):
            records = records.to_dict(orient="records")

        try:
            async with Db.get_async_session() as session:
                # Fetch records if query is provided
                if query is not None:
                    result = await session.execute(query)
                    records = [row._asdict() for row in result.mappings().all()]  # Convert result to list of dicts

                if not records:
                    logger.warning("No records to insert.")
                    return

                for i in range(0, len(records), batch_size):
                    batch = records[i: i + batch_size]  # Process in chunks

                    stmt = insert(self.model).values(batch)
                    if index_elements:
                        stmt = stmt.on_conflict_do_nothing(index_elements=index_elements)  # Ignore duplicates

                    await session.execute(stmt)
                    await session.commit()

                    logger.info(f"Bulk inserted {len(batch)} records into {self.model}")

        except SQLAlchemyError as e:
            logger.exception(f"Bulk insert failed: {e}")
            raise