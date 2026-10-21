"""
Tests for WebSocket hardening: Origin allowlist, client message size cap,
and the bounded in-memory threat history.
"""
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app
from routers import websocket as ws_router

client = TestClient(app)


class TestWebSocketOrigin:

    def test_allowed_origin_connects(self):
        origin = next(iter(ws_router.ALLOWED_WS_ORIGINS))
        with client.websocket_connect("/ws", headers={"origin": origin}) as ws:
            ws.send_text("ping")
            assert '"ack"' in ws.receive_text()

    def test_missing_origin_connects(self):
        with client.websocket_connect("/ws") as ws:
            ws.send_text("ping")
            assert '"ack"' in ws.receive_text()

    def test_disallowed_origin_is_rejected(self):
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect("/ws", headers={"origin": "https://evil.example"}) as ws:
                ws.receive_text()
        assert exc.value.code == 1008


class TestWebSocketMessageSize:

    def test_oversized_message_closes_connection(self):
        with client.websocket_connect("/ws") as ws:
            ws.send_text("x" * (ws_router.MAX_CLIENT_MESSAGE_CHARS + 1))
            with pytest.raises(WebSocketDisconnect) as exc:
                ws.receive_text()
            assert exc.value.code == 1009


class TestThreatStoreCap:

    def test_cap_is_reasonable(self):
        assert 10 <= ws_router.MAX_STORED_THREATS <= 1000
