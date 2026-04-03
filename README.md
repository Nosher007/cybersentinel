# CyberSentinel

An **AI-powered cybersecurity simulation game** built with LangChain/LangGraph. Attack a fictional fintech company in natural language and watch a multi-agent AI pipeline detect, classify, and remediate the threat in real time.

---

## What It Does

1. You land on a page showing **NovaPay** — a fictional digital bank — operating live (transactions ticking, users logging in, servers humming)
2. A **CyberSentinel monitoring window** sits alongside it — calm and green when everything is normal
3. You type a freeform attack prompt: *"try to steal customer credit card data"* or *"flood the payment server"*
4. An **LLM interprets the attack**, maps it to a scenario, and generates realistic logs
5. **NovaPay reacts** — affected departments go yellow → orange → red, metrics spike
6. **CyberSentinel fires** — alert banner slams in, logs stream in real time, AI solution panel populates step by step

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │  NovaPay Live View   │  │  CyberSentinel Alert Window  │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
│           [ Attack Prompt Input — type anything ]           │
└───────────────────────────┬─────────────────────────────────┘
                            │ WebSocket + REST
┌───────────────────────────▼─────────────────────────────────┐
│                   FastAPI Backend                           │
│  /ws (WebSocket)  /attack (POST)  /threats (GET)           │
└────────────┬──────────────────────────┬────────────────────┘
             │                          │
┌────────────▼──────────┐  ┌────────────▼─────────────────────┐
│  Simulation Engine    │  │  LangGraph Multi-Agent Pipeline  │
│  5 attack scenarios   │  │  1. Attack Prompt Interpreter    │
│  Realistic log gen    │  │  2. Log Parser Agent             │
│  NovaPay context      │  │  3. Threat Detector Agent        │
│  Timed phase runner   │  │  4. Severity Classifier Agent    │
└───────────────────────┘  │  5. Remediation Agent            │
                           └──────────────┬───────────────────┘
                                          │
                           ┌──────────────▼───────────────────┐
                           │  ChromaDB + RAG                  │
                           │  CVE database + OWASP playbooks  │
                           └──────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TailwindCSS |
| Realtime | WebSockets (FastAPI native) |
| Backend | FastAPI + Uvicorn |
| Agent Orchestration | LangGraph (StateGraph) |
| LLM Chains | LangChain |
| LLM Model | GPT-4o / Claude 3.5 Sonnet |
| Vector DB | ChromaDB (local) |
| Embeddings | OpenAI text-embedding-ada-002 |
| Data Models | Pydantic v2 |
| Simulation | Python + Faker |
| Pipeline | Apache Airflow (nightly CVE updates) |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## Attack Scenarios

| Scenario | Target | Duration |
|---|---|---|
| Account Takeover | Auth Service | ~3 min |
| Transaction Fraud | Transaction Engine + API Gateway | ~4 min |
| SQL Injection | Database + API Gateway | ~2 min |
| Insider Threat | Database + Compliance | ~5 min |
| DDoS Attack | API Gateway + Web Server | ~2 min |

---

## LangGraph Agent Pipeline

- **Agent 1 — Attack Prompt Interpreter:** Maps natural language input to attack type, target service, and scenario ID
- **Agent 2 — Log Parser:** Converts raw log strings into structured `ParsedLog` Pydantic models
- **Agent 3 — Threat Detector:** Cross-correlates logs to identify attack patterns using LLM + RAG
- **Agent 4 — Severity Classifier:** Scores threat as `CRITICAL / HIGH / MEDIUM / LOW` with justification
- **Agent 5 — Remediation Agent:** Generates step-by-step fix plan referencing CVEs and OWASP playbooks

---

## Airflow CVE Pipeline

Nightly DAG that fetches new CVEs from the NVD API, generates embeddings, and upserts them into ChromaDB — keeping the agent knowledge base current.

---

## Getting Started

```bash
git clone https://github.com/Nosher007/cybersentinel.git
cd cybersentinel
cp cybersentinel/.env.example cybersentinel/.env
# Add your OPENAI_API_KEY and NVD_API_KEY

docker-compose -f cybersentinel/docker-compose.yml up
```

- Backend: `http://localhost:8000`
- Airflow UI: `http://localhost:8080`
- Frontend (dev): `http://localhost:3000`

---

## Project Status

| Phase | Status |
|---|---|
| Phase 1 — Foundation (FastAPI, models, WebSocket) | Complete |
| Phase 2 — Simulation Engine (5 scenarios, log generators) | In Progress |
| Phase 3 — LangGraph Agent Pipeline | In Progress |
| Phase 4 — Airflow CVE Pipeline | In Progress |
| Phase 5 — Full Backend Integration | Pending |
| Phase 6 — React Frontend | Pending |
| Phase 7 — Deployment (GCP + Firebase) | Pending |
