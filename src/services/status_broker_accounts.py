from src.core.database_manager import DatabaseManager as Db
from src.models import BrokerAccounts


def insert_account(account_data, sync=True):
    """Insert a new broker account record."""
    with Db.get_session(sync) as session:
        new_account = BrokerAccounts(**account_data)
        session.add(new_account)
        session.commit()
        return new_account


def get_all_accounts(sync=False):
    """Fetch all broker accounts."""
    with Db.get_session(sync) as session:
        return session.query(BrokerAccounts).all()


# Insert default records on table creation
