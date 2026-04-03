"""
TICKET-009 — TDD tests for SQL injection log generator.
Red phase: written before implementation exists.
"""
import re
import pytest
from simulation.log_generators.sql_injection_logs import generate_sql_injection_log

TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
VALID_STAGES = {"probe", "injection", "dump"}


class TestSQLInjectionLogGenerator:

    def test_returns_a_string(self):
        assert isinstance(generate_sql_injection_log(), str)

    def test_log_is_not_empty(self):
        assert generate_sql_injection_log().strip() != ""

    def test_contains_timestamp(self):
        assert TIMESTAMP_PATTERN.search(generate_sql_injection_log())

    def test_contains_injection_payload(self):
        """Log must contain recognisable SQL injection syntax."""
        log = generate_sql_injection_log()
        payloads = {"'", "OR 1=1", "--", "UNION", "SELECT", "DROP", ";"}
        assert any(p in log for p in payloads), f"No injection payload found: {log}"

    def test_contains_source_ip(self):
        log = generate_sql_injection_log()
        assert re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", log), (
            f"Missing IP: {log}"
        )

    def test_each_call_produces_different_log(self):
        logs = {generate_sql_injection_log() for _ in range(10)}
        assert len(logs) > 1

    def test_accepts_stage_probe(self):
        log = generate_sql_injection_log(stage="probe")
        assert isinstance(log, str) and log.strip()

    def test_accepts_stage_injection(self):
        log = generate_sql_injection_log(stage="injection")
        assert isinstance(log, str) and log.strip()

    def test_accepts_stage_dump(self):
        log = generate_sql_injection_log(stage="dump")
        assert isinstance(log, str) and log.strip()

    def test_dump_stage_mentions_table_or_rows(self):
        """Dump stage should reference table data being extracted."""
        for _ in range(5):
            log = generate_sql_injection_log(stage="dump").lower()
            assert any(k in log for k in {"table", "rows", "dump", "record", "extract"}), (
                f"Dump stage missing data exfiltration context: {log}"
            )

    def test_injection_stage_contains_payload(self):
        for _ in range(5):
            log = generate_sql_injection_log(stage="injection")
            assert any(p in log for p in {"'", "OR 1=1", "--", "UNION"}), (
                f"Injection stage missing payload: {log}"
            )

    def test_invalid_stage_raises(self):
        with pytest.raises(ValueError):
            generate_sql_injection_log(stage="explode")

    def test_empty_stage_raises(self):
        with pytest.raises(ValueError):
            generate_sql_injection_log(stage="")
