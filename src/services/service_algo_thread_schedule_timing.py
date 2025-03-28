import asyncio

from sqlalchemy import select
from src.core.database_manager import DatabaseManager as Db
from src.models import AlgoScheduleTime, AlgoThreadSchedule, AlgoThreads
from src.services.service_algo_schedules import get_market_hours_for_today


async def get_active_thread_schedule_times(account=None):
    """Fetch start and end times for active threads based on market hours."""
    async with Db.get_async_session() as session:
        stmt = (
            select(
                AlgoThreads.thread,
                AlgoThreadSchedule.schedule,
                AlgoScheduleTime.start_time,
                AlgoScheduleTime.end_time
            )
            .join(AlgoThreadSchedule, AlgoThreads.thread == AlgoThreadSchedule.thread)
            .join(AlgoScheduleTime, AlgoThreadSchedule.schedule == AlgoScheduleTime.schedule)
            .where(AlgoThreads.is_active == True)
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


# Simple test runner for async SQLAlchemy call
async def main():
    results = await get_active_thread_schedule_times()
    print("\n🧪 Active Thread Schedule Timings:\n")
    print(results)  # pretty prints list of tuples

if __name__ == "__main__":
    asyncio.run(main())
