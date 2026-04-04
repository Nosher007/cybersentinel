"""
TICKET-026 — Full DAG end-to-end wiring tests.
Tests the complete pipeline: fetch → parse → embed → upsert → validate
by calling each task function in sequence with mocked external dependencies.
"""
import pytest
from unittest.mock import patch, MagicMock


MOCK_NVD_RESPONSE = {
    "resultsPerPage": 2,
    "totalResults": 2,
    "vulnerabilities": [
        {
            "cve": {
                "id": "CVE-2026-1001",
                "published": "2026-04-04T01:00:00.000",
                "descriptions": [{"lang": "en", "value": "Remote code execution in test software."}],
                "metrics": {
                    "cvssMetricV31": [{"cvssData": {"baseScore": 9.8, "baseSeverity": "CRITICAL"}}]
                },
            }
        },
        {
            "cve": {
                "id": "CVE-2026-1002",
                "published": "2026-04-04T02:00:00.000",
                "descriptions": [{"lang": "en", "value": "SQL injection in test API endpoint."}],
                "metrics": {},
            }
        },
    ],
}


class TestFullPipelineFlow:

    @patch("airflow.tasks.validate_ingestion.get_collection")
    @patch("airflow.tasks.embed_cves.get_collection")
    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_full_pipeline_runs_without_error(
        self, mock_requests, mock_embed_col, mock_validate_col
    ):
        # Mock NVD API
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_NVD_RESPONSE
        mock_resp.raise_for_status.return_value = None
        mock_requests.return_value = mock_resp

        # Mock ChromaDB for upsert
        mock_col = MagicMock()
        mock_embed_col.return_value = mock_col

        # Mock ChromaDB for validation
        mock_val_col = MagicMock()
        mock_val_col.query.return_value = {
            "documents": [["CVE-2026-1001: Remote code execution."]],
            "ids": [["CVE-2026-1001"]],
        }
        mock_val_col.count.return_value = 22
        mock_validate_col.return_value = mock_val_col

        from airflow.tasks.fetch_cves import fetch_cves
        from airflow.tasks.parse_cves import parse_cves
        from airflow.tasks.embed_cves import embed_cves, upsert_to_chromadb
        from airflow.tasks.validate_ingestion import validate

        # Step 1: Fetch
        raw = fetch_cves()
        assert len(raw) == 2

        # Step 2: Parse
        parsed = parse_cves(raw)
        assert len(parsed) == 2
        assert parsed[0]["cve_id"] == "CVE-2026-1001"
        assert parsed[1]["severity"] == "UNKNOWN"  # no CVSS

        # Step 3: Embed (pass-through)
        embedded = embed_cves(parsed)
        assert embedded == parsed

        # Step 4: Upsert
        count = upsert_to_chromadb(embedded)
        assert count == 2
        mock_col.upsert.assert_called_once()

        # Step 5: Validate
        result = validate()
        assert result is True

    @patch("airflow.tasks.validate_ingestion.get_collection")
    @patch("airflow.tasks.embed_cves.get_collection")
    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_pipeline_upsert_called_with_correct_ids(
        self, mock_requests, mock_embed_col, mock_validate_col
    ):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_NVD_RESPONSE
        mock_resp.raise_for_status.return_value = None
        mock_requests.return_value = mock_resp

        mock_col = MagicMock()
        mock_embed_col.return_value = mock_col

        mock_val_col = MagicMock()
        mock_val_col.query.return_value = {"documents": [["some result"]], "ids": [["CVE-2026-1001"]]}
        mock_val_col.count.return_value = 22
        mock_validate_col.return_value = mock_val_col

        from airflow.tasks.fetch_cves import fetch_cves
        from airflow.tasks.parse_cves import parse_cves
        from airflow.tasks.embed_cves import upsert_to_chromadb

        raw = fetch_cves()
        parsed = parse_cves(raw)
        upsert_to_chromadb(parsed)

        ids_passed = mock_col.upsert.call_args[1]["ids"]
        assert "CVE-2026-1001" in ids_passed
        assert "CVE-2026-1002" in ids_passed

    @patch("airflow.tasks.validate_ingestion.get_collection")
    @patch("airflow.tasks.embed_cves.get_collection")
    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_pipeline_empty_fetch_skips_upsert(
        self, mock_requests, mock_embed_col, mock_validate_col
    ):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {**MOCK_NVD_RESPONSE, "vulnerabilities": [], "totalResults": 0}
        mock_resp.raise_for_status.return_value = None
        mock_requests.return_value = mock_resp

        mock_col = MagicMock()
        mock_embed_col.return_value = mock_col

        from airflow.tasks.fetch_cves import fetch_cves
        from airflow.tasks.parse_cves import parse_cves
        from airflow.tasks.embed_cves import upsert_to_chromadb

        raw = fetch_cves()
        parsed = parse_cves(raw)
        count = upsert_to_chromadb(parsed)

        assert count == 0
        mock_col.upsert.assert_not_called()

    @patch("airflow.tasks.validate_ingestion.get_collection")
    @patch("airflow.tasks.embed_cves.get_collection")
    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_pipeline_validation_fails_on_empty_chromadb(
        self, mock_requests, mock_embed_col, mock_validate_col
    ):
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_NVD_RESPONSE
        mock_resp.raise_for_status.return_value = None
        mock_requests.return_value = mock_resp

        mock_col = MagicMock()
        mock_embed_col.return_value = mock_col

        mock_val_col = MagicMock()
        mock_val_col.query.return_value = {"documents": [[]], "ids": [[]]}
        mock_validate_col.return_value = mock_val_col

        from airflow.tasks.fetch_cves import fetch_cves
        from airflow.tasks.parse_cves import parse_cves
        from airflow.tasks.embed_cves import upsert_to_chromadb
        from airflow.tasks.validate_ingestion import validate

        raw = fetch_cves()
        parsed = parse_cves(raw)
        upsert_to_chromadb(parsed)

        with pytest.raises(ValueError):
            validate()
