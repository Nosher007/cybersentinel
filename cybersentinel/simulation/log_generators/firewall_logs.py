"""Firewall log generator — network traffic allow/deny events."""
from datetime import datetime
from faker import Faker

fake = Faker()

VALID_ACTIONS = {"ALLOW", "DENY", "DROP", "BLOCK"}
PROTOCOLS = ["TCP", "UDP", "ICMP"]


def generate_firewall_log(action: str = "ALLOW") -> str:
    action = action.upper()
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid action '{action}'. Must be one of {VALID_ACTIONS}")

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_ip = fake.ipv4()
    dst_ip = fake.ipv4_private()
    src_port = fake.random_int(1024, 65535)
    dst_port = fake.random_element([80, 443, 8001, 8002, 8003, 5432, 22])
    protocol = fake.random_element(PROTOCOLS)

    return (f"{ts} [FIREWALL] {action} {protocol} "
            f"src={src_ip}:{src_port} dst={dst_ip}:{dst_port} "
            f"bytes={fake.random_int(64, 9000)}")
