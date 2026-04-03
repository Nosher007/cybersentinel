"""
TICKET-012 — TDD tests for the simulation engine runner.
Red phase: written before implementation exists.
Engine receives a scenario ID, runs it, emits logs into an asyncio.Queue.
"""
import asyncio
import pytest
from simulation.engine import SimulationEngine, SCENARIO_REGISTRY

ALL_SCENARIO_IDS = {
    "account_takeover",
    "transaction_fraud",
    "sql_injection",
    "insider_threat",
    "ddos_attack",
}


class TestScenarioRegistry:

    def test_registry_is_a_dict(self):
        assert isinstance(SCENARIO_REGISTRY, dict)

    def test_registry_contains_all_five_scenarios(self):
        assert set(SCENARIO_REGISTRY.keys()) == ALL_SCENARIO_IDS

    def test_registry_values_are_classes_not_instances(self):
        """Values must be classes so engine can instantiate them fresh each run."""
        for scenario_id, cls in SCENARIO_REGISTRY.items():
            assert isinstance(cls, type), (
                f"Registry value for '{scenario_id}' must be a class, not an instance"
            )

    def test_each_registered_class_is_instantiable(self):
        for scenario_id, cls in SCENARIO_REGISTRY.items():
            instance = cls(speed_multiplier=100)
            assert instance.id == scenario_id


class TestSimulationEngineInit:

    def test_engine_instantiates(self):
        engine = SimulationEngine()
        assert engine is not None

    def test_engine_has_queue(self):
        engine = SimulationEngine()
        assert isinstance(engine.queue, asyncio.Queue)

    def test_engine_is_not_running_on_init(self):
        engine = SimulationEngine()
        assert engine.is_running is False

    def test_engine_current_scenario_is_none_on_init(self):
        engine = SimulationEngine()
        assert engine.current_scenario_id is None


class TestSimulationEngineRun:

    @pytest.mark.asyncio
    async def test_run_puts_logs_into_queue(self):
        engine = SimulationEngine()
        await engine.start("account_takeover", speed_multiplier=100)
        await asyncio.sleep(0.5)
        await engine.stop()
        assert not engine.queue.empty(), "Queue should have logs after running"

    @pytest.mark.asyncio
    async def test_queued_items_are_strings(self):
        engine = SimulationEngine()
        await engine.start("sql_injection", speed_multiplier=100)
        await asyncio.sleep(0.5)
        await engine.stop()
        while not engine.queue.empty():
            item = engine.queue.get_nowait()
            assert isinstance(item, str) and item.strip()

    @pytest.mark.asyncio
    async def test_engine_is_running_after_start(self):
        engine = SimulationEngine()
        await engine.start("ddos_attack", speed_multiplier=100)
        assert engine.is_running is True
        await engine.stop()

    @pytest.mark.asyncio
    async def test_engine_is_not_running_after_stop(self):
        engine = SimulationEngine()
        await engine.start("insider_threat", speed_multiplier=100)
        await engine.stop()
        assert engine.is_running is False

    @pytest.mark.asyncio
    async def test_current_scenario_id_set_during_run(self):
        engine = SimulationEngine()
        await engine.start("transaction_fraud", speed_multiplier=100)
        assert engine.current_scenario_id == "transaction_fraud"
        await engine.stop()

    @pytest.mark.asyncio
    async def test_current_scenario_id_cleared_after_stop(self):
        engine = SimulationEngine()
        await engine.start("account_takeover", speed_multiplier=100)
        await engine.stop()
        assert engine.current_scenario_id is None

    @pytest.mark.asyncio
    async def test_all_five_scenarios_run_without_error(self):
        for scenario_id in ALL_SCENARIO_IDS:
            engine = SimulationEngine()
            await engine.start(scenario_id, speed_multiplier=100)
            await asyncio.sleep(0.3)
            await engine.stop()
            assert not engine.queue.empty(), f"No logs for scenario: {scenario_id}"

    @pytest.mark.asyncio
    async def test_cannot_start_while_already_running(self):
        engine = SimulationEngine()
        await engine.start("account_takeover", speed_multiplier=100)
        with pytest.raises(RuntimeError):
            await engine.start("ddos_attack", speed_multiplier=100)
        await engine.stop()

    @pytest.mark.asyncio
    async def test_stop_without_start_does_not_raise(self):
        engine = SimulationEngine()
        await engine.stop()  # should be a no-op


class TestSimulationEngineEdgeCases:

    @pytest.mark.asyncio
    async def test_unknown_scenario_id_raises(self):
        engine = SimulationEngine()
        with pytest.raises(ValueError):
            await engine.start("unknown_attack", speed_multiplier=100)

    @pytest.mark.asyncio
    async def test_empty_scenario_id_raises(self):
        engine = SimulationEngine()
        with pytest.raises(ValueError):
            await engine.start("", speed_multiplier=100)

    @pytest.mark.asyncio
    async def test_invalid_speed_multiplier_raises(self):
        engine = SimulationEngine()
        with pytest.raises(ValueError):
            await engine.start("account_takeover", speed_multiplier=0)

    @pytest.mark.asyncio
    async def test_negative_speed_multiplier_raises(self):
        engine = SimulationEngine()
        with pytest.raises(ValueError):
            await engine.start("account_takeover", speed_multiplier=-1)
