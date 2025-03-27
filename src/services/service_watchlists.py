from sqlalchemy import select

from src.models import Watchlists
from src.models.watchlists import logger
from src.settings.constants_manager import DEFAULT_WATCHLISTS


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = Watchlists.__table__
        for record in DEFAULT_WATCHLISTS:
            exists = connection.execute(
                select(table.c.watchlist, table.c.account).where(
                    (table.c.watchlist == record['watchlist']) & (table.c.account == record.get('account'))
                )
            ).scalar_one_or_none()

            if exists is None:  # Fixes the boolean check issue
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Watchlist records inserted/updated')
    except Exception as e:
        logger.error(f"Error inserting default Watchlist records: {e}", exc_info=True)
        raise
