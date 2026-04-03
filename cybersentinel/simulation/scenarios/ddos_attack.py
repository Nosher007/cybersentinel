"""
TICKET-011 — DDoS Attack scenario.
Phases: Normal Traffic → Traffic Spike → Gateway Degradation → Botnet Flood
Targets: API Gateway + Web Server
Key: Botnet flood uses 400+ unique IPs — distributed attack pattern.
"""
import asyncio
from dataclasses import dataclass, field
from faker import Faker
from datetime import datetime

fake = Faker()


@dataclass
class Phase:
    id: str
    duration_seconds: float
    log_count: int


@dataclass
class DDoSAttackScenario:
    id: str = "ddos_attack"
    name: str = "DDoS Attack"
    target_services: list = field(default_factory=lambda: ["api_gateway", "web_server"])
    speed_multiplier: float = 1.0
    phases: list = field(default_factory=lambda: [
        Phase(id="normal_traffic",      duration_seconds=20, log_count=5),
        Phase(id="traffic_spike",       duration_seconds=20, log_count=15),
        Phase(id="gateway_degradation", duration_seconds=20, log_count=20),
        Phase(id="botnet_flood",        duration_seconds=30, log_count=50),
    ])

    def __post_init__(self):
        if self.speed_multiplier <= 0:
            raise ValueError(f"speed_multiplier must be > 0, got {self.speed_multiplier}")
        # Pre-generate botnet IP pool — 400+ unique IPs
        self._botnet_ips = [fake.ipv4_public() for _ in range(420)]

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

        endpoints = ["/api/v1/login", "/api/v1/balance", "/api/v1/transfer", "/health"]

        for phase in phases_to_run:
            delay = (phase.duration_seconds / phase.log_count) / self.speed_multiplier

            for i in range(phase.log_count):
                log = self._generate_log(phase.id, i, endpoints)
                yield log
                await asyncio.sleep(delay)

    def _generate_log(self, phase_id: str, index: int, endpoints: list) -> str:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        endpoint = fake.random_element(endpoints)

        if phase_id == "normal_traffic":
            ip = fake.ipv4_public()
            return (f"{ts} [NGINX] {ip} GET {endpoint} "
                    f"status=200 duration={fake.random_int(10, 100)}ms req_rate=50/s")

        elif phase_id == "traffic_spike":
            ip = fake.ipv4_public()
            rate = fake.random_int(500, 3000)
            return (f"{ts} [API-GW] {ip} GET {endpoint} "
                    f"status=200 duration={fake.random_int(100, 800)}ms req_rate={rate}/s spike=true")

        elif phase_id == "gateway_degradation":
            ip = fake.ipv4_public()
            status = fake.random_element([503, 503, 503, 429, 502])
            return (f"{ts} [API-GW] {ip} GET {endpoint} "
                    f"status={status} duration={fake.random_int(800, 5000)}ms "
                    f"req_rate={fake.random_int(4000, 8000)}/s degraded=true")

        else:  # botnet_flood
            # Draw from pre-generated botnet pool for variety
            ip = self._botnet_ips[index % len(self._botnet_ips)]
            status = fake.random_element([429, 503, 503, 200])
            return (f"{ts} [BOTNET] {ip} GET {endpoint} "
                    f"status={status} duration={fake.random_int(1000, 9000)}ms "
                    f"req_rate={fake.random_int(6000, 8000)}/s botnet=true")
