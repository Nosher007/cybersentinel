"""SQL Injection log generator — probe, injection payload, and table dump stages."""
from datetime import datetime
from faker import Faker

fake = Faker()

VALID_STAGES = {"probe", "injection", "dump"}

INJECTION_PAYLOADS = [
    "' OR 1=1--",
    "' UNION SELECT null,null,null--",
    "'; DROP TABLE users;--",
    "' OR 'a'='a",
    "1; SELECT * FROM users--",
    "' OR 1=1#",
]

TABLES = ["users", "accounts", "transactions", "sessions", "payments"]


def generate_sql_injection_log(stage: str = "injection") -> str:
    if not stage:
        raise ValueError("stage cannot be empty")
    if stage not in VALID_STAGES:
        raise ValueError(f"Invalid stage '{stage}'. Must be one of {VALID_STAGES}")

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = fake.ipv4()
    table = fake.random_element(TABLES)

    if stage == "probe":
        payload = fake.random_element(["'", "\"", ";", "1=1"])
        return (f"{ts} [DB] WARN  ip={ip} query=SELECT * FROM {table} "
                f"WHERE id='{payload}' status=error rows=0")

    elif stage == "injection":
        payload = fake.random_element(INJECTION_PAYLOADS)
        return (f"{ts} [DB] ERROR ip={ip} query=SELECT * FROM {table} "
                f"WHERE username='{payload}' status=success rows={fake.random_int(1, 50)}")

    else:  # dump
        rows = fake.random_int(500, 5000)
        return (f"{ts} [DB] CRITICAL ip={ip} event=table_dump table={table} "
                f"rows_extracted={rows} destination={fake.ipv4()} status=complete")
