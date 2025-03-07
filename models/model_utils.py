import enum


class WeekdayEnum(enum.Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class Schedule(enum.Enum):
    MARKET = "MARKET"
    WEEKEND = 'WEEKEND'


class ThreadName(enum.Enum):
    WEBSOCKET = "WEBSOCKET"
    DB_UPDATE = "DB_UPDATE"
    REFRESH = "REFRESH"
    REPORTS = "REPORTS"
    DATA_SCAN = "DATA_SCAN"
    POSITION_SCAN = "POSITION_SCAN"
    ORDER_TRACK = "ORDER_TRACK"
    ORDER_TRIGGER = "ORDER_TRIGGER"
    MARKET_CHECK = "MARKET_CHECK"
    FUND_TRACK = "FUND_TRACK"


class source(enum.Enum):
    API = "API"
    MANUAL = "MANUAL"
    WEBSOCKET = "WEBSOCKET"
    REPORTS = "REPORTS"
    FRONTEND = 'FRONTEND'
    CODE = "CODE"
