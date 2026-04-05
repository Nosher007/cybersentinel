# CyberSentinel — Session Report

> This file is updated at the end of every session where all tests are passing.
> Read this at the START of every new session to restore context.

---

## Session — 2026-04-03

### Tickets Completed
- TICKET-005: NovaPay context module — `Service`, `Department` Pydantic models, `get_service()` helper
- TICKET-006: All 5 log generators (auth, nginx, firewall, database, api) + transaction_logs generator
- TICKET-007: Account Takeover scenario — 4 phases, async generator, `speed_multiplier` support
- TICKET-008: Transaction Fraud scenario — probe ($1-$2) → large transfer ($48k) → API scraping
- TICKET-009: SQL Injection scenario — normal traffic → malformed queries → injection → table dump
- TICKET-010: Insider Threat scenario — off-hours admin login, logs look LEGITIMATE, pattern-based suspicion
- TICKET-011: DDoS Attack scenario — 400+ botnet IPs, traffic spike → 503 flood
- TICKET-012: Simulation engine runner — `SCENARIO_REGISTRY` dict, `asyncio.create_task()`, lazy queue
- TICKET-013: Wire simulation to WebSocket — `POST /attack`, `POST /stop`, log streaming to WS clients

### Tests Passing
- 222 / 222 passing
- `python -m pytest simulation/tests/ backend/tests/ --tb=short -q`

### Current Phase Status
- Phase 1 — Foundation: COMPLETE
- Phase 2 — Simulation Engine: COMPLETE
- Phase 3 — LangGraph Agents: NOT STARTED
- Phase 4 — Airflow CVE Pipeline: NOT STARTED
- Phase 5 — Full Backend Integration: NOT STARTED
- Phase 6 — Frontend: NOT STARTED (blocked on Phase 5)
- Phase 7 — Deployment: NOT STARTED

### Architecture Decisions Made
- All scenarios use `@dataclass` (not Pydantic) — internal simulation objects, no API boundary
- `SCENARIO_REGISTRY` dict maps scenario IDs to classes — O(1) lookup, open/closed principle
- Engine queue is lazy (`asyncio.Queue` created on `start()`) — avoids event loop binding issues in tests
- `asyncio.create_task()` runs scenarios as background tasks — non-blocking
- `broadcast_from_engine()` lifespan background task reads from queue and pushes to all WS clients

### GitHub
- Repo: https://github.com/Nosher007/cybersentinel
- Branch: main
- Last commit: [TICKET-013] Wire simulation to WebSocket

### Next Up — Phase 3: LangGraph Agents
- TICKET-014: ChromaDB setup — local instance, seed with 20 CVEs + 5 OWASP playbook entries
- TICKET-015: Agent 2 — Log Parser (raw log string → `ParsedLog` Pydantic model)
- TICKET-016: Agent 3 — Threat Detector (list of `ParsedLog` → `ThreatEvent`)
- TICKET-017: Agent 4 — Severity Classifier (`ThreatEvent` → `ScoredThreat` CRITICAL/HIGH/MED/LOW)
- TICKET-018: Agent 5 — Remediation Agent (`ScoredThreat` → `RemediationPlan`)
- TICKET-019: LangGraph Orchestrator — StateGraph wiring all agents, streaming callbacks
- TICKET-020: Agent 1 — Attack Prompt Interpreter (NLP → attack_type + scenario_id)

### Key Things to Know for Next Session
- Run `python -m pytest simulation/tests/ backend/tests/` from `cybersentinel/` to verify baseline
- `OPENAI_API_KEY` needed in `.env` before Phase 3 agents can run
- Phase 3 will require `langchain`, `langgraph`, `chromadb` — all in `requirements.txt`
- TDD rules still apply — write failing tests before any agent implementation
- Learning mode still active — interview questions before every new piece of code

---

## Session — 2026-04-04

### Tickets Completed
- TICKET-016: Threat Detector Agent — with_structured_output, RAG via ChromaDB, 10 TDD tests
- TICKET-017: Severity Classifier Agent — CRITICAL/HIGH/MED/LOW, 10 TDD tests
- TICKET-017B: Switch LLM from OpenAI to Gemini — ChatGoogleGenerativeAI, gemini-2.5-flash
- TICKET-018: Remediation Agent — immediate + hardening steps, RAG, 12 TDD tests
- TICKET-019: LangGraph Orchestrator — StateGraph, 4 agent nodes, error handling, 8 TDD tests
- TICKET-020: Attack Prompt Interpreter — NLP to scenario mapping, Literal enforcement, 11 TDD tests
- TEST-PHASE-3: Full pipeline smoke test passing with real Gemini API calls

