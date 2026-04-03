"""
TICKET-008 — TDD tests for Transaction Fraud scenario.
Red phase: written before implementation exists.
Phases: Login → Probe → Large Transfer → API Scraping
"""
import pytest
from simulation.scenarios.transaction_fraud import TransactionFraudScenario

VALID_PHASES = {"login", "probe", "large_transfer", "api_scrape"}


class TestTransactionFraudStructure:

    def test_scenario_has_id(self):
        s = TransactionFraudScenario()
        assert s.id == "transaction_fraud"

    def test_scenario_has_name(self):
        s = TransactionFraudScenario()
        assert isinstance(s.name, str) and s.name.strip()

    def test_scenario_targets_two_services(self):
        s = TransactionFraudScenario()
        assert set(s.target_services) == {"transaction_engine", "api_gateway"}

    def test_scenario_has_four_phases(self):
        s = TransactionFraudScenario()
        assert len(s.phases) == 4

    def test_phase_ids_are_correct(self):
        s = TransactionFraudScenario()
        assert {p.id for p in s.phases} == VALID_PHASES

    def test_phases_are_ordered(self):
        s = TransactionFraudScenario()
        assert [p.id for p in s.phases] == ["login", "probe", "large_transfer", "api_scrape"]

    def test_each_phase_has_positive_duration(self):
        s = TransactionFraudScenario()
        for phase in s.phases:
            assert phase.duration_seconds > 0

    def test_each_phase_has_positive_log_count(self):
        s = TransactionFraudScenario()
        for phase in s.phases:
            assert phase.log_count > 0


class TestTransactionFraudLogGeneration:

    @pytest.mark.asyncio
    async def test_run_yields_logs(self):
        s = TransactionFraudScenario(speed_multiplier=100)
        logs = []
        async for log in s.run():
            logs.append(log)
        assert len(logs) > 0

    @pytest.mark.asyncio
    async def test_all_logs_are_non_empty_strings(self):
        s = TransactionFraudScenario(speed_multiplier=100)
        async for log in s.run():
            assert isinstance(log, str) and log.strip()

    @pytest.mark.asyncio
    async def test_probe_phase_logs_contain_small_amounts(self):
        """Probe phase should show small $1-$5 test transactions."""
        import re
        s = TransactionFraudScenario(speed_multiplier=100)
        probe_logs = []
        async for log in s.run(phases=["probe"]):
            probe_logs.append(log)
        amounts = [re.search(r"\$(\d+)", log) for log in probe_logs]
        amounts = [int(m.group(1)) for m in amounts if m]
        assert any(a <= 10 for a in amounts), "Probe phase should have small amounts"

    @pytest.mark.asyncio
    async def test_large_transfer_phase_contains_large_amount(self):
        """Large transfer phase must include a $48k transfer."""
        s = TransactionFraudScenario(speed_multiplier=100)
        transfer_logs = []
        async for log in s.run(phases=["large_transfer"]):
            transfer_logs.append(log)
        combined = " ".join(transfer_logs)
        assert "48000" in combined or "48,000" in combined, (
            f"Large transfer missing $48k amount: {combined}"
        )

    @pytest.mark.asyncio
    async def test_api_scrape_logs_contain_api_keywords(self):
        """API scrape phase should produce API gateway logs."""
        s = TransactionFraudScenario(speed_multiplier=100)
        scrape_logs = []
        async for log in s.run(phases=["api_scrape"]):
            scrape_logs.append(log.lower())
        assert any("api" in l or "gateway" in l or "429" in l for l in scrape_logs), (
            "API scrape phase missing API-related logs"
        )

    @pytest.mark.asyncio
    async def test_logs_include_phase_metadata(self):
        s = TransactionFraudScenario(speed_multiplier=100)
        async for log in s.run():
            assert any(p in log.upper() for p in ["LOGIN", "PROBE", "TRANSFER", "SCRAPE", "API"]), (
                f"Log missing phase context: {log}"
            )


class TestTransactionFraudEdgeCases:

    def test_invalid_speed_multiplier_raises(self):
        with pytest.raises(ValueError):
            TransactionFraudScenario(speed_multiplier=0)

    def test_negative_speed_multiplier_raises(self):
        with pytest.raises(ValueError):
            TransactionFraudScenario(speed_multiplier=-1)

    @pytest.mark.asyncio
    async def test_unknown_phase_raises(self):
        s = TransactionFraudScenario(speed_multiplier=100)
        with pytest.raises(ValueError):
            async for _ in s.run(phases=["nonexistent"]):
                pass

    @pytest.mark.asyncio
    async def test_empty_phases_raises(self):
        s = TransactionFraudScenario(speed_multiplier=100)
        with pytest.raises(ValueError):
            async for _ in s.run(phases=[]):
                pass
