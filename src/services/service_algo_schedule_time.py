from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.models import AlgoScheduleTime
from src.models.algo_schedule_time import logger
from src.settings.constants_manager import DEFAULT_ALGO_SCHEDULE_TIME_RECORDS


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = AlgoScheduleTime.__table__
        for record in DEFAULT_ALGO_SCHEDULE_TIME_RECORDS:
            exists = connection.execute(
                select(table).where(
                    table.c.schedule == record['schedule'],
                    table.c.weekday == record['weekday']
                )
            ).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Schedule Time records inserted/updated')
    except SQLAlchemyError as e:
        logger.error(f"Error managing default Algo Schedule Time records: {e}")
        raise
