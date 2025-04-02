from sqlalchemy import text, insert

from src.helpers.logger import get_logger

logger = get_logger(__name__)


async def setup_table_records(session, default_records, update_columns=None):
    """Insert default records, updating all columns except timestamp, source, and notes when needed."""
    async with session:
        try:
            table = self.model.__table__
            table_columns = {col.name for col in table.columns}

            # Columns that should NOT be updated on conflict
            exclude_update = {"timestamp", "source", "notes"}

            # If update_columns is not provided, update all non-PK columns except the excluded ones
            if not update_columns:
                update_columns = [
                    col.name for col in table.columns
                    if not col.primary_key and col.name not in exclude_update
                ]

            for record in default_records:
                valid_record = {k: v for k, v in record.items() if k in table_columns}

                insert_stmt = insert(self.model).values(valid_record)

                # Build update dictionary, excluding `timestamp`, `source`, `notes`
                update_dict = {}
                for col in update_columns:
                    if col in table_columns:
                        col_def = table.c[col].server_default  # Get default value if exists
                        update_dict[col] = (
                            text(f"COALESCE(EXCLUDED.{col}, {col_def})") if col_def else text(f"EXCLUDED.{col}")
                        )

                on_conflict_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=self.conflict_cols,
                    set_=update_dict
                )

                session.execute(on_conflict_stmt)

            session.commit()
            logger.info(f'Default records inserted/updated in {self.model.__tablename__}')
        except Exception as e:
            logger.error(f"Error managing default records in {self.model.__tablename__}: {e}", exc_info=True)
            raise
