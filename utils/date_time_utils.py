from datetime import datetime
from zoneinfo import ZoneInfo

from utils.config_loader import sc  # Importing timezone settings

# Define constants for timezones
EST_ZONE = ZoneInfo(sc.EST_TIMEZONE)
INDIAN_ZONE = ZoneInfo(sc.INDIAN_TIMEZONE)


# Helper functions for direct use
def timestamp_local():
    """Returns today's date in the local timezone."""
    return datetime.today()  # Uses system's local timezone


def timestamp_est():
    return datetime.now(tz=EST_ZONE)


def timestamp_indian():
    return datetime.now(tz=INDIAN_ZONE)


def today_local():
    """Returns today's date in the local timezone."""
    return datetime.today().date()  # Uses system's local timezone


def today_est():
    return datetime.now(tz=EST_ZONE).date()


def today_indian():
    return datetime.now(tz=INDIAN_ZONE).date()


def current_time_local():
    """Returns the current time in the local timezone."""
    return datetime.today().time()  # Uses system's local timezone


def current_time_est():
    return datetime.now(tz=EST_ZONE).time()


def current_time_indian():
    return datetime.now(tz=INDIAN_ZONE).time()


# Test Code in __main__
if __name__ == "__main__":
    print(f"EST timestamp: {timestamp_est()}")
    print(f"Indian timestamp: {timestamp_indian()}")
    print(f"Local timestamp: {timestamp_local()}")

    print(f"Today's Date in EST: {today_est()}")
    print(f"Today's Date in IST: {today_indian()}")
    print(f"Current Time in IST: {today_local()}")

    print(f"Current Time in IST: {current_time_indian()}")
    print(f"Current Time in EST: {current_time_local()}")
    print(f"Current Time in EST: {current_time_est()}")
