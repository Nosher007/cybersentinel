"""
Tests for FastAPI endpoints — health check + attack pipeline.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

client = TestClient(app)


# ── Health check ─────────────────────────────────────────────────────────────

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "cybersentinel-backend"


# ── POST /attack ──────────────────────────────────────────────────────────────

class TestAttackEndpoint:

    @patch("routers.attack.AttackPromptInterpreter")
    @patch("routers.attack.engine")
    def test_attack_accepts_prompt(self, mock_engine, mock_interpreter_class):
        mock_engine.is_running = False
        mock_interp = MagicMock()
        mock_interp.interpret.return_value = MagicMock(
            scenario_id="account_takeover",
            attack_type=MagicMock(value="brute_force"),
            target_service="auth",
            intensity="high",
            reasoning="brute force detected",
        )
        mock_interpreter_class.return_value = mock_interp
        mock_engine.start = AsyncMock()

        response = client.post("/attack", json={"prompt": "try to brute force the login"})
        assert response.status_code == 200

    @patch("routers.attack.AttackPromptInterpreter")
    @patch("routers.attack.engine")
    def test_attack_calls_interpreter_with_prompt(self, mock_engine, mock_interpreter_class):
        mock_engine.is_running = False
        mock_interp = MagicMock()
        mock_interp.interpret.return_value = MagicMock(
            scenario_id="account_takeover",
            attack_type=MagicMock(value="brute_force"),
            target_service="auth",
            intensity="high",
            reasoning="brute force",
        )
        mock_interpreter_class.return_value = mock_interp
        mock_engine.start = AsyncMock()

        client.post("/attack", json={"prompt": "try to brute force the login"})
        mock_interp.interpret.assert_called_once_with("try to brute force the login")

    @patch("routers.attack.AttackPromptInterpreter")
    @patch("routers.attack.engine")
    def test_attack_response_includes_scenario_id(self, mock_engine, mock_interpreter_class):
        mock_engine.is_running = False
        mock_interp = MagicMock()
        mock_interp.interpret.return_value = MagicMock(
            scenario_id="sql_injection",
            attack_type=MagicMock(value="sql_injection"),
            target_service="database",
            intensity="medium",
            reasoning="sql injection",
        )
        mock_interpreter_class.return_value = mock_interp
        mock_engine.start = AsyncMock()

        response = client.post("/attack", json={"prompt": "inject SQL into the database"})
        assert response.json()["scenario_id"] == "sql_injection"

    @patch("routers.attack.AttackPromptInterpreter")
    @patch("routers.attack.engine")
    def test_attack_response_includes_attack_info(self, mock_engine, mock_interpreter_class):
        mock_engine.is_running = False
        mock_interp = MagicMock()
        mock_interp.interpret.return_value = MagicMock(
            scenario_id="ddos_attack",
            attack_type=MagicMock(value="ddos"),
            target_service="api_gateway",
            intensity="high",
            reasoning="flooding detected",
        )
        mock_interpreter_class.return_value = mock_interp
        mock_engine.start = AsyncMock()

        response = client.post("/attack", json={"prompt": "flood the API with traffic"})
        data = response.json()
        assert "attack_type" in data
        assert "target_service" in data

    @patch("routers.attack.AttackPromptInterpreter")
    @patch("routers.attack.engine")
    def test_attack_empty_prompt_returns_400(self, mock_engine, mock_interpreter_class):
        mock_engine.is_running = False
        response = client.post("/attack", json={"prompt": ""})
        assert response.status_code == 400

    @patch("routers.attack.AttackPromptInterpreter")
    @patch("routers.attack.engine")
    def test_attack_while_running_returns_409(self, mock_engine, mock_interpreter_class):
        mock_engine.is_running = True
        mock_engine.current_scenario_id = "account_takeover"
        response = client.post("/attack", json={"prompt": "brute force login"})
        assert response.status_code == 409

    @patch("routers.attack.AttackPromptInterpreter")
    @patch("routers.attack.engine")
    def test_attack_starts_simulation_with_correct_scenario(self, mock_engine, mock_interpreter_class):
        mock_engine.is_running = False
        mock_interp = MagicMock()
        mock_interp.interpret.return_value = MagicMock(
            scenario_id="insider_threat",
            attack_type=MagicMock(value="insider_threat"),
            target_service="database",
            intensity="low",
            reasoning="insider access",
        )
        mock_interpreter_class.return_value = mock_interp
        mock_engine.start = AsyncMock()

        client.post("/attack", json={"prompt": "access records after hours"})
        mock_engine.start.assert_called_once()
        call_args = mock_engine.start.call_args[0]
        assert call_args[0] == "insider_threat"


# ── POST /stop ────────────────────────────────────────────────────────────────

class TestStopEndpoint:

    @patch("routers.attack.engine")
    def test_stop_returns_200(self, mock_engine):
        mock_engine.stop = AsyncMock()
        response = client.post("/stop")
        assert response.status_code == 200

    @patch("routers.attack.engine")
    def test_stop_calls_engine_stop(self, mock_engine):
        mock_engine.stop = AsyncMock()
        client.post("/stop")
        mock_engine.stop.assert_called_once()
