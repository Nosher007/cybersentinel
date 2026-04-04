"""
TICKET-025 — validate_ingestion task.
Runs a test similarity query against ChromaDB to confirm that
newly upserted CVEs are retrievable via the RAG query path.
Raises ValueError if no results are returned — fails the DAG task.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from backend.rag.chromadb_client import get_collection

VALIDATION_QUERY = "security vulnerability exploit attack remediation"


def validate() -> bool:
    collection = get_collection()

    results = collection.query(
        query_texts=[VALIDATION_QUERY],
        n_results=3,
    )

    documents = results.get("documents", [[]])[0]

    if not documents:
        raise ValueError(
            "Validation failed: ChromaDB similarity search returned no results. "
            "CVE ingestion may have failed."
        )

    total = collection.count()
    print(f"Validation passed: {len(documents)} results returned. Total records in collection: {total}.")

    return True
