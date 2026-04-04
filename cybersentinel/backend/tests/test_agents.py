"""
TICKET-015 — TDD tests for Log Parser Agent.
Red phase: written before implementation exists.
Agent takes a raw log string and returns a ParsedLog Pydantic model.

NOTE: These tests use mocked LLM responses — no real API calls.
Real LLM integration is tested in TEST-PHASE-3 smoke test.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from backend.models.logs import ParsedLog, LogType
from backend.agents.log_parser import LogParserAgent

AUTH_LOG = "2026-04-03 02:47:13 [AUTH] INFO user=admin_john ip=192.168.1.5 event=login status=success session_id=abc12345"
NGINX_LOG = '2026-04-03 10:22:01 [NGINX] 203.45.12.8 - "GET /api/v1/balance HTTP/1.1" 200 1024B 45ms "Mozilla/5.0"'
FIREWALL_LOG = "2026-04-03 10:22:05 [FIREWALL] DENY TCP src=198.51.100.42:54321 dst=10.0.0.1:22 bytes=128"
DATABASE_LOG = "2026-04-03 02:51:44 [DB] INFO user=admin_john query=SELECT * FROM users rows=3400 duration=820ms status=success"
API_LOG = "2026-04-03 10:22:10 [API-GW] GET /api/v1/transfer status=429 ip=45.33.32.156 latency=12ms request_id=req_abc1"


def _make_parsed_log(raw: str, log_type: LogType, **kwargs) -> ParsedLog:
    return ParsedLog(
        raw=raw,
        log_type=log_type,
        timestamp=datetime(2026, 4, 3, 10, 22, 1),
        **kwargs
    )


class TestLogParserAgentInit:

    def test_agent_instantiates(self):
        agent = LogParserAgent()
        assert agent is not None

    def test_agent_has_parse_method(self):
        assert hasattr(LogParserAgent(), "parse")

    def test_agent_has_parse_batch_method(self):
        assert hasattr(LogParserAgent(), "parse_batch")


class TestLogParserAgentParse:

    @patch("backend.agents.log_parser.ChatGoogleGenerativeAI")
    def test_parse_returns_parsed_log(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_parsed_log(AUTH_LOG, LogType.AUTH, user="admin_john", source_ip="192.168.1.5")
        mock_llm.with_structured_output.return_value = mock_chain
        agent = LogParserAgent()
        result = agent.parse(AUTH_LOG, log_type=LogType.AUTH)
        assert isinstance(result, ParsedLog)

    @patch("backend.agents.log_parser.ChatGoogleGenerativeAI")
    def test_parse_preserves_raw_log(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_parsed_log(AUTH_LOG, LogType.AUTH)
        mock_llm.with_structured_output.return_value = mock_chain
        agent = LogParserAgent()
        result = agent.parse(AUTH_LOG, log_type=LogType.AUTH)
        assert result.raw == AUTH_LOG

    @patch("backend.agents.log_parser.ChatGoogleGenerativeAI")
    def test_parse_sets_correct_log_type(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_parsed_log(FIREWALL_LOG, LogType.FIREWALL)
        mock_llm.with_structured_output.return_value = mock_chain
        agent = LogParserAgent()
        result = agent.parse(FIREWALL_LOG, log_type=LogType.FIREWALL)
        assert result.log_type == LogType.FIREWALL

    @patch("backend.agents.log_parser.ChatGoogleGenerativeAI")
    def test_parse_empty_log_raises(self, mock_llm_class):
        agent = LogParserAgent()
        with pytest.raises(ValueError):
            agent.parse("", log_type=LogType.AUTH)

    @patch("backend.agents.log_parser.ChatGoogleGenerativeAI")
    def test_parse_whitespace_only_raises(self, mock_llm_class):
        agent = LogParserAgent()
        with pytest.raises(ValueError):
            agent.parse("   ", log_type=LogType.AUTH)

    @patch("backend.agents.log_parser.ChatGoogleGenerativeAI")
    def test_parse_uses_with_structured_output(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_parsed_log(AUTH_LOG, LogType.AUTH)
        mock_llm.with_structured_output.return_value = mock_chain
        agent = LogParserAgent()
        agent.parse(AUTH_LOG, log_type=LogType.AUTH)
        mock_llm.with_structured_output.assert_called_once_with(ParsedLog)

    @patch("backend.agents.log_parser.ChatGoogleGenerativeAI")
    def test_parse_all_five_log_types(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        test_cases = [
            (AUTH_LOG, LogType.AUTH),
            (NGINX_LOG, LogType.NGINX),
            (FIREWALL_LOG, LogType.FIREWALL),
            (DATABASE_LOG, LogType.DATABASE),
            (API_LOG, LogType.API),
        ]
        for raw_log, log_type in test_cases:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = _make_parsed_log(raw_log, log_type)
            mock_llm.with_structured_output.return_value = mock_chain
            agent = LogParserAgent()
            result = agent.parse(raw_log, log_type=log_type)
            assert isinstance(result, ParsedLog)
            assert result.log_type == log_type


class TestLogParserAgentBatch:

    @patch("backend.agents.log_parser.ChatGoogleGenerativeAI")
    def test_parse_batch_returns_list(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_parsed_log(AUTH_LOG, LogType.AUTH)
        mock_llm.with_structured_output.return_value = mock_chain
        agent = LogParserAgent()
        results = agent.parse_batch([(AUTH_LOG, LogType.AUTH), (DATABASE_LOG, LogType.DATABASE)])
        assert isinstance(results, list)
        assert len(results) == 2

    @patch("backend.agents.log_parser.ChatGoogleGenerativeAI")
    def test_parse_batch_all_results_are_parsed_logs(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_parsed_log(AUTH_LOG, LogType.AUTH)
        mock_llm.with_structured_output.return_value = mock_chain
        agent = LogParserAgent()
        results = agent.parse_batch([(AUTH_LOG, LogType.AUTH), (NGINX_LOG, LogType.NGINX)])
        for result in results:
            assert isinstance(result, ParsedLog)

    @patch("backend.agents.log_parser.ChatGoogleGenerativeAI")
    def test_parse_batch_empty_list_returns_empty(self, mock_llm_class):
        agent = LogParserAgent()
        assert agent.parse_batch([]) == []


# ═══════════════════════════════════════════════════════════════════════════════
# TICKET-016 — Threat Detector Agent Tests
# ═══════════════════════════════════════════════════════════════════════════════

from backend.models.threats import ThreatEvent, AttackType
from backend.agents.threat_detector import ThreatDetectorAgent
import uuid


def _make_brute_force_logs() -> list:
    logs = []
    for i in range(10):
        logs.append(_make_parsed_log(
            f"2026-04-03 10:0{i}:00 [AUTH] WARN user=victim ip=45.33.32.156 event=login status=failed attempt={i+1}",
            LogType.AUTH,
            user="victim",
            source_ip="45.33.32.156",
            action="login",
        ))
    return logs


def _make_threat_event(attack_type: AttackType = AttackType.BRUTE_FORCE) -> ThreatEvent:
    return ThreatEvent(
        threat_id=str(uuid.uuid4()),
        attack_type=attack_type,
        affected_service="auth",
        evidence_logs=_make_brute_force_logs()[:3],
        description="Multiple failed login attempts detected from single IP",
    )


class TestThreatDetectorAgentInit:

    def test_agent_instantiates(self):
        assert ThreatDetectorAgent() is not None

    def test_agent_has_detect_method(self):
        assert hasattr(ThreatDetectorAgent(), "detect")


class TestThreatDetectorAgentDetect:

    @patch("backend.agents.threat_detector.ChatGoogleGenerativeAI")
    def test_detect_returns_threat_event(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_threat_event()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = ThreatDetectorAgent()
        result = agent.detect(_make_brute_force_logs())
        assert isinstance(result, ThreatEvent)

    @patch("backend.agents.threat_detector.ChatGoogleGenerativeAI")
    def test_detect_uses_with_structured_output(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_threat_event()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = ThreatDetectorAgent()
        agent.detect(_make_brute_force_logs())
        mock_llm.with_structured_output.assert_called_once_with(ThreatEvent)

    @patch("backend.agents.threat_detector.ChatGoogleGenerativeAI")
    def test_detect_empty_logs_raises(self, mock_llm_class):
        agent = ThreatDetectorAgent()
        with pytest.raises(ValueError):
            agent.detect([])

    @patch("backend.agents.threat_detector.ChatGoogleGenerativeAI")
    def test_detect_result_has_evidence_logs(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_threat_event()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = ThreatDetectorAgent()
        result = agent.detect(_make_brute_force_logs())
        assert len(result.evidence_logs) > 0

    @patch("backend.agents.threat_detector.ChatGoogleGenerativeAI")
    def test_detect_result_has_attack_type(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_threat_event(AttackType.BRUTE_FORCE)
        mock_llm.with_structured_output.return_value = mock_chain

        agent = ThreatDetectorAgent()
        result = agent.detect(_make_brute_force_logs())
        assert result.attack_type in list(AttackType)

    @patch("backend.agents.threat_detector.ChatGoogleGenerativeAI")
    def test_detect_result_has_affected_service(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_threat_event()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = ThreatDetectorAgent()
        result = agent.detect(_make_brute_force_logs())
        assert result.affected_service

    @patch("backend.agents.threat_detector.ChatGoogleGenerativeAI")
    def test_detect_queries_chromadb_for_context(self, mock_llm_class):
        """Threat detector must query ChromaDB — RAG enrichment."""
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_threat_event()
        mock_llm.with_structured_output.return_value = mock_chain

        with patch("backend.agents.threat_detector.get_collection") as mock_col:
            mock_col.return_value.query.return_value = {
                "documents": [["CVE-2021-44228 brute force auth"]],
                "ids": [["CVE-2021-44228"]],
            }
            agent = ThreatDetectorAgent()
            agent.detect(_make_brute_force_logs())
            mock_col.return_value.query.assert_called_once()

    @patch("backend.agents.threat_detector.ChatGoogleGenerativeAI")
    def test_detect_non_parsed_log_list_raises(self, mock_llm_class):
        agent = ThreatDetectorAgent()
        with pytest.raises((ValueError, AttributeError, TypeError)):
            agent.detect(["not a parsed log", "also not"])


# ═══════════════════════════════════════════════════════════════════════════════
# TICKET-017 — Severity Classifier Agent Tests
# ═══════════════════════════════════════════════════════════════════════════════

from backend.models.threats import ScoredThreat, Severity
from backend.agents.severity_classifier import SeverityClassifierAgent


def _make_scored_threat(severity: Severity = Severity.CRITICAL) -> ScoredThreat:
    return ScoredThreat(
        threat=_make_threat_event(),
        severity=severity,
        score=9.5,
        justification="Multiple failed logins from single IP indicating brute force",
        blast_radius=["auth", "transaction_engine"],
    )


class TestSeverityClassifierAgentInit:

    def test_agent_instantiates(self):
        assert SeverityClassifierAgent() is not None

    def test_agent_has_classify_method(self):
        assert hasattr(SeverityClassifierAgent(), "classify")


class TestSeverityClassifierAgentClassify:

    @patch("backend.agents.severity_classifier.ChatGoogleGenerativeAI")
    def test_classify_returns_scored_threat(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_scored_threat()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = SeverityClassifierAgent()
        result = agent.classify(_make_threat_event())
        assert isinstance(result, ScoredThreat)

    @patch("backend.agents.severity_classifier.ChatGoogleGenerativeAI")
    def test_classify_uses_with_structured_output(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_scored_threat()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = SeverityClassifierAgent()
        agent.classify(_make_threat_event())
        mock_llm.with_structured_output.assert_called_once_with(ScoredThreat)

    @patch("backend.agents.severity_classifier.ChatGoogleGenerativeAI")
    def test_classify_severity_is_valid_enum(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_scored_threat(Severity.HIGH)
        mock_llm.with_structured_output.return_value = mock_chain

        agent = SeverityClassifierAgent()
        result = agent.classify(_make_threat_event())
        assert result.severity in list(Severity)

    @patch("backend.agents.severity_classifier.ChatGoogleGenerativeAI")
    def test_classify_score_in_valid_range(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_scored_threat()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = SeverityClassifierAgent()
        result = agent.classify(_make_threat_event())
        assert 0.0 <= result.score <= 10.0

    @patch("backend.agents.severity_classifier.ChatGoogleGenerativeAI")
    def test_classify_has_justification(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_scored_threat()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = SeverityClassifierAgent()
        result = agent.classify(_make_threat_event())
        assert result.justification and len(result.justification) > 0

    @patch("backend.agents.severity_classifier.ChatGoogleGenerativeAI")
    def test_classify_preserves_original_threat(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        threat = _make_threat_event()
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_scored_threat()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = SeverityClassifierAgent()
        result = agent.classify(threat)
        assert isinstance(result.threat, ThreatEvent)

    @patch("backend.agents.severity_classifier.ChatGoogleGenerativeAI")
    def test_classify_none_raises(self, mock_llm_class):
        agent = SeverityClassifierAgent()
        with pytest.raises((ValueError, AttributeError, TypeError)):
            agent.classify(None)

    @patch("backend.agents.severity_classifier.ChatGoogleGenerativeAI")
    def test_classify_all_severities_accepted(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm

        for severity in Severity:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = _make_scored_threat(severity)
            mock_llm.with_structured_output.return_value = mock_chain

            agent = SeverityClassifierAgent()
            result = agent.classify(_make_threat_event())
            assert result.severity == severity


# ═══════════════════════════════════════════════════════════════════════════════
# TICKET-018 — Remediation Agent Tests
# ═══════════════════════════════════════════════════════════════════════════════

from backend.models.remediation import RemediationPlan, RemediationStep
from backend.agents.remediation import RemediationAgent


def _make_remediation_step(order: int = 1, immediate: bool = True) -> RemediationStep:
    return RemediationStep(
        order=order,
        action="Block source IP at firewall",
        detail="Add rule to block 45.33.32.156 on all inbound ports via iptables",
        is_immediate=immediate,
    )


def _make_remediation_plan() -> RemediationPlan:
    import uuid
    return RemediationPlan(
        plan_id=str(uuid.uuid4()),
        threat=_make_scored_threat(),
        immediate_steps=[_make_remediation_step(1, True), _make_remediation_step(2, True)],
        hardening_steps=[_make_remediation_step(3, False)],
        cve_references=["CVE-2021-44228", "OWASP-A07"],
        summary="Brute force attack detected on auth service. Block IP, reset credentials, enable MFA.",
    )


class TestRemediationAgentInit:

    def test_agent_instantiates(self):
        assert RemediationAgent() is not None

    def test_agent_has_remediate_method(self):
        assert hasattr(RemediationAgent(), "remediate")


class TestRemediationAgentRemediate:

    @patch("backend.agents.remediation.ChatGoogleGenerativeAI")
    def test_remediate_returns_remediation_plan(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_remediation_plan()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = RemediationAgent()
        result = agent.remediate(_make_scored_threat())
        assert isinstance(result, RemediationPlan)

    @patch("backend.agents.remediation.ChatGoogleGenerativeAI")
    def test_remediate_uses_with_structured_output(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_remediation_plan()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = RemediationAgent()
        agent.remediate(_make_scored_threat())
        mock_llm.with_structured_output.assert_called_once_with(RemediationPlan)

    @patch("backend.agents.remediation.ChatGoogleGenerativeAI")
    def test_remediate_has_immediate_steps(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_remediation_plan()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = RemediationAgent()
        result = agent.remediate(_make_scored_threat())
        assert len(result.immediate_steps) > 0

    @patch("backend.agents.remediation.ChatGoogleGenerativeAI")
    def test_remediate_has_hardening_steps(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_remediation_plan()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = RemediationAgent()
        result = agent.remediate(_make_scored_threat())
        assert len(result.hardening_steps) > 0

    @patch("backend.agents.remediation.ChatGoogleGenerativeAI")
    def test_remediate_has_cve_references(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_remediation_plan()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = RemediationAgent()
        result = agent.remediate(_make_scored_threat())
        assert isinstance(result.cve_references, list)

    @patch("backend.agents.remediation.ChatGoogleGenerativeAI")
    def test_remediate_has_summary(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_remediation_plan()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = RemediationAgent()
        result = agent.remediate(_make_scored_threat())
        assert result.summary and len(result.summary) > 0

    @patch("backend.agents.remediation.ChatGoogleGenerativeAI")
    def test_remediate_preserves_scored_threat(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_remediation_plan()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = RemediationAgent()
        result = agent.remediate(_make_scored_threat())
        assert isinstance(result.threat, ScoredThreat)

    @patch("backend.agents.remediation.ChatGoogleGenerativeAI")
    def test_remediate_queries_chromadb(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_remediation_plan()
        mock_llm.with_structured_output.return_value = mock_chain

        with patch("backend.agents.remediation.get_collection") as mock_col:
            mock_col.return_value.query.return_value = {
                "documents": [["CVE-2021-44228 brute force remediation steps"]],
                "ids": [["CVE-2021-44228"]],
            }
            agent = RemediationAgent()
            agent.remediate(_make_scored_threat())
            mock_col.return_value.query.assert_called_once()

    @patch("backend.agents.remediation.ChatGoogleGenerativeAI")
    def test_remediate_none_raises(self, mock_llm_class):
        agent = RemediationAgent()
        with pytest.raises((ValueError, AttributeError, TypeError)):
            agent.remediate(None)

    @patch("backend.agents.remediation.ChatGoogleGenerativeAI")
    def test_immediate_steps_are_remediation_step_instances(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_remediation_plan()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = RemediationAgent()
        result = agent.remediate(_make_scored_threat())
        assert all(isinstance(s, RemediationStep) for s in result.immediate_steps)


# ═══════════════════════════════════════════════════════════════════════════════
# TICKET-019 — LangGraph Orchestrator Tests
# ═══════════════════════════════════════════════════════════════════════════════

from backend.agents.orchestrator import build_pipeline, AgentState


class TestOrchestratorBuild:

    def test_build_pipeline_returns_compiled_graph(self):
        graph = build_pipeline()
        assert graph is not None

    def test_agent_state_has_required_keys(self):
        state = AgentState(
            raw_logs=[],
            parsed_logs=None,
            threat_event=None,
            scored_threat=None,
            remediation_plan=None,
            error=None,
        )
        assert "raw_logs" in state
        assert "parsed_logs" in state
        assert "threat_event" in state
        assert "scored_threat" in state
        assert "remediation_plan" in state

    def test_build_pipeline_is_callable(self):
        graph = build_pipeline()
        assert callable(graph.invoke)


class TestOrchestratorRun:

    @patch("backend.agents.orchestrator.LogParserAgent")
    @patch("backend.agents.orchestrator.ThreatDetectorAgent")
    @patch("backend.agents.orchestrator.SeverityClassifierAgent")
    @patch("backend.agents.orchestrator.RemediationAgent")
    def test_pipeline_runs_end_to_end(
        self, mock_rem, mock_sev, mock_threat, mock_parser
    ):
        mock_parser.return_value.parse_batch.return_value = _make_brute_force_logs()
        mock_threat.return_value.detect.return_value = _make_threat_event()
        mock_sev.return_value.classify.return_value = _make_scored_threat()
        mock_rem.return_value.remediate.return_value = _make_remediation_plan()

        graph = build_pipeline()
        raw = [("log line 1", "auth"), ("log line 2", "auth")]
        result = graph.invoke({"raw_logs": raw})

        assert result["remediation_plan"] is not None
        assert isinstance(result["remediation_plan"], RemediationPlan)

    @patch("backend.agents.orchestrator.LogParserAgent")
    @patch("backend.agents.orchestrator.ThreatDetectorAgent")
    @patch("backend.agents.orchestrator.SeverityClassifierAgent")
    @patch("backend.agents.orchestrator.RemediationAgent")
    def test_pipeline_all_agents_called(
        self, mock_rem, mock_sev, mock_threat, mock_parser
    ):
        mock_parser.return_value.parse_batch.return_value = _make_brute_force_logs()
        mock_threat.return_value.detect.return_value = _make_threat_event()
        mock_sev.return_value.classify.return_value = _make_scored_threat()
        mock_rem.return_value.remediate.return_value = _make_remediation_plan()

        graph = build_pipeline()
        graph.invoke({"raw_logs": [("log line", "auth")]})

        mock_parser.return_value.parse_batch.assert_called_once()
        mock_threat.return_value.detect.assert_called_once()
        mock_sev.return_value.classify.assert_called_once()
        mock_rem.return_value.remediate.assert_called_once()

    @patch("backend.agents.orchestrator.LogParserAgent")
    @patch("backend.agents.orchestrator.ThreatDetectorAgent")
    @patch("backend.agents.orchestrator.SeverityClassifierAgent")
    @patch("backend.agents.orchestrator.RemediationAgent")
    def test_pipeline_produces_scored_threat(
        self, mock_rem, mock_sev, mock_threat, mock_parser
    ):
        mock_parser.return_value.parse_batch.return_value = _make_brute_force_logs()
        mock_threat.return_value.detect.return_value = _make_threat_event()
        mock_sev.return_value.classify.return_value = _make_scored_threat()
        mock_rem.return_value.remediate.return_value = _make_remediation_plan()

        graph = build_pipeline()
        result = graph.invoke({"raw_logs": [("log line", "auth")]})

        assert isinstance(result["scored_threat"], ScoredThreat)

    @patch("backend.agents.orchestrator.LogParserAgent")
    @patch("backend.agents.orchestrator.ThreatDetectorAgent")
    @patch("backend.agents.orchestrator.SeverityClassifierAgent")
    @patch("backend.agents.orchestrator.RemediationAgent")
    def test_pipeline_parser_failure_sets_error(
        self, mock_rem, mock_sev, mock_threat, mock_parser
    ):
        mock_parser.return_value.parse_batch.side_effect = Exception("parse failed")

        graph = build_pipeline()
        result = graph.invoke({"raw_logs": [("bad log", "auth")]})

        assert result.get("error") is not None

    @patch("backend.agents.orchestrator.LogParserAgent")
    @patch("backend.agents.orchestrator.ThreatDetectorAgent")
    @patch("backend.agents.orchestrator.SeverityClassifierAgent")
    @patch("backend.agents.orchestrator.RemediationAgent")
    def test_pipeline_empty_logs_sets_error(
        self, mock_rem, mock_sev, mock_threat, mock_parser
    ):
        graph = build_pipeline()
        result = graph.invoke({"raw_logs": []})

        assert result.get("error") is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TICKET-020 — Attack Prompt Interpreter Tests
# ═══════════════════════════════════════════════════════════════════════════════

from backend.agents.prompt_interpreter import AttackPromptInterpreter, InterpretedAttack
from backend.models.threats import AttackType


VALID_SCENARIO_IDS = {
    "account_takeover",
    "transaction_fraud",
    "sql_injection",
    "insider_threat",
    "ddos_attack",
}


def _make_interpreted_attack(
    scenario_id: str = "account_takeover",
    attack_type: AttackType = AttackType.BRUTE_FORCE,
) -> InterpretedAttack:
    return InterpretedAttack(
        attack_type=attack_type,
        target_service="auth",
        intensity="high",
        scenario_id=scenario_id,
        reasoning="Multiple failed login attempts suggest brute force on auth service",
    )


class TestAttackPromptInterpreterInit:

    def test_agent_instantiates(self):
        assert AttackPromptInterpreter() is not None

    def test_agent_has_interpret_method(self):
        assert hasattr(AttackPromptInterpreter(), "interpret")


class TestAttackPromptInterpreterInterpret:

    @patch("backend.agents.prompt_interpreter.ChatGoogleGenerativeAI")
    def test_interpret_returns_interpreted_attack(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_interpreted_attack()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = AttackPromptInterpreter()
        result = agent.interpret("try to brute force the login")
        assert isinstance(result, InterpretedAttack)

    @patch("backend.agents.prompt_interpreter.ChatGoogleGenerativeAI")
    def test_interpret_uses_with_structured_output(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_interpreted_attack()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = AttackPromptInterpreter()
        agent.interpret("flood the payment server")
        mock_llm.with_structured_output.assert_called_once_with(InterpretedAttack)

    @patch("backend.agents.prompt_interpreter.ChatGoogleGenerativeAI")
    def test_interpret_scenario_id_is_valid(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_interpreted_attack("ddos_attack")
        mock_llm.with_structured_output.return_value = mock_chain

        agent = AttackPromptInterpreter()
        result = agent.interpret("flood the server with traffic")
        assert result.scenario_id in VALID_SCENARIO_IDS

    @patch("backend.agents.prompt_interpreter.ChatGoogleGenerativeAI")
    def test_interpret_has_target_service(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_interpreted_attack()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = AttackPromptInterpreter()
        result = agent.interpret("hack the login system")
        assert result.target_service and len(result.target_service) > 0

    @patch("backend.agents.prompt_interpreter.ChatGoogleGenerativeAI")
    def test_interpret_has_intensity(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_interpreted_attack()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = AttackPromptInterpreter()
        result = agent.interpret("gently probe the API")
        assert result.intensity in ("low", "medium", "high")

    @patch("backend.agents.prompt_interpreter.ChatGoogleGenerativeAI")
    def test_interpret_has_reasoning(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_interpreted_attack()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = AttackPromptInterpreter()
        result = agent.interpret("steal customer credit card data")
        assert result.reasoning and len(result.reasoning) > 0

    @patch("backend.agents.prompt_interpreter.ChatGoogleGenerativeAI")
    def test_interpret_empty_prompt_raises(self, mock_llm_class):
        agent = AttackPromptInterpreter()
        with pytest.raises(ValueError):
            agent.interpret("")

    @patch("backend.agents.prompt_interpreter.ChatGoogleGenerativeAI")
    def test_interpret_attack_type_is_valid_enum(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = _make_interpreted_attack()
        mock_llm.with_structured_output.return_value = mock_chain

        agent = AttackPromptInterpreter()
        result = agent.interpret("try to brute force the login")
        assert result.attack_type in list(AttackType)

    @patch("backend.agents.prompt_interpreter.ChatGoogleGenerativeAI")
    def test_interpret_all_scenario_ids_mappable(self, mock_llm_class):
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm

        for scenario_id in VALID_SCENARIO_IDS:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = _make_interpreted_attack(scenario_id)
            mock_llm.with_structured_output.return_value = mock_chain

            agent = AttackPromptInterpreter()
            result = agent.interpret("some attack prompt")
            assert result.scenario_id == scenario_id
