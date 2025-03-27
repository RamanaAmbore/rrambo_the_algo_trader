from sqlalchemy import select

from src.models import AlgoThreadScheduleXref
from src.models.algo_thread_schedule_xref import logger
from src.settings.constants_manager import DEFAULT_THREAD_SCHEDULE_XREF


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = AlgoThreadScheduleXref.__table__
        for record in DEFAULT_THREAD_SCHEDULE_XREF:
            exists = connection.execute(
                select(table).where(
                    table.c.thread == record['thread'],
                    table.c.schedule == record['schedule']
                )
            ).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Algo Thread Schedule Xref records inserted/updated')
    except Exception as e:
        logger.error(f"Error managing default Algo Thread Schedule Xref records: {e}")
        raise
