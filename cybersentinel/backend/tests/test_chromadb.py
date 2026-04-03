"""
TICKET-014 — TDD tests for ChromaDB setup and seed knowledge base.
Red phase: written before implementation exists.
Tests cover: client connects, collections exist, seed data queryable.
"""
import pytest
from backend.rag.chromadb_client import get_chroma_client, get_collection, COLLECTION_NAME
from backend.rag.seed_knowledge_base import seed_knowledge_base


class TestChromaDBClient:

    def test_client_connects(self):
        client = get_chroma_client()
        assert client is not None

    def test_get_collection_returns_collection(self):
        col = get_collection()
        assert col is not None

    def test_collection_has_correct_name(self):
        col = get_collection()
        assert col.name == COLLECTION_NAME

    def test_collection_name_is_string(self):
        assert isinstance(COLLECTION_NAME, str) and COLLECTION_NAME.strip()


class TestSeedKnowledgeBase:

    def test_seed_runs_without_error(self):
        """Seeding must complete without raising."""
        seed_knowledge_base()

    def test_collection_has_at_least_25_entries_after_seed(self):
        """20 CVEs + 5 OWASP entries = minimum 25."""
        seed_knowledge_base()
        col = get_collection()
        count = col.count()
        assert count >= 25, f"Expected at least 25 entries, got {count}"

    def test_collection_has_cve_entries(self):
        seed_knowledge_base()
        col = get_collection()
        results = col.get(where={"type": "cve"})
        assert len(results["ids"]) >= 20, (
            f"Expected at least 20 CVE entries, got {len(results['ids'])}"
        )

    def test_collection_has_owasp_entries(self):
        seed_knowledge_base()
        col = get_collection()
        results = col.get(where={"type": "owasp"})
        assert len(results["ids"]) >= 5, (
            f"Expected at least 5 OWASP entries, got {len(results['ids'])}"
        )

    def test_seed_is_idempotent(self):
        """Running seed twice must not duplicate entries."""
        seed_knowledge_base()
        count_first = get_collection().count()
        seed_knowledge_base()
        count_second = get_collection().count()
        assert count_first == count_second, (
            f"Seed is not idempotent: {count_first} vs {count_second} entries"
        )

    def test_cve_entries_have_required_metadata(self):
        """Each CVE must have id, severity, and description metadata."""
        seed_knowledge_base()
        col = get_collection()
        results = col.get(where={"type": "cve"}, include=["metadatas"])
        for meta in results["metadatas"]:
            assert "type" in meta, f"CVE missing 'type': {meta}"
            assert "severity" in meta, f"CVE missing 'severity': {meta}"
            assert "cve_id" in meta, f"CVE missing 'cve_id': {meta}"

    def test_owasp_entries_have_required_metadata(self):
        """Each OWASP entry must have type and category metadata."""
        seed_knowledge_base()
        col = get_collection()
        results = col.get(where={"type": "owasp"}, include=["metadatas"])
        for meta in results["metadatas"]:
            assert "type" in meta, f"OWASP missing 'type': {meta}"
            assert "category" in meta, f"OWASP missing 'category': {meta}"


class TestSimilaritySearch:

    def test_query_returns_results(self):
        """Querying for SQL injection must return relevant entries."""
        seed_knowledge_base()
        col = get_collection()
        results = col.query(
            query_texts=["SQL injection attack database"],
            n_results=3
        )
        assert len(results["ids"][0]) > 0, "Query returned no results"

    def test_query_returns_relevant_results(self):
        """SQL injection query must return SQL-related entries."""
        seed_knowledge_base()
        col = get_collection()
        results = col.query(
            query_texts=["SQL injection attack database"],
            n_results=3,
            include=["documents"]
        )
        docs = " ".join(results["documents"][0]).lower()
        assert any(k in docs for k in {"sql", "injection", "database", "query"}), (
            f"SQL query returned irrelevant results: {docs}"
        )

    def test_query_brute_force_returns_auth_results(self):
        """Brute force query must return auth-related entries."""
        seed_knowledge_base()
        col = get_collection()
        results = col.query(
            query_texts=["brute force login authentication"],
            n_results=3,
            include=["documents"]
        )
        docs = " ".join(results["documents"][0]).lower()
        assert any(k in docs for k in {"auth", "login", "brute", "password", "credential"}), (
            f"Brute force query returned irrelevant results: {docs}"
        )
