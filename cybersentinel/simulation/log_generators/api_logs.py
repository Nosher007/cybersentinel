"""API Gateway log generator — rate limiting, routing, response logs."""
from datetime import datetime
from faker import Faker

fake = Faker()

VALID_STATUS_CODES = {200, 201, 400, 401, 403, 404, 422, 429, 500, 502, 503}
ENDPOINTS = ["/api/v1/transfer", "/api/v1/balance", "/api/v1/login",
             "/api/v1/payments", "/api/v1/users/me", "/api/v1/history"]
METHODS = ["GET", "POST", "PUT", "DELETE"]


def generate_api_log(status_code: int = 200) -> str:
    if status_code not in VALID_STATUS_CODES:
        raise ValueError(f"Invalid status_code {status_code}. Must be one of {VALID_STATUS_CODES}")

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = fake.ipv4()
    method = fake.random_element(METHODS)
    endpoint = fake.random_element(ENDPOINTS)
    duration = fake.random_int(5, 1500)
    request_id = fake.uuid4()[:8]

    return (f"{ts} [API-GW] {method} {endpoint} status={status_code} "
            f"ip={ip} latency={duration}ms request_id={request_id}")
