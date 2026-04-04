"""
TICKET-022 — fetch_cves task tests.
Tests NVD API fetching: date range construction, request format,
response parsing, and error handling.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone


# ── Helpers ───────────────────────────────────────────────────────────────────

SAMPLE_NVD_RESPONSE = {
    "resultsPerPage": 2,
    "startIndex": 0,
    "totalResults": 2,
    "format": "NVD_CVE",
    "version": "2.0",
    "timestamp": "2026-04-04T00:00:00.000",
    "vulnerabilities": [
        {
            "cve": {
                "id": "CVE-2026-0001",
                "published": "2026-04-03T10:00:00.000",
                "lastModified": "2026-04-03T12:00:00.000",
                "descriptions": [
                    {"lang": "en", "value": "A critical buffer overflow in example software."}
                ],
                "metrics": {
                    "cvssMetricV31": [
                        {
                            "cvssData": {
                                "baseScore": 9.8,
                                "baseSeverity": "CRITICAL"
                            }
                        }
                    ]
                },
                "references": [],
            }
        },
        {
            "cve": {
                "id": "CVE-2026-0002",
                "published": "2026-04-03T11:00:00.000",
                "lastModified": "2026-04-03T13:00:00.000",
                "descriptions": [
                    {"lang": "en", "value": "An authentication bypass in example API."}
                ],
                "metrics": {},
                "references": [],
            }
        },
    ],
}


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestFetchCvesFunction:

    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_fetch_cves_returns_list(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = SAMPLE_NVD_RESPONSE
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        from airflow.tasks.fetch_cves import fetch_cves
        result = fetch_cves()
        assert isinstance(result, list)

    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_fetch_cves_returns_correct_count(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = SAMPLE_NVD_RESPONSE
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        from airflow.tasks.fetch_cves import fetch_cves
        result = fetch_cves()
        assert len(result) == 2

    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_fetch_cves_result_has_cve_id(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = SAMPLE_NVD_RESPONSE
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        from airflow.tasks.fetch_cves import fetch_cves
        result = fetch_cves()
        assert result[0]["id"] == "CVE-2026-0001"

    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_fetch_cves_hits_nvd_api(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = SAMPLE_NVD_RESPONSE
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        from airflow.tasks.fetch_cves import fetch_cves
        fetch_cves()
        call_url = mock_get.call_args[0][0]
        assert "services.nvd.nist.gov" in call_url

    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_fetch_cves_sends_date_range(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = SAMPLE_NVD_RESPONSE
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        from airflow.tasks.fetch_cves import fetch_cves
        fetch_cves()
        params = mock_get.call_args[1].get("params", {})
        assert "pubStartDate" in params
        assert "pubEndDate" in params

    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_fetch_cves_sends_api_key_header(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = SAMPLE_NVD_RESPONSE
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        with patch.dict("os.environ", {"NVD_API_KEY": "test-key-123"}):
            from airflow.tasks.fetch_cves import fetch_cves
            fetch_cves()
            headers = mock_get.call_args[1].get("headers", {})
            assert "apiKey" in headers

    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_fetch_cves_empty_response_returns_empty_list(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {**SAMPLE_NVD_RESPONSE, "vulnerabilities": [], "totalResults": 0}
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        from airflow.tasks.fetch_cves import fetch_cves
        result = fetch_cves()
        assert result == []

    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_fetch_cves_http_error_raises(self, mock_get):
        import requests
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")
        mock_get.return_value = mock_resp

        from airflow.tasks.fetch_cves import fetch_cves
        with pytest.raises(requests.HTTPError):
            fetch_cves()

    @patch("airflow.tasks.fetch_cves.requests.get")
    def test_fetch_cves_result_items_are_dicts(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = SAMPLE_NVD_RESPONSE
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        from airflow.tasks.fetch_cves import fetch_cves
        result = fetch_cves()
        assert all(isinstance(item, dict) for item in result)