### Tests Passing
- 300 / 300 passing
- `python -m pytest cybersentinel/backend/tests/ cybersentinel/simulation/tests/`

### Current Phase Status
- Phase 1 — Foundation: COMPLETE
- Phase 2 — Simulation Engine: COMPLETE
- Phase 3 — LangGraph Agents: COMPLETE
- Phase 4 — Airflow CVE Pipeline: NOT STARTED
- Phase 5 — Full Backend Integration: NOT STARTED
- Phase 6 — Frontend: NOT STARTED (blocked on Phase 5)
- Phase 7 — Deployment: NOT STARTED

### Architecture Decisions Made
- Switched LLM provider from OpenAI to Google Gemini (gemini-2.5-flash) — free API key available
- All agents use ChatGoogleGenerativeAI + with_structured_output — no free-form text between agents
- ChromaDB uses local default embeddings (not Gemini) — no re-seeding needed on LLM switch
- AttackPromptInterpreter uses Pydantic Literal types to enforce valid scenario IDs at schema level
- LangGraph StateGraph: 4 nodes (parse_logs, detect_threat, classify_severity, remediate) linear chain
- Each orchestrator node catches exceptions and sets state["error"] — no crash cascades
- GOOGLE_API_KEY stored in cybersentinel/.env (gitignored) — never committed to GitHub

### GitHub
- Repo: https://github.com/Nosher007/cybersentinel
- Branch: main
- Last commit: [TEST-PHASE-3] Smoke test passing — gemini-2.5-flash, full pipeline end-to-end verified

### Next Up — Phase 4: Airflow CVE Pipeline
- TICKET-021: Airflow setup in Docker — LocalExecutor, web UI accessible, hello world DAG runs
- TICKET-022: Task fetch_cves — hits NVD API, returns raw CVE JSON for last 24hrs
- TICKET-023: Task parse_and_clean — extracts CVE ID, description, severity, affected systems
- TICKET-024: Task embed_and_upsert — generates embeddings, upserts to ChromaDB
- TICKET-025: Task validate_ingestion — runs test query, confirms new CVEs are retrievable
- TICKET-026: Wire full DAG — all tasks connected, manual trigger works end-to-end

### Key Things to Know for Next Session
- Run `python -m pytest cybersentinel/backend/tests/ cybersentinel/simulation/tests/` to verify baseline
- GOOGLE_API_KEY is in cybersentinel/.env — already configured with Gemini key
- Phase 4 requires Docker — Airflow runs as a separate Docker service
- NVD_API_KEY needed in .env for the CVE fetcher task (free from nvd.nist.gov)
- TDD rules still apply — write failing tests before any implementation
- Learning mode still active — interview questions before every new piece of code

---

## Session — 2026-04-04 (Phase 4)

### Tickets Completed
- TICKET-021: Airflow DAG setup — cve_knowledge_updater, 5 tasks, PostgreSQL, Airflow 3.1.8, 16 TDD tests
- TICKET-022: fetch_cves task — NVD API, 24hr date range, apiKey header, 9 TDD tests
- TICKET-023: parse_and_clean task — CVE field extraction, CVSS fallbacks, text field for embedding, 15 TDD tests
- TICKET-024: embed_and_upsert task — ChromaDB upsert, idempotent, 11 TDD tests
- TICKET-025: validate_ingestion task — similarity query, raises on empty results, 6 TDD tests
- TICKET-026: Full DAG e2e wiring — fetch→parse→embed→upsert→validate, 4 integration tests

### Tests Passing
- 361 / 361 passing
- `python -m pytest cybersentinel/ --ignore=cybersentinel/frontend`

### Current Phase Status
- Phase 1 — Foundation: COMPLETE
- Phase 2 — Simulation Engine: COMPLETE
- Phase 3 — LangGraph Agents: COMPLETE
- Phase 4 — Airflow CVE Pipeline: COMPLETE
- Phase 5 — Full Backend Integration: NOT STARTED
- Phase 6 — Frontend: NOT STARTED (blocked on Phase 5)
- Phase 7 — Deployment: NOT STARTED

