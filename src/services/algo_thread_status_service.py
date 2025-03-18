import pandas as pd
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert

from src.core.database_manager import DatabaseManager as Db
from src.models import AlgoThreadStatus
from src.services.base_service import BaseService
from src.helpers.date_time_utils import convert_to_timezone
from src.helpers.logger import get_logger

logger = get_logger(__name__)


class AlgoThreadStatusService(BaseService):
    """Service class for handling ReportTradebook database operations."""

    model = AlgoThreadStatus

    @classmethod
    def validate_clean_records(cls, data_record) :
        """Cleans and validates trade records before inserting into the database."""

        return data_record

