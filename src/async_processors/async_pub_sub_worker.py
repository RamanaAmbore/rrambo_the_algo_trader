import asyncio
from typing import Callable, Awaitable, Any, List

class AsyncPubSubWorker:
    def __init__(self, fetcher: Callable[[], Awaitable[list]],
                 processor: Callable[[Any], Awaitable[None]],
                 additional_tasks: List[Awaitable] = None,
                 name: str = "worker"):
        self.queue = asyncio.Queue()
        self.fetcher = fetcher
        self.processor = processor
        self.additional_tasks = additional_tasks or []
        self.name = name

    async def publish(self):
        items = await self.fetcher()
        for item in items:
            await self.queue.put(item)
        await self.queue.put(None)  # signal end

    async def consume(self):
        while True:
            item = await self.queue.get()
            if item is None:
                break
            await self.processor(item)

    async def run(self):
        await asyncio.gather(
            self.publish(),
            self.consume(),
            *self.additional_tasks
        )
