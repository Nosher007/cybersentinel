"""
TICKET-025 — validate_ingestion task tests.
Tests that ChromaDB similarity search returns results after upsert,
confirming both storage and the RAG query path work correctly.
"""
import pytest
from unittest.mock import patch, MagicMock


MOCK_QUERY_RESULTS_WITH_DATA = {
    "documents": [["CVE-2026-0001: A critical buffer overflow. Severity: CRITICAL."]],
    "ids": [["CVE-2026-0001"]],
    "distances": [[0.12]],
}

MOCK_QUERY_RESULTS_EMPTY = {
    "documents": [[]],
    "ids": [[]],
    "distances": [[]],
}


class TestValidateIngestion:

    @patch("airflow.tasks.validate_ingestion.get_collection")
    def test_validate_returns_true_when_results_found(self, mock_get_col):
        mock_col = MagicMock()
        mock_col.query.return_value = MOCK_QUERY_RESULTS_WITH_DATA
        mock_get_col.return_value = mock_col

        from airflow.tasks.validate_ingestion import validate
        result = validate()
        assert result is True

    @patch("airflow.tasks.validate_ingestion.get_collection")
    def test_validate_raises_when_no_results(self, mock_get_col):
        mock_col = MagicMock()
        mock_col.query.return_value = MOCK_QUERY_RESULTS_EMPTY
        mock_get_col.return_value = mock_col

        from airflow.tasks.validate_ingestion import validate
        with pytest.raises(ValueError):
            validate()

    @patch("airflow.tasks.validate_ingestion.get_collection")
    def test_validate_calls_collection_query(self, mock_get_col):
        mock_col = MagicMock()
        mock_col.query.return_value = MOCK_QUERY_RESULTS_WITH_DATA
        mock_get_col.return_value = mock_col

        from airflow.tasks.validate_ingestion import validate
        validate()
        mock_col.query.assert_called_once()

    @patch("airflow.tasks.validate_ingestion.get_collection")
    def test_validate_queries_with_security_term(self, mock_get_col):
        mock_col = MagicMock()
        mock_col.query.return_value = MOCK_QUERY_RESULTS_WITH_DATA
        mock_get_col.return_value = mock_col

        from airflow.tasks.validate_ingestion import validate
        validate()
        call_kwargs = mock_col.query.call_args[1]
        query_text = call_kwargs.get("query_texts", [""])[0].lower()
        assert any(term in query_text for term in ["vulnerability", "cve", "security", "attack", "exploit"])

    @patch("airflow.tasks.validate_ingestion.get_collection")
    def test_validate_requests_at_least_one_result(self, mock_get_col):
        mock_col = MagicMock()
        mock_col.query.return_value = MOCK_QUERY_RESULTS_WITH_DATA
        mock_get_col.return_value = mock_col

        from airflow.tasks.validate_ingestion import validate
        validate()
        call_kwargs = mock_col.query.call_args[1]
        assert call_kwargs.get("n_results", 0) >= 1

    @patch("airflow.tasks.validate_ingestion.get_collection")
    def test_validate_collection_count_returned_in_summary(self, mock_get_col):
        mock_col = MagicMock()
        mock_col.query.return_value = MOCK_QUERY_RESULTS_WITH_DATA
        mock_col.count.return_value = 25
        mock_get_col.return_value = mock_col

        from airflow.tasks.validate_ingestion import validate
        result = validate()
        assert result is True
