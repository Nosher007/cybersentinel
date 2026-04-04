"""
TICKET-024 — embed_and_upsert task tests.
Tests ChromaDB upsert: correct fields passed, idempotency,
empty input handling, and metadata structure.
"""
import pytest
from unittest.mock import patch, MagicMock


PARSED_CVES = [
    {
        "cve_id": "CVE-2026-0001",
        "description": "A critical buffer overflow in example software.",
        "severity": "CRITICAL",
        "base_score": 9.8,
        "published": "2026-04-03T10:00:00.000",
        "text": "CVE-2026-0001: A critical buffer overflow. Severity: CRITICAL. Score: 9.8.",
    },
    {
        "cve_id": "CVE-2026-0002",
        "description": "An authentication bypass in example API.",
        "severity": "HIGH",
        "base_score": 7.5,
        "published": "2026-04-03T11:00:00.000",
        "text": "CVE-2026-0002: An authentication bypass. Severity: HIGH. Score: 7.5.",
    },
]


class TestUpsertToChromadb:

    @patch("airflow.tasks.embed_cves.get_collection")
    def test_upsert_calls_collection_upsert(self, mock_get_col):
        mock_col = MagicMock()
        mock_get_col.return_value = mock_col

        from airflow.tasks.embed_cves import upsert_to_chromadb
        upsert_to_chromadb(PARSED_CVES)
        mock_col.upsert.assert_called_once()

    @patch("airflow.tasks.embed_cves.get_collection")
    def test_upsert_passes_correct_ids(self, mock_get_col):
        mock_col = MagicMock()
        mock_get_col.return_value = mock_col

        from airflow.tasks.embed_cves import upsert_to_chromadb
        upsert_to_chromadb(PARSED_CVES)
        call_kwargs = mock_col.upsert.call_args[1]
        assert call_kwargs["ids"] == ["CVE-2026-0001", "CVE-2026-0002"]

    @patch("airflow.tasks.embed_cves.get_collection")
    def test_upsert_passes_text_as_documents(self, mock_get_col):
        mock_col = MagicMock()
        mock_get_col.return_value = mock_col

        from airflow.tasks.embed_cves import upsert_to_chromadb
        upsert_to_chromadb(PARSED_CVES)
        call_kwargs = mock_col.upsert.call_args[1]
        assert "CVE-2026-0001" in call_kwargs["documents"][0]

    @patch("airflow.tasks.embed_cves.get_collection")
    def test_upsert_passes_metadata(self, mock_get_col):
        mock_col = MagicMock()
        mock_get_col.return_value = mock_col

        from airflow.tasks.embed_cves import upsert_to_chromadb
        upsert_to_chromadb(PARSED_CVES)
        call_kwargs = mock_col.upsert.call_args[1]
        assert "metadatas" in call_kwargs
        assert call_kwargs["metadatas"][0]["severity"] == "CRITICAL"

    @patch("airflow.tasks.embed_cves.get_collection")
    def test_upsert_metadata_has_cve_id(self, mock_get_col):
        mock_col = MagicMock()
        mock_get_col.return_value = mock_col

        from airflow.tasks.embed_cves import upsert_to_chromadb
        upsert_to_chromadb(PARSED_CVES)
        call_kwargs = mock_col.upsert.call_args[1]
        assert call_kwargs["metadatas"][0]["cve_id"] == "CVE-2026-0001"

    @patch("airflow.tasks.embed_cves.get_collection")
    def test_upsert_metadata_has_base_score(self, mock_get_col):
        mock_col = MagicMock()
        mock_get_col.return_value = mock_col

        from airflow.tasks.embed_cves import upsert_to_chromadb
        upsert_to_chromadb(PARSED_CVES)
        call_kwargs = mock_col.upsert.call_args[1]
        assert call_kwargs["metadatas"][0]["base_score"] == 9.8

    @patch("airflow.tasks.embed_cves.get_collection")
    def test_upsert_empty_list_skips_upsert(self, mock_get_col):
        mock_col = MagicMock()
        mock_get_col.return_value = mock_col

        from airflow.tasks.embed_cves import upsert_to_chromadb
        upsert_to_chromadb([])
        mock_col.upsert.assert_not_called()

    @patch("airflow.tasks.embed_cves.get_collection")
    def test_upsert_returns_count_of_upserted(self, mock_get_col):
        mock_col = MagicMock()
        mock_get_col.return_value = mock_col

        from airflow.tasks.embed_cves import upsert_to_chromadb
        result = upsert_to_chromadb(PARSED_CVES)
        assert result == 2

    @patch("airflow.tasks.embed_cves.get_collection")
    def test_upsert_empty_returns_zero(self, mock_get_col):
        mock_col = MagicMock()
        mock_get_col.return_value = mock_col

        from airflow.tasks.embed_cves import upsert_to_chromadb
        result = upsert_to_chromadb([])
        assert result == 0


class TestEmbedCves:

    @patch("airflow.tasks.embed_cves.get_collection")
    def test_embed_cves_returns_parsed_cves_unchanged(self, mock_get_col):
        """embed_cves passes through parsed CVEs for XCom — ChromaDB does its own embedding."""
        mock_col = MagicMock()
        mock_get_col.return_value = mock_col

        from airflow.tasks.embed_cves import embed_cves
        result = embed_cves(PARSED_CVES)
        assert result == PARSED_CVES

    @patch("airflow.tasks.embed_cves.get_collection")
    def test_embed_cves_empty_returns_empty(self, mock_get_col):
        mock_col = MagicMock()
        mock_get_col.return_value = mock_col

        from airflow.tasks.embed_cves import embed_cves
        result = embed_cves([])
        assert result == []
