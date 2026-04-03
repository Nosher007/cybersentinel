"""
TICKET-007 — Account Takeover scenario.
Phases: Recon → Brute Force → 2FA Bypass → Account Lock
"""
import asyncio
from dataclasses import dataclass, field
from simulation.log_generators.auth_logs import generate_auth_log


@dataclass
class Phase:
    id: str
    duration_seconds: float
    log_count: int


@dataclass
class AccountTakeoverScenario:
    id: str = "account_takeover"
    name: str = "Account Takeover"
    target_service: str = "auth"
    speed_multiplier: float = 1.0
    phases: list = field(default_factory=lambda: [
        Phase(id="recon",        duration_seconds=30,  log_count=5),
        Phase(id="brute_force",  duration_seconds=60,  log_count=20),
        Phase(id="2fa_bypass",   duration_seconds=20,  log_count=8),
        Phase(id="account_lock", duration_seconds=10,  log_count=3),
    ])

    def __post_init__(self):
        if self.speed_multiplier <= 0:
            raise ValueError(f"speed_multiplier must be > 0, got {self.speed_multiplier}")

    async def run(self, phases: list[str] | None = None):
        """
        Async generator — yields log strings one at a time across all phases.
        phases: optional list of phase IDs to run. Defaults to all 4 in order.
        """
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

        phase_log_map = {
            "recon":        lambda: generate_auth_log(event_type="success"),
            "brute_force":  lambda: generate_auth_log(event_type="failure"),
            "2fa_bypass":   lambda: generate_auth_log(event_type="2fa"),
            "account_lock": lambda: generate_auth_log(event_type="lockout"),
        }

        for phase in phases_to_run:
            delay = (phase.duration_seconds / phase.log_count) / self.speed_multiplier
            for _ in range(phase.log_count):
                raw_log = phase_log_map[phase.id]()
                yield f"[{phase.id.upper()}] {raw_log}"
                await asyncio.sleep(delay)
