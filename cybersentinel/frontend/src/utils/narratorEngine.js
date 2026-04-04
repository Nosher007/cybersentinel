/**
 * narratorEngine.js
 * Maps simulation phase IDs and threat data → plain English sentences
 * for non-technical users. No API calls — purely rule-based.
 */

// Phase ID → plain English description
const PHASE_NARRATIONS = {
  // Account Takeover
  recon:         "An attacker is quietly scanning the login system, looking for weaknesses before making a move.",
  brute_force:   "Thousands of rapid password attempts are flooding the login system. Someone is trying to guess their way in.",
  '2fa_bypass':  "The attacker is now trying to bypass two-factor authentication — attempting to intercept or skip the second verification step.",
  account_lock:  "Multiple user accounts are being locked out as a result of repeated failed login attempts. Real users can no longer sign in.",

  // Transaction Fraud
  login:         "A suspicious user has logged in and is quietly observing the payment system.",
  probe:         "Small test transactions are being made — the attacker is checking how much money can be moved without triggering alerts.",
  large_transfer:"A large unauthorized transfer is being attempted. The attacker is moving significant funds out of NovaPay accounts.",
  api_scrape:    "The attacker is rapidly scraping the API, harvesting account data in bulk at an abnormal rate.",

  // SQL Injection
  normal_traffic:    null,
  malformed_queries: "Unusual database queries are being sent — the attacker is probing for SQL injection vulnerabilities.",
  injection:         "A successful SQL injection is underway. The attacker has gained unauthorized access to the database.",
  table_dump:        "The database is being dumped. Customer records, account details, and transaction history are being extracted.",

  // Insider Threat
  offhours_login:   "An admin account has logged in at 2:47 AM — highly unusual activity outside business hours.",
  mass_access:      "An admin user is accessing thousands of customer records at once. This volume of access is far beyond normal operations.",
  pii_download:     "Sensitive personal information — including SSNs, emails, and dates of birth — is being bulk-exported.",
  external_transfer:"Data is being transferred to an external destination. A potential data breach is in progress.",

  // DDoS
  traffic_spike:       "Incoming web traffic is rising rapidly beyond normal levels. The servers are starting to feel the pressure.",
  gateway_degradation: "The API gateway is struggling to keep up. Response times are climbing and some requests are being dropped entirely.",
  botnet_flood:        "A coordinated botnet is hammering NovaPay with traffic from thousands of IP addresses worldwide. The payment system is becoming unavailable to real users.",
}

// Attack type → plain intro sentence for post-analysis narration
const ATTACK_TYPE_INTROS = {
  brute_force:        "An attacker systematically tried every possible password combination to break into the system.",
  account_takeover:   "An attacker gained unauthorized access to a user account by bypassing authentication controls.",
  transaction_fraud:  "Fraudulent transactions were made from a compromised account, moving funds without the account owner's knowledge.",
  sql_injection:      "Malicious code was injected into database queries, giving the attacker direct access to customer data.",
  data_exfiltration:  "Sensitive customer data was extracted from NovaPay's systems without authorization.",
  insider_threat:     "A trusted user with elevated access misused their privileges to access and export sensitive data.",
  ddos:               "NovaPay's servers were flooded with fake traffic from thousands of machines, making the platform unavailable to real users.",
  ddos_attack:        "NovaPay's servers were flooded with fake traffic from thousands of machines, making the platform unavailable to real users.",
}

/**
 * Extract a plain English narration from a raw log line.
 * Returns null if the phase is not notable (e.g. normal_traffic).
 */
export function getNarrationFromLog(logLine) {
  if (!logLine) return null
  const match = logLine.match(/^\[([A-Z0-9_]+)\]/)
  if (!match) return null
  const phaseId = match[1].toLowerCase()
  return PHASE_NARRATIONS[phaseId] ?? null
}

/**
 * Build a plain English summary from a threat_detected payload.
 * Uses the LLM-written justification as the body, with a layman intro.
 */
export function getNarrationFromThreat(threat) {
  if (!threat) return null
  const attackType = threat.attack_type?.toLowerCase().replace(/ /g, '_') ?? ''
  const intro = ATTACK_TYPE_INTROS[attackType] ?? ''
  const justification = threat.justification ?? ''
  return intro && justification
    ? `${intro} ${justification}`
    : intro || justification || null
}
