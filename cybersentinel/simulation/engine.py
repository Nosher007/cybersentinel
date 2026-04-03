"""
TICKET-012 — Simulation Engine Runner.
Receives a scenario ID, instantiates the right scenario, runs it as a
background task, and puts logs into an asyncio.Queue for the WS handler.
Queue is created lazily to avoid event loop binding issues in tests.
"""
import asyncio
from simulation.scenarios.account_takeover import AccountTakeoverScenario
from simulation.scenarios.transaction_fraud import TransactionFraudScenario
from simulation.scenarios.sql_injection import SQLInjectionScenario
from simulation.scenarios.insider_threat import InsiderThreatScenario
from simulation.scenarios.ddos_attack import DDoSAttackScenario

SCENARIO_REGISTRY: dict = {
    "account_takeover":  AccountTakeoverScenario,
    "transaction_fraud": TransactionFraudScenario,
    "sql_injection":     SQLInjectionScenario,
    "insider_threat":    InsiderThreatScenario,
    "ddos_attack":       DDoSAttackScenario,
}


class SimulationEngine:

    def __init__(self):
        self._queue: asyncio.Queue | None = None
        self.is_running: bool = False
        self.current_scenario_id: str | None = None
        self._task: asyncio.Task | None = None

    @property
    def queue(self) -> asyncio.Queue:
        """Lazy queue creation — binds to the running event loop on first access."""
        if self._queue is None:
            self._queue = asyncio.Queue()
        return self._queue

    async def start(self, scenario_id: str, speed_multiplier: float = 1.0) -> None:
        if not scenario_id:
            raise ValueError("scenario_id cannot be empty")
        if scenario_id not in SCENARIO_REGISTRY:
            raise ValueError(
                f"Unknown scenario '{scenario_id}'. "
                f"Available: {set(SCENARIO_REGISTRY.keys())}"
            )
        if speed_multiplier <= 0:
            raise ValueError(f"speed_multiplier must be > 0, got {speed_multiplier}")
        if self.is_running:
            raise RuntimeError(
                f"Engine already running scenario '{self.current_scenario_id}'. "
                "Call stop() first."
            )

        # Reset queue for new run
        self._queue = asyncio.Queue()
        scenario = SCENARIO_REGISTRY[scenario_id](speed_multiplier=speed_multiplier)
        self.current_scenario_id = scenario_id
        self.is_running = True
        self._task = asyncio.create_task(self._run_scenario(scenario))

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.is_running = False
        self.current_scenario_id = None
        self._task = None

    async def _run_scenario(self, scenario) -> None:
        try:
            async for log in scenario.run():
                await self.queue.put(log)
        except asyncio.CancelledError:
            raise
        finally:
            self.is_running = False
            self.current_scenario_id = None