### Architecture Decisions Made
- Airflow 3.1.8 used (2.x not available on PyPI for Python 3.13)
- PostgreSQL replaces SQLite for Airflow metadata DB (LocalExecutor parallel tasks need it)
- XCom passes parsed CVE lists between tasks — acceptable size for daily CVE volume
- ChromaDB handles its own embeddings — no separate embedding call needed in embed task
- validate_ingestion uses similarity query (not count/get) — validates the actual RAG search path

### GitHub
- Repo: https://github.com/Nosher007/cybersentinel
- Branch: main
- Last commit: [TICKET-026] Full DAG e2e wiring

### Next Up — Phase 5: Full Backend Integration
- TICKET-027: Connect full pipeline — POST /attack → Prompt Interpreter → Simulation Engine → Agent Pipeline → WS stream
- TICKET-028: Error handling — agent failures, WS disconnects, invalid prompts
- TICKET-029: GET /threats endpoint — returns history of detected threats in session

### Key Things to Know for Next Session
- Run `python -m pytest cybersentinel/` to verify 361 baseline
- All API keys in cybersentinel/.env (GOOGLE_API_KEY, NVD_API_KEY)
- Phase 5 wires everything together — read attack.py, websocket.py, orchestrator.py before starting
- TDD rules still apply — write failing tests before any implementation
- Learning mode still active — interview questions before every new piece of code

---

## Session — 2026-04-04 (Phase 5)

### Tickets Completed
- TICKET-027: Connect full pipeline — prompt→interpreter→simulation→agents→WS, run_in_executor, 10 TDD tests
- TICKET-028: Error handling — interpreter 500, pipeline error broadcast, WS resilience, 13 TDD tests
- TICKET-029: GET /threats endpoint — in-memory threat_store, appends on detection, 11 TDD tests

### Tests Passing
- 393 / 393 passing
- `python -m pytest cybersentinel/`

### Current Phase Status
- Phase 1 — Foundation: COMPLETE
- Phase 2 — Simulation Engine: COMPLETE
- Phase 3 — LangGraph Agents: COMPLETE
- Phase 4 — Airflow CVE Pipeline: COMPLETE
- Phase 5 — Full Backend Integration: COMPLETE
- Phase 6 — Frontend: NOT STARTED
- Phase 7 — Deployment: NOT STARTED

### Architecture Decisions Made
- POST /attack now accepts `prompt` (natural language) not `scenario_id` — interpreter maps it
- `run_in_executor` used for sync interpreter + agent calls to keep event loop free
- `_run_agent_pipeline` catches all exceptions and returns `{"error": ...}` — never crashes WS
- `threat_store` is module-level list in `threats.py` — in-memory, resets on restart
- WS broadcasts: `log`, `status`, `threat_detected`, `remediation_plan`, `pipeline_error`

### GitHub
- Repo: https://github.com/Nosher007/cybersentinel
- Branch: main
- Last commit: [TICKET-029] GET /threats endpoint

### Next Up — Phase 6: Frontend
- TICKET-030: React + Vite + Tailwind setup, connects to backend
- TICKET-031: useWebSocket hook
- TICKET-032: NovaPay company dashboard (live metrics, health bars)
- TICKET-033: Department health map (5 departments, HEALTHY→BREACHED)
- TICKET-034: Attack prompt input (text field → POST /attack)
- TICKET-035: CyberSentinel alert window (calm/green base state)
- TICKET-036: Log terminal (real-time streaming logs, color coded)
- TICKET-037: Threat card (severity badge, attack type, evidence)
- TICKET-038: Remediation panel (AI steps populate one by one)
- TICKET-039: Attack animation (departments react visually on attack)
- TICKET-040: Full UI integration test

### Key Things to Know for Next Session
- Run `python -m pytest cybersentinel/` to verify 393 baseline before touching anything
- All API keys in cybersentinel/.env (GOOGLE_API_KEY, NVD_API_KEY)
- Frontend lives in cybersentinel/frontend/ — use Vite + React 18 + TailwindCSS
- Backend must be running on port 8000 for frontend dev server to connect
- WS message types to handle: log, status, threat_detected, remediation_plan, pipeline_error
- Learning mode still active — interview questions before every new piece of code

