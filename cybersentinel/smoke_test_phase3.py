"""
TEST-PHASE-3 Smoke Test
=======================
Runs a full attack prompt through all 5 agents end-to-end:
  AttackPromptInterpreter → LogParser → ThreatDetector → SeverityClassifier → RemediationAgent

Usage:
    cd cybersentinel
    python smoke_test_phase3.py
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

from backend.agents.prompt_interpreter import AttackPromptInterpreter
from backend.agents.orchestrator import build_pipeline
from backend.models.logs import LogType
from simulation.log_generators.auth_logs import generate_auth_log

ATTACK_PROMPT = "try to brute force the login system"
SINGLE_IP = "45.33.32.156"


def generate_brute_force_logs(n: int = 15) -> list[tuple[str, str]]:
    """Generate realistic brute force log lines from a single IP."""
    import re
    logs = []
    for _ in range(n):
        raw = generate_auth_log("failure")
        raw = re.sub(r"ip=\S+", f"ip={SINGLE_IP}", raw)
        logs.append((raw, LogType.AUTH.value))
    logs.append((generate_auth_log("lockout"), LogType.AUTH.value))
    return logs


def main():
    print("=" * 60)
    print("  CyberSentinel — TEST-PHASE-3 Smoke Test")
    print("=" * 60)

    # ── Step 1: Interpret the attack prompt ───────────────────────
    print(f"\n[1/3] Interpreting prompt: \"{ATTACK_PROMPT}\"")
    interpreter = AttackPromptInterpreter()
    interpreted = interpreter.interpret(ATTACK_PROMPT)
    print(f"      attack_type   : {interpreted.attack_type.value}")
    print(f"      target_service: {interpreted.target_service}")
    print(f"      intensity     : {interpreted.intensity}")
    print(f"      scenario_id   : {interpreted.scenario_id}")
    print(f"      reasoning     : {interpreted.reasoning}")

    # ── Step 2: Generate logs matching the scenario ───────────────
    print(f"\n[2/3] Generating brute force logs (16 lines, IP={SINGLE_IP})")
    raw_logs = generate_brute_force_logs()
    print(f"      Generated {len(raw_logs)} log lines")
    print(f"      Sample: {raw_logs[0][0]}")

    # ── Step 3: Run full LangGraph pipeline ───────────────────────
    print("\n[3/3] Running LangGraph pipeline (LogParser -> ThreatDetector -> SeverityClassifier -> Remediation)...")
    pipeline = build_pipeline()
    result = pipeline.invoke({"raw_logs": raw_logs})

    if result.get("error"):
        print(f"\n  PIPELINE ERROR: {result['error']}")
        return

    plan = result["remediation_plan"]
    threat = result["scored_threat"]

    # ── Output ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  THREAT DETECTED")
    print("=" * 60)
    print(f"  Attack Type    : {threat.threat.attack_type.value}")
    print(f"  Affected Service: {threat.threat.affected_service}")
    print(f"  Severity       : {threat.severity.value}  (score: {threat.score}/10)")
    print(f"  Justification  : {threat.justification}")
    print(f"  Blast Radius   : {', '.join(threat.blast_radius) or 'none'}")

    print("\n" + "=" * 60)
    print("  REMEDIATION PLAN")
    print("=" * 60)
    print(f"  Summary: {plan.summary}\n")

    print("  IMMEDIATE STEPS:")
    for step in plan.immediate_steps:
        print(f"    {step.order}. {step.action}")
        print(f"       {step.detail}")

    print("\n  HARDENING STEPS:")
    for step in plan.hardening_steps:
        print(f"    {step.order}. {step.action}")
        print(f"       {step.detail}")

    if plan.cve_references:
        print(f"\n  CVE REFERENCES: {', '.join(plan.cve_references)}")

    print("\n" + "=" * 60)
    print("  TEST-PHASE-3 PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
