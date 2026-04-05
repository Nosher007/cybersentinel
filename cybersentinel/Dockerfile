# ── Stage 1: dependencies ────────────────────────────────────────────────────
FROM python:3.11-slim AS deps

WORKDIR /app

# Layer-cache: install deps only when requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: seed ChromaDB ────────────────────────────────────────────────────
FROM deps AS seeded

WORKDIR /app

# Copy source so seed script can run
COPY backend/ backend/
COPY simulation/ simulation/

# Bake ChromaDB into the image at build time (Option A)
ENV CHROMA_PATH=/app/chroma-data
RUN mkdir -p /app/chroma-data && \
    python -m backend.rag.seed_knowledge_base && \
    echo "--- ChromaDB files after seed ---" && \
    find /app/chroma-data -type f && \
    echo "--- end ---"

# ── Stage 3: final runtime image ─────────────────────────────────────────────
FROM deps AS final

WORKDIR /app

# Copy pre-seeded ChromaDB data from the seed stage
COPY --from=seeded /app/chroma-data /app/chroma-data

# Copy all application source
COPY backend/ backend/
COPY simulation/ simulation/

# Runtime env defaults (API keys injected at deploy time — never baked in)
ENV CHROMA_PATH=/app/chroma-data
ENV CHROMA_COLLECTION_NAME=cybersentinel_kb
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO

# Expose FastAPI port
EXPOSE 8000

# Start Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
