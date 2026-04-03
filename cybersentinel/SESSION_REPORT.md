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
