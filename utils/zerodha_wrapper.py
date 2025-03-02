from functools import wraps

from utils.logger import get_logger
from kiteconnect.exceptions import TokenException

from utils.config_loader import sc
from zerodha_kite import ZerodhaKite

logger = get_logger(__name__)


def zerodha_conn_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TokenException as e:
            logger.warning(f"Kite API call failed : {e}. Retrying...")
            for attempt in range(sc.MAX_KITE_CONN_RETRY_COUNT):
                try:
                    return func(*args, **kwargs)
                except TokenException as e:
                    logger.warning(
                        f"Kite API call failed: {e}. Retrying... ({attempt + 1} of {sc.MAX_KITE_CONN_RETRY_COUNT})")
                    ZerodhaKite.get_kite_conn(test_conn=True)
            logger.error(f"Kite API call failed after {sc.MAX_KITE_CONN_RETRY_COUNT} attempts.")
            raise
        except  Exception as e:
            logger.error(str(e))
            raise

    return wrapper
