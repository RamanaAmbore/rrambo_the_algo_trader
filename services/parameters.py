import logging
from collections import defaultdict

from utils.db_connect import DbConnection as Db
from models import Parameters

logger = logging.getLogger(__name__)


def fetch_all_records(sync=True):
    """Fetch all parameters as a nested dictionary."""
    try:
        with Db.get_session(sync) as session:
            return session.query(Parameters).all()
    except Exception as e:
        print('Error in fetching records from parameter table: {e}')
        return {}


