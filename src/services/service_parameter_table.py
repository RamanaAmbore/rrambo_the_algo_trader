from src.core.singleton_base import SingletonBase
from src.helpers.logger import get_logger
from src.models import ParameterTable
from src.services.service_base import ServiceBase

logger = get_logger(__name__)


class ServiceParameterTable(SingletonBase, ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    model = ParameterTable
    conflict_cols = ['account', 'parameter']

    def __init__(self):
        """Ensure __init__ is only called once."""
        if getattr(self, '_singleton_initialized', True):
            logger.debug(f"Instance for {self.__class__.__name__} already initialized.")
            return
        super().__init__(self.model, self.conflict_cols)


# Singleton instance
service_parameter_table = ServiceParameterTable()
