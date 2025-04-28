import asyncio

from sqlalchemy import select

from src.helpers.database_manager import db
from src.models import ScheduleTime, ThreadSchedule, ThreadList
from src.services.service_schedule_list import get_market_hours_for_today


async def get_active_thread_schedule_time(account=None):
    """Fetch start and end times for active threads based on market hours."""
    async with db.get_async_session() as session:
        stmt = (
            select(
                ThreadList.thread,
                ThreadSchedule.schedule,
                ScheduleTime.start_time,
                ScheduleTime.end_time
            )
            .join(ThreadSchedule, ThreadList.thread == ThreadSchedule.thread)
            .join(ScheduleTime, ThreadSchedule.schedule == ScheduleTime.schedule)
            .where(ThreadList.is_active == True)
        )
        result = await session.execute(stmt)
        thread_schedules = result.all()  # List of tuples

    # Apply market schedule filtering
    market_hours = get_market_hours_for_today(account)
    if market_hours:
        filtered_threads = [
            (thread, schedule, start_time, end_time)
            for thread, schedule, start_time, end_time in thread_schedules
            if (start_time >= market_hours.start_time and end_time <= market_hours.end_time)
        ]
        return filtered_threads

    return thread_schedules  # Return all if no market hours found
