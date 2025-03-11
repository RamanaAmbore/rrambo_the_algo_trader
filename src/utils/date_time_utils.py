from datetime import datetime
from zoneinfo import ZoneInfo

from src.utils.parameter_manager import sc  # Importing timezone settings
from src.utils.logger import get_logger

logger  = get_logger(__name__)

# Define constants for timezones
EST_ZONE = ZoneInfo(sc.EST_TIMEZONE)
INDIAN_TIMEZONE = ZoneInfo(sc.INDIAN_TIMEZONE)


# Helper functions for direct use
def timestamp_local():
    """Returns today's date in the local timezone."""
    return datetime.today()  # Uses system's local timezone


def timestamp_est():
    return datetime.now(tz=EST_ZONE)


def timestamp_indian():
    return datetime.now(tz=INDIAN_TIMEZONE)


def today_local():
    """Returns today's date in the local timezone."""
    return datetime.today().date()  # Uses system's local timezone


def today_est():
    return datetime.now(tz=EST_ZONE).date()


def today_indian():
    return datetime.now(tz=INDIAN_TIMEZONE).date()


def current_time_local():
    """Returns the current time in the local timezone."""
    return datetime.today().time()  # Uses system's local timezone


def current_time_est():
    return datetime.now(tz=EST_ZONE).time()


def current_time_indian():
    return datetime.now(tz=INDIAN_TIMEZONE).time()


# Test Code in __main__
if __name__ == "__main__":
    logger.info(f"EST timestamp: {timestamp_est()}")
    logger.info(f"Indian timestamp: {timestamp_indian()}")
    logger.info(f"Local timestamp: {timestamp_local()}")

    logger.info(f"Today's Date in EST: {today_est()}")
    logger.info(f"Today's Date in IST: {today_indian()}")
    logger.info(f"Current Time in IST: {today_local()}")

    logger.info(f"Current Time in IST: {current_time_indian()}")
    logger.info(f"Current Time in EST: {current_time_local()}")
    logger.info(f"Current Time in EST: {current_time_est()}")
