"""
TICKET-014 — Seed ChromaDB with 20 CVEs and 5 OWASP playbook entries.
Uses ChromaDB default embedding (no OpenAI key needed for seeding).
Idempotent — safe to run multiple times.
"""
from backend.rag.chromadb_client import get_collection

CVE_ENTRIES = [
    {"id": "CVE-2021-44228", "cve_id": "CVE-2021-44228", "severity": "CRITICAL", "type": "cve",
     "text": "Log4Shell: Remote code execution in Apache Log4j2 via JNDI lookup in log messages. Affects versions 2.0-2.14.1. Remediation: upgrade to 2.15.0+, disable JNDI lookups."},
    {"id": "CVE-2021-26855", "cve_id": "CVE-2021-26855", "severity": "CRITICAL", "type": "cve",
     "text": "ProxyLogon: SSRF in Microsoft Exchange allowing unauthenticated HTTP requests. Allows full mailbox access and RCE. Remediation: apply KB5000871 patch immediately."},
    {"id": "CVE-2017-5638", "cve_id": "CVE-2017-5638", "severity": "CRITICAL", "type": "cve",
     "text": "Apache Struts2 RCE via Content-Type header injection. Used in Equifax breach. Remediation: upgrade Struts, validate Content-Type headers, deploy WAF rules."},
    {"id": "CVE-2019-0708", "cve_id": "CVE-2019-0708", "severity": "CRITICAL", "type": "cve",
     "text": "BlueKeep: Wormable RCE in Windows RDP. Unauthenticated attacker executes arbitrary code. Remediation: patch KB4499175, disable RDP if unused, enable NLA."},
    {"id": "CVE-2014-0160", "cve_id": "CVE-2014-0160", "severity": "HIGH", "type": "cve",
     "text": "Heartbleed: OpenSSL buffer over-read leaking private keys and session tokens from memory. Remediation: upgrade OpenSSL, revoke and reissue certificates, invalidate sessions."},
    {"id": "CVE-2021-34527", "cve_id": "CVE-2021-34527", "severity": "CRITICAL", "type": "cve",
     "text": "PrintNightmare: Windows Print Spooler RCE with SYSTEM privileges. Affects all Windows versions. Remediation: disable Print Spooler, apply KB5004945, restrict Point and Print."},
    {"id": "CVE-2020-1472", "cve_id": "CVE-2020-1472", "severity": "CRITICAL", "type": "cve",
     "text": "Zerologon: Netlogon privilege escalation enabling full domain takeover. Attacker impersonates domain controller. Remediation: apply patch, enable secure channel enforcement."},
    {"id": "CVE-2022-30190", "cve_id": "CVE-2022-30190", "severity": "HIGH", "type": "cve",
     "text": "Follina: MSDT RCE triggered via Office documents without macros. Remediation: disable MSDT URL protocol, apply MSDT patch, block ms-msdt URIs at perimeter."},
    {"id": "CVE-2021-21985", "cve_id": "CVE-2021-21985", "severity": "CRITICAL", "type": "cve",
     "text": "VMware vCenter RCE via vSAN Health Check. Unauthenticated admin-level code execution. Remediation: upgrade to vCenter 7.0 U2b+, restrict vCenter network access."},
    {"id": "CVE-2018-7600", "cve_id": "CVE-2018-7600", "severity": "CRITICAL", "type": "cve",
     "text": "Drupalgeddon2: Drupal CMS RCE via form API property injection. No authentication required. Remediation: upgrade to Drupal 7.58 or 8.5.1+, apply SA-CORE-2018-002."},
    {"id": "CVE-2019-11510", "cve_id": "CVE-2019-11510", "severity": "CRITICAL", "type": "cve",
     "text": "Pulse Secure VPN arbitrary file read exposing credentials and session tokens. Remediation: upgrade to 8.1R15.1+, reset all passwords, revoke active sessions."},
    {"id": "CVE-2020-0601", "cve_id": "CVE-2020-0601", "severity": "HIGH", "type": "cve",
     "text": "CurveBall: Windows CryptoAPI certificate spoofing enabling HTTPS MITM attacks. Remediation: apply KB4528760, audit certificate trust chains, enable certificate transparency."},
    {"id": "CVE-2022-22965", "cve_id": "CVE-2022-22965", "severity": "CRITICAL", "type": "cve",
     "text": "Spring4Shell: Spring Framework RCE via data binding on JDK 9+. Affects Spring MVC and WebFlux. Remediation: upgrade Spring Framework to 5.3.18+ or 5.2.20+."},
    {"id": "CVE-2021-3156", "cve_id": "CVE-2021-3156", "severity": "HIGH", "type": "cve",
     "text": "Baron Samedit: sudo heap buffer overflow allowing local root privilege escalation. Remediation: upgrade sudo to 1.9.5p2+, restrict sudo access to necessary users only."},
    {"id": "CVE-2023-23397", "cve_id": "CVE-2023-23397", "severity": "CRITICAL", "type": "cve",
     "text": "Outlook zero-click NTLM hash theft via calendar invite. No user interaction required. Remediation: apply March 2023 patch, block TCP 445 outbound, disable NTLM authentication."},
    {"id": "CVE-2022-1388", "cve_id": "CVE-2022-1388", "severity": "CRITICAL", "type": "cve",
     "text": "F5 BIG-IP iControl REST authentication bypass enabling admin RCE. Remediation: upgrade BIG-IP, restrict iControl REST access, apply K23605346 mitigation."},
    {"id": "CVE-2019-19781", "cve_id": "CVE-2019-19781", "severity": "CRITICAL", "type": "cve",
     "text": "Citrix ADC directory traversal leading to unauthenticated RCE. Exploited in ransomware campaigns. Remediation: upgrade Citrix ADC, apply responder policy workaround."},
    {"id": "CVE-2020-5902", "cve_id": "CVE-2020-5902", "severity": "CRITICAL", "type": "cve",
     "text": "F5 BIG-IP TMUI RCE allowing unauthenticated command execution. Remediation: upgrade BIG-IP firmware, restrict TMUI access to management network only."},
    {"id": "CVE-2021-40444", "cve_id": "CVE-2021-40444", "severity": "HIGH", "type": "cve",
     "text": "Microsoft MSHTML RCE via malicious ActiveX control in Office documents. Exploited in targeted attacks. Remediation: apply September 2021 patch, disable ActiveX in Office."},
    {"id": "CVE-2023-44487", "cve_id": "CVE-2023-44487", "severity": "HIGH", "type": "cve",
     "text": "HTTP/2 Rapid Reset DDoS: stream cancellation abuse causing record-breaking volumetric attacks. Remediation: upgrade web servers, implement HTTP/2 stream rate limiting, deploy DDoS protection."},
]

