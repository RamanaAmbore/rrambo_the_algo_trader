import logging

from sqlalchemy import select

from src.core.database_manager import DatabaseManager as Db
from src.models import ParameterTable
from src.models.parameter_table import logger
from src.settings.constants_manager import DEFAULT_PARAMETERS

logger = logging.getLogger(__name__)


def fetch_all_records(sync=True):
    """Fetch all parameters as a nested dictionary."""
    try:
        with Db.get_session(sync) as session:
            return session.query(ParameterTable).all()
    except Exception as e:
        print('Error in fetching records from parameter table: {e}')
        return {}


def refresh_parms():
    Db.initialize_parameters()


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = ParameterTable.__table__
        for record in DEFAULT_PARAMETERS:
            exists = connection.execute(
                select(table).where(
                    table.c.parameter == record['parameter'],
                    table.c.account == record.get('account')
                )
            ).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Parameter records inserted/updated')
    except Exception as e:
        logger.error(f"Error managing default Parameter records: {e}")
        raise
