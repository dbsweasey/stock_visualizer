import asyncio
import random

queue = asyncio.Queue()

async def producer():
    while True:
        await queue.put(random.random())
        await asyncio.sleep(1)

async def consumer():
    while True:
        item = await queue.get()
        print(item)

async def main():
    asyncio.create_task(producer())
    asyncio.create_task(consumer())

    await asyncio.sleep(20)
