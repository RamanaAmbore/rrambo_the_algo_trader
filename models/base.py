from sqlalchemy.ext.declarative import declarative_base

from utils.logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()
