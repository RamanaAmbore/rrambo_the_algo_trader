from typing import Type, TypeVar, List, Set, Tuple, Any, Dict, Union
import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.core.database_manager import DatabaseManager as Db
from src.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class BaseService:
    """Generic service class providing common database operations for both async and sync modes."""

    model: Type[T] = None  # This must be defined in subclasses

    @classmethod
    async def validate_model_name(cls) -> None:
        """Ensure that the subclass has defined a model."""
        if not cls.model:
            raise ValueError("Model not defined in subclass")

    @classmethod
    async def get_all_records(cls, async_mode: bool = True) -> List[T]:
        """Fetch all records from the model."""
        await cls.validate_model_name()

        async with Db.get_session_maker(async_mode) as session:
            result = await session.execute(select(cls.model)) if async_mode else session.execute(select(cls.model))
            return result.scalars().all()

    @classmethod
    async def get_by_id(cls, record_id: Any, async_mode: bool = True) -> T:
        """Fetch a record by its primary key."""
        await cls.validate_model_name()

        async with Db.get_session_maker(async_mode) as session:
            query = select(cls.model).where(cls.model.id == record_id)
            result = await session.execute(query) if async_mode else session.execute(query)
            return result.scalars().first()

    @classmethod
    async def insert_record(cls, record: Union[Dict[str, Any], pd.Series], async_mode: bool = True) -> T:
        """Insert a single record into the database.

        Args:
            record (Union[Dict[str, Any], pd.Series]): The record data to insert.
            async_mode (bool): Whether to use async execution.

        Returns:
            The inserted record object.
        """
        await cls.validate_model_name()

        # Convert Pandas Series to dictionary
        if isinstance(record, pd.Series):
            record = record.to_dict()

        record_obj = cls.model(**record)  # Convert dictionary to model instance

        async with Db.get_session_maker(async_mode) as session:
            try:
                session.add(record_obj)
                if async_mode:
                    await session.commit()
                else:
                    session.commit()
                logger.info(f"Inserted record: {record_obj}")
                return record_obj
            except IntegrityError as e:
                await session.rollback() if async_mode else session.rollback()
                logger.error(f"Integrity error inserting record: {e}")
            except Exception as e:
                await session.rollback() if async_mode else session.rollback()
                logger.error(f"Unexpected error inserting record: {e}")

    @classmethod
    async def bulk_insert_records(cls, records: Union[List[Dict[str, Any]], pd.DataFrame], async_mode: bool = True) -> None:
        """Bulk insert multiple records into the database.

        Args:
            records (Union[List[Dict[str, Any]], pd.DataFrame]): The list of records or DataFrame to insert.
            async_mode (bool): Whether to use async execution.
        """
        await cls.validate_model_name()

        # Convert DataFrame to list of dictionaries
        if isinstance(records, pd.DataFrame):
            records = records.to_dict(orient="records")

        record_objs = [cls.model(**record) for record in records]  # Convert dictionaries to model instances

        async with Db.get_session_maker(async_mode) as session:
            try:
                session.add_all(record_objs)
                if async_mode:
                    await session.commit()
                else:
                    session.commit()
                logger.info(f"Inserted {len(records)} records successfully.")
            except IntegrityError as e:
                await session.rollback() if async_mode else session.rollback()
                logger.error(f"Integrity error in bulk record insertion: {e}")
            except Exception as e:
                await session.rollback() if async_mode else session.rollback()
                logger.error(f"Unexpected error in bulk record insertion: {e}")

    @classmethod
    async def get_existing_records(cls, unique_fields: List[str], async_mode: bool = True) -> Set[Tuple[Any, ...]]:
        """Fetch existing records as a set of tuples based on unique fields.

        Args:
            unique_fields (List[str]): The fields used to check for uniqueness.
            async_mode (bool): Whether to use async execution.
        """
        await cls.validate_model_name()

        async with Db.get_session_maker(async_mode) as session:
            query = select(*[getattr(cls.model, field) for field in unique_fields])
            result = await session.execute(query) if async_mode else session.execute(query)
            return {tuple(row) for row in result.fetchall()}

    @classmethod
    async def update_record(cls, record_id: Any, update_data: Dict[str, Any], async_mode: bool = True) -> None:
        """Update a record with new values.

        Args:
            record_id (Any): The primary key of the record to update.
            update_data (Dict[str, Any]): The data to update.
            async_mode (bool): Whether to use async execution.
        """
        await cls.validate_model_name()

        async with Db.get_session_maker(async_mode) as session:
            record = await cls.get_by_id(record_id, async_mode)
            if not record:
                logger.warning(f"Record with id {record_id} not found.")
                return

            for key, value in update_data.items():
                setattr(record, key, value)

            try:
                if async_mode:
                    await session.commit()
                else:
                    session.commit()
                logger.info(f"Updated record {record_id} with {update_data}.")
            except Exception as e:
                await session.rollback() if async_mode else session.rollback()
                logger.error(f"Error updating record {record_id}: {e}")


