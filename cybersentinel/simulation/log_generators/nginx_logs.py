"""Nginx Web Server log generator — HTTP request/response logs."""
from datetime import datetime
from faker import Faker

fake = Faker()

VALID_STATUS_CODES = {200, 201, 301, 302, 400, 401, 403, 404, 429, 500, 502, 503}
ENDPOINTS = ["/api/v1/login", "/api/v1/transfer", "/api/v1/balance",
             "/api/v1/users", "/health", "/api/v1/payments", "/static/app.js"]
METHODS = ["GET", "POST", "PUT", "DELETE"]


def generate_nginx_log(status_code: int = 200) -> str:
    if status_code not in VALID_STATUS_CODES:
        raise ValueError(f"Invalid status_code {status_code}. Must be one of {VALID_STATUS_CODES}")

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = fake.ipv4()
    method = fake.random_element(METHODS)
    endpoint = fake.random_element(ENDPOINTS)
    size = fake.random_int(200, 8192)
    duration = fake.random_int(5, 800)

    return (f'{ts} [NGINX] {ip} - "{method} {endpoint} HTTP/1.1" '
            f'{status_code} {size}B {duration}ms "{fake.user_agent()}"')
