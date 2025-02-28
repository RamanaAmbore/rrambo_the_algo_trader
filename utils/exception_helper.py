from functools import wraps

from dotenv import load_dotenv
from kiteconnect.exceptions import TokenException

from utils.config_loader import sc
from zerodha_kite import ZerodhaKite
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


def exception_helper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TokenException as e:
            logger.warning(f"Kite API call failed : {e}. Retrying...")
            for attempt in range(sc.conn_retry_count):
                try:
                    return func(*args, **kwargs)
                except TokenException as e:
                    logger.warning(f"Kite API call failed: {e}. Retrying... ({attempt + 1} of {sc.conn_retry_count})")
                    ZerodhaKite.get_kite_conn(test_conn=True)
            logger.error(f"Kite API call failed after {sc.conn_retry_count} attempts.")
            raise
        except  Exception as e:
            logger.error(str(e))
            raise

    return wrapper