OWASP_ENTRIES = [
    {"id": "OWASP-A01", "category": "Broken Access Control", "type": "owasp",
     "text": "OWASP A01 Broken Access Control: Authentication restrictions not enforced. Attackers access unauthorized data. Remediation: deny-by-default, log access failures, invalidate sessions on logout, implement RBAC."},
    {"id": "OWASP-A02", "category": "Cryptographic Failures", "type": "owasp",
     "text": "OWASP A02 Cryptographic Failures: Weak encryption exposing sensitive data. Remediation: AES-256 at rest, TLS 1.3 in transit, bcrypt for passwords, disable TLS 1.0/1.1, use HSTS headers."},
    {"id": "OWASP-A03", "category": "Injection", "type": "owasp",
     "text": "OWASP A03 Injection: SQL, NoSQL, OS, LDAP injection via hostile input. Remediation: parameterized queries, input validation, ORM usage, least privilege DB accounts, WAF injection rules."},
    {"id": "OWASP-A07", "category": "Identification and Authentication Failures", "type": "owasp",
     "text": "OWASP A07 Authentication Failures: Brute force, credential stuffing, missing MFA. Remediation: enforce MFA, rate limit login endpoints, lock accounts after failed attempts, use secure session tokens."},
    {"id": "OWASP-A09", "category": "Security Logging and Monitoring Failures", "type": "owasp",
     "text": "OWASP A09 Logging Failures: Insufficient logging enables persistent undetected attacks. Remediation: log all auth events, alert on anomalous patterns, off-hours access, bulk exports, multiple failed logins from same IP."},
]


def seed_knowledge_base() -> None:
    col = get_collection()
    existing_ids = set(col.get()["ids"])

    cve_to_add = [e for e in CVE_ENTRIES if e["id"] not in existing_ids]
    owasp_to_add = [e for e in OWASP_ENTRIES if e["id"] not in existing_ids]

    if cve_to_add:
        col.add(
            ids=[e["id"] for e in cve_to_add],
            documents=[e["text"] for e in cve_to_add],
            metadatas=[{"type": e["type"], "severity": e["severity"], "cve_id": e["cve_id"]} for e in cve_to_add],
        )

    if owasp_to_add:
        col.add(
            ids=[e["id"] for e in owasp_to_add],
            documents=[e["text"] for e in owasp_to_add],
            metadatas=[{"type": e["type"], "category": e["category"]} for e in owasp_to_add],
        )
