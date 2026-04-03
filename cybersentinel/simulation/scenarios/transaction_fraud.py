"""
TICKET-008 — Transaction Fraud scenario.
Phases: Login → Probe ($1-$2) → Large Transfer ($48k) → API Scraping
Targets: Transaction Engine + API Gateway
"""
import asyncio
from dataclasses import dataclass, field
from simulation.log_generators.auth_logs import generate_auth_log
from simulation.log_generators.transaction_logs import generate_transaction_log
from simulation.log_generators.api_logs import generate_api_log


@dataclass
class Phase:
    id: str
    duration_seconds: float
    log_count: int


@dataclass
class TransactionFraudScenario:
    id: str = "transaction_fraud"
    name: str = "Transaction Fraud"
    target_services: list = field(default_factory=lambda: ["transaction_engine", "api_gateway"])
    speed_multiplier: float = 1.0
    phases: list = field(default_factory=lambda: [
        Phase(id="login",          duration_seconds=20,  log_count=3),
        Phase(id="probe",          duration_seconds=40,  log_count=6),
        Phase(id="large_transfer", duration_seconds=30,  log_count=4),
        Phase(id="api_scrape",     duration_seconds=90,  log_count=20),
    ])

    def __post_init__(self):
        if self.speed_multiplier <= 0:
            raise ValueError(f"speed_multiplier must be > 0, got {self.speed_multiplier}")

    async def run(self, phases: list[str] | None = None):
        valid_ids = {p.id for p in self.phases}

        if phases is not None:
            if len(phases) == 0:
                raise ValueError("phases list cannot be empty")
            unknown = set(phases) - valid_ids
            if unknown:
                raise ValueError(f"Unknown phase IDs: {unknown}. Valid: {valid_ids}")
            phases_to_run = [p for p in self.phases if p.id in phases]
        else:
            phases_to_run = self.phases

        for phase in phases_to_run:
            delay = (phase.duration_seconds / phase.log_count) / self.speed_multiplier

            for i in range(phase.log_count):
                if phase.id == "login":
                    log = generate_auth_log(event_type="success")
                    yield f"[LOGIN] {log}"

                elif phase.id == "probe":
                    log = generate_transaction_log(
                        transaction_type="probe",
                        amount=fake_probe_amount(i)
                    )
                    yield f"[PROBE] {log}"

                elif phase.id == "large_transfer":
                    amount = 48000.00 if i == 0 else None
                    log = generate_transaction_log(transaction_type="transfer", amount=amount)
                    yield f"[LARGE_TRANSFER] {log}"

                elif phase.id == "api_scrape":
                    status = 429 if i > 10 else 200
                    log = generate_api_log(status_code=status)
                    yield f"[API_SCRAPE] {log}"

                await asyncio.sleep(delay)


def fake_probe_amount(index: int) -> float:
    """Return small probe amounts cycling through $1, $2."""
    return float((index % 2) + 1)
