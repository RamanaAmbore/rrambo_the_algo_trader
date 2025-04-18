import inspect
from typing import List, Set, Tuple, Any, Dict, Union, Optional, Type, TypeVar

import pandas as pd
from sqlalchemy import select, delete, Column
from sqlalchemy.dialects.postgresql import insert as pg_insert  # Use alias to avoid conflict if needed
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect as sqlainspect  # Alias to avoid name clash
from sqlalchemy.orm import DeclarativeBase  # Assuming use of declarative base for model type hint

from src.core.decorators import track_exec_time
# Assuming db and logger setup are correct
from src.helpers.database_manager import db
from src.helpers.logger import get_logger

logger = get_logger(__name__)

# Generic Type Variable for the SQLAlchemy model
ModelType = TypeVar("ModelType", bound=DeclarativeBase)  # Bound to DeclarativeBase or your base class


def _normalize_record(record: Union[Dict[str, Any], pd.Series]) -> Dict[str, Any]:
    """Convert input record (dict or Series) to a dictionary."""
    if isinstance(record, pd.Series):
        # Convert pandas dtypes carefully if needed (e.g., timestamps)
        # For simplicity, basic to_dict is often sufficient
        return record.to_dict()
    if isinstance(record, dict):
        return record
    raise TypeError(f"Unsupported record type: {type(record)}. Must be dict or pd.Series.")


