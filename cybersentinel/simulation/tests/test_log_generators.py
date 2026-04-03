"""
TICKET-006 — TDD tests for all 5 log generators.
Red phase: written before any implementation exists.
Each generator must produce realistic, parseable log strings.
"""
import re
import pytest
from simulation.log_generators.auth_logs import generate_auth_log
from simulation.log_generators.nginx_logs import generate_nginx_log
from simulation.log_generators.firewall_logs import generate_firewall_log
from simulation.log_generators.database_logs import generate_database_log
from simulation.log_generators.api_logs import generate_api_log

# ── Shared helpers ────────────────────────────────────────────────────────────

IPV4_PATTERN = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")


def has_ip(log: str) -> bool:
    return bool(IPV4_PATTERN.search(log))


def has_timestamp(log: str) -> bool:
    return bool(TIMESTAMP_PATTERN.search(log))


# ── Auth log tests ────────────────────────────────────────────────────────────

class TestAuthLogGenerator:

    def test_returns_a_string(self):
        assert isinstance(generate_auth_log(), str)

    def test_log_is_not_empty(self):
        assert generate_auth_log().strip() != ""

    def test_contains_timestamp(self):
        assert has_timestamp(generate_auth_log()), "Auth log missing timestamp"

    def test_contains_ip_address(self):
        assert has_ip(generate_auth_log()), "Auth log missing IP address"

    def test_contains_auth_related_keyword(self):
        log = generate_auth_log().lower()
        keywords = {"login", "logout", "auth", "password", "session", "2fa", "failed", "success"}
        assert any(k in log for k in keywords), f"Auth log has no auth keyword: {log}"

    def test_each_call_produces_different_log(self):
        logs = {generate_auth_log() for _ in range(10)}
        assert len(logs) > 1, "Auth log generator produces identical output every call"

    def test_accepts_event_type_success(self):
        log = generate_auth_log(event_type="success")
        assert isinstance(log, str) and log.strip()

    def test_accepts_event_type_failure(self):
        log = generate_auth_log(event_type="failure")
        assert isinstance(log, str) and log.strip()

    def test_invalid_event_type_raises(self):
        with pytest.raises(ValueError):
            generate_auth_log(event_type="invalid_type")


# ── Nginx log tests ───────────────────────────────────────────────────────────

class TestNginxLogGenerator:

    def test_returns_a_string(self):
        assert isinstance(generate_nginx_log(), str)

    def test_log_is_not_empty(self):
        assert generate_nginx_log().strip() != ""

    def test_contains_timestamp(self):
        assert has_timestamp(generate_nginx_log()), "Nginx log missing timestamp"

    def test_contains_ip_address(self):
        assert has_ip(generate_nginx_log()), "Nginx log missing IP address"

    def test_contains_http_method(self):
        log = generate_nginx_log()
        methods = {"GET", "POST", "PUT", "DELETE", "PATCH"}
        assert any(m in log for m in methods), f"Nginx log missing HTTP method: {log}"

    def test_contains_http_status_code(self):
        log = generate_nginx_log()
        codes = {"200", "201", "301", "400", "401", "403", "404", "500", "503"}
        assert any(c in log for c in codes), f"Nginx log missing status code: {log}"

    def test_each_call_produces_different_log(self):
        logs = {generate_nginx_log() for _ in range(10)}
        assert len(logs) > 1

    def test_accepts_status_code(self):
        log = generate_nginx_log(status_code=503)
        assert "503" in log


# ── Firewall log tests ────────────────────────────────────────────────────────

class TestFirewallLogGenerator:

    def test_returns_a_string(self):
        assert isinstance(generate_firewall_log(), str)

    def test_log_is_not_empty(self):
        assert generate_firewall_log().strip() != ""

    def test_contains_timestamp(self):
        assert has_timestamp(generate_firewall_log()), "Firewall log missing timestamp"

    def test_contains_source_ip(self):
        assert has_ip(generate_firewall_log()), "Firewall log missing IP address"

    def test_contains_action(self):
        log = generate_firewall_log().upper()
        actions = {"ALLOW", "DENY", "DROP", "BLOCK", "REJECT"}
        assert any(a in log for a in actions), f"Firewall log missing action: {log}"

    def test_contains_port_number(self):
        log = generate_firewall_log()
        assert re.search(r"\b\d{2,5}\b", log), f"Firewall log missing port number: {log}"

    def test_each_call_produces_different_log(self):
        logs = {generate_firewall_log() for _ in range(10)}
        assert len(logs) > 1

    def test_accepts_action_deny(self):
        log = generate_firewall_log(action="DENY")
        assert "DENY" in log.upper()

    def test_invalid_action_raises(self):
        with pytest.raises(ValueError):
            generate_firewall_log(action="EXPLODE")


# ── Database log tests ────────────────────────────────────────────────────────

class TestDatabaseLogGenerator:

    def test_returns_a_string(self):
        assert isinstance(generate_database_log(), str)

    def test_log_is_not_empty(self):
        assert generate_database_log().strip() != ""

    def test_contains_timestamp(self):
        assert has_timestamp(generate_database_log()), "Database log missing timestamp"

    def test_contains_sql_keyword(self):
        log = generate_database_log().upper()
        keywords = {"SELECT", "INSERT", "UPDATE", "DELETE", "QUERY", "TABLE", "FROM"}
        assert any(k in log for k in keywords), f"Database log missing SQL keyword: {log}"

    def test_contains_duration_or_rows(self):
        log = generate_database_log().lower()
        assert any(k in log for k in {"ms", "rows", "duration", "affected"}), (
            f"Database log missing performance info: {log}"
        )

    def test_each_call_produces_different_log(self):
        logs = {generate_database_log() for _ in range(10)}
        assert len(logs) > 1

    def test_accepts_query_type_select(self):
        log = generate_database_log(query_type="SELECT")
        assert "SELECT" in log.upper()

    def test_invalid_query_type_raises(self):
        with pytest.raises(ValueError):
            generate_database_log(query_type="HACK")


# ── API log tests ─────────────────────────────────────────────────────────────

class TestApiLogGenerator:

    def test_returns_a_string(self):
        assert isinstance(generate_api_log(), str)

    def test_log_is_not_empty(self):
        assert generate_api_log().strip() != ""

    def test_contains_timestamp(self):
        assert has_timestamp(generate_api_log()), "API log missing timestamp"

    def test_contains_ip_address(self):
        assert has_ip(generate_api_log()), "API log missing IP address"

    def test_contains_endpoint(self):
        log = generate_api_log()
        assert "/" in log, f"API log missing endpoint path: {log}"

    def test_contains_http_method(self):
        log = generate_api_log()
        methods = {"GET", "POST", "PUT", "DELETE", "PATCH"}
        assert any(m in log for m in methods), f"API log missing HTTP method: {log}"

    def test_contains_response_time(self):
        log = generate_api_log().lower()
        assert any(k in log for k in {"ms", "latency", "response_time", "duration"}), (
            f"API log missing response time: {log}"
        )

    def test_each_call_produces_different_log(self):
        logs = {generate_api_log() for _ in range(10)}
        assert len(logs) > 1

    def test_accepts_status_code(self):
        log = generate_api_log(status_code=429)
        assert "429" in log

    def test_invalid_status_code_raises(self):
        with pytest.raises(ValueError):
            generate_api_log(status_code=999)
