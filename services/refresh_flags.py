from sqlalchemy.orm import Session

from models import RefreshFlags

from utils.db_connect import DbConnect as Db
def get_setting(sync=False):
    """
    Fetch a setting value by key from the database.
    If account is provided, fetch account-specific settings first, else fallback to global settings.
    """
    with Db.get_session(sync) as session:
        result = session.query(RefreshFlags.thread_name, RefreshFlags.value).filter(RefreshFlags.value.is_(True)).order_by(
            RefreshFlags.account.desc()).all()
        return result


def set_setting(key: str, value: bool, account: str, notes: str = None):
    """Insert or update a setting value for a given account."""
    with Db.get_session(sync) as session:
        record = session.query(RefreshFlags).filter(RefreshFlags.thread_name.is_(key),
                                                    RefreshFlags.account.is_(account)).first()
        if record:
            record.value = value
            record.notes = notes
        else:
            record = RefreshFlags(account=account, key=key, value=value, notes=notes)
            session.add(record)
        return record
