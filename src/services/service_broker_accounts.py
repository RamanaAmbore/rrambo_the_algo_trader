from sqlalchemy import select

from src.models import BrokerAccounts
from src.models.broker_accounts import logger
from src.settings.constants_manager import DEF_BROKER_ACCOUNTS


def initialize_default_records(connection):
    """Initialize default records in the table."""
    try:
        table = BrokerAccounts.__table__
        for record in DEF_BROKER_ACCOUNTS:
            exists = connection.execute(
                select(table.c.account).where(
                    table.c.account == record['account']
                )
            ).scalar_one_or_none() is not None

            if not exists:
                connection.execute(table.insert(), record)
        connection.commit()
        logger.info('Default Broker Accounts records inserted/updated')
    except Exception as e:
        logger.error(f"Error managing default Broker Account records: {e}")
        raise
