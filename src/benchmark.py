import asyncio
import time

from src.server import ConnectionManager

class MockConnection:
    def __init__(self, delay=0.01):
        self.delay = delay

    async def send_text(self, message):
        await asyncio.sleep(self.delay)

async def main():
    num_connections = 100
    delay = 0.01
    print(f"Measuring broadcast time with {num_connections} connections, {delay}s delay each...")

    manager = ConnectionManager()
    for _ in range(num_connections):
        manager.active_connections.append(MockConnection(delay))

    start_time = time.perf_counter()
    await manager.broadcast("test message")
    end_time = time.perf_counter()
    print(f"Time taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
