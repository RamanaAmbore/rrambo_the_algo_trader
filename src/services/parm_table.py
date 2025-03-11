import logging

from src.utils import DbConnect as Db
from src.models import ParmTable

logger = logging.getLogger(__name__)


def fetch_all_records(sync=True):
    """Fetch all parameters as a nested dictionary."""
    try:
        with Db.get_session(sync) as session:
            return session.query(ParmTable).all()
    except Exception as e:
        print('Error in fetching records from parameter table: {e}')
        return {}


def refresh_parms():
    Db.initialize_parameters()