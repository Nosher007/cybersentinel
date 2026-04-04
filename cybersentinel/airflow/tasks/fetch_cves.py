"""
TICKET-022 — fetch_cves task.
Hits the NVD API and returns raw CVE records published in the last 24 hours.
"""
import os
import requests
from datetime import datetime, timedelta, timezone

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.000"


def fetch_cves(hours_back: int = 24) -> list[dict]:
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours_back)

    params = {
        "pubStartDate": start.strftime(DATE_FORMAT),
        "pubEndDate": now.strftime(DATE_FORMAT),
    }

    headers = {}
    api_key = os.getenv("NVD_API_KEY")
    if api_key:
        headers["apiKey"] = api_key

    response = requests.get(NVD_API_URL, params=params, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    vulnerabilities = data.get("vulnerabilities", [])

    return [item["cve"] for item in vulnerabilities]
