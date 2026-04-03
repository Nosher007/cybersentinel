"""
TICKET-005 — TDD tests for novapay_context.py
Red phase: all tests written before implementation exists.
Tests are designed to fail in as many ways as possible.
"""
import pytest
from simulation.novapay_context import (
    NOVAPAY_SERVICES,
    NOVAPAY_DEPARTMENTS,
    Service,
    Department,
    get_service,
)

REQUIRED_SERVICE_IDS = {
    "auth",
    "transaction_engine",
    "api_gateway",
    "database",
    "web_server",
    "firewall",
}

REQUIRED_DEPARTMENT_IDS = {
    "payments",
    "authentication",
    "database",
    "api_layer",
    "network",
}

VALID_HEALTH_STATUSES = {"HEALTHY", "WARNING", "CRITICAL", "BREACHED"}


# ── Service contract tests ────────────────────────────────────────────────────

class TestServiceContract:

    def test_all_required_services_exist(self):
        """All 6 NovaPay services must be present."""
        ids = {s.id for s in NOVAPAY_SERVICES}
        assert REQUIRED_SERVICE_IDS == ids, (
            f"Missing services: {REQUIRED_SERVICE_IDS - ids}"
        )

    def test_every_service_has_required_fields(self):
        """Every service must have id, name, type, and port."""
        for service in NOVAPAY_SERVICES:
            assert service.id, f"Service missing id: {service}"
            assert service.name, f"Service missing name: {service}"
            assert service.type, f"Service missing type: {service}"
            assert service.port > 0, f"Service has invalid port: {service}"

    def test_service_ports_are_unique(self):
        """No two services should share the same port."""
        ports = [s.port for s in NOVAPAY_SERVICES]
        assert len(ports) == len(set(ports)), "Duplicate ports found across services"

    def test_service_ids_are_unique(self):
        """Service IDs must be unique."""
        ids = [s.id for s in NOVAPAY_SERVICES]
        assert len(ids) == len(set(ids)), "Duplicate service IDs found"

    def test_service_port_in_valid_range(self):
        """Ports must be in valid range 1-65535."""
        for service in NOVAPAY_SERVICES:
            assert 1 <= service.port <= 65535, (
                f"Port {service.port} out of range for service {service.id}"
            )

    def test_service_type_is_non_empty_string(self):
        """Service type must be a non-empty string."""
        for service in NOVAPAY_SERVICES:
            assert isinstance(service.type, str) and service.type.strip(), (
                f"Service {service.id} has blank or non-string type"
            )


# ── Department contract tests ─────────────────────────────────────────────────

class TestDepartmentContract:

    def test_all_required_departments_exist(self):
        """All 5 NovaPay departments must be present."""
        ids = {d.id for d in NOVAPAY_DEPARTMENTS}
        assert REQUIRED_DEPARTMENT_IDS == ids, (
            f"Missing departments: {REQUIRED_DEPARTMENT_IDS - ids}"
        )

    def test_every_department_has_required_fields(self):
        """Every department must have id, name, and default_health."""
        for dept in NOVAPAY_DEPARTMENTS:
            assert dept.id, f"Department missing id: {dept}"
            assert dept.name, f"Department missing name: {dept}"
            assert dept.default_health, f"Department missing default_health: {dept}"

    def test_default_health_is_healthy(self):
        """All departments must start as HEALTHY."""
        for dept in NOVAPAY_DEPARTMENTS:
            assert dept.default_health == "HEALTHY", (
                f"Department {dept.id} does not default to HEALTHY"
            )

    def test_department_ids_are_unique(self):
        """Department IDs must be unique."""
        ids = [d.id for d in NOVAPAY_DEPARTMENTS]
        assert len(ids) == len(set(ids)), "Duplicate department IDs found"

    def test_department_health_values_are_valid(self):
        """default_health must be one of the 4 allowed values."""
        for dept in NOVAPAY_DEPARTMENTS:
            assert dept.default_health in VALID_HEALTH_STATUSES, (
                f"Department {dept.id} has invalid health: {dept.default_health}"
            )

    def test_each_department_maps_to_at_least_one_service(self):
        """Every department must reference at least one service ID."""
        service_ids = {s.id for s in NOVAPAY_SERVICES}
        for dept in NOVAPAY_DEPARTMENTS:
            assert dept.service_ids, f"Department {dept.id} has no linked services"
            for sid in dept.service_ids:
                assert sid in service_ids, (
                    f"Department {dept.id} references unknown service: {sid}"
                )


# ── get_service() helper tests ────────────────────────────────────────────────

class TestGetService:

    def test_get_service_returns_correct_service(self):
        """get_service('auth') must return the auth service."""
        service = get_service("auth")
        assert service.id == "auth"

    def test_get_service_unknown_id_raises(self):
        """get_service with unknown ID must raise ValueError."""
        with pytest.raises(ValueError):
            get_service("nonexistent_service")

    def test_get_service_empty_string_raises(self):
        """get_service with empty string must raise ValueError."""
        with pytest.raises(ValueError):
            get_service("")

    def test_get_service_none_raises(self):
        """get_service with None must raise TypeError or ValueError."""
        with pytest.raises((TypeError, ValueError)):
            get_service(None)
