import json
from unittest.mock import patch, mock_open, AsyncMock

import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket

from server import app, ConnectionManager, manager


@pytest.fixture
def client():
    return TestClient(app)


class MockWebSocket:
    def __init__(self):
        self.sent_messages = []
        self.accepted = False

    async def accept(self):
        self.accepted = True

    async def send_text(self, data: str):
        self.sent_messages.append(data)


@pytest.mark.asyncio
async def test_connection_manager_connect():
    test_manager = ConnectionManager()
    ws = MockWebSocket()
    await test_manager.connect(ws)

    assert ws.accepted is True
    assert ws in test_manager.active_connections


@pytest.mark.asyncio
async def test_connection_manager_disconnect():
    test_manager = ConnectionManager()
    ws = MockWebSocket()
    await test_manager.connect(ws)
    assert ws in test_manager.active_connections

    test_manager.disconnect(ws)
    assert ws not in test_manager.active_connections


@pytest.mark.asyncio
async def test_connection_manager_broadcast():
    test_manager = ConnectionManager()
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()

    await test_manager.connect(ws1)
    await test_manager.connect(ws2)

    await test_manager.broadcast("test message")

    assert "test message" in ws1.sent_messages
    assert "test message" in ws2.sent_messages


@pytest.mark.asyncio
async def test_connection_manager_broadcast_empty():
    test_manager = ConnectionManager()
    # active_connections is empty
    await test_manager.broadcast("should return early")

@pytest.mark.asyncio
async def test_connection_manager_broadcast_error(caplog):
    test_manager = ConnectionManager()
    ws = MockWebSocket()
    await test_manager.connect(ws)

    # Make send_text raise an exception
    async def mock_send_text(msg):
        raise Exception("Test broadcast error")

    ws.send_text = mock_send_text

    await test_manager.broadcast("test message")
    assert "Error broadcasting: Test broadcast error" in caplog.text


def test_websocket_sync_endpoint(client):
    # Ensure manager is empty at start
    manager.active_connections.clear()

    with client.websocket_connect("/ws/sync") as websocket1:
        with client.websocket_connect("/ws/sync") as websocket2:
            # Send from client 1
            websocket1.send_text("hello from 1")

            # Client 1 should receive its own broadcast
            data1 = websocket1.receive_text()
            assert data1 == "hello from 1"

            # Client 2 should also receive it
            data2 = websocket2.receive_text()
            assert data2 == "hello from 1"


def test_websocket_disconnect(client):
    manager.active_connections.clear()

    with client.websocket_connect("/ws/sync") as websocket:
        assert len(manager.active_connections) == 1

    # Once the context manager exits, the disconnect happens
    assert len(manager.active_connections) == 0

def test_websocket_endpoint_general_error(client, caplog):
    manager.active_connections.clear()

    with patch.object(WebSocket, "receive_text", side_effect=Exception("General WS Error")):
        # We catch the exception and assert on the log
        try:
            with client.websocket_connect("/ws/sync") as websocket:
                pass
        except Exception:
            pass

    assert "WebSocket Error: General WS Error" in caplog.text


@patch("server.aiofiles.open")
def test_receive_data_success(mock_file, client):
    # Mock the asynchronous context manager returned by aiofiles.open
    mock_file_instance = AsyncMock()
    mock_file.return_value.__aenter__.return_value = mock_file_instance

    test_data = {"user_id": "123", "action": "click"}
    response = client.post("/api/data", json=test_data)

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify file was written to
    mock_file_instance.write.assert_called_once()
    write_args = mock_file_instance.write.call_args[0][0]
    written_data = json.loads(write_args.strip())
    assert written_data == test_data


@patch("server.aiofiles.open")
def test_receive_data_error(mock_file, client):
    mock_file_instance = AsyncMock()
    mock_file.return_value.__aenter__.return_value = mock_file_instance
    mock_file_instance.write.side_effect = Exception("Disk full")

    test_data = {"user_id": "123", "action": "click"}
    response = client.post("/api/data", json=test_data)

    assert response.status_code == 200
    assert response.json() == {"status": "error", "message": "Disk full"}


@patch("server.tomllib.load")
def test_get_allowed_origins_error(mock_toml_load, caplog):
    from server import get_allowed_origins
    mock_toml_load.side_effect = Exception("Toml load error")
    origins = get_allowed_origins()
    assert origins == ["http://localhost:8000", "http://127.0.0.1:8000"]
    assert "Could not load CORS origins from config: Toml load error" in caplog.text


@patch("uvicorn.run")
def test_main_execution(mock_run):
    import runpy
    # Execute the server module as if it were run from the command line
    runpy.run_module("server", run_name="__main__")

    mock_run.assert_called_once()
    assert mock_run.call_args[1]["host"] == "0.0.0.0"
    assert mock_run.call_args[1]["port"] == 8000
