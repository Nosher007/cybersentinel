"""
TICKET-010 — TDD tests for Insider Threat scenario.
Red phase: written before implementation exists.
Phases: Off-hours Login → Mass Record Access → PII Download → External Transfer
Key property: early logs must look NORMAL — suspicion is in the pattern, not errors.
"""
import re
import pytest
from simulation.scenarios.insider_threat import InsiderThreatScenario

VALID_PHASES = {"offhours_login", "mass_access", "pii_download", "external_transfer"}


class TestInsiderThreatStructure:

    def test_scenario_has_correct_id(self):
        assert InsiderThreatScenario().id == "insider_threat"

    def test_scenario_has_name(self):
        s = InsiderThreatScenario()
        assert isinstance(s.name, str) and s.name.strip()

    def test_scenario_targets_correct_services(self):
        s = InsiderThreatScenario()
        assert set(s.target_services) == {"database", "compliance"}

    def test_scenario_has_four_phases(self):
        assert len(InsiderThreatScenario().phases) == 4

    def test_phase_ids_are_correct(self):
        ids = {p.id for p in InsiderThreatScenario().phases}
        assert ids == VALID_PHASES

    def test_phases_are_ordered(self):
        ids = [p.id for p in InsiderThreatScenario().phases]
        assert ids == ["offhours_login", "mass_access", "pii_download", "external_transfer"]

    def test_each_phase_has_positive_duration(self):
        for phase in InsiderThreatScenario().phases:
            assert phase.duration_seconds > 0

    def test_each_phase_has_positive_log_count(self):
        for phase in InsiderThreatScenario().phases:
            assert phase.log_count > 0


class TestInsiderThreatLogGeneration:

    @pytest.mark.asyncio
    async def test_run_yields_logs(self):
        s = InsiderThreatScenario(speed_multiplier=100)
        logs = [log async for log in s.run()]
        assert len(logs) > 0

    @pytest.mark.asyncio
    async def test_all_logs_are_non_empty_strings(self):
        s = InsiderThreatScenario(speed_multiplier=100)
        async for log in s.run():
            assert isinstance(log, str) and log.strip()

    @pytest.mark.asyncio
    async def test_offhours_login_looks_legitimate(self):
        """Login phase must show SUCCESS — no failed attempts, no errors."""
        s = InsiderThreatScenario(speed_multiplier=100)
        login_logs = [log async for log in s.run(phases=["offhours_login"])]
        for log in login_logs:
            assert "failed" not in log.lower(), (
                f"Offhours login should look legitimate, not failed: {log}"
            )
            assert "error" not in log.lower(), (
                f"Offhours login should look legitimate, not error: {log}"
            )

    @pytest.mark.asyncio
    async def test_offhours_login_contains_offhours_time(self):
        """Login must happen between midnight and 5 AM."""
        s = InsiderThreatScenario(speed_multiplier=100)
        login_logs = [log async for log in s.run(phases=["offhours_login"])]
        combined = " ".join(login_logs)
        times = re.findall(r"(\d{2}):\d{2}:\d{2}", combined)
        assert any(int(h) < 5 for h in times), (
            f"Offhours login must occur between midnight and 5AM: {combined}"
        )

    @pytest.mark.asyncio
    async def test_mass_access_shows_high_record_count(self):
        """Mass access phase must show access to many records (1000+)."""
        s = InsiderThreatScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["mass_access"])]
        combined = " ".join(logs)
        counts = re.findall(r"rows[=_](\d+)", combined)
        assert any(int(c) >= 100 for c in counts), (
            f"Mass access should show high row counts: {combined}"
        )

    @pytest.mark.asyncio
    async def test_pii_download_mentions_sensitive_data(self):
        """PII download phase must reference personal data fields."""
        s = InsiderThreatScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["pii_download"])]
        combined = " ".join(logs).lower()
        assert any(k in combined for k in {"pii", "ssn", "email", "phone", "personal", "sensitive"}), (
            f"PII download missing sensitive data reference: {combined}"
        )

    @pytest.mark.asyncio
    async def test_external_transfer_contains_external_ip(self):
        """External transfer must show data going to an external destination."""
        s = InsiderThreatScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["external_transfer"])]
        combined = " ".join(logs).lower()
        assert any(k in combined for k in {"external", "destination", "dst", "upload", "exfil"}), (
            f"External transfer missing destination context: {combined}"
        )

    @pytest.mark.asyncio
    async def test_mass_access_logs_show_no_errors(self):
        """Mass access looks legitimate — admin has valid credentials."""
        s = InsiderThreatScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["mass_access"])]
        for log in logs:
            assert "injection" not in log.lower(), (
                f"Mass access should look normal, not like an attack: {log}"
            )

    @pytest.mark.asyncio
    async def test_logs_include_phase_metadata(self):
        s = InsiderThreatScenario(speed_multiplier=100)
        async for log in s.run():
            assert any(p in log.upper() for p in
                       ["LOGIN", "ACCESS", "PII", "TRANSFER", "DB", "ADMIN"]), (
                f"Log missing phase context: {log}"
            )


class TestInsiderThreatEdgeCases:

    def test_invalid_speed_multiplier_raises(self):
        with pytest.raises(ValueError):
            InsiderThreatScenario(speed_multiplier=0)

    def test_negative_speed_multiplier_raises(self):
        with pytest.raises(ValueError):
            InsiderThreatScenario(speed_multiplier=-1)

    @pytest.mark.asyncio
    async def test_unknown_phase_raises(self):
        s = InsiderThreatScenario(speed_multiplier=100)
        with pytest.raises(ValueError):
            async for _ in s.run(phases=["nonexistent"]):
                pass

    @pytest.mark.asyncio
    async def test_empty_phases_raises(self):
        s = InsiderThreatScenario(speed_multiplier=100)
        with pytest.raises(ValueError):
            async for _ in s.run(phases=[]):
                pass
