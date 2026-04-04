"""
Maps log tags → NovaPay metric snapshots.
Keys are the actual tags that appear inside [...] in emitted log lines.
The websocket router uses re.search to find the first [TAG] in each log.
"""

HEALTHY_METRICS = {
    "txPerSec": 42,
    "activeUsers": 1284,
    "apiLatencyMs": 38,
    "uptimePct": 99.97,
}

LOG_TAG_METRICS: dict[str, dict] = {

    # ── Account Takeover ──────────────────────────────────────────
    # logs: [RECON] ..., [BRUTE_FORCE] ..., [2FA_BYPASS] ..., [ACCOUNT_LOCK] ...
    "RECON": {
        "txPerSec": 44,
        "activeUsers": 1280,
        "apiLatencyMs": 52,
        "uptimePct": 99.97,
    },
    "BRUTE_FORCE": {
        "txPerSec": 38,
        "activeUsers": 1190,
        "apiLatencyMs": 340,
        "uptimePct": 99.81,
    },
    "2FA_BYPASS": {
        "txPerSec": 35,
        "activeUsers": 1050,
        "apiLatencyMs": 480,
        "uptimePct": 99.60,
    },
    "ACCOUNT_LOCK": {
        "txPerSec": 28,
        "activeUsers": 720,
        "apiLatencyMs": 620,
        "uptimePct": 99.10,
    },

    # ── Transaction Fraud ─────────────────────────────────────────
    # logs: [LOGIN] ..., [PROBE] ..., [LARGE_TRANSFER] ..., [API_SCRAPE] ...
    "LOGIN": {
        "txPerSec": 43,
        "activeUsers": 1290,
        "apiLatencyMs": 41,
        "uptimePct": 99.97,
    },
    "PROBE": {
        "txPerSec": 55,
        "activeUsers": 1295,
        "apiLatencyMs": 68,
        "uptimePct": 99.95,
    },
    "LARGE_TRANSFER": {
        "txPerSec": 62,
        "activeUsers": 1300,
        "apiLatencyMs": 120,
        "uptimePct": 99.90,
    },
    "API_SCRAPE": {
        "txPerSec": 310,
        "activeUsers": 1240,
        "apiLatencyMs": 890,
        "uptimePct": 99.40,
    },

    # ── SQL Injection ─────────────────────────────────────────────
    # logs: [NORMAL] ..., [MALFORMED] ..., [INJECT] ..., [DUMP] ...
    "NORMAL": HEALTHY_METRICS,
    "MALFORMED": {
        "txPerSec": 36,
        "activeUsers": 1260,
        "apiLatencyMs": 180,
        "uptimePct": 99.90,
    },
    "INJECT": {
        "txPerSec": 22,
        "activeUsers": 980,
        "apiLatencyMs": 760,
        "uptimePct": 98.80,
    },
    "DUMP": {
        "txPerSec": 8,
        "activeUsers": 540,
        "apiLatencyMs": 1840,
        "uptimePct": 97.20,
    },

    # ── DDoS Attack ───────────────────────────────────────────────
    # logs contain embedded service tags: [NGINX], [API-GW], [BOTNET]
    "NGINX": HEALTHY_METRICS,
    "API-GW": {
        "txPerSec": 5800,
        "activeUsers": 420,
        "apiLatencyMs": 3200,
        "uptimePct": 96.10,
    },
    "BOTNET": {
        "txPerSec": 9100,
        "activeUsers": 95,
        "apiLatencyMs": 6400,
        "uptimePct": 91.40,
    },

    # ── Insider Threat ────────────────────────────────────────────
    # logs contain embedded service tags: [AUTH], [DB], [COMPLIANCE]
    "AUTH": {
        "txPerSec": 6,
        "activeUsers": 12,
        "apiLatencyMs": 44,
        "uptimePct": 99.97,
    },
    "DB": {
        "txPerSec": 4,
        "activeUsers": 14,
        "apiLatencyMs": 390,
        "uptimePct": 99.70,
    },
    "COMPLIANCE": {
        "txPerSec": 2,
        "activeUsers": 14,
        "apiLatencyMs": 520,
        "uptimePct": 99.50,
    },
}


def get_metrics_for_tag(tag: str) -> dict | None:
    """Return metric snapshot for a log tag, or None if not a known attack tag."""
    return LOG_TAG_METRICS.get(tag)
