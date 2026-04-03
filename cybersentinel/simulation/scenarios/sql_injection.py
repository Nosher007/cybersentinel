"""
TICKET-009 — SQL Injection scenario.
Phases: Normal Traffic → Malformed Queries → Injection → Table Dump
Targets: Database + API Gateway
"""
import asyncio
from dataclasses import dataclass, field
from simulation.log_generators.database_logs import generate_database_log
from simulation.log_generators.api_logs import generate_api_log
from simulation.log_generators.sql_injection_logs import generate_sql_injection_log


@dataclass
class Phase:
    id: str
    duration_seconds: float
    log_count: int


@dataclass
class SQLInjectionScenario:
    id: str = "sql_injection"
    name: str = "SQL Injection Attack"
    target_services: list = field(default_factory=lambda: ["database", "api_gateway"])
    speed_multiplier: float = 1.0
    phases: list = field(default_factory=lambda: [
        Phase(id="normal_traffic",   duration_seconds=20, log_count=6),
        Phase(id="malformed_queries",duration_seconds=30, log_count=8),
        Phase(id="injection",        duration_seconds=25, log_count=6),
        Phase(id="table_dump",       duration_seconds=15, log_count=4),
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

            for _ in range(phase.log_count):
                if phase.id == "normal_traffic":
                    log = generate_database_log(query_type="SELECT")
                    yield f"[NORMAL] {log}"

                elif phase.id == "malformed_queries":
                    log = generate_sql_injection_log(stage="probe")
                    yield f"[MALFORMED] {log}"

                elif phase.id == "injection":
                    log = generate_sql_injection_log(stage="injection")
                    yield f"[INJECT] {log}"

                elif phase.id == "table_dump":
                    log = generate_sql_injection_log(stage="dump")
                    yield f"[DUMP] {log}"

                await asyncio.sleep(delay)
