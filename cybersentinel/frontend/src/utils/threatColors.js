/**
 * Maps scenario_id → ordered list of department escalation phases.
 * Each phase is an object of { departmentId: status } applied after a delay.
 */
export const SCENARIO_DEPARTMENT_PHASES = {
  account_takeover: [
    { auth: 'WARNING' },
    { auth: 'CRITICAL', api: 'WARNING' },
    { auth: 'BREACHED', api: 'CRITICAL' },
  ],
  transaction_fraud: [
    { payments: 'WARNING', api: 'WARNING' },
    { payments: 'CRITICAL', api: 'CRITICAL', database: 'WARNING' },
    { payments: 'BREACHED', database: 'CRITICAL' },
  ],
  sql_injection: [
    { api: 'WARNING', database: 'WARNING' },
    { api: 'CRITICAL', database: 'CRITICAL' },
    { database: 'BREACHED', api: 'BREACHED' },
  ],
  insider_threat: [
    { database: 'WARNING' },
    { database: 'CRITICAL', auth: 'WARNING' },
    { database: 'BREACHED', auth: 'CRITICAL' },
  ],
  ddos_attack: [
    { network: 'WARNING', api: 'WARNING' },
    { network: 'CRITICAL', api: 'CRITICAL', payments: 'WARNING' },
    { network: 'BREACHED', api: 'BREACHED', payments: 'CRITICAL' },
  ],
}

export const PHASE_DELAY_MS = 4000

export const SEVERITY_COLORS = {
  CRITICAL: 'text-red-400',
  HIGH: 'text-orange-400',
  MEDIUM: 'text-amber-400',
  LOW: 'text-yellow-400',
}
