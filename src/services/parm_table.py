import logging

from src.utils import DbConnect as Db
from src.models import ParameterTable

logger = logging.getLogger(__name__)


def fetch_all_records(sync=True):
    """Fetch all parameters as a nested dictionary."""
    try:
        with Db.get_session_maker(sync) as session:
            return session.query(ParameterTable).all()
    except Exception as e:
        print('Error in fetching records from parameter table: {e}')
        return {}


def refresh_parms():
    Db.initialize_parameters()