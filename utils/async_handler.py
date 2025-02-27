import asyncio
import logging
from logging.handlers import QueueHandler, QueueListener


class AsyncQueueHandler(QueueHandler):
    """Custom async logging handler using asyncio queue."""

    def __init__(self, queue):
        super().__init__(queue)
        self.queue = queue


async def async_log_worker(queue):
    """Background task to process log records."""
    while True:
        record = await queue.get()
        if record is None:  # Stop condition
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)


def setup_async_logger():
    """Setup an async logger using asyncio queue."""
    log_queue = asyncio.Queue()
    queue_handler = AsyncQueueHandler(log_queue)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Attach queue handler to logger
    logger.addHandler(queue_handler)
    logger.addHandler(stream_handler)

    # Start async logging worker
    asyncio.create_task(async_log_worker(log_queue))

    return logger, log_queue


# Initialize async logger
logger, log_queue = setup_async_logger()


# Usage
async def test_logging():
    logger.info("Async logging test 1")
    logger.debug("Async logging test 2")
    await asyncio.sleep(1)  # Give time for async processing


asyncio.run(test_logging())