---

## Session — 2026-04-04 (Phase 6)

### Tickets Completed
- TICKET-030: React + Vite + Tailwind v4 setup — `@tailwindcss/vite` plugin, Vite proxy to backend port 8000
- TICKET-031: useWebSocket hook — logs, threat, remediation, metrics, attackInfo state; clearState on stop
- TICKET-032: NovaPay CompanyDashboard — idle drift via setInterval, backend-driven metrics during attack
- TICKET-033: Department health map — 5 departments, HEALTHY/WARNING/CRITICAL/BREACHED with animated dots
- TICKET-034: Attack prompt input — gradient border, example chips, "Launch Attack"/"Stop Attack" toggle
- TICKET-035: CyberSentinel AlertWindow — CSS radar sweep idle animation, scrollable body
- TICKET-036: LogTerminal — real-time streaming, auto-scroll via useRef, color-coded by tag type
- TICKET-037: ThreatCard — severity badge, slide-in opacity/translate animation
- TICKET-038: RemediationPanel — step reveal with checkmark animation (✓ after 450ms)
- TICKET-039: Attack animation — phase_metrics.py maps log tags → metric snapshots, broadcast as metric_update WS message
- TICKET-040: Full UI integration — asymmetric grid (1/3 NovaPay + 2/3 AlertWindow), NarrationBox, AttackStatusBanner, Inter font

### Tests Passing
- 125 / 125 backend tests passing (frontend has no unit tests — verified by manual smoke test)
- `python -m pytest cybersentinel/backend/tests/ cybersentinel/simulation/tests/`

### Current Phase Status
- Phase 1 — Foundation: COMPLETE
- Phase 2 — Simulation Engine: COMPLETE
- Phase 3 — LangGraph Agents: COMPLETE
- Phase 4 — Airflow CVE Pipeline: COMPLETE
- Phase 5 — Full Backend Integration: COMPLETE
- Phase 6 — Frontend: COMPLETE
- Phase 7 — Deployment: NOT STARTED

### Architecture Decisions Made
- Metrics moved to backend — `phase_metrics.py` maps actual log tags (uppercase) to metric snapshots; WS broadcasts `metric_update` on each log
- `re.search` (not `re.match`) used to find `[TAG]` anywhere in log line — required for timestamped logs
- Regex `[A-Z0-9_-]` includes hyphen to match `API-GW` tag
- Rule-based NarrationBox (zero API cost) — `narratorEngine.js` maps log tags to plain English; uses LLM's own `justification` post-analysis
- ChromaDB will be baked into Docker image at build time for deployment (Option A) — pre-seeded at `docker build`, no persistent store needed for portfolio
- `null` return from `getNarrationFromLog` means known tag with no narration — don't overwrite existing message; `undefined` means unknown tag

### Manual Smoke Tests Passing
- DDoS: 9,100 tx/s, 95 users, 6,400ms latency, 91.4% uptime — botnet narration, banner timer, department escalation
- Insider Threat: 4 tx/s, 14 users, AUTH/DB/COMPLIANCE tags, off-hours narration — subtle metrics vs DDoS confirmed

### GitHub
- Repo: https://github.com/Nosher007/cybersentinel
- Branch: main

### Next Up — Phase 7: Deployment
- TICKET-041: Dockerfile for FastAPI backend (ChromaDB baked in at build time)
- TICKET-042: Docker Compose — backend + ChromaDB as single service
- TICKET-043: GitHub Actions CI — pytest on push to main, auto-deploy on green
- TICKET-044: Google Cloud Run — deploy backend container, WebSocket support
- TICKET-045: Firebase Hosting — deploy React build

### Key Things to Know for Next Session
- Frontend: `cd cybersentinel/frontend && npm run dev` (port 3000)
- Backend: `cd cybersentinel && uvicorn backend.main:app --reload` (port 8000)
- ChromaDB baked into Docker image at build time — `seed_knowledge_base.py` runs during `docker build`
- Cloud Run for backend (WebSocket support, same Google ecosystem as Gemini, free tier)
- Firebase Hosting for frontend (one-command deploy, free tier)
- GitHub Actions auto-deploys on push to main — pytest must pass first

---

