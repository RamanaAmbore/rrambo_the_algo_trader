import asyncio

from sqlalchemy import select

from src.core.database_manager import DatabaseManager as Db
from src.models import AlgoScheduleTime, AlgoThreadScheduleXref, AlgoThreads


async def get_active_thread_schedule_times():
    async with Db.get_async_session() as session:
        stmt = (
            select(
                AlgoThreads.thread,
                AlgoThreadScheduleXref.schedule,
                AlgoScheduleTime.start_time,
                AlgoScheduleTime.end_time
            )
            .join(AlgoThreadScheduleXref, AlgoThreads.thread == AlgoThreadScheduleXref.thread)
            .join(AlgoScheduleTime, AlgoThreadScheduleXref.schedule == AlgoScheduleTime.schedule)
            .where(AlgoThreads.is_active == True)
        )
        result = await session.execute(stmt)
        return result.all()  # List of tuples


# Simple test runner for async SQLAlchemy call
async def main():
    results = await get_active_thread_schedule_times()
    print("\n🧪 Active Thread Schedule Timings:\n")
    print(results)  # pretty prints list of tuples

if __name__ == "__main__":
    asyncio.run(main())
