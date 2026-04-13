import json
import logging
from unittest.mock import patch, mock_open, AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket, WebSocketDisconnect

from server import app, ConnectionManager, manager, get_allowed_origins, websocket_endpoint


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


def test_get_allowed_origins_exception(caplog):
    with patch("tomllib.load", side_effect=Exception("Mocked tomllib error")):
        origins = get_allowed_origins()
        assert origins == ["http://localhost:8000", "http://127.0.0.1:8000"]
        assert "Could not load CORS origins from config" in caplog.text


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


def test_get_allowed_origins_exception(caplog):
    with patch("builtins.open", side_effect=Exception("Test open error")):
        with caplog.at_level(logging.WARNING):
            origins = get_allowed_origins()

    assert origins == ["http://localhost:8000", "http://127.0.0.1:8000"]
    assert "Could not load CORS origins from config: Test open error" in caplog.text


@pytest.mark.asyncio
async def test_connection_manager_broadcast_empty():
    test_manager = ConnectionManager()
    test_manager.active_connections = []

    # Should just return and not raise an error
    await test_manager.broadcast("test")


@pytest.mark.asyncio
async def test_empty_broadcast():
    test_manager = ConnectionManager()
    # Should return early without raising error
    await test_manager.broadcast("test message")


@pytest.mark.asyncio
async def test_connection_manager_broadcast():
    test_manager = ConnectionManager()
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()

    await test_manager.connect(ws1)
    await test_manager.connect(ws2)

    await test_manager.broadcast("test message")

    # Since tasks are created in the background, we need to yield to the event loop
    import asyncio
    await asyncio.sleep(0)

    assert "test message" in ws1.sent_messages
    assert "test message" in ws2.sent_messages


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

    # Since tasks are created in the background, we need to yield to the event loop
    import asyncio
    await asyncio.sleep(0)

    assert "Error broadcasting: Test broadcast error" in caplog.text


@pytest.mark.asyncio
async def test_websocket_endpoint_exception(caplog):
    class ErrorWebSocket(MockWebSocket):
        async def receive_text(self):
            raise Exception("Test generic socket error")

    ws = ErrorWebSocket()
    # It should not raise, just log the error and disconnect
    with caplog.at_level(logging.ERROR):
        await websocket_endpoint(ws)

    assert "WebSocket Error: Test generic socket error" in caplog.text
    assert ws not in manager.active_connections


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


def test_websocket_exception(caplog, client):
    manager.active_connections.clear()
    with patch.object(WebSocket, "receive_text", side_effect=Exception("Generic WS error")):
        with client.websocket_connect("/ws/sync") as websocket:
            pass
    assert "WebSocket Error: Generic WS error" in caplog.text


def test_websocket_disconnect(client):
    manager.active_connections.clear()

    with client.websocket_connect("/ws/sync") as websocket:
        assert len(manager.active_connections) == 1

    # Once the context manager exits, the disconnect happens
    assert len(manager.active_connections) == 0


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


@patch("uvicorn.run")
def test_main(mock_run):
    import runpy
    # Run the server module as __main__ to hit the if __name__ == "__main__": block
    runpy.run_module("server", run_name="__main__")
    # assert_called_once checks that it was called once.
    # The actual app instance differs because runpy loads a new instance of the module,
    # so we just assert the host and port kwargs.
    mock_run.assert_called_once()
    assert mock_run.call_args.kwargs["host"] == "0.0.0.0"
    assert mock_run.call_args.kwargs["port"] == 8000
