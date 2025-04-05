from pubsub_worker import AsyncPubSubWorker
from some_module import get_kite_conn, service_positions  # Adjust to your module

# Define fetcher and processor
def positions_fetcher():
    return asyncio.to_thread(lambda: get_kite_conn().positions)

async def position_processor(position):
    await service_positions.process_records(position)

# Optional independent task
async def reorders_task():
    await service_positions.process_reorders()

# Instantiate the worker
positions_worker = AsyncPubSubWorker(
    fetcher=positions_fetcher,
    processor=position_processor,
    additional_tasks=[reorders_task()],
    name="positions_worker"
)

# Run the worker (e.g., inside your main async function)
await positions_worker.run()
