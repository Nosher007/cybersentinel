"""
TICKET-028 — Error handling tests.
Tests: agent failures, WS disconnects, invalid prompts, pipeline errors.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

client = TestClient(app)


def _mock_interpreter(scenario_id: str = "account_takeover"):
    mock = MagicMock()
    mock.interpret.return_value = MagicMock(
        scenario_id=scenario_id,
        attack_type=MagicMock(value="brute_force"),
        target_service="auth",
        intensity="high",
        reasoning="test",
    )
    return mock


# ── Invalid prompt handling ───────────────────────────────────────────────────

class TestInvalidPromptHandling:

    def test_empty_prompt_returns_400(self):
        res = client.post("/attack", json={"prompt": ""})
        assert res.status_code == 400

    def test_whitespace_prompt_returns_400(self):
        res = client.post("/attack", json={"prompt": "   "})
        assert res.status_code == 400

    def test_missing_prompt_field_returns_422(self):
        res = client.post("/attack", json={})
        assert res.status_code == 422

    def test_null_prompt_returns_422(self):
        res = client.post("/attack", json={"prompt": None})
        assert res.status_code == 422

    @patch("routers.attack.AttackPromptInterpreter")
    @patch("routers.attack.engine")
    def test_interpreter_exception_returns_500(self, mock_engine, mock_cls):
        mock_engine.is_running = False
        mock_interp = MagicMock()
        mock_interp.interpret.side_effect = Exception("Gemini API down")
        mock_cls.return_value = mock_interp

        res = client.post("/attack", json={"prompt": "try to hack"})
        assert res.status_code == 500

    @patch("routers.attack.AttackPromptInterpreter")
    @patch("routers.attack.engine")
    def test_interpreter_exception_returns_error_detail(self, mock_engine, mock_cls):
        mock_engine.is_running = False
        mock_interp = MagicMock()
        mock_interp.interpret.side_effect = Exception("Gemini API down")
        mock_cls.return_value = mock_interp

        res = client.post("/attack", json={"prompt": "try to hack"})
        assert "detail" in res.json()


# ── Pipeline error broadcasting ───────────────────────────────────────────────

class TestPipelineErrorBroadcasting:

    def test_run_agent_pipeline_returns_error_dict_on_failure(self):
        from routers.websocket import _run_agent_pipeline
        with patch("routers.websocket.build_pipeline") as mock_build:
            mock_pipeline = MagicMock()
            mock_pipeline.invoke.side_effect = Exception("LLM timeout")
            mock_build.return_value = mock_pipeline

            result = _run_agent_pipeline([("some log", "auth")])
            assert result is not None
            assert "error" in result

    def test_run_agent_pipeline_empty_logs_returns_none(self):
        from routers.websocket import _run_agent_pipeline
        result = _run_agent_pipeline([])
        assert result is None

    def test_run_agent_pipeline_orchestrator_error_returns_error_dict(self):
        from routers.websocket import _run_agent_pipeline
        with patch("routers.websocket.build_pipeline") as mock_build:
            mock_pipeline = MagicMock()
            mock_pipeline.invoke.return_value = {"error": "ThreatDetector failed: timeout"}
            mock_build.return_value = mock_pipeline

            result = _run_agent_pipeline([("log line", "auth")])
            assert "error" in result


# ── WebSocket connection handling ─────────────────────────────────────────────

class TestWebSocketConnectionHandling:

    def test_websocket_connects_successfully(self):
        with TestClient(app) as c:
            with c.websocket_connect("/ws") as ws:
                ws.send_text("ping")
                data = ws.receive_text()
                assert data is not None

    def test_websocket_ack_has_correct_type(self):
        import json
        # Use client directly without lifespan to avoid event loop conflicts
        c = TestClient(app, raise_server_exceptions=False)
        with c.websocket_connect("/ws") as ws:
            ws.send_text("ping")
            data = json.loads(ws.receive_text())
            assert data.get("type") == "ack"

    def test_connection_manager_tracks_connections(self):
        """ConnectionManager adds and removes clients correctly."""
        import asyncio
        from routers.websocket import ConnectionManager

        async def run():
            mgr = ConnectionManager()
            ws = MagicMock()
            ws.accept = AsyncMock()
            await mgr.connect(ws)
            assert ws in mgr.active
            mgr.disconnect(ws)
            assert ws not in mgr.active

        asyncio.run(run())

    def test_broadcast_skips_dead_connections(self):
        import asyncio
        from routers.websocket import ConnectionManager

        async def run():
            mgr = ConnectionManager()
            dead_ws = MagicMock()
            dead_ws.send_text = AsyncMock(side_effect=Exception("connection closed"))
            mgr.active.append(dead_ws)
            await mgr.broadcast({"type": "test"})
            assert dead_ws not in mgr.active

        asyncio.run(run())
