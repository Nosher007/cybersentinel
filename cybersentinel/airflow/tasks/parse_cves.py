"""
TICKET-023 — parse_and_clean task.
Takes raw CVE dicts from the NVD API and extracts the fields
needed for embedding and ChromaDB storage.
"""


def parse_cve(cve: dict) -> dict:
    cve_id = cve.get("id", "UNKNOWN")
    published = cve.get("published", "")

    descriptions = cve.get("descriptions", [])
    description = next(
        (d["value"] for d in descriptions if d.get("lang") == "en"),
        ""
    )

    metrics = cve.get("metrics", {})
    cvss_list = metrics.get("cvssMetricV31", [{}])
    cvss_data = (cvss_list[0] if cvss_list else {}).get("cvssData", {})
    severity = cvss_data.get("baseSeverity", "UNKNOWN")
    base_score = cvss_data.get("baseScore", 0.0)

    text = f"{cve_id}: {description} Severity: {severity}. Score: {base_score}."

    return {
        "cve_id": cve_id,
        "description": description,
        "severity": severity,
        "base_score": base_score,
        "published": published,
        "text": text,
    }


def parse_cves(raw_cves: list[dict]) -> list[dict]:
    return [parse_cve(cve) for cve in raw_cves]
