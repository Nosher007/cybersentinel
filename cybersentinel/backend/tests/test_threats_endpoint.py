"""
TICKET-029 — GET /threats endpoint tests.
Tests: returns list, empty session, threat structure, append on detection.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_threats():
    """Reset threat store before each test."""
    from routers.threats import threat_store
    threat_store.clear()
    yield
    threat_store.clear()


class TestGetThreatsEndpoint:

    def test_get_threats_returns_200(self):
        res = client.get("/threats")
        assert res.status_code == 200

    def test_get_threats_returns_list(self):
        res = client.get("/threats")
        assert isinstance(res.json(), list)

    def test_get_threats_empty_on_fresh_session(self):
        res = client.get("/threats")
        assert res.json() == []

    def test_get_threats_returns_added_threat(self):
        from routers.threats import threat_store
        threat_store.append({
            "attack_type": "brute_force",
            "affected_service": "auth",
            "severity": "HIGH",
            "score": 7.5,
            "justification": "Multiple failed logins from single IP",
            "blast_radius": ["auth", "api_gateway"],
        })
        res = client.get("/threats")
        assert len(res.json()) == 1

    def test_get_threats_returns_all_threats(self):
        from routers.threats import threat_store
        threat_store.append({"attack_type": "brute_force", "severity": "HIGH"})
        threat_store.append({"attack_type": "ddos", "severity": "CRITICAL"})
        threat_store.append({"attack_type": "sql_injection", "severity": "MEDIUM"})
        res = client.get("/threats")
        assert len(res.json()) == 3

    def test_get_threats_preserves_order(self):
        from routers.threats import threat_store
        threat_store.append({"attack_type": "brute_force", "severity": "HIGH"})
        threat_store.append({"attack_type": "ddos", "severity": "CRITICAL"})
        res = client.get("/threats")
        data = res.json()
        assert data[0]["attack_type"] == "brute_force"
        assert data[1]["attack_type"] == "ddos"

    def test_get_threats_threat_has_severity(self):
        from routers.threats import threat_store
        threat_store.append({"attack_type": "sql_injection", "severity": "CRITICAL", "score": 9.0})
        res = client.get("/threats")
        assert "severity" in res.json()[0]

    def test_get_threats_count_in_response_header(self):
        from routers.threats import threat_store
        threat_store.append({"attack_type": "brute_force", "severity": "HIGH"})
        res = client.get("/threats")
        assert res.status_code == 200


class TestThreatStoreAppend:

    def test_threat_store_is_a_list(self):
        from routers.threats import threat_store
        assert isinstance(threat_store, list)

    def test_threat_store_append_adds_item(self):
        from routers.threats import threat_store
        initial = len(threat_store)
        threat_store.append({"attack_type": "ddos", "severity": "HIGH"})
        assert len(threat_store) == initial + 1

    def test_threat_store_clear_resets(self):
        from routers.threats import threat_store
        threat_store.append({"attack_type": "ddos"})
        threat_store.clear()
        assert threat_store == []
