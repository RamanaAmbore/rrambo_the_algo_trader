from src.models import BrokerAccounts
from src.utils import DbConnect as Db


def insert_account(account_data, sync=True):
    """Insert a new broker account record."""
    with Db.get_session_maker(sync) as session:
        new_account = BrokerAccounts(**account_data)
        session.add(new_account)
        session.commit()
        return new_account


def get_all_accounts(sync=False):
    """Fetch all broker accounts."""
    with Db.get_session_maker(sync) as session:
        return session.query(BrokerAccounts).all()


# Insert default records on table creation
