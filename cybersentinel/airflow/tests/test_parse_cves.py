"""
TICKET-023 — parse_and_clean task tests.
Tests CVE record parsing: field extraction, missing field handling,
severity fallback, and batch processing.
"""
import pytest


FULL_CVE = {
    "id": "CVE-2026-0001",
    "published": "2026-04-03T10:00:00.000",
    "descriptions": [
        {"lang": "en", "value": "A critical buffer overflow in example software."},
        {"lang": "es", "value": "Un desbordamiento de buffer critico."},
    ],
    "metrics": {
        "cvssMetricV31": [
            {
                "cvssData": {
                    "baseScore": 9.8,
                    "baseSeverity": "CRITICAL",
                }
            }
        ]
    },
    "configurations": [
        {"nodes": [{"cpeMatch": [{"criteria": "cpe:2.3:a:example:software:*:*:*:*:*:*:*:*"}]}]}
    ],
}

CVE_NO_CVSS = {
    "id": "CVE-2026-0002",
    "published": "2026-04-03T11:00:00.000",
    "descriptions": [
        {"lang": "en", "value": "An authentication bypass with no CVSS score yet."}
    ],
    "metrics": {},
}

CVE_V2_ONLY = {
    "id": "CVE-2026-0003",
    "published": "2026-04-03T12:00:00.000",
    "descriptions": [
        {"lang": "en", "value": "An older CVE with only CVSS v2 score."}
    ],
    "metrics": {
        "cvssMetricV2": [
            {"cvssData": {"baseScore": 7.5, "baseSeverity": "HIGH"}}
        ]
    },
}

CVE_EMPTY_CVSS_LIST = {
    "id": "CVE-2026-0004",
    "published": "2026-04-03T13:00:00.000",
    "descriptions": [{"lang": "en", "value": "CVE with empty CVSS list."}],
    "metrics": {"cvssMetricV31": []},
}


class TestParseCve:

    def test_parse_returns_dict(self):
        from airflow.tasks.parse_cves import parse_cve
        result = parse_cve(FULL_CVE)
        assert isinstance(result, dict)

    def test_parse_extracts_cve_id(self):
        from airflow.tasks.parse_cves import parse_cve
        result = parse_cve(FULL_CVE)
        assert result["cve_id"] == "CVE-2026-0001"

    def test_parse_extracts_english_description(self):
        from airflow.tasks.parse_cves import parse_cve
        result = parse_cve(FULL_CVE)
        assert "buffer overflow" in result["description"]

    def test_parse_extracts_severity(self):
        from airflow.tasks.parse_cves import parse_cve
        result = parse_cve(FULL_CVE)
        assert result["severity"] == "CRITICAL"

    def test_parse_extracts_base_score(self):
        from airflow.tasks.parse_cves import parse_cve
        result = parse_cve(FULL_CVE)
        assert result["base_score"] == 9.8

    def test_parse_extracts_published_date(self):
        from airflow.tasks.parse_cves import parse_cve
        result = parse_cve(FULL_CVE)
        assert result["published"] == "2026-04-03T10:00:00.000"

    def test_parse_missing_cvss_defaults_to_unknown(self):
        from airflow.tasks.parse_cves import parse_cve
        result = parse_cve(CVE_NO_CVSS)
        assert result["severity"] == "UNKNOWN"

    def test_parse_missing_cvss_score_defaults_to_zero(self):
        from airflow.tasks.parse_cves import parse_cve
        result = parse_cve(CVE_NO_CVSS)
        assert result["base_score"] == 0.0

    def test_parse_empty_cvss_list_defaults_gracefully(self):
        from airflow.tasks.parse_cves import parse_cve
        result = parse_cve(CVE_EMPTY_CVSS_LIST)
        assert result["severity"] == "UNKNOWN"
        assert result["base_score"] == 0.0

    def test_parse_result_has_text_field_for_embedding(self):
        from airflow.tasks.parse_cves import parse_cve
        result = parse_cve(FULL_CVE)
        assert "text" in result
        assert len(result["text"]) > 0

    def test_parse_text_contains_cve_id_and_description(self):
        from airflow.tasks.parse_cves import parse_cve
        result = parse_cve(FULL_CVE)
        assert "CVE-2026-0001" in result["text"]
        assert "buffer overflow" in result["text"]


class TestParseCves:

    def test_parse_cves_returns_list(self):
        from airflow.tasks.parse_cves import parse_cves
        result = parse_cves([FULL_CVE, CVE_NO_CVSS])
        assert isinstance(result, list)

    def test_parse_cves_correct_count(self):
        from airflow.tasks.parse_cves import parse_cves
        result = parse_cves([FULL_CVE, CVE_NO_CVSS, CVE_V2_ONLY])
        assert len(result) == 3

    def test_parse_cves_empty_input_returns_empty(self):
        from airflow.tasks.parse_cves import parse_cves
        assert parse_cves([]) == []

    def test_parse_cves_none_input_raises(self):
        from airflow.tasks.parse_cves import parse_cves
        with pytest.raises((TypeError, AttributeError)):
            parse_cves(None)
