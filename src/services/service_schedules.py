from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.database_manager import DatabaseManager as Db
from src.helpers.date_time_utils import today_indian
from src.helpers.logger import get_logger
from src.models.schedule_time import ScheduleTime
from src.settings.constants_manager import DEFAULT_ALGO_SCHEDULES
from src.settings.parameter_manager import parms

logger = get_logger(__name__)

market = "MARKET"


def get_market_hours_for_today(account):
    """Retrieve today's market hours with a fallback mechanism."""

    today = today_indian()
    weekday = today.strftime("%A")

    for acc_id in [account, None]:  # Try account-specific first, then global
        with Db.get_sync_session() as session:
            logger.info(f"Checking for MARKET hours for {today} with acc_id {acc_id}")

            query = select(ScheduleTime).where(ScheduleTime.market_date.is_(today),
                                                   ScheduleTime.schedule.is_(market))
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours

            logger.info(f"Checking default weekday MARKET hours for {weekday} with acc_id {acc_id}")
            query = select(ScheduleTime).where(ScheduleTime.weekday.is_(weekday),
                                                   ScheduleTime.schedule.is_(market))
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours

            logger.info(f"Checking for GLOBAL default MARKET hours with acc_id {acc_id}")
            query = select(ScheduleTime).where(ScheduleTime.weekday.is_("GLOBAL"),
                                                   ScheduleTime.schedule.is_(market))
            market_hours = session.execute(query).scalars().first()
            if market_hours:
                return market_hours

    return None  # Return None if no matching schedule is found


def get_batch_schedules(session: Session, account, batch_type=None):
    """Retrieve today's batch processing schedules."""

    today = today_indian()

    if batch_type and not isinstance(batch_type, (list, tuple, set)):
        batch_type = [batch_type]

    schedules = []

    for acc_id in [account, None]:
        logger.info(f"Checking batch schedules of type {batch_type} for {today} with account {acc_id}")

        query = select(ScheduleTime).where(ScheduleTime.market_date.is_(today),
                                               ScheduleTime.schedule.is_(market),
                                               ScheduleTime.account.is_(
                                                   acc_id) if acc_id is None else ScheduleTime.account == acc_id)

        if batch_type:
            query = query.where(ScheduleTime.schedule.in_(batch_type))

        found_schedules = session.execute(query).scalars().all()
        if found_schedules:
            schedules.extend(found_schedules)

    if not schedules:
        logger.info(f"No batch schedules found for {batch_type} on {today}")

    return schedules  # Return list instead of None


# Add this function to manually insert defaults if needed
def ensure_default_records():
    """Manually ensure default records exist."""
    with Db.get_sync_session() as session:
        existing = session.query(ScheduleTime).filter(
            ScheduleTime.weekday.in_(["GLOBAL", parms.SATURDAY, parms.SUNDAY])
        ).all()

        if not existing:
            try:
                for record in DEFAULT_ALGO_SCHEDULES:
                    session.add(ScheduleTime(**record))
                session.commit()
                logger.info("Default market hours inserted manually")
            except Exception as e:
                logger.error(f"Error inserting default records: {e}")
                session.rollback()