## Session — 2026-04-05 (Phase 7)

### Tickets Completed
- TICKET-041: Dockerfile — 3-stage build (deps → seeded → final), ChromaDB baked in at build time
- TICKET-042: Docker Compose — backend only, Airflow commented out, ChromaDB no longer separate service
- TICKET-043: GitHub Actions CI/CD — pytest on PR, auto-deploy backend + frontend on push to main
- TICKET-044: Cloud Run setup — Artifact Registry, service account, IAM roles, GCP project cybersentinel-prod
- TICKET-045: Firebase Hosting — firebase init, firebase.json, FIREBASE_SERVICE_ACCOUNT secret

### Tests Passing
- 332 / 332 passing (11 TestInit tests fixed with fallback API key in CI)

### Current Phase Status
- Phase 1 — Foundation: COMPLETE
- Phase 2 — Simulation Engine: COMPLETE
- Phase 3 — LangGraph Agents: COMPLETE
- Phase 4 — Airflow CVE Pipeline: COMPLETE
- Phase 5 — Full Backend Integration: COMPLETE
- Phase 6 — Frontend: COMPLETE
- Phase 7 — Deployment: COMPLETE

### Live URLs
- Frontend: https://cybersentinel-prod.web.app
- Backend: https://cybersentinel-backend-5803836062.us-central1.run.app
- Health check: https://cybersentinel-backend-5803836062.us-central1.run.app/health

### Architecture Decisions Made
- ChromaDB baked into Docker image (Option A) — seed runs at build time, no persistent store needed
- CORS fix: `ALLOWED_ORIGINS` set via `gcloud run services update` with `^@^` delimiter escape
- CI uses `GOOGLE_API_KEY || 'test_api_key_ci'` fallback — allows TestInit tests to pass without real key
- `VITE_BACKEND_URL` injected at frontend build time via GitHub variable `BACKEND_URL`
- WebSocket URL derived from `VITE_BACKEND_URL` via `.replace(/^http/, 'ws') + '/ws'`

### GitHub
- Repo: https://github.com/Nosher007/cybersentinel
- Branch: main

### Project Complete
All 7 phases done. Full game loop works in production.

---

## Session — 2026-04-05 (Post-deployment hardening)

### Work Completed
- Welcome modal — fade-in popup on page load summarising the project (dismiss on button or backdrop click)
- Simulation disclaimer banner — amber strip below header clarifying this is an educational AI demo
- Detection timeline — ThreatCard now shows elapsed seconds from attack start → AI detected
- Rate limiting bug fix — `attack.py` had its own always-on `Limiter` instance; now reads `ENVIRONMENT` to disable in test (was causing 429s mid-test suite in CI)
- Error leakage fix — raw exception detail no longer returned to client on 500; generic message returned, exception logged server-side
- Swagger/OpenAPI disabled in production — `/docs` and `/openapi.json` hidden when `ENVIRONMENT=production`
- API key validation — all 5 agents now raise `ValueError` at init if `GOOGLE_API_KEY` is missing (replaces silent `"placeholder"` default)

### Tests Passing
- 332 / 332 passing
- CI: all 3 jobs green (Backend Tests ✓, Deploy Backend ✓, Deploy Frontend ✓)
- Run ID: 24006502154

### Current Phase Status
- Phase 1 — Foundation: COMPLETE
- Phase 2 — Simulation Engine: COMPLETE
- Phase 3 — LangGraph Agents: COMPLETE
- Phase 4 — Airflow CVE Pipeline: COMPLETE
- Phase 5 — Full Backend Integration: COMPLETE
- Phase 6 — Frontend: COMPLETE
- Phase 7 — Deployment: COMPLETE

### Live URLs
- Frontend: https://cybersentinel-prod.web.app
- Backend: https://cybersentinel-backend-5803836062.us-central1.run.app
- Health check: https://cybersentinel-backend-5803836062.us-central1.run.app/health

### Key Things to Know for Next Session
- All 7 phases complete — project is in production
- CI auto-deploys on every push to main (tests must pass first)
- `ENVIRONMENT=test` in CI disables rate limiting — both `main.py` and `attack.py` read this
- Swagger docs only visible locally/dev; hidden in production
- Node.js 20 deprecation warnings in CI are non-breaking (deadline June 2026 — update actions versions then)
