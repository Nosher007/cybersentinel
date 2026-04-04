"""
TICKET-024 — embed_and_upsert task.
Takes parsed CVE records, upserts them into ChromaDB.
ChromaDB handles embeddings internally using its default embedding function.
Returns the parsed CVEs for XCom passthrough to the next task.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from backend.rag.chromadb_client import get_collection


def embed_cves(parsed_cves: list[dict]) -> list[dict]:
    """Pass-through — ChromaDB embeds documents itself on upsert."""
    return parsed_cves


def upsert_to_chromadb(parsed_cves: list[dict]) -> int:
    if not parsed_cves:
        return 0

    collection = get_collection()

    collection.upsert(
        ids=[cve["cve_id"] for cve in parsed_cves],
        documents=[cve["text"] for cve in parsed_cves],
        metadatas=[
            {
                "cve_id": cve["cve_id"],
                "severity": cve["severity"],
                "base_score": cve["base_score"],
                "published": cve["published"],
                "type": "cve",
            }
            for cve in parsed_cves
        ],
    )

    return len(parsed_cves)
