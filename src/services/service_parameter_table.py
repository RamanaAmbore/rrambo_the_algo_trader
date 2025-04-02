import logging

from src.models import ParameterTable
from src.services.service_base import ServiceBase

logger = logging.getLogger(__name__)


class ServiceParameterTable(ServiceBase):
    """Service class for handling ReportProfitLoss database operations."""

    _instance = None
    model = ParameterTable
    conflict_cols = ['account', 'parameter']

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ServiceParameterTable, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Ensure __init__ is only called once."""
        if not hasattr(self, "_initialized"):  # Ensure _initialized is instance-scoped
            super().__init__(self.model, self.conflict_cols)
            self._initialized = True  # Mark as initialized


# Singleton instance
service_parameter_table = ServiceParameterTable()
