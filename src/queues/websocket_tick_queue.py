import asyncio

class WebsocketTickQueue:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def push(self, tick_data):
        await self.queue.put(tick_data)

    async def pop(self):
        return await self.queue.get()

tick_queue = WebsocketTickQueue()
