"""
Phase-based metric snapshots for the NovaPay dashboard.
Each phase_id maps to realistic metric values for that point in the attack.
The frontend displays these directly — no client-side calculation needed.
"""

HEALTHY_METRICS = {
    "txPerSec": 42,
    "activeUsers": 1284,
    "apiLatencyMs": 38,
    "uptimePct": 99.97,
}

# Maps phase_id → metric snapshot
# Values represent the peak/representative state during that phase.
PHASE_METRICS: dict[str, dict] = {
    # --- Account Takeover ---
    "recon": {
        "txPerSec": 44,
        "activeUsers": 1280,
        "apiLatencyMs": 52,
        "uptimePct": 99.97,
    },
    "brute_force": {
        "txPerSec": 38,
        "activeUsers": 1190,
        "apiLatencyMs": 340,
        "uptimePct": 99.81,
    },
    "2fa_bypass": {
        "txPerSec": 35,
        "activeUsers": 1050,
        "apiLatencyMs": 480,
        "uptimePct": 99.60,
    },
    "account_lock": {
        "txPerSec": 28,
        "activeUsers": 720,
        "apiLatencyMs": 620,
        "uptimePct": 99.10,
    },

    # --- Transaction Fraud ---
    "login": {
        "txPerSec": 43,
        "activeUsers": 1290,
        "apiLatencyMs": 41,
        "uptimePct": 99.97,
    },
    "probe": {
        "txPerSec": 55,
        "activeUsers": 1295,
        "apiLatencyMs": 68,
        "uptimePct": 99.95,
    },
    "large_transfer": {
        "txPerSec": 62,
        "activeUsers": 1300,
        "apiLatencyMs": 120,
        "uptimePct": 99.90,
    },
    "api_scrape": {
        "txPerSec": 310,
        "activeUsers": 1240,
        "apiLatencyMs": 890,
        "uptimePct": 99.40,
    },

    # --- SQL Injection ---
    "malformed_queries": {
        "txPerSec": 36,
        "activeUsers": 1260,
        "apiLatencyMs": 180,
        "uptimePct": 99.90,
    },
    "injection": {
        "txPerSec": 22,
        "activeUsers": 980,
        "apiLatencyMs": 760,
        "uptimePct": 98.80,
    },
    "table_dump": {
        "txPerSec": 8,
        "activeUsers": 540,
        "apiLatencyMs": 1840,
        "uptimePct": 97.20,
    },

    # --- Insider Threat ---
    "offhours_login": {
        "txPerSec": 6,
        "activeUsers": 12,
        "apiLatencyMs": 44,
        "uptimePct": 99.97,
    },
    "mass_access": {
        "txPerSec": 9,
        "activeUsers": 14,
        "apiLatencyMs": 210,
        "uptimePct": 99.85,
    },
    "pii_download": {
        "txPerSec": 4,
        "activeUsers": 14,
        "apiLatencyMs": 390,
        "uptimePct": 99.70,
    },
    "external_transfer": {
        "txPerSec": 2,
        "activeUsers": 14,
        "apiLatencyMs": 520,
        "uptimePct": 99.50,
    },

    # --- DDoS Attack ---
    "normal_traffic": HEALTHY_METRICS,
    "traffic_spike": {
        "txPerSec": 2400,
        "activeUsers": 890,
        "apiLatencyMs": 820,
        "uptimePct": 99.50,
    },
    "gateway_degradation": {
        "txPerSec": 5800,
        "activeUsers": 420,
        "apiLatencyMs": 3200,
        "uptimePct": 96.10,
    },
    "botnet_flood": {
        "txPerSec": 9100,
        "activeUsers": 95,
        "apiLatencyMs": 6400,
        "uptimePct": 91.40,
    },
}


def get_metrics_for_phase(phase_id: str) -> dict:
    """Return metric snapshot for a given phase ID, or healthy metrics if unknown."""
    return PHASE_METRICS.get(phase_id, HEALTHY_METRICS)
