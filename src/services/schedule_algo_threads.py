from src.models import AlgoThreads
from src.services.service_base import ServiceBase


class ServiceAccessToken(ServiceBase):
    """Service class for handling AccessTokens database operations."""

    model = AlgoThreads  # Assign model at the class level

    def __init__(self):
        """Initialize the service with the AccessTokens model."""
        super().__init__(self.model)
