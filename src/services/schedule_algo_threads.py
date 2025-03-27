from sqlalchemy import select

from src.models import AlgoThreads
from src.models.algo_threads import logger
from src.settings.constants_manager import DEFAULT_ALGO_THREADS


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = AlgoThreads.__table__
        for record in DEFAULT_ALGO_THREADS:
            exists = connection.execute(select(table.c.thread).where(
                table.c.thread == record['thread'])).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Algo Thread records inserted/updated')
    except Exception as e:
        logger.error(f"Error managing default Algo Threads records: {e}")
        raise
