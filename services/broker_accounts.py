from sqlalchemy import event

from models import BrokerAccounts
from sqlalchemy.orm import Session
from utils.db_connection import DbConnection as Db


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
@event.listens_for(BrokerAccounts.__table__, "after_create")
def insert_default_records(target, connection, **kwargs):
    default_records =[{"account_id": "ZG0790", "broker_name": "Zerodha", "notes": "Haritha account"},
     {"account_id": "ZJ6294", "broker_name": "Zerodha",
      "notes": "Ramana account"}, ]
    connection.execute(target.insert(), default_records)
