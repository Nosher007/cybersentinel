"""
TICKET-011 — TDD tests for DDoS Attack scenario.
Red phase: written before implementation exists.
Phases: Normal Traffic → Traffic Spike → Gateway Degradation → Botnet Flood
Key property: logs must show MANY different source IPs — botnet pattern.
"""
import re
import pytest
from simulation.scenarios.ddos_attack import DDoSAttackScenario

VALID_PHASES = {"normal_traffic", "traffic_spike", "gateway_degradation", "botnet_flood"}
IPV4_PATTERN = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")


class TestDDoSAttackStructure:

    def test_scenario_has_correct_id(self):
        assert DDoSAttackScenario().id == "ddos_attack"

    def test_scenario_has_name(self):
        s = DDoSAttackScenario()
        assert isinstance(s.name, str) and s.name.strip()

    def test_scenario_targets_two_services(self):
        s = DDoSAttackScenario()
        assert set(s.target_services) == {"api_gateway", "web_server"}

    def test_scenario_has_four_phases(self):
        assert len(DDoSAttackScenario().phases) == 4

    def test_phase_ids_are_correct(self):
        ids = {p.id for p in DDoSAttackScenario().phases}
        assert ids == VALID_PHASES

    def test_phases_are_ordered(self):
        ids = [p.id for p in DDoSAttackScenario().phases]
        assert ids == ["normal_traffic", "traffic_spike", "gateway_degradation", "botnet_flood"]

    def test_each_phase_has_positive_duration(self):
        for phase in DDoSAttackScenario().phases:
            assert phase.duration_seconds > 0

    def test_each_phase_has_positive_log_count(self):
        for phase in DDoSAttackScenario().phases:
            assert phase.log_count > 0

    def test_botnet_flood_has_more_logs_than_normal(self):
        """Botnet phase must emit significantly more logs than normal traffic."""
        s = DDoSAttackScenario()
        normal = next(p for p in s.phases if p.id == "normal_traffic")
        botnet = next(p for p in s.phases if p.id == "botnet_flood")
        assert botnet.log_count > normal.log_count * 3, (
            "Botnet phase should have many more logs than normal traffic"
        )


class TestDDoSAttackLogGeneration:

    @pytest.mark.asyncio
    async def test_run_yields_logs(self):
        s = DDoSAttackScenario(speed_multiplier=100)
        logs = [log async for log in s.run()]
        assert len(logs) > 0

    @pytest.mark.asyncio
    async def test_all_logs_are_non_empty_strings(self):
        s = DDoSAttackScenario(speed_multiplier=100)
        async for log in s.run():
            assert isinstance(log, str) and log.strip()

    @pytest.mark.asyncio
    async def test_normal_traffic_has_no_503s(self):
        """Normal phase must not contain 503 errors."""
        s = DDoSAttackScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["normal_traffic"])]
        for log in logs:
            assert "503" not in log, f"Normal traffic should not have 503s: {log}"

    @pytest.mark.asyncio
    async def test_gateway_degradation_contains_503s(self):
        """Degradation phase must show 503 Service Unavailable responses."""
        s = DDoSAttackScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["gateway_degradation"])]
        combined = " ".join(logs)
        assert "503" in combined, f"Degradation phase missing 503 errors: {combined}"

    @pytest.mark.asyncio
    async def test_botnet_flood_uses_many_different_ips(self):
        """Botnet phase must show 10+ unique source IPs — distributed attack."""
        s = DDoSAttackScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["botnet_flood"])]
        all_ips = set()
        for log in logs:
            matches = IPV4_PATTERN.findall(log)
            all_ips.update(matches)
        assert len(all_ips) >= 10, (
            f"Botnet flood should have 10+ unique IPs, found {len(all_ips)}: {all_ips}"
        )

    @pytest.mark.asyncio
    async def test_traffic_spike_shows_high_request_volume(self):
        """Spike phase logs must indicate high request rates."""
        s = DDoSAttackScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["traffic_spike"])]
        combined = " ".join(logs).lower()
        assert any(k in combined for k in {"req", "request", "spike", "rate", "flood"}), (
            f"Traffic spike missing volume indicators: {combined}"
        )

    @pytest.mark.asyncio
    async def test_botnet_flood_logs_contain_429_or_503(self):
        """Botnet flood must trigger rate limiting or server errors."""
        s = DDoSAttackScenario(speed_multiplier=100)
        logs = [log async for log in s.run(phases=["botnet_flood"])]
        combined = " ".join(logs)
        assert "429" in combined or "503" in combined, (
            f"Botnet flood should trigger 429/503 responses: {combined}"
        )

    @pytest.mark.asyncio
    async def test_logs_include_phase_metadata(self):
        s = DDoSAttackScenario(speed_multiplier=100)
        async for log in s.run():
            assert any(p in log.upper() for p in
                       ["NORMAL", "SPIKE", "DEGRAD", "BOTNET", "API", "NGINX"]), (
                f"Log missing phase context: {log}"
            )


class TestDDoSAttackEdgeCases:

    def test_invalid_speed_multiplier_raises(self):
        with pytest.raises(ValueError):
            DDoSAttackScenario(speed_multiplier=0)

    def test_negative_speed_multiplier_raises(self):
        with pytest.raises(ValueError):
            DDoSAttackScenario(speed_multiplier=-1)

    @pytest.mark.asyncio
    async def test_unknown_phase_raises(self):
        s = DDoSAttackScenario(speed_multiplier=100)
        with pytest.raises(ValueError):
            async for _ in s.run(phases=["nonexistent"]):
                pass

    @pytest.mark.asyncio
    async def test_empty_phases_raises(self):
        s = DDoSAttackScenario(speed_multiplier=100)
        with pytest.raises(ValueError):
            async for _ in s.run(phases=[]):
                pass
