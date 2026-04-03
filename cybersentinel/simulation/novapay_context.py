"""
TICKET-005 — NovaPay context module
Defines the static infrastructure of the fictional NovaPay fintech company.
This is the source of truth for service definitions and department mappings.
"""
from pydantic import BaseModel


class Service(BaseModel):
    id: str
    name: str
    type: str
    port: int


class Department(BaseModel):
    id: str
    name: str
    default_health: str
    service_ids: list[str]


NOVAPAY_SERVICES: list[Service] = [
    Service(id="auth",               name="Auth Service",        type="authentication", port=8001),
    Service(id="transaction_engine", name="Transaction Engine",  type="payments",       port=8002),
    Service(id="api_gateway",        name="API Gateway",         type="gateway",        port=8003),
    Service(id="database",           name="PostgreSQL Database", type="database",       port=5432),
    Service(id="web_server",         name="Nginx Web Server",    type="web",            port=80),
    Service(id="firewall",           name="Firewall",            type="network",        port=8004),
]

NOVAPAY_DEPARTMENTS: list[Department] = [
    Department(id="payments",       name="Payments",         default_health="HEALTHY", service_ids=["transaction_engine"]),
    Department(id="authentication", name="Authentication",   default_health="HEALTHY", service_ids=["auth"]),
    Department(id="database",       name="Database",         default_health="HEALTHY", service_ids=["database"]),
    Department(id="api_layer",      name="API Layer",        default_health="HEALTHY", service_ids=["api_gateway"]),
    Department(id="network",        name="Network/Firewall", default_health="HEALTHY", service_ids=["web_server", "firewall"]),
]

_SERVICE_MAP: dict[str, Service] = {s.id: s for s in NOVAPAY_SERVICES}


def get_service(service_id: str) -> Service:
    if not isinstance(service_id, str):
        raise TypeError(f"service_id must be a string, got {type(service_id)}")
    if not service_id:
        raise ValueError("service_id cannot be empty")
    if service_id not in _SERVICE_MAP:
        raise ValueError(f"Unknown service: '{service_id}'")
    return _SERVICE_MAP[service_id]
