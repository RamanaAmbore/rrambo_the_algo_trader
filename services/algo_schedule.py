from datetime import datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy import select, event
from sqlalchemy.orm import Session

from models import AlgoSchedule
from utils.date_time_utils import today_indian
from utils.logger import get_logger
from utils.settings_loader import sc
from utils.db_connection import DbConnection as Db

logger = get_logger(__name__)

market = "MARKET"


def get_market_hours_for_today(account_id):
    """Retrieve today's market hours with a fallback mechanism."""

    today = datetime.now(tz=ZoneInfo(sc.INDIAN_TIMEZONE)).date()
    weekday = today.strftime("%A")

    for acc_id in [account_id, None]:  # Try account-specific first, then global
        with Db.get_sync_session() as session:
            logger.info(f"Checking for MARKET hours for {today} with acc_id {acc_id}")

            query = select(AlgoSchedule).where(AlgoSchedule.market_date.is_(today),
                                               AlgoSchedule.thread_name.is_(market), AlgoSchedule.account_id.is_(
                    acc_id) if acc_id is None else AlgoSchedule.account_id == acc_id)
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours

            logger.info(f"Checking default weekday MARKET hours for {weekday} with acc_id {acc_id}")
            query = select(AlgoSchedule).where(AlgoSchedule.weekday.is_(weekday), AlgoSchedule.thread_name.is_(market),
                                               AlgoSchedule.account_id.is_(
                                                   acc_id) if acc_id is None else AlgoSchedule.account_id == acc_id)
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours

            logger.info(f"Checking for GLOBAL default MARKET hours with acc_id {acc_id}")
            query = select(AlgoSchedule).where(AlgoSchedule.weekday.is_("GLOBAL"), AlgoSchedule.thread_name.is_(market),
                                               AlgoSchedule.account_id.is_(
                                                   acc_id) if acc_id is None else AlgoSchedule.account_id == acc_id)
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours

    return None  # Return None if no matching schedule is found


def get_batch_schedules(session: Session, account_id, batch_type=None):
    """Retrieve today's batch processing schedules."""

    today = today_indian()

    if batch_type and not isinstance(batch_type, (list, tuple, set)):
        batch_type = [batch_type]

    schedules = []

    for acc_id in [account_id, None]:
        logger.info(f"Checking batch schedules of type {batch_type} for {today} with account_id {acc_id}")

        query = select(AlgoSchedule).where(AlgoSchedule.market_date.is_(today), AlgoSchedule.thread_name.is_(market),
                                           AlgoSchedule.account_id.is_(
                                               acc_id) if acc_id is None else AlgoSchedule.account_id == acc_id)

        if batch_type:
            query = query.where(AlgoSchedule.thread_name.in_(batch_type))

        found_schedules = session.execute(query).scalars().all()
        if found_schedules:
            schedules.extend(found_schedules)

    if not schedules:
        logger.info(f"No batch schedules found for {batch_type} on {today}")

    return schedules  # Return list instead of None




@event.listens_for(AlgoSchedule.__table__, "after_create")
def insert_default_records(target, connection, **kwargs):
    """Ensure default market hour records exist for 'GLOBAL' and weekends.

    - Creates a GLOBAL default schedule (09:00 - 15:30).
    - Marks Saturday and Sunday as closed.
    - Prevents duplicate default entries.
    """

    default_records = [("GLOBAL", "MARKET", time(9, 0), time(15, 30), True), ("Saturday", "MARKET", None, None, False),
                       ("Sunday", "MARKET", None, None, False), ]

    connection.execute(target.insert(),default_records)


