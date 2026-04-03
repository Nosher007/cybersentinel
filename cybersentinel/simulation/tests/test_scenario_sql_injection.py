"""
TICKET-009 — TDD tests for SQL Injection scenario.
Red phase: written before implementation exists.
Phases: Normal Traffic → Malformed Queries → Injection → Table Dump
"""
import pytest
from simulation.scenarios.sql_injection import SQLInjectionScenario

VALID_PHASES = {"normal_traffic", "malformed_queries", "injection", "table_dump"}


class TestSQLInjectionStructure:

    def test_scenario_has_correct_id(self):
        assert SQLInjectionScenario().id == "sql_injection"

    def test_scenario_has_name(self):
        s = SQLInjectionScenario()
        assert isinstance(s.name, str) and s.name.strip()

    def test_scenario_targets_two_services(self):
        s = SQLInjectionScenario()
        assert set(s.target_services) == {"database", "api_gateway"}

    def test_scenario_has_four_phases(self):
        assert len(SQLInjectionScenario().phases) == 4

    def test_phase_ids_are_correct(self):
        ids = {p.id for p in SQLInjectionScenario().phases}
        assert ids == VALID_PHASES

    def test_phases_are_ordered(self):
        ids = [p.id for p in SQLInjectionScenario().phases]
        assert ids == ["normal_traffic", "malformed_queries", "injection", "table_dump"]

    def test_each_phase_has_positive_duration(self):
        for phase in SQLInjectionScenario().phases:
            assert phase.duration_seconds > 0

    def test_each_phase_has_positive_log_count(self):
        for phase in SQLInjectionScenario().phases:
            assert phase.log_count > 0


class TestSQLInjectionLogGeneration:

    @pytest.mark.asyncio
    async def test_run_yields_logs(self):
        s = SQLInjectionScenario(speed_multiplier=100)
        logs = [log async for log in s.run()]
        assert len(logs) > 0

    @pytest.mark.asyncio
    async def test_all_logs_are_non_empty_strings(self):
        s = SQLInjectionScenario(speed_multiplier=100)
        async for log in s.run():
            assert isinstance(log, str) and log.strip()

    @pytest.mark.asyncio
    async def test_normal_traffic_produces_clean_logs(self):
        """Normal traffic phase must not contain injection payloads."""
        s = SQLInjectionScenario(speed_multiplier=100)
        normal_logs = [log async for log in s.run(phases=["normal_traffic"])]
        for log in normal_logs:
            assert "OR 1=1" not in log and "UNION SELECT" not in log, (
                f"Normal traffic phase contains injection payload: {log}"
            )

    @pytest.mark.asyncio
    async def test_malformed_queries_contain_bad_syntax(self):
        """Malformed queries phase must contain injection-like patterns."""
        s = SQLInjectionScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["malformed_queries"])]
        combined = " ".join(logs)
        assert any(p in combined for p in {"'", "--", "OR 1=1", ";"}), (
            f"Malformed queries phase missing bad syntax: {combined}"
        )

    @pytest.mark.asyncio
    async def test_injection_phase_contains_payload(self):
        s = SQLInjectionScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["injection"])]
        combined = " ".join(logs)
        assert any(p in combined for p in {"'", "OR 1=1", "UNION", "--"}), (
            f"Injection phase missing payload: {combined}"
        )

    @pytest.mark.asyncio
    async def test_table_dump_phase_mentions_data_exfiltration(self):
        s = SQLInjectionScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["table_dump"])]
        combined = " ".join(logs).lower()
        assert any(k in combined for k in {"dump", "rows", "table", "record", "extract"}), (
            f"Table dump phase missing exfiltration context: {combined}"
        )

    @pytest.mark.asyncio
    async def test_logs_include_phase_metadata(self):
        s = SQLInjectionScenario(speed_multiplier=100)
        async for log in s.run():
            assert any(p in log.upper() for p in
                       ["NORMAL", "MALFORMED", "INJECT", "DUMP", "DB", "API"]), (
                f"Log missing phase context: {log}"
            )


class TestSQLInjectionEdgeCases:

    def test_invalid_speed_multiplier_raises(self):
        with pytest.raises(ValueError):
            SQLInjectionScenario(speed_multiplier=0)

    def test_negative_speed_multiplier_raises(self):
        with pytest.raises(ValueError):
            SQLInjectionScenario(speed_multiplier=-1)

    @pytest.mark.asyncio
    async def test_unknown_phase_raises(self):
        s = SQLInjectionScenario(speed_multiplier=100)
        with pytest.raises(ValueError):
            async for _ in s.run(phases=["nonexistent"]):
                pass

    @pytest.mark.asyncio
    async def test_empty_phases_raises(self):
        s = SQLInjectionScenario(speed_multiplier=100)
        with pytest.raises(ValueError):
            async for _ in s.run(phases=[]):
                pass
