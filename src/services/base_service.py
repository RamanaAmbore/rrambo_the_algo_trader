from typing import TypeVar, List, Set, Tuple, Any, Dict, Union
import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.core.database_manager import DatabaseManager as Db
from src.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class BaseService:
    """Generic service class providing common database operations for both async and sync modes."""

    @classmethod
    def validate_model_name(cls, model) -> None:
        """Ensure that the model is provided."""
        if model is None:
            raise ValueError("Model is required but not provided")

    @classmethod
    async def get_all_records(cls, model) -> List[T]:
        """Fetch all records from the model."""
        cls.validate_model_name(model)

        async with Db.get_async_session() as session:
            result = await session.execute(select(model))
            return result.scalars().all()

    @classmethod
    async def get_by_id(cls, model, record_id: Any) -> T:
        """Fetch a record by its primary key."""
        cls.validate_model_name(model)

        async with Db.get_async_session() as session:
            query = select(model).where(model.id == record_id)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def insert_record(cls, model, record: Union[Dict[str, Any], pd.Series]) -> Union[T, None]:
        """Insert a single record and return it."""
        cls.validate_model_name(model)

        if isinstance(record, pd.Series):
            record = record.to_dict()

        record_obj = model(**record)

        async with Db.get_async_session() as session:
            try:
                session.add(record_obj)
                await session.commit()
                logger.info(f"Inserted record: {record_obj}")
                return record_obj
            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Integrity error inserting record: {e}")
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error inserting record: {e}")

        return None  # Explicitly return None on failure

    @classmethod
    async def bulk_insert_records(cls, model, records: Union[List[Dict[str, Any]], pd.DataFrame]) -> None:
        """Bulk insert multiple records into the database."""
        cls.validate_model_name(model)

        if isinstance(records, pd.DataFrame):
            records = records.to_dict(orient="records")

        record_objs = [model(**record) for record in records]

        async with Db.get_async_session() as session:
            try:
                session.add_all(record_objs)
                await session.commit()
                logger.info(f"Inserted {len(records)} records successfully.")
            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Integrity error in bulk record insertion: {e}")
            except Exception as e:
                await session.rollback()
                logger.error(f"Unexpected error in bulk record insertion: {e}")

    @classmethod
    async def get_existing_records(cls, model, unique_fields: List[str]) -> Set[Tuple[Any, ...]]:
        """Fetch existing records as a set of tuples based on unique fields."""
        cls.validate_model_name(model)

        async with Db.get_async_session() as session:
            query = select(*[getattr(model, field) for field in unique_fields])
            result = await session.execute(query)
            return {tuple(row) for row in result.scalars().all()}  # FIXED

    @classmethod
    async def update_record(cls, model, record_id: Any, update_data: Dict[str, Any]) -> None:
        """Update a record with new values."""
        cls.validate_model_name(model)

        async with Db.get_async_session() as session:
            record = await cls.get_by_id(model, record_id)  # FIXED
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
