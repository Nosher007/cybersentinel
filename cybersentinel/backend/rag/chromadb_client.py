"""
TICKET-014 — ChromaDB client.
Local persistent ChromaDB — no server required.
"""
import os
import chromadb

COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "cybersentinel_kb")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma-data")


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=CHROMA_PATH)


def get_collection() -> chromadb.Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
