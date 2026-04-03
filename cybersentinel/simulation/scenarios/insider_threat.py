"""
TICKET-010 — Insider Threat scenario.
Phases: Off-hours Login → Mass Record Access → PII Download → External Transfer
Targets: Database + Compliance
Key: logs look LEGITIMATE — suspicion comes from pattern, not errors.
"""
import asyncio
import random
from dataclasses import dataclass, field
from datetime import datetime
from faker import Faker

fake = Faker()


@dataclass
class Phase:
    id: str
    duration_seconds: float
    log_count: int


@dataclass
class InsiderThreatScenario:
    id: str = "insider_threat"
    name: str = "Insider Threat"
    target_services: list = field(default_factory=lambda: ["database", "compliance"])
    speed_multiplier: float = 1.0
    phases: list = field(default_factory=lambda: [
        Phase(id="offhours_login",   duration_seconds=10,  log_count=2),
        Phase(id="mass_access",      duration_seconds=120, log_count=15),
        Phase(id="pii_download",     duration_seconds=60,  log_count=8),
        Phase(id="external_transfer",duration_seconds=30,  log_count=5),
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

        # Fixed admin user for consistency across the scenario
        admin_user = "admin_" + fake.user_name()
        external_ip = fake.ipv4_public()

        for phase in phases_to_run:
            delay = (phase.duration_seconds / phase.log_count) / self.speed_multiplier

            for i in range(phase.log_count):
                log = self._generate_log(phase.id, i, admin_user, external_ip)
                yield log
                await asyncio.sleep(delay)

    def _generate_log(self, phase_id: str, index: int, admin_user: str, external_ip: str) -> str:
        # Off-hours timestamp: between 02:00 and 04:00 AM
        offhours_hour = random.randint(2, 4)
        offhours_ts = datetime.now().replace(
            hour=offhours_hour,
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        ).strftime("%Y-%m-%d %H:%M:%S")

        ts = offhours_ts  # All logs use off-hours time
        tables = ["users", "accounts", "transactions", "customers"]
        table = fake.random_element(tables)

        if phase_id == "offhours_login":
            return (f"{ts} [AUTH] INFO  user={admin_user} ip={fake.ipv4_private()} "
                    f"event=login status=success role=admin session_id={fake.uuid4()[:8]}")

        elif phase_id == "mass_access":
            rows = fake.random_int(200, 500)
            return (f"{ts} [DB] INFO  user={admin_user} "
                    f"query=SELECT * FROM {table} rows={rows} duration={fake.random_int(10,200)}ms "
                    f"status=success")

        elif phase_id == "pii_download":
            records = fake.random_int(300, 600)
            field_names = fake.random_element(["ssn,email,phone", "email,dob,address", "pii_fields"])
            return (f"{ts} [DB] WARN  user={admin_user} event=bulk_export "
                    f"table={table} sensitive_fields={field_names} "
                    f"records_exported={records} format=csv status=success")

        else:  # external_transfer
            size_mb = round(fake.random.uniform(10, 80), 1)
            return (f"{ts} [COMPLIANCE] CRITICAL user={admin_user} "
                    f"event=external_data_transfer destination={external_ip} "
                    f"size={size_mb}MB exfil=true status=complete")
