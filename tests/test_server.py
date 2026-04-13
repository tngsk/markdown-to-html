import pytest
from fastapi.testclient import TestClient
import tomllib
from unittest.mock import patch, mock_open

from server import app, get_allowed_origins

client = TestClient(app)

def test_cors_allowed_origin():
    # Test request from an allowed origin (http://localhost:8000)
    response = client.options(
        "/api/data",
        headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:8000"

def test_cors_disallowed_origin():
    # Test request from a disallowed origin
    response = client.options(
        "/api/data",
        headers={
            "Origin": "http://malicious-site.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    # The middleware typically responds with 400 Bad Request or lacks the Access-Control-Allow-Origin header
    # Let's check for the absence of the allowed origin header or 400
    if response.status_code == 200:
        assert "access-control-allow-origin" not in response.headers or response.headers.get("access-control-allow-origin") != "http://malicious-site.com"
    else:
        assert response.status_code == 400

@patch("builtins.open", new_callable=mock_open, read_data=b"[security]\ncors-allowed-origins = [\"http://test-origin.com\"]\n")
def test_get_allowed_origins_with_config(mock_file):
    origins = get_allowed_origins()
    assert origins == ["http://test-origin.com"]

@patch("builtins.open", side_effect=FileNotFoundError)
def test_get_allowed_origins_default(mock_file):
    origins = get_allowed_origins()
    assert origins == ["http://localhost:8000", "http://127.0.0.1:8000"]
