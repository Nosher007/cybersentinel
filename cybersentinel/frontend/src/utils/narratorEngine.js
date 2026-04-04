/**
 * narratorEngine.js
 * Maps actual log tags → plain English sentences for non-technical users.
 * Keys are lowercase versions of what appears inside [...] in log lines.
 */

const LOG_TAG_NARRATIONS = {
  // ── Account Takeover ──────────────────────────────────────────
  recon:        "An attacker is quietly scanning the login system, looking for weaknesses before making a move.",
  brute_force:  "Thousands of rapid password attempts are flooding the login system. Someone is trying to guess their way in.",
  '2fa_bypass': "The attacker is now trying to bypass two-factor authentication — attempting to intercept or skip the second verification step.",
  account_lock: "Multiple user accounts are being locked out from repeated failed login attempts. Real users can no longer sign in.",

  // ── Transaction Fraud ─────────────────────────────────────────
  login:         "A suspicious user has logged in and is quietly observing the payment system.",
  probe:         "Small test transactions are being made — the attacker is checking how much money can be moved without triggering alerts.",
  large_transfer:"A large unauthorized transfer is being attempted. The attacker is moving significant funds out of NovaPay accounts.",
  api_scrape:    "The attacker is rapidly scraping the API, harvesting account data in bulk at an abnormal rate.",

  // ── SQL Injection ─────────────────────────────────────────────
  normal:    null,
  malformed: "Unusual database queries are being sent — the attacker is probing for SQL injection vulnerabilities.",
  inject:    "A successful SQL injection is underway. The attacker has gained unauthorized access to the database.",
  dump:      "The database is being dumped. Customer records, account details, and transaction history are being extracted.",

  // ── DDoS Attack (service tags embedded in logs) ───────────────
  nginx:    null,
  'api-gw': "The API gateway is struggling to keep up. Response times are climbing and requests are being dropped.",
  botnet:   "A coordinated botnet is hammering NovaPay with traffic from thousands of IP addresses worldwide. The payment system is becoming unavailable to real users.",

  // ── Insider Threat (service tags embedded in logs) ────────────
  auth:       "An admin account has logged in at an unusual hour — activity outside normal business hours.",
  db:         "An admin user is accessing large volumes of customer records. This is far beyond normal operations.",
  compliance: "Sensitive personal data is being transferred to an external destination. A potential data breach is in progress.",
}

// Attack type → plain intro sentence
const ATTACK_TYPE_INTROS = {
  brute_force:       "An attacker systematically tried every possible password combination to break into the system.",
  account_takeover:  "An attacker gained unauthorized access to a user account by bypassing authentication controls.",
  transaction_fraud: "Fraudulent transactions were made from a compromised account, moving funds without the owner's knowledge.",
  sql_injection:     "Malicious code was injected into database queries, giving the attacker direct access to customer data.",
  data_exfiltration: "Sensitive customer data was extracted from NovaPay's systems without authorization.",
  insider_threat:    "A trusted user with elevated access misused their privileges to access and export sensitive data.",
  ddos:              "NovaPay's servers were flooded with fake traffic from thousands of machines, making the platform unavailable to real users.",
  ddos_attack:       "NovaPay's servers were flooded with fake traffic from thousands of machines, making the platform unavailable to real users.",
}

/**
 * Find first [TAG] anywhere in the log line and return plain English narration.
 * Returns null if the tag is not notable (e.g. normal traffic).
 */
export function getNarrationFromLog(logLine) {
  if (!logLine) return null
  const match = logLine.match(/\[([A-Z0-9_-]+)\]/)
  if (!match) return null
  const tag = match[1].toLowerCase()
  const narration = LOG_TAG_NARRATIONS[tag]
  return narration ?? null  // undefined → null, null stays null (explicit "no narration")
}

/**
 * Build plain English summary from a threat_detected payload.
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
