"""
TICKET-008 — TDD tests for transaction log generator.
Red phase: written before implementation exists.
"""
import re
import pytest
from simulation.log_generators.transaction_logs import generate_transaction_log

TIMESTAMP_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
VALID_TRANSACTION_TYPES = {"transfer", "payment", "probe", "scrape"}


class TestTransactionLogGenerator:

    def test_returns_a_string(self):
        assert isinstance(generate_transaction_log(), str)

    def test_log_is_not_empty(self):
        assert generate_transaction_log().strip() != ""

    def test_contains_timestamp(self):
        log = generate_transaction_log()
        assert TIMESTAMP_PATTERN.search(log), f"Missing timestamp: {log}"

    def test_contains_amount(self):
        log = generate_transaction_log()
        assert re.search(r"\$[\d,]+\.?\d*", log), f"Missing dollar amount: {log}"

    def test_contains_transaction_id(self):
        log = generate_transaction_log()
        assert re.search(r"txn_id=[a-z0-9\-]+", log, re.IGNORECASE), (
            f"Missing transaction ID: {log}"
        )

    def test_contains_status(self):
        log = generate_transaction_log().lower()
        assert any(s in log for s in {"success", "failed", "pending", "flagged"}), (
            f"Missing status: {log}"
        )

    def test_each_call_produces_different_log(self):
        logs = {generate_transaction_log() for _ in range(10)}
        assert len(logs) > 1

    def test_accepts_transaction_type_transfer(self):
        log = generate_transaction_log(transaction_type="transfer")
        assert isinstance(log, str) and log.strip()

    def test_accepts_transaction_type_probe(self):
        log = generate_transaction_log(transaction_type="probe")
        assert isinstance(log, str) and log.strip()

    def test_probe_has_small_amount(self):
        """Probe transactions should be small amounts ($1-$5)."""
        for _ in range(10):
            log = generate_transaction_log(transaction_type="probe")
            amount = re.search(r"\$([\d]+)", log)
            assert amount and int(amount.group(1)) <= 10, (
                f"Probe transaction amount too large: {log}"
            )

    def test_accepts_amount_override(self):
        log = generate_transaction_log(amount=48000)
        assert "48000" in log or "48,000" in log

    def test_invalid_transaction_type_raises(self):
        with pytest.raises(ValueError):
            generate_transaction_log(transaction_type="steal")

    def test_negative_amount_raises(self):
        with pytest.raises(ValueError):
            generate_transaction_log(amount=-100)

    def test_zero_amount_raises(self):
        with pytest.raises(ValueError):
            generate_transaction_log(amount=0)
