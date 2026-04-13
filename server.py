import json
import logging
import aiofiles
import tomllib
from typing import List

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_allowed_origins() -> List[str]:
    origins = ["http://localhost:8000", "http://127.0.0.1:8000"]
    try:
        with open("config.toml", "rb") as f:
            config_data = tomllib.load(f)
            if "security" in config_data and "cors-allowed-origins" in config_data["security"]:
                origins = config_data["security"]["cors-allowed-origins"]
    except Exception as e:
        logger.warning(f"Could not load CORS origins from config: {e}")
    return origins

app = FastAPI(title="Interactive-MD Sync Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Active: {len(self.active_connections)}")

    async def _send_to_connection(self, connection: WebSocket, message: str):
        try:
            await connection.send_text(message)
        except Exception as e:
            logger.error(f"Error broadcasting: {e}")

    async def broadcast(self, message: str):
        import asyncio
        if not self.active_connections:
            return
        tasks = [self._send_to_connection(conn, message) for conn in self.active_connections]
        await asyncio.gather(*tasks)


manager = ConnectionManager()


@app.websocket("/ws/sync")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast all messages received from host
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        manager.disconnect(websocket)


@app.post("/api/data")
async def receive_data(request: Request):
    try:
        data = await request.json()
        # Use aiofiles for asynchronous file I/O to avoid blocking the event loop
        async with aiofiles.open("data.jsonl", "a", encoding="utf-8") as f:
            await f.write(json.dumps(data) + "\n")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
