from functools import wraps
from typing import List, Set, Tuple, Any, Dict, Union, Optional, Callable

import pandas as pd
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.database_manager import DatabaseManager as Db
from src.helpers.logger import get_logger

logger = get_logger(__name__)


class ServiceBase:
    """Generic service class providing common database operations."""

    def __init__(self, model):
        if not model:
            raise ValueError("Model is required but not provided")
        self.model = model

    async def get_all_records(self) -> List[Any]:
        """Fetch all records from the model."""
        async with Db.get_async_session() as session:
            result = await session.execute(select(self.model))
            return result.scalars().all()

    async def delete_all_records(self) -> None:
        """Delete all records from the model."""
        async with Db.get_async_session() as session:
            try:
                await session.execute(delete(self.model))
                await session.commit()
                logger.info(f"Deleted all records from {self.model.__tablename__}")
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Error deleting records from {self.model.__tablename__}: {e}")
                raise

    async def get_by_id(self, record_id: Any) -> Optional[Any]:
        """Fetch a record by its primary key."""
        async with Db.get_async_session() as session:
            result = await session.execute(select(self.model).where(self.model.id == record_id))
            return result.scalars().first()

    async def insert_record(self, record: Union[Dict[str, Any], pd.Series]) -> Optional[int]:
        """Insert a single record and return its ID."""
        if isinstance(record, pd.Series):
            record = record.to_dict()

        async with Db.get_async_session() as session:
            try:
                stmt = insert(self.model).values(record).returning(self.model.id)
                result = await session.execute(stmt)
                inserted_id = result.scalar_one()
                await session.commit()

                logger.info(f"Inserted record with ID: {inserted_id}")
                return inserted_id

            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Integrity error inserting record: {e}")
                return None
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Unexpected error inserting record: {e}")
                raise

    async def get_existing_records(self, unique_fields: List[str]) -> Set[Tuple[Any, ...]]:
        """Fetch existing records as a set of tuples based on unique fields."""
        async with Db.get_async_session() as session:
            query = select(*[getattr(self.model, field) for field in unique_fields]).execution_options(yield_per=1000)
            result = await session.execute(query)
            return set(result.fetchall())  # Faster than list comprehension

    async def update_record(self, record_id: Any, update_data: Dict[str, Any]) -> bool:
        """Update a record with new values."""
        async with Db.get_async_session() as session:
            query = select(self.model).where(self.model.id == record_id)
            result = await session.execute(query)
            record = result.scalars().first()

            if not record:
                logger.warning(f"Record with id {record_id} not found.")
                return False

            for key, value in update_data.items():
                setattr(record, key, value)

            try:
                await session.commit()
                logger.info(f"Updated record {record_id} with {update_data}.")
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Error updating record {record_id}: {e}")
                raise

    async def bulk_insert_records(
            self,
            query=None,
            records: Optional[Union[List[Dict[str, Any]], pd.DataFrame]] = None,
            index_elements: Optional[List[str]] = None,
            update_on_conflict: bool = False,
            batch_size: int = 500
    ) -> None:
        """
        Performs bulk insert while handling conflicts.

        :param query: SQLAlchemy query to fetch records if records are not provided.
        :param records: List of dictionaries or Pandas DataFrame representing records.
        :param index_elements: List of columns for conflict resolution.
        :param update_on_conflict: If True, updates existing records instead of ignoring them.
        :param batch_size: Number of records to insert per batch (default: 500).
        """
        if (query is None) == (records is None):
            logger.info("Either provide `query` or `records`, not both or neither.")
            return

        if isinstance(records, pd.DataFrame):
            records = records.to_dict(orient="records")

        async with Db.get_async_session() as session:
            try:
                if query:
                    result = await session.execute(query)
                    records = [row._asdict() for row in result.mappings().all()]

                if not records:
                    logger.warning("No records to insert.")
                    return

                for i in range(0, len(records), batch_size):
                    batch = records[i: i + batch_size]

                    stmt = insert(self.model).values(batch)

                    if index_elements:
                        # Handle ON CONFLICT (either update or do nothing)
                        if update_on_conflict:
                            stmt = stmt.on_conflict_do_update(
                                index_elements=index_elements,
                                set_={col: getattr(stmt.excluded, col) for col in batch[0] if col not in index_elements}
                            )
                        else:
                            stmt = stmt.on_conflict_do_nothing(index_elements=index_elements)
                        await session.execute(stmt, batch)
                    else:
                        # Perform bulk insert if index_elements is empty
                        await session.execute(self.model.__table__.insert(), batch)

                    await session.execute(stmt)
                    await session.commit()

                    logger.info(f"Bulk inserted/updated {len(batch)} records into {self.model.__tablename__}")

            except SQLAlchemyError as e:
                await session.rollback()
                logger.exception(f"Bulk insert failed: {e}")
                raise


def validate_cast_parameter(func: Callable):
    """Decorator to validate and convert records before processing."""

    @wraps(func)
    async def wrapper(self, records: Union[pd.DataFrame, List[dict]], *args, **kwargs):
        if not records or (isinstance(records, pd.DataFrame) and records.empty):
            logger.info("No valid records to process.")
            return

        # Convert list of dicts to DataFrame if needed
        records_df = pd.DataFrame(records) if isinstance(records, list) else records

        return await func(self, records_df, *args, **kwargs)  # Call original function with DataFrame

    return wrapper
