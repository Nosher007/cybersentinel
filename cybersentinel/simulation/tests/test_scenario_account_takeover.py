"""
TICKET-007 — TDD tests for Account Takeover scenario.
Red phase: written before implementation exists.
Tests cover phase structure, log content, timing, and edge cases.
"""
import pytest
from simulation.scenarios.account_takeover import AccountTakeoverScenario

VALID_PHASES = {"recon", "brute_force", "2fa_bypass", "account_lock"}


class TestAccountTakeoverStructure:

    def test_scenario_has_id(self):
        s = AccountTakeoverScenario()
        assert s.id == "account_takeover"

    def test_scenario_has_name(self):
        s = AccountTakeoverScenario()
        assert isinstance(s.name, str) and s.name.strip()

    def test_scenario_has_target_service(self):
        s = AccountTakeoverScenario()
        assert s.target_service == "auth"

    def test_scenario_has_four_phases(self):
        s = AccountTakeoverScenario()
        assert len(s.phases) == 4

    def test_phase_ids_are_correct(self):
        s = AccountTakeoverScenario()
        ids = {p.id for p in s.phases}
        assert ids == VALID_PHASES

    def test_phases_are_ordered(self):
        s = AccountTakeoverScenario()
        ids = [p.id for p in s.phases]
        assert ids == ["recon", "brute_force", "2fa_bypass", "account_lock"]

    def test_each_phase_has_duration(self):
        s = AccountTakeoverScenario()
        for phase in s.phases:
            assert phase.duration_seconds > 0, f"Phase {phase.id} has no duration"

    def test_each_phase_has_log_count(self):
        s = AccountTakeoverScenario()
        for phase in s.phases:
            assert phase.log_count > 0, f"Phase {phase.id} has no log_count"


class TestAccountTakeoverLogGeneration:

    @pytest.mark.asyncio
    async def test_run_yields_logs(self):
        """run() must yield at least one log string."""
        s = AccountTakeoverScenario(speed_multiplier=100)
        logs = []
        async for log in s.run():
            logs.append(log)
            if len(logs) >= 3:
                break
        assert len(logs) > 0

    @pytest.mark.asyncio
    async def test_all_logs_are_strings(self):
        s = AccountTakeoverScenario(speed_multiplier=100)
        async for log in s.run():
            assert isinstance(log, str), f"Non-string log yielded: {log}"

    @pytest.mark.asyncio
    async def test_all_logs_are_non_empty(self):
        s = AccountTakeoverScenario(speed_multiplier=100)
        async for log in s.run():
            assert log.strip(), "Empty log string yielded"

    @pytest.mark.asyncio
    async def test_recon_logs_contain_auth_keywords(self):
        """Recon phase should produce reconnaissance-style auth logs."""
        s = AccountTakeoverScenario(speed_multiplier=100)
        recon_logs = []
        async for log in s.run(phases=["recon"]):
            recon_logs.append(log.lower())
        assert any("login" in l or "auth" in l or "recon" in l for l in recon_logs)

    @pytest.mark.asyncio
    async def test_brute_force_logs_contain_failure_keywords(self):
        """Brute force phase must have failed login attempts."""
        s = AccountTakeoverScenario(speed_multiplier=100)
        bf_logs = []
        async for log in s.run(phases=["brute_force"]):
            bf_logs.append(log.lower())
        assert any("fail" in l or "invalid" in l or "attempt" in l for l in bf_logs)

    @pytest.mark.asyncio
    async def test_account_lock_logs_contain_lockout_keyword(self):
        """Account lock phase must mention lockout."""
        s = AccountTakeoverScenario(speed_multiplier=100)
        lock_logs = []
        async for log in s.run(phases=["account_lock"]):
            lock_logs.append(log.lower())
        assert any("lock" in l or "blocked" in l or "suspend" in l for l in lock_logs)

    @pytest.mark.asyncio
    async def test_run_yields_logs_for_each_phase(self):
        """Full run must yield logs — one set per phase."""
        s = AccountTakeoverScenario(speed_multiplier=100)
        all_logs = []
        async for log in s.run():
            all_logs.append(log)
        assert len(all_logs) >= 4, "Expected at least one log per phase"

    @pytest.mark.asyncio
    async def test_each_log_includes_phase_metadata(self):
        """Each yielded log must indicate which phase it came from."""
        s = AccountTakeoverScenario(speed_multiplier=100)
        async for log in s.run():
            assert any(p in log.lower() for p in ["recon", "brute", "2fa", "lock", "auth"]), (
                f"Log has no phase context: {log}"
            )


class TestAccountTakeoverEdgeCases:

    def test_invalid_speed_multiplier_raises(self):
        with pytest.raises(ValueError):
            AccountTakeoverScenario(speed_multiplier=0)

    def test_negative_speed_multiplier_raises(self):
        with pytest.raises(ValueError):
            AccountTakeoverScenario(speed_multiplier=-5)

    @pytest.mark.asyncio
    async def test_run_with_unknown_phase_raises(self):
        s = AccountTakeoverScenario(speed_multiplier=100)
        with pytest.raises(ValueError):
            async for _ in s.run(phases=["nonexistent_phase"]):
                pass

    @pytest.mark.asyncio
    async def test_run_with_empty_phases_raises(self):
        s = AccountTakeoverScenario(speed_multiplier=100)
        with pytest.raises(ValueError):
            async for _ in s.run(phases=[]):
                pass
