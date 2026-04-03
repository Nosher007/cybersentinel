"""PostgreSQL Database log generator — query execution logs."""
from datetime import datetime
from faker import Faker

fake = Faker()

VALID_QUERY_TYPES = {"SELECT", "INSERT", "UPDATE", "DELETE"}
TABLES = ["users", "transactions", "accounts", "sessions", "audit_log", "payments"]


def generate_database_log(query_type: str = "SELECT") -> str:
    query_type = query_type.upper()
    if query_type not in VALID_QUERY_TYPES:
        raise ValueError(f"Invalid query_type '{query_type}'. Must be one of {VALID_QUERY_TYPES}")

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table = fake.random_element(TABLES)
    duration = fake.random_int(1, 2000)
    rows = fake.random_int(0, 5000)
    user = fake.random_element(["app_user", "admin", "readonly", "api_service"])

    templates = {
        "SELECT": f"{ts} [DB] INFO  user={user} query=SELECT FROM {table} WHERE ... rows={rows} duration={duration}ms",
        "INSERT": f"{ts} [DB] INFO  user={user} query=INSERT INTO {table} rows_affected={fake.random_int(1,10)} duration={duration}ms",
        "UPDATE": f"{ts} [DB] INFO  user={user} query=UPDATE {table} SET ... rows_affected={fake.random_int(1,100)} duration={duration}ms",
        "DELETE": f"{ts} [DB] WARN  user={user} query=DELETE FROM {table} rows_affected={fake.random_int(1,50)} duration={duration}ms",
    }
    return templates[query_type]