class ServiceBase:
    """
    Generic asynchronous service class providing common database operations
    for a SQLAlchemy model.
    """

    def __init__(self, model: Type[ModelType], conflict_cols: Optional[List[str]] = None):
        """
        Initializes the service.

        Args:
            model: The SQLAlchemy model class.
            conflict_cols: Optional list of column names forming a unique constraint,
                           used for upsert operations if not specified explicitly later.
        """
        if not model or not inspect.isclass(model):  # Basic validation
            raise ValueError("A valid SQLAlchemy model class is required.")

        self.model = model
        self._model_inspect = sqlainspect(self.model)  # Inspector for metadata
        self._pk_columns = self._model_inspect.primary_key  # Tuple of Column objects

        if not self._pk_columns:
            raise TypeError(f"Model {model.__name__} does not have a primary key defined.")
        # Store PK names for convenience, handle single/composite PKs later if needed
        self._pk_names = [pk.name for pk in self._pk_columns]
        # Simple case assumption: often we need *the* primary key name, works for single PK
        self._pk_name = self._pk_names[0] if len(self._pk_names) == 1 else None

        self.conflict_cols = conflict_cols
        self.table_name = self.model.__tablename__  # Cache table name for logging
        self.records = []

    async def _execute_and_commit(self, session: AsyncSession, stmt: Any, operation_desc: str) -> Any:
        """Helper to execute a statement and commit, with standardized error handling."""
        try:
            result = await session.execute(stmt)
            await session.commit()
            logger.debug(f"Successfully executed and committed: {operation_desc}")
            return result
        except IntegrityError as e:
            await session.rollback()
            logger.warning(f"Integrity error during '{operation_desc}': {e}")
            # Depending on context, might return None/False or re-raise specific error
            raise  # Re-raise for now, caller can decide how to handle
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error during '{operation_desc}' on {self.table_name}: {e}", exc_info=True)
            raise  # Re-raise the original error

    async def get_all_records(self, refresh=True) -> List[ModelType]:
        """Fetch all records from the model."""
        if not self.records or refresh:
            async with db.get_async_session() as session:
                result = await session.execute(select(self.model))
                self.records = list(result.scalars().all())  # Ensure list return type
        return self.records

    async def delete_all_records(self) -> None:
        """Delete all records from the model's table."""
        stmt = delete(self.model)
        async with db.get_async_session() as session:
            # Use helper for execution, commit, and error handling
            await self._execute_and_commit(session, stmt, f"delete all records from {self.table_name}")
            logger.info(f"Deleted all records from {self.table_name}")
            # Clear the cached records
            self.records = []

    async def get_by_id(self, record_id: Any) -> Optional[ModelType]:
        """
        Fetch a record by its primary key.
        Currently supports single-column primary keys only.
        """
        if not self._pk_name:
            logger.error(f"get_by_id currently only supports single-column primary keys for {self.table_name}.")
            raise NotImplementedError("Composite primary key handling not implemented for get_by_id.")

        pk_col: Column = getattr(self.model, self._pk_name)
        stmt = select(self.model).where(pk_col == record_id)

        async with db.get_async_session() as session:
            result = await session.execute(stmt)
            return result.scalars().first()

    async def insert_record(self, record: Union[Dict[str, Any], pd.Series]) -> Optional[Any]:
        """
        Insert a single record and return its primary key value(s).
        Returns the PK value for single PK, or a tuple for composite PK.
        Returns None on IntegrityError (e.g., constraint violation).
        """
        record_dict = _normalize_record(record)

        # Dynamically get PK columns for returning clause
        returning_cols = [getattr(self.model, name) for name in self._pk_names]
        stmt = pg_insert(self.model).values(record_dict).returning(*returning_cols)

        async with db.get_async_session() as session:
            try:
                result = await self._execute_and_commit(
                    session, stmt, f"insert record into {self.table_name}"
                )
                # scalar_one() works for single PK, fetchone() for composite
                inserted_pk = result.scalar_one() if len(returning_cols) == 1 else result.fetchone()
                logger.info(f"Inserted record into {self.table_name} with PK: {inserted_pk}")
                # Clear cached records to ensure fresh data on next fetch
                self.records = []
                return inserted_pk
            except IntegrityError:
                # Handled by _execute_and_commit's rollback, just return None here
                logger.warning(f"Record insertion into {self.table_name} failed due to integrity constraint.")
                return None
            # Other SQLAlchemyErrors are raised by _execute_and_commit

    async def get_existing_records(self, unique_fields: List[str]) -> Set[Tuple[Any, ...]]:
        """
        Fetch existing records as a set of tuples based on specified unique fields.
        Uses server-side cursors for potentially large results.
        """
        if not unique_fields:
            return set()

        select_cols = [getattr(self.model, field) for field in unique_fields]
        query = select(*select_cols).execution_options(stream_results=True)  # Use stream_results for server-side cursor

        existing_records = set()
        async with db.get_async_session() as session:
            result = await session.stream(query)  # Use stream for server-side cursor
            async for row in result:  # Iterate over async result
                existing_records.add(row)  # Rows are already tuples

        return existing_records

    async def update_record(self, record_id: Any, update_data: Dict[str, Any]) -> bool:
        """
        Update a record identified by its primary key (single column only).

        Returns:
            True if the update was successful, False if the record was not found.
        Raises:
            SQLAlchemyError on database errors during update.
            NotImplementedError if the model has a composite primary key.
        """
        if not update_data:
            logger.warning("No update data provided.")
            return False  # Or True? Arguably nothing needed to be done.

        if not self._pk_name:
            logger.error(f"update_record currently only supports single-column primary keys for {self.table_name}.")
            raise NotImplementedError("Composite primary key handling not implemented for update_record.")

        async with db.get_async_session() as session:
            # Fetch the record using ORM capabilities for easy update
            record_to_update = await self.get_by_id(record_id)  # get_by_id uses its own session scope

            if not record_to_update:
                logger.warning(f"Record with PK {record_id} not found in {self.table_name} for update.")
                return False

            # Update attributes on the ORM object
            for key, value in update_data.items():
                if hasattr(record_to_update, key):
                    setattr(record_to_update, key, value)
                else:
                    logger.warning(f"Attribute '{key}' not found on model {self.model.__name__}, skipping.")

            # Add the (potentially modified) object to the session for tracking
            session.add(record_to_update)

            # Commit the session - SQLAlchemy handles the UPDATE statement
            try:
                await session.commit()
                logger.info(f"Updated record {record_id} in {self.table_name} with {list(update_data.keys())}.")
                # Clear cached records to ensure fresh data on next fetch
                self.records = []
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Error updating record {record_id} in {self.table_name}: {e}", exc_info=True)
                raise

    @track_exec_time()
    async def bulk_insert_records(
            self,
            records: Union[List[Dict[str, Any]], pd.DataFrame] = None,
            index_elements: Optional[List[str]] = None,
            update_on_conflict: bool = False,
            skip_update_if_exists: bool = False,
            batch_size: int = 500,
            update_columns: Optional[List[str]] = None,
            ignore_extra_columns: bool = False,
    ) -> List[ModelType]:
        """
        Performs bulk insert/upsert using PostgreSQL's ON CONFLICT clause.

        Args:
            records: List of dictionaries or Pandas DataFrame representing records.
            index_elements: List of columns for conflict resolution (unique constraint).
                            Defaults to `self.conflict_cols` if set during init.
            update_on_conflict: If True, updates existing records instead of ignoring them.
            skip_update_if_exists: If True, does not update existing records, only inserts new ones.
            batch_size: Number of records to process per database batch.
            update_columns: Explicit list of columns to update on conflict.
                            If None and update_on_conflict is True, updates all columns
                            not in index_elements.
            ignore_extra_columns: If True, silently ignores keys not in table columns.
                                  If False, raises error on invalid keys.

        Returns:
            List of all records after the operation completes.
        """
        if records is None:
            records = []

        if not isinstance(records, list) and not isinstance(records, tuple):
            if isinstance(records, pd.DataFrame):
                records = records.to_dict(orient="records")
            else:
                logger.error("Invalid format for 'records'. Must be list of dicts or DataFrame.")
                return []

        if not records:
            logger.info("No records provided for bulk insert.")
            return await self.get_all_records(refresh=True)

        model_columns = {c.name for c in self._model_inspect.columns}

        # Validate or filter fields based on the flag
        if ignore_extra_columns:
            records = [
                {k: v for k, v in record.items() if k in model_columns}
                for record in records
            ]
        else:
            for i, record in enumerate(records):
                extra_keys = set(record.keys()) - model_columns
                if extra_keys:
                    logger.error(f"Record {i} has invalid keys not in model: {extra_keys}")
                    raise ValueError(f"Invalid keys in record {i}: {extra_keys}")

        # Conflict target
        conflict_target = index_elements if index_elements is not None else self.conflict_cols
        if not conflict_target:
            if update_on_conflict:
                logger.error("`index_elements` or `self.conflict_cols` must be provided for `update_on_conflict=True`.")
                raise ValueError("Conflict target required for updates.")
            logger.warning(
                f"No conflict target specified for bulk insert into {self.table_name}. Performing plain inserts.")

        async with db.get_async_session() as session:
            try:
                non_conflict_cols = list(model_columns - set(conflict_target or []))

                if update_columns is None and update_on_conflict:
                    update_columns = non_conflict_cols

                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    stmt = pg_insert(self.model).values(batch)

                    if update_on_conflict and not skip_update_if_exists and conflict_target:
                        stmt = stmt.on_conflict_do_update(
                            index_elements=conflict_target,
                            set_={col: getattr(stmt.excluded, col) for col in update_columns}
                        )
                    elif update_on_conflict and skip_update_if_exists and conflict_target:
                        stmt = stmt.on_conflict_do_nothing(index_elements=conflict_target)

                    await session.execute(stmt)

                await session.commit()
                # Clear cached records to force refresh
                self.records = []

            except Exception as e:
                logger.exception(f"Error in bulk insert into {self.table_name}: {e}")
                await session.rollback()

        # Return fresh records after bulk insert
        return await self.get_all_records(refresh=True)

    async def delete_setup_table_records(self, *args, **kwargs) -> List[ModelType]:
        """
        Delete all existing records and then set up new default records.

        Returns:
            List of all records after the operation completes.
        """
        await self.delete_all_records()
        return await self.setup_table_records(*args, **kwargs)

    async def setup_table_records(self,
                                  default_records: List[Dict[str, Any]],
                                  update_columns: Optional[List[str]] = None,
                                  exclude_from_update=('timestamp',),
                                  skip_update_if_exists: bool = False,
                                  ignore_extra_columns: bool = False,
                                  ) -> List[ModelType]:
        """
        Insert default records using the bulk mechanism for efficiency.
        Performs an update on conflict based on `self.conflict_cols` unless `skip_update_if_exists` is True.

        Args:
            default_records: List of dictionaries representing records to insert/update.
            update_columns: Specific columns to update on conflict. If None, updates
                            all columns except PKs and a predefined exclude list.
            exclude_from_update: Columns to exclude from updates.
            skip_update_if_exists: If True, does not update existing records.
            ignore_extra_columns: If True, silently ignores keys not in table columns.

        Returns:
            List of all records after the operation completes.
        """
        if not self.conflict_cols:
            raise ValueError("`self.conflict_cols` must be set in __init__ to use setup_table_records.")

        if not default_records:
            logger.info(f"No default records provided for {self.table_name}.")
            return []

        if update_columns is None:
            pk_names_set = set(self._pk_names)
            model_columns = {c.name for c in self._model_inspect.columns}

            update_columns = [
                col_name for col_name in model_columns
                if col_name not in pk_names_set
                   and col_name not in exclude_from_update
                   and col_name not in self.conflict_cols
            ]
        else:
            model_columns = {c.name for c in self._model_inspect.columns}
            update_columns = [
                col for col in update_columns
                if col in model_columns and col not in self.conflict_cols
            ]

        logger.info(
            f"Setting up default records for {self.table_name} using conflict target {self.conflict_cols} "
            f"and updating columns: {update_columns}, skipping updates: {skip_update_if_exists}")

        result = await self.bulk_insert_records(
            records=default_records,
            index_elements=self.conflict_cols,
            update_on_conflict=True,
            skip_update_if_exists=skip_update_if_exists,
            update_columns=update_columns,
            batch_size=100,
            ignore_extra_columns=ignore_extra_columns
        )
        logger.info(f"Default records setup completed for {self.table_name}.")

        return result

    async def get_records_map(self, key_attr: str = 'id', value_attr: str = None) -> Dict[Any, Any]:
        """
        Creates a dictionary map of records.

        Args:
            key_attr: The attribute to use as the dictionary key. Defaults to the primary key.
            value_attr: The attribute to use as the dictionary value. If None, the entire record object is used.

        Returns:
            A dictionary mapping the key attribute to either the value attribute or the entire record.
        """
        records = await self.get_all_records(refresh=True)

        # Default to using the primary key as the key
        if not key_attr:
            if not self._pk_name:
                raise ValueError("No primary key column found and no key_attr specified")
            key_attr = self._pk_name

        # Create the map
        if value_attr:
            # Map key_attr -> value_attr
            return {
                getattr(record, key_attr): getattr(record, value_attr)
                for record in records
                if hasattr(record, key_attr) and hasattr(record, value_attr)
            }
        else:
            # Map key_attr -> record
            result = {}
            for record in records:
                if hasattr(record, key_attr):
                    key = getattr(record, key_attr)
                    result[key] = record
            return result
